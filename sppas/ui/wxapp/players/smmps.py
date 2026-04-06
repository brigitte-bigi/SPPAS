# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.smmps.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The SPPAS Multi Media Player System.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

The SPPAS Multi Media Player System
===================================

Requires simpleaudio or pyaudio library to play the audio file streams.
Raise a FeatureException at init if 'audioplay' feature is not enabled.

A player to play several media files really synchronously: during the
tests, the maximum time lag I observed was less than 15ms when playing
4 audios and 1 video.

Limitations:
=============

The followings will raise a Runtime error:

    1. can't add a new media when playing or paused;
    2. can't play if at least a media is loading;
    3. can't set period if at least a media is paused or playing.

"""

import logging
import os
import wx
import datetime
import threading

from sppas.core.config import paths
from sppas.core.coreutils import b

from sppas.ui.wxapp.page_editor.media.mediaevents import MediaEvents
from sppas.ui.wxapp.players import sppasAudioPlayer
from sppas.ui.wxapp.players import sppasVideoPlayer

from .baseplayer import sppasBasePlayer
from .undplayer import sppasUndPlayer

# ---------------------------------------------------------------------------


class sppasMMPS(wx.Object):
    """A multi-media player.

    The main difficulty in this class is that when all the media
    finished to play, there's no event, so there's no way to know it then
    to seek at the beginning of the period, etc.

    """

    def __init__(self, owner):
        """Create an instance of sppasMMPS.

        :param owner: (wx.Window) Owner of this class.

        """
        super(sppasMMPS, self).__init__()

        # A time period to play the audio stream. Default is whole.
        self._period = (0., 0.)

        # The parent wx.Window
        self._owner = owner

        # Key = the media player / value = bool:enabled
        self._players = dict()

        # Observed delays between 2 consecutive "play".
        # Used to synchronize files.
        self._all_delays = [0.01]
        self.__cur_time = -1.    # position (in seconds) to start playing

    # -----------------------------------------------------------------------

    def __del__(self):
        try:
            if self.is_playing():
                self.reset()
        except AttributeError:
            pass

    # -----------------------------------------------------------------------

    def reset(self):
        """Forget everything about the media players.

        :raise: RuntimeError

        """
        if self.are_playing():
            raise RuntimeError("Can't reset SMMPS when playing.")
        if self.are_paused():
            self.stop()

        self._period = (0., 0.)
        self.__cur_time = -1.    # position (in seconds) to start playing

        for mp in self._players:
            mp.reset()

    # -----------------------------------------------------------------------

    def get_period(self):
        """Return the currently defined period (start, end)."""
        p0, p1 = self._period
        return p0, p1

    # -----------------------------------------------------------------------

    def set_period(self, start_time, end_time):
        """Fix the range period of time to play.

        :param start_time: (float) Time to start playing in seconds
        :param end_time: (float) Time to stop playing in seconds

        """
        if self.is_playing():
            raise RuntimeError("The period can't be changed while playing.")

        start_time = float(start_time)
        end_time = float(end_time)
        if end_time <= start_time:
            logging.error("Invalid period of time: {:f} {:f}"
                          "".format(start_time, end_time))
            start_time = 0.
            end_time = 0.
            self.__cur_time = -1.

        self._period = (start_time, end_time)
        # Also, update the period of the players -- if any.
        for mp in self._players:
            if mp.is_video() or mp.is_audio():
                mp.set_period(start_time, end_time)

        # invalidate current time positions if out of the period and seek
        if self.__cur_time < start_time or self.__cur_time > end_time or self.__cur_time == -1:
            # self.__cur_time = -1.
            if self.is_paused() is True:
                self.stop()
            self.seek(start_time)
            self.__cur_time = start_time

    # -----------------------------------------------------------------------
    # List players
    # -----------------------------------------------------------------------

    def add_audio(self, filename):
        """Load the files that filenames refers to.

        The event MediaLoaded or MediaNotLoaded is sent when the audio
        finished to load. Loaded successfully or not, the audio is disabled.

        :param filename: (str) Name of a file or list of file names
        :return: (bool) Always returns False

        """
        if isinstance(filename, (list, tuple)) is True:
            # Create threads with a target function of loading with name as args
            new_th = list()
            for name in filename:
                th = threading.Thread(target=self.__load_audio, args=(name,))
                new_th.append(th)
            # Start the new threads
            for th in new_th:
                th.start()
        else:
            self.__load_audio(filename)

    # -----------------------------------------------------------------------

    def add_video(self, filename, player=None):
        """Add a video into the list of media managed by this control.

        The new video is disabled.

        :param filename: (str) A filename or a list of file names
        :param player: (wx.Window) a window or a list of wx windows
        :return: (bool)

        """
        if isinstance(filename, (list, tuple)) is True:
            # Invalidate the list of players if lengths don't match
            if isinstance(player, (list, tuple)):
                if len(player) != len(filename):
                    player = None

            # Create threads with a target function of loading
            new_th = list()
            for i, name in enumerate(filename):
                if isinstance(player, (list, tuple)):
                    dest_player = player[i]
                else:
                    dest_player = player

                th = threading.Thread(target=self.__load_video, args=(name, dest_player))
                new_th.append(th)
            # Start the new threads
            for th in new_th:
                th.start()
        else:
            self.__load_video(filename, player)

    # -----------------------------------------------------------------------

    def add_unsupported(self, filename, duration):
        """Add a file into the list of media in order to add only its duration.

        :param filename: (str)
        :param duration: (float) Time value in seconds.

        """
        if self.exists(filename) is False:
            fake_media = sppasUndPlayer(self._owner)
            fake_media.load(filename)
            fake_media.set_duration(duration)
            self._players[fake_media] = False

    # -----------------------------------------------------------------------

    def add_media(self, media):
        """Add a media into the list of media managed by this control.

        The new media is disabled.

        :param media: (sppasBasePlayer)
        :return: (bool)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add media: at least a media is still playing.")

        if isinstance(media, sppasBasePlayer) is False:
            return False
        self._players[media] = False

    # -----------------------------------------------------------------------

    def remove_media(self, filename):
        """Remove a media of the list.

        :param filename: (str) Name of the file of the media to be removed
        :return: (bool)

        """
        if self.exists(filename) is False:
            return False

        media_obj = None
        for mp in self._players:
            if mp.get_filename() == filename:
                if mp.is_playing() or mp.is_paused():
                    mp.stop()
                if mp.is_video() is True:
                    mp.close_player()
                mp.reset()
                media_obj = mp
                break

        del self._players[media_obj]
        return True

    # -----------------------------------------------------------------------

    def get_duration(self, filename=None):
        """Return the duration this player must consider (in seconds).

        This estimation does not take into account the fact that a media is
        enabled or disabled. All valid media are considered.

        :param filename: (str) The media to get duration or None to get the max duration
        :return: (float)

        """
        if filename is None:
            dur = list()
            if len(self._players) > 0:
                while len(dur) == 0:
                    try:
                        for mp in self._players:
                            if mp.is_unknown() is False and mp.is_loading() is False:
                                dur.append(mp.get_duration())
                    except RuntimeError:
                        pass

            if len(dur) > 0:
                return max(dur)

        elif self.exists(filename) is True:
            return self._get_media(filename).get_duration()

        return 0.

    # -----------------------------------------------------------------------

    def get_filenames(self):
        """Return the list of the filename of each player."""
        return [mp.get_filename() for mp in self._players]

    # -----------------------------------------------------------------------

    def exists(self, filename):
        """Return True if the given filename is matching an existing media.

        :param filename: (str)
        :return: (bool)

        """
        for mp in self._players:
            if mp.get_filename() == filename:
                return True
        return False

    # -----------------------------------------------------------------------

    def is_enabled(self, filename=None):
        """Return True if any media or the given one is enabled.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([self._players[mp] for mp in self._players])

        for mp in self._players:
            if self._players[mp] is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def enable(self, filename, value=True):
        """Enable or disable the given media.

        When a media is disabled, it can't be paused nor played. It can only
        stay in the stopped state.

        :param filename: (str)
        :param value: (bool)
        :return: (bool)

        """
        for mp in self._players:
            if mp.get_filename() == filename:
                self._players[mp] = bool(value)
                if mp.is_playing():
                    mp.stop()

        return False

    # -----------------------------------------------------------------------

    def are_playing(self):
        """Return True if all enabled media are playing.

        :return: (bool)

        """
        playing = [mp.is_playing() for mp in self._players if self._players[mp] is True]
        if len(playing) == 0:
            return False
        # needed to care about len(playing) because: all([]) is True
        return all(playing)

    # -----------------------------------------------------------------------

    def is_playing(self, filename=None):
        """Return True if any media or if the given media is playing.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_playing() for mp in self._players])

        for mp in self._players:
            if mp.is_playing() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_paused(self):
        """Return True if all enabled media are paused.

        :return: (bool)

        """
        paused = [mp.is_paused() for mp in self._players if self._players[mp] is True]
        if len(paused) == 0:
            return False

        # all([]) is True
        return all(paused)

    # -----------------------------------------------------------------------

    def is_paused(self, filename=None):
        """Return True if any media or if the given media is paused.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_paused() for mp in self._players])

        for mp in self._players:
            if mp.is_paused() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def are_stopped(self):
        """Return True if all enabled media are stopped.

        :return: (bool)

        """
        stopped = [mp.is_stopped() for mp in self._players if self._players[mp] is True]
        if len(stopped) == 0:
            return False

        # all([]) is True
        return all(stopped)

    # -----------------------------------------------------------------------

    def is_stopped(self, filename=None):
        """Return True if any media or if the given one is stopped.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_stopped() for mp in self._players])

        for mp in self._players:
            if mp.is_stopped() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_loading(self, filename=None):
        """Return True if any media or if the given one is loading.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            try:
                ret = any([mp.is_loading() for mp in self._players])
                return ret
            except RuntimeError:
                # dictionary changed size during iteration -- so there's a loading
                return True

        for mp in self._players:
            if mp.is_loading() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_unknown(self, filename=None):
        """Return True if any media type or if the given one is unknown.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_unknown() for mp in self._players])

        for mp in self._players:
            if mp.is_unknown() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_audio(self, filename=None):
        """Return True if any media or if the given one is an audio.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_audio() for mp in self._players])

        for mp in self._players:
            if mp.is_audio() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------

    def is_video(self, filename=None):
        """Return True if any media or if the given one is a video.

        :param filename: (str)
        :return: (bool)

        """
        if filename is None:
            return any([mp.is_video() for mp in self._players])

        for mp in self._players:
            if mp.is_video() is True and filename == mp.get_filename():
                return True
        return False

    # -----------------------------------------------------------------------
    # Player
    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the current interval or the whole streams.

        Start playing only if the audio streams are currently stopped or
        paused. Play in the range of the defined period.

        So, it starts playing an audio only if the defined period is inside
        or overlapping the audio stream AND if the the current position is
        inside the period. It stops at the end of the period or at the end
        of the stream.

        :return: (bool) True if the action of playing was started

        """
        if self.is_playing() is False:
            # Check if cur_time is valid.
            if self.__cur_time == -1 or self.__cur_time < self._period[0] or self.__cur_time > self._period[1]:
                self.__cur_time = self._period[0]
            # Play from the current time to the end of the period
            self.play_interval()

    # -----------------------------------------------------------------------

    def play_interval(self, from_time=None, to_time=None):
        """Start to play an interval of the enabled media streams.

        Start playing only the media streams that are currently stopped or
        paused and if enabled.

        Under Windows and MacOS, the delay between 2 runs of "play" is 11ms.
        Except the 1st one, the other medias will be 'in late' so we do not
        play during the elapsed time instead of playing the media shifted!
        This problem CANNOT be solved with:
            - threading because of the GIL;
            - multiprocessing because the elapsed time is only reduced to 4ms
              instead of 11ms, but the audios can't be eared!

        :param from_time: (float) Start to play at this given time or at the current from time if None
        :param to_time: (float) Stop to play at this given time or at the current end time if None
        :return: (bool) True if the action of playing was performed for at least one media

        """
        if self.is_loading():
            raise RuntimeError("Can't play: at least a media is still loading.")

        # Update the from/to time positions
        if from_time is None:
            from_time = self.__cur_time
        if to_time is None:
            to_time = self._period[1]

        # Start to play all videos
        videos = list()
        started_time = None
        for mp in self._players:
            if self._players[mp] is True and mp.is_video() is True:
                if mp.prepare_play(from_time, to_time) is True:
                    videos.append(mp)
        for mp in videos:
            mp.play()
            if started_time is None:
                started_time = mp.get_time_value()

        process_time = None
        shift = 0.
        # Invalidate current time when playing. Allows consistency between play/play_frame.
        # i.e cur_time is valid only when "play_frame" or "paused"
        self.__cur_time = -1

        # Start to play & synchronize all audios
        for mp in self._players:
            if self._players[mp] is True and mp.is_audio() is True:
                if started_time is not None and process_time is not None:
                    delta = process_time - started_time
                    delay = delta.seconds + delta.microseconds / 1000000.
                    logging.debug(" ... observed delay is {:.4f}".format(delay))
                    self._all_delays.append(delay)
                    shift += delay

                if mp.prepare_play(from_time + shift, to_time):
                    mp.play()
                    started_time = process_time
                    process_time = mp.get_time_value()
                    if started_time is None:
                        mean_delay = sum(self._all_delays) / float(len(self._all_delays))
                        logging.debug(" ... process time is {}".format(process_time))
                        logging.debug(" ... mean delay is {:.4f}".format(mean_delay))
                        started_time = process_time - datetime.timedelta(seconds=mean_delay)

    # -----------------------------------------------------------------------

    def play_frame(self, direction=1):
        """Play a single frame of the videos.

        Direction indicates which "next/previous" frame is to play.

        :param direction: positive value = next; negative value = previous
        :return: (bool)

        """
        # No period is defined.
        if self._period[1] == self._period[0]:
            return False
        # Already playing.
        direction = int(direction)
        if direction == 0 or self.are_playing():
            return False
        if self.are_paused() is True:
            for mp in self._players:
                mp.stop()

        if self.__cur_time == -1.:
            self.__cur_time = self._period[0]
        else:
            self.seek(self.__cur_time)

        # Fix the list of enabled video medias
        videos = list()
        for mp in self._players:
            if self._players[mp] is True and mp.is_video() is True:
                videos.append(mp)
        logging.info(" ... Play frames of {:d} videos with direction {:d}"
                     "".format(len(videos), direction))

        # Search for the video media player with the highest framerate
        hmp = self.get_highest_framerate(videos)
        if hmp is None:
            # no enabled video media
            return False
        frame_dur = 1. / hmp.get_framerate()
        if hmp is None:
            return False

        if direction < 0:
            # We are at the beginning of the period. Can't go before.
            if self.__cur_time + ((direction+1) * frame_dur) < self._period[0]:
                return False
        else:
            # We already reached the end of the period. Can't go after.
            if self.__cur_time + (direction * frame_dur) > self._period[1]:
                return False

        # play frame of the video with the highest framerate
        hfrm = hmp.get_framerate()
        success = hmp.play_frame(direction)
        if success is False:
            return False
        position = hmp.media_tell()
        # set cur_time to align properly the next time play_frame or play is invoked
        self.__cur_time = float(position) / float(hfrm)

        # play the other videos
        videos.remove(hmp)
        for mp in videos:
            # only take into account enabled video players
            if hfrm != mp.get_framerate():
                # fix direction, allowing positioning videos to the nearest
                # position of the one with the highest framerate
                mp_direction = int(round(direction / (hfrm / mp.get_framerate()), 0))
                mp.play_frame(mp_direction)
            else:
                mp.play_frame(direction)

        # seek at the exact moment of the selected video, as players are now
        # one frame ahead of the excepted time position
        self.seek(self.__cur_time)
        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def get_highest_framerate(videos):
        """Return the highest framerate among the currently enabled video players."""
        # The media player to be found
        mp = None
        # Browse through the media to get the highest video framerate
        for media_player in videos:
            if mp is not None:
                if mp.get_framerate() < media_player.get_framerate():
                    mp = media_player
            else:
                mp = media_player
        return mp

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause the medias that are currently playing."""
        # self.Stop()
        paused = False
        for mp in self._players:
            p = mp.pause()
            if p is True and paused is False:
                paused = True
                position = mp.media_tell()
                self.__cur_time = float(position) / float(mp.get_framerate())
        return paused

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the media.

        :return: (bool) True if the action of stopping was performed

        """
        # self.Stop()
        # self.DeletePendingEvents()
        stopped = False
        for mp in self._players:
            s = mp.stop()
            if s is True:
                stopped = True

        self.__cur_time = self._period[0]
        self.seek(self._period[0])
        return stopped

    # -----------------------------------------------------------------------

    def seek(self, value):
        """Seek all media streams to the given position in time.

        :param value: (float) Time value in seconds.

        """
        time_pos = float(value)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()
        if time_pos > self._period[1]:
            time_pos = self._period[1]
        if time_pos < self._period[0]:
            time_pos = self._period[0]

        force_pause = False
        if self.is_paused() is True:
            force_pause = True
        if self.is_playing() is True:
            self.pause()
            force_pause = True

        for mp in self._players:
            if mp.is_unknown() is False and mp.is_unsupported() is False and mp.is_loading() is False:
                mp.seek(time_pos)

        if force_pause is True:
            self.__cur_time = time_pos
            self.play()

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the latest time position in the media streams (float)."""
        values = list()
        for media in reversed(list(self._players.keys())):
            if media.is_unknown() is False and media.is_unsupported() is False and media.is_loading() is False:
                values.append(media.tell())

        # In theory, all media should return the same value except
        # when playing or paused after the max length of some media.
        if len(values) > 0:
            return max(values)

        return 0

    # -----------------------------------------------------------------------
    # About the audio
    # -----------------------------------------------------------------------

    def get_nchannels(self, filename):
        """Return the number of channels."""
        for mp in self._players:
            if mp.is_audio() is True and filename == mp.get_filename():
                return mp.get_nchannels()
        return 0

    # -----------------------------------------------------------------------

    def get_sampwidth(self, filename):
        for mp in self._players:
            if mp.is_audio() is True and filename == mp.get_filename():
                return mp.get_sampwidth()
        return 0

    # -----------------------------------------------------------------------

    def get_framerate(self, filename):
        for mp in self._players:
            if (mp.is_audio() is True or mp.is_video() is True) and filename == mp.get_filename():
                return mp.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_frames(self, filename):
        for mp in self._players:
            if (mp.is_audio() is True or mp.is_video() is True) and filename == mp.get_filename():
                return mp.get_frames()
        return b("")

    # -----------------------------------------------------------------------
    # About the video
    # -----------------------------------------------------------------------

    def get_video_width(self, filename):
        for mp in self._players:
            if mp.is_video() is True and filename == mp.get_filename():
                return mp.get_width()
        return 0

    def get_video_height(self, filename):
        for mp in self._players:
            if mp.is_video() is True and filename == mp.get_filename():
                return mp.get_height()
        return 0

    # -----------------------------------------------------------------------
    # Private & Protected methods
    # -----------------------------------------------------------------------

    def _get_media(self, filename):
        """Return the media matching the given filename."""
        for mp in self._players:
            if filename == mp.get_filename():
                return mp
        raise KeyError

    # -----------------------------------------------------------------------

    def __load_audio(self, filename):
        """Really load and add the file that filename refers to.

        Send a media event when a loading is finished.

        :param filename: (str)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add audio: at least a media is still playing.")

        if self.exists(filename):
            return False

        try:
            # Create the audio player.
            new_audio = sppasAudioPlayer(self._owner)
            # Add the audio player into our list of media. not enabled.
            self._players[new_audio] = False

            # Custom event to inform the media is loaded (or not)
            new_audio.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_load_finished)
            new_audio.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_load_finished)
            # Start loading. An event is sent when loading is finished.
            new_audio.load(filename)
        except Exception as e:
            wx.LogError(str(e))

    # -----------------------------------------------------------------------

    def __load_video(self, filename, player):
        """Really load and add the file that filename refers to.

        Send a media event when a loading is finished.

        :param filename: (str)

        """
        if self.is_playing() or self.is_paused():
            raise RuntimeError("Can't add video: at least a media is still playing.")

        if self.exists(filename):
            return False

        try:
            new_video = sppasVideoPlayer(owner=self._owner, player=player)
            self._players[new_video] = False

            # Custom event to inform the media is loaded (or not)
            new_video.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_load_finished)
            new_video.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_load_finished)
            # Start loading. An event is sent when loading is finished.
            new_video.load(filename)
        except Exception as e:
            wx.LogError(str(e))

    # -----------------------------------------------------------------------

    def __on_load_finished(self, evt):
        wx.PostEvent(self._owner, evt)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        return len(self._players)

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="Multi Media Player System")

        # The player!
        self.ap = sppasMMPS(owner=self)

        # Actions to perform with the player
        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)
        btn5 = wx.Button(self, -1, "Prev Frame")
        self.Bind(wx.EVT_BUTTON, self._on_prev_frame_ap, btn5)
        btn6 = wx.Button(self, -1, "Next Frame")
        self.Bind(wx.EVT_BUTTON, self._on_next_frame_ap, btn6)

        sizer = wx.BoxSizer()
        sizer.Add(btn2, 0, wx.ALL, 4)
        sizer.Add(btn3, 0, wx.ALL, 4)
        sizer.Add(btn4, 0, wx.ALL, 4)
        sizer.Add(btn5, 0, wx.ALL, 4)
        sizer.Add(btn6, 0, wx.ALL, 4)

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
        self.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every 15ms (in theory) when the audio is playing
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        # Example to add&enable a media:
        # >>> m = sppasVideoPlayer(owner=self)
        # >>> m.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        # >>> if m.is_unknown() is False:
        # >>>     self.ap.add_media(m)
        # >>>     self.ap.enable(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        self.ap.add_unsupported("a filename of a file", 65.)
        self.ap.add_video(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        # self.ap.add_video("D:\\data\\corpus\\FRA\\Multimodal\\CLeLfPC\\01_syll\\syll_2_MZ_dd520f\\syll_2_MZ_dd520f_front.mkv")
        self.ap.add_audio(
             [
                 "toto.xyz",
                 os.path.join(paths.samples, "samples-fra", "F_F_B003_P8.wav"),
                 os.path.join(paths.samples, "samples-fra", "F_F_B003_P9.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
                 os.path.join(paths.samples, "samples-eng", "oriana2.WAV")
             ]
        )
        while self.ap.is_loading() is True:
            pass
        # all the media are loaded now:
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))
        self.FindWindow("btn_play").Enable(True)

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        filename = event.filename
        logging.debug("**** MEDIA EVENT **** File loaded successfully: {}. Duration: {}. NB MEDIA={}"
                      "".format(filename, self.ap.get_duration(filename), len(self.ap)))
        self.ap.enable(filename)
        duration = self.ap.get_duration()
        self.ap.set_period(0., duration)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        filename = event.filename
        logging.error("**** MEDIA EVENT **** Media file {} not loaded".format(filename))

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        logging.debug("................PLAY EVENT RECEIVED..................")
        if self.ap.is_playing() is False:
            # if self.ap.is_paused() is False:
            #     duration = self.ap.get_duration()
            #     self.ap.set_period(0., duration)
            self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        logging.debug("................PAUSE EVENT RECEIVED..................")
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        logging.debug("................STOP EVENT RECEIVED..................")
        self.ap.stop()
        self.slider.SetValue(0)

    # ----------------------------------------------------------------------

    def _on_prev_frame_ap(self, event):
        logging.debug("................PLAY PREVIOUS FRAME EVENT RECEIVED..................")
        self.ap.play_frame(direction=-2)
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_next_frame_ap(self, event):
        logging.debug("................PLAY NEXT FRAME EVENT RECEIVED..................")
        self.ap.play_frame(direction=2)
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def _on_seek_slider(self, event):
        p = self.ap.get_period()
        time_pos = float(self.slider.GetValue()) / 1000.
        if p[0] < time_pos < p[1]:
            self.ap.set_period(time_pos, p[1])
        else:
            self.ap.set_period(time_pos, self.ap.get_duration())
        self.ap.play_frame(direction=1)
