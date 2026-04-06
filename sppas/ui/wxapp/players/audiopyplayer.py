# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.audiopyplayer.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: An audio player based on the library "PyAudio".

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

A simple audio player based on PyAudio library.
http://people.csail.mit.edu/hubert/pyaudio/docs/

Notice that the PyAudio Stream library only allows to play/stop; seek, tell
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
import logging
import pyaudio
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


class sppasAudioPlayer(sppasBasePlayer):
    """An audio player based on simpleaudio library and wx.

    Load/play/pause/stop/seek throw the audio stream of a given file.

    """

    def __init__(self, owner):
        super(sppasAudioPlayer, self).__init__(owner)

        # PyAudio
        self.__pya = pyaudio.PyAudio()

        # Delay in seconds to update the position value in the stream
        # and to notify.
        if wx.Platform == "__WXMSW__":
            self._time_delay = 0.015
        else:
            self._time_delay = 0.010

        # Loaded frames of the audio stream
        self._frames = b("")

    # -----------------------------------------------------------------------

    def __del__(self):
        self.__pya.terminate()

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
            # Ask PyAudio library to play a buffer of frames
            if len(frames) > 0:
                # Open a Stream object to write the frames of the audio to.
                # 'output = True' indicates that the sound will be played rather than recorded
                self._player = self.__pya.open(
                    format=self.__pya.get_format_from_width(self._media.get_sampwidth()),
                    channels=self._media.get_nchannels(),
                    rate=self._media.get_framerate(),
                    output=True)

                # Play the sound by writing the audio data to the stream
                # Send a chunk of frames.
                chunk = self._media.get_framerate() // 10

                # reposition in stream since it was asked to start playing the frames
                cur_time_value = datetime.datetime.now()
                # since how many time we started "play_process" but we did not played...
                time_delta = cur_time_value - self._start_datenow
                delta = time_delta.total_seconds()
                # how many frames this delta is representing
                position = round(delta * float(self._media.get_framerate()))

                # Check if the stream is really ready then play
                if self._player.is_active() is True and position < len(frames):
                    while self._ms == PlayerState().playing:
                        # if we reached the end of the frames
                        if position >= len(frames):
                            self.stop()
                            break
                        try:
                            end_at = min(position + chunk, len(frames))
                            # really play the frames now!!!
                            self._player.write(frames[position:end_at])
                            position += chunk
                            # if the state changed during the frames were playing
                            if self._ms != PlayerState().playing:
                                break
                        except OSError:
                            logging.error("The audio stream player was unexpectedly interrupted.")
                            self.stop()
                            self._player = None
                            return False

                    return True
                else:
                    self._player = None
                    return False
            else:
                logging.warning("No frames to play in the given period "
                                "for audio {:s}.".format(self._filename))

        except Exception as e:
            self.stop()
            logging.error("An error occurred when attempted to play "
                          "the audio stream of {:s} with the "
                          "pyaudio library: {:s}".format(self._filename, str(e)))

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
                # seek at the exact moment we asked to stop to play
                self._update_now()
                return True

        return False

    # -----------------------------------------------------------------------

    def _stop(self):
        """Really stops the player."""
        if self._player is not None:
            self._player.stop_stream()
            self._player.close()
            self._player = None

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
            self.reposition_stream()

            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

        elif self._ms != PlayerState().paused:
            self.stop()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Audio PyPlayer")

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
