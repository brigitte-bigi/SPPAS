# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.audiomaplayer.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: An audio player based on the library "miniaudio".

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

Description:
============

A simple audio player based on miniaudio library.
https://github.com/irmen/pyminiaudio

Unlike PyAudio and sounddevice, miniaudio does not rely on PortAudio and it
plays the stream from its own native audio thread (WASAPI/CoreAudio/ALSA/
PulseAudio). The raw PCM frames are fed to it through a generator yielding
'memoryview' slices - no numpy involved.

To prevent the "cracha" (buffer underruns) caused by Python's garbage
collector pausing while the audio thread needs data, the garbage collector
is disabled during playback and a large buffer is used to absorb scheduling
pauses.

Notice that the miniaudio device only allows to play/stop; seek, tell
or pause are not supported. There are then implemented here with wx, so a
wx.App() must be created in order to use this player.

Example:
========

    >>> p = sppasAudioPlayer(owner=FRAME)
    >>> p.load("audio.wav")
    >>> if p.prepare_play(0., p.get_duration()) is True:
    >>>     p.play()

"""

import os
import gc
import logging
import miniaudio
import datetime
import wx

from sppas.core.coreutils import b
from sppas.core.config import paths
import audioopy.aio
from sppas.ui.wxapp.page_editor.media.mediaevents import MediaEvents

from .penum import PlayerState
from .penum import PlayerType
from .baseplayer import sppasBasePlayer

# ---------------------------------------------------------------------------
# Garbage collector control, shared by all the audio players.
# The gc is disabled while at least one audio is playing, and enabled again
# only when the last one stopped. It avoids gc pauses to interrupt the feeding
# of the hardware buffer - the cause of the "cracha" playback artifacts.
# ---------------------------------------------------------------------------

_gc_disable_count = 0


def _acquire_gc_disable():
    """Disable the garbage collector for the duration of a playback."""
    global _gc_disable_count
    if _gc_disable_count == 0:
        gc.disable()
    _gc_disable_count += 1


def _release_gc_disable():
    """Re-enable the garbage collector when no more audio is playing."""
    global _gc_disable_count
    if _gc_disable_count > 0:
        _gc_disable_count -= 1
        if _gc_disable_count == 0:
            gc.enable()

# ---------------------------------------------------------------------------


class sppasAudioPlayer(sppasBasePlayer):
    """An audio player based on miniaudio library and wx.

    Load/play/pause/stop/seek throw the audio stream of a given file.

    """

    # Duration of the device buffer, in milliseconds. A large buffer absorbs
    # the garbage collector and scheduling pauses that would otherwise starve
    # the audio thread. Raise it if underruns ("cracha") still occur.
    BUFFER_MSEC = 250

    def __init__(self, owner):
        super(sppasAudioPlayer, self).__init__(owner)

        # Delay in seconds to update the position value in the stream
        # and to notify.
        if wx.Platform == "__WXMSW__":
            self._time_delay = 0.015
        else:
            self._time_delay = 0.010

        # Loaded frames of the audio stream
        self._frames = b("")

        # True when the feeding generator reached the end of the frames
        self.__done = False
        # True when this player currently holds a gc-disable request
        self.__gc_held = False

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        sppasBasePlayer.reset(self)
        self._frames = b("")
        if self._player is not None:
            self.stop()

    # -----------------------------------------------------------------------

    def _load(self, filename):
        """Load all the frames of the file that filename refers to.

        :param filename: (str) Name of an audio file
        :return: (bool) True if both successfully opened and loaded.

        """
        self.reset()
        self._filename = filename
        self._ms = PlayerState().loading

        try:
            self._media = audioopy.aio.open(filename)
        except Exception as e:
            logging.error("File {:s} not opened: {:s}".format(filename, str(e)))
            self._media = None
            self._ms = PlayerState().unknown
            self._mt = PlayerType().unknown
        else:
            try:
                self._frames = self._media.read_frames(self._media.get_nframes())
                self._media.rewind()
                self._ms = PlayerState().stopped
                self._mt = PlayerType().audio
                logging.info("Audio frames {:s} successfully loaded".format(filename))
                return True

            except Exception as e:
                logging.error("Audio frames {:s} not loaded: {:s}".format(filename, str(e)))
                self._media = None
                self._ms = PlayerState().unknown
                self._mt = PlayerType().unsupported

        return False

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Launch the player. Fix the start time of playing.

        """
        try:
            frames = self._extract_frames()
            # Ask miniaudio library to play a buffer of frames
            if len(frames) > 0:
                # Close a previously paused device, if any
                self._close_device()

                self.__done = False
                view = memoryview(frames)
                frame_size = self._media.get_sampwidth() * self._media.get_nchannels()

                def _pcm_stream():
                    # Feed raw PCM frames to miniaudio's audio thread. Yields
                    # 'memoryview' slices of the already loaded frames: no copy,
                    # no allocation, minimal Python work in the callback.
                    required_frames = yield b""  # generator initialization
                    pos = 0
                    while True:
                        required_bytes = required_frames * frame_size
                        sample_data = view[pos:pos + required_bytes]
                        pos += len(sample_data)
                        if len(sample_data) == 0:
                            self.__done = True
                            break
                        required_frames = yield sample_data

                stream = _pcm_stream()
                next(stream)  # start the generator

                # Disable the gc and open a large-buffered device, then play
                _acquire_gc_disable()
                self.__gc_held = True
                self._player = miniaudio.PlaybackDevice(
                    output_format=self._sampleformat_from_sampwidth(self._media.get_sampwidth()),
                    nchannels=self._media.get_nchannels(),
                    sample_rate=self._media.get_framerate(),
                    buffersize_msec=sppasAudioPlayer.BUFFER_MSEC)
                self._player.start(stream)
                self._start_datenow = datetime.datetime.now()
                return True

            else:
                logging.warning("No frames to play in the given period "
                                "for audio {:s}.".format(self._filename))

        except Exception as e:
            self.stop()
            logging.error("An error occurred when attempted to play "
                          "the audio stream of {:s} with the "
                          "miniaudio library: {:s}".format(self._filename, str(e)))

        self._start_datenow = None
        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        if self._player is not None:
            if self._ms == PlayerState().playing:
                # set our state
                self._ms = PlayerState().paused
                # stop the thread
                self._th.join()
                # stop playing the device
                try:
                    self._player.stop()
                except Exception:
                    pass
                self._release_gc()
                # seek at the exact moment we asked to stop to play
                self._update_now()
                return True

        return False

    # -----------------------------------------------------------------------

    def _stop(self):
        """Really stops the player."""
        self._close_device()
        self._release_gc()

    # -----------------------------------------------------------------------

    def _close_device(self):
        """Stop and close the miniaudio device if any."""
        if self._player is not None:
            try:
                self._player.stop()
                self._player.close()
            except Exception:
                pass
            self._player = None

    # -----------------------------------------------------------------------

    def _release_gc(self):
        """Release this player's gc-disable request, if held."""
        if self.__gc_held is True:
            _release_gc_disable()
            self.__gc_held = False

    # -----------------------------------------------------------------------

    def _seek(self, time_pos=0):
        """Seek the audio stream at the given position in time.

        :param time_pos: (float) A valid time in seconds

        """
        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # how many frames this time position is representing since the beginning
        self._from_time = float(time_pos)
        position = int(self._from_time * self._media.get_framerate())
        if self._period is not None and self._from_time > self._period[1]:
            self.stop()

        # seek at the expected position
        try:
            self._media.seek(int(position))
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()
        except:
            # It can happen if we attempted to seek after the audio length
            self.stop()
            return False

        return True

    # -----------------------------------------------------------------------

    def media_tell(self):
        if self._ms not in (PlayerState().unknown, PlayerState().loading):
            return self._media.tell()
        return 0

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the audio stream (float)."""
        offset = self.media_tell()
        return float(offset * self._media.get_nchannels()) / float(self._media.get_framerate())

    # -----------------------------------------------------------------------
    # About the audio
    # -----------------------------------------------------------------------

    def get_nchannels(self):
        """Return the number of channels."""
        if self._media is not None:
            return self._media.get_nchannels()
        return 0

    # -----------------------------------------------------------------------

    def get_sampwidth(self):
        if self._media is not None:
            return self._media.get_sampwidth()
        return 0

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._media is not None:
            return self._media.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_duration(self):
        if self._media is not None:
            return self._media.get_duration()
        return 0.

    # -----------------------------------------------------------------------

    def get_frames(self):
        """Return the frames of the audio."""
        return self._frames

    # -----------------------------------------------------------------------
    # Override base class
    # -----------------------------------------------------------------------

    @staticmethod
    def _sampleformat_from_sampwidth(sampwidth):
        """Return the miniaudio sample format matching the given sample width.

        :param sampwidth: (int) Number of bytes of a sample
        :return: (miniaudio.SampleFormat)

        """
        formats = {
            1: miniaudio.SampleFormat.UNSIGNED8,
            2: miniaudio.SampleFormat.SIGNED16,
            3: miniaudio.SampleFormat.SIGNED24,
            4: miniaudio.SampleFormat.SIGNED32,
        }
        return formats[sampwidth]

    # -----------------------------------------------------------------------

    def _extract_frames(self):
        """Return the frames to play in the currently stored time values.

        """
        #logging.debug(" ... {} extract frame for the period: {} {}"
        #              "".format(self._filename, self._from_time, self._period[1]))
        # Check if the current period is inside or overlapping this audio
        if self._from_time < self._period[1]:
            # Convert the time (in seconds) into a position in the frames
            start_pos = self._time_to_frames(self._from_time)
            end_pos = self._time_to_frames(self._period[1])
            logging.debug("  -> audio player {:s} - offsets range: {}, {}"
                          "".format(self._filename, start_pos, end_pos))
            return self._frames[start_pos:end_pos]

        return b("")

    # -----------------------------------------------------------------------

    def _time_to_frames(self, time_value):
        return int(time_value * float(self._media.get_framerate())) * \
               self._media.get_sampwidth() * \
               self._media.get_nchannels()

    # -----------------------------------------------------------------------

    def _update_now(self):
        """Consider that current time is the start of playing.

        Needed if the player is different of the object stream...
        The current position in the played stream is estimated using the
        delay between the stored time value and now().

        :return: (datetime) New time value

        """
        position = self.reposition_stream()
        self._start_datenow = datetime.datetime.now()
        self._from_time = position / float(self._media.get_framerate())

    # -----------------------------------------------------------------------

    def reposition_stream(self):
        """Seek the media at the current position in the played stream.

        Needed if the player is different of the object stream...
        The current position in the played stream is estimated using the
        delay between the stored time value and now().

        :return: (int) New position or -1 if no change

        """
        if self._start_datenow is None:
            return -1
        cur_time_value = datetime.datetime.now()
        time_delta = cur_time_value - self._start_datenow
        delta = time_delta.total_seconds()

        # how many frames this new time is representing
        position = (self._from_time + delta) * float(self._media.get_framerate())

        # if the position is after the end of the audio file
        if position > self._media.get_nframes():
            position = self._media.get_nframes()

        # seek at the new position in the media
        self._media.seek(int(position))
        # logging.debug(" > audio seek at: pos={} time={} delta={}".format(position, self._media.tell(), cur_time_value, delta))
        return position

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        if self._player is None:
            self.stop()
            return

        # Nothing to do if we are not playing (probably paused).
        if self._ms == PlayerState().playing:
            if self.__done is True:
                # the audio stream reached the end of the frames and it stopped
                self.stop()
            else:
                # the audio stream is currently playing
                self.reposition_stream()

            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

        elif self._ms != PlayerState().paused:
            self.stop()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Audio MaPlayer")

        # The player!
        self.ap = sppasAudioPlayer(owner=self)

        # Actions to perform with the player
        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)
        sizer = wx.BoxSizer()
        sizer.Add(btn2, 0, wx.ALL, 4)
        sizer.Add(btn3, 0, wx.ALL, 4)
        sizer.Add(btn4, 0, wx.ALL, 4)

        # a slider to display the current position
        self.slider = wx.Slider(self, -1, 0, 0, 10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.slider.SetMinSize(wx.Size(250, -1))
        self.Bind(wx.EVT_SLIDER, self._on_seek_slider, self.slider)

        # Organize items
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(sizer, 1, wx.EXPAND)
        main_sizer.Add(self.slider, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        # Events
        # Custom event to inform the media is loaded
        self.ap.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.ap.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every 10ms (in theory) when the audio is playing
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "samples-eng", "oriana2.WAV"))

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Audio file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Audio file not loaded")
        self.FindWindow("btn_play").Enable(False)
        self.slider.SetRange(0, 0)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()
        self.slider.SetValue(int(self.ap.tell()*1000.))

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()
        self.slider.SetValue(0)

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def _on_seek_slider(self, event):
        time_pos_ms = self.slider.GetValue()
        self.ap.seek(float(time_pos_ms) / 1000.)
