# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.baseplayer.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class to implement inherited audio/video players.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

A player is a generic "bridge" between raw media data and a tool to play the
media stream. Requires wx to play/display the stream and to implement seek
and tell.

"""

import logging
import datetime
import threading
import wx

from sppas.ui.wxapp.page_editor.media.mediaevents import MediaEvents
from .penum import PlayerState
from .penum import PlayerType

# ---------------------------------------------------------------------------


class sppasBasePlayer(wx.Timer):
    """A base class for a wx-based player of any stream.

    Load, play and stop the data stream of a given file.

    This class is inheriting a wxTimer in order to update the position
    in the stream and thus to implement the 'tell' method.

    Events emitted by this class:

        - wx.EVT_TIMER when the stream is playing every "DELAY" seconds
        - MediaEvents.EVT_MEDIA_LOADED when the stream is loaded
        - MediaEvents.EVT_MEDIA_NOT_LOADED when an error occurred

    The wx.Timer documentation indicates that its precision is
    platform-dependent, but in general will not be better than 1ms
    nor worse than 1s... We attempted to measure:

    When the timer delay is fixed to 10ms, the observed delays are:
       - about 15 ms under Windows;
       - 10 ms under MacOS;
       - 10 ms under Linux.

    When the timer delay is fixed to 5ms, the observed delays are:
       - about 15 ms under Windows;
       - 6 ms under MacOS;
       - 5.5 ms under Linux.

    When the timer delay is fixed to 1ms, the observed delays are:
       - about 15 ms under Windows;
       - 2 ms under MacOS;
       - 1.3 ms under Linux.

    4. Under Windows, the timer delay is always a multiple of 15 - exactly
       like for the time.sleep() method. Under Linux&Mac, the delay is
       always slightly higher than requested.

    """

    def __init__(self, owner):
        wx.Timer.__init__(self, owner)

        # The state of the player: unknown, loading, playing, paused or stopped
        self._ms = PlayerState().unknown
        # The type of the player: unknown, unsupported, audio, video...
        self._mt = PlayerType().unknown

        # The name of the media file
        self._filename = None

        # The instance of the media - i.e. its content, when loading is finished
        self._media = None

        # The instance of the media player - when playing, and the boundaries
        self._player = None
        self._start_datenow = None  # datetime.now() of the last start playing
        self._from_time = 0.        # position (in seconds) of start to play

        # A time period to play the stream. Default is whole.
        self._period = None

        # Delay in seconds to update the position value in the stream & to notify
        self._time_delay = 0.05

        # thread to play the stream
        self._th = None

    # -----------------------------------------------------------------------

    def __del__(self):
        self.reset()

    # -----------------------------------------------------------------------
    # State of this player
    # -----------------------------------------------------------------------

    def is_loading(self):
        """Return True if the player state is loading."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().loading

    # -----------------------------------------------------------------------

    def is_playing(self):
        """Return True if the player state is playing."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().playing

    # -----------------------------------------------------------------------

    def is_paused(self):
        """Return True if the player state is paused."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().paused

    # -----------------------------------------------------------------------

    def is_stopped(self):
        """Return True if the player state is stopped."""
        if self._filename is None:
            return False

        return self._ms == PlayerState().stopped

    # -----------------------------------------------------------------------
    # Type of this player
    # -----------------------------------------------------------------------

    def is_unknown(self):
        """Return True if the player type is unknown."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().unknown

    # -----------------------------------------------------------------------

    def is_unsupported(self):
        """Return True if the player type is known but unsupported."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().unsupported

    # -----------------------------------------------------------------------

    def is_audio(self):
        """Return True if the player type is a valid audio."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().audio

    # -----------------------------------------------------------------------

    def is_video(self):
        """Return True if the player type is a valid video."""
        if self._filename is None:
            return False

        return self._mt == PlayerType().video

    # -----------------------------------------------------------------------
    # Getters&Setters
    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file this media refers to or None."""
        return self._filename

    # -----------------------------------------------------------------------

    def get_time_value(self):
        """Return the exact time the audio started to play or None."""
        return self._start_datenow

    # -----------------------------------------------------------------------

    def set_period(self, start_time, end_time):
        """Fix the range period of time to play.

        :param start_time: (float) Time to start playing in seconds
        :param end_time: (float) Time to stop playing in seconds (max is duration)

        """
        start_time = float(start_time)
        end_time = float(end_time)
        if start_time > end_time:
            raise Exception("Invalid period. Start {} > end {}".format(start_time, end_time))
        start_time = min(start_time, self.get_duration())
        end_time = min(end_time, self.get_duration())

        self._period = (start_time, end_time)
        cur_state = self._ms
        cur_pos = self.tell()
        # Stop playing (if any), and seek at the beginning of the period
        self.stop()

        # Restore the situation in which the media was before stopping
        if cur_state in (PlayerState().playing, PlayerState().paused):
            if self._period[0] < cur_pos <= self._period[1]:
                # Restore the previous position in time if it was inside
                # the new period.
                self.seek(cur_pos)
            # Play again. It will re-create the thread, etc.
            self.play()
            # Then pause if it was the previous state.
            if cur_state == PlayerState().paused:
                self.pause()
                # Ensure to be paused at the right position
                self.seek(cur_pos)

    # -----------------------------------------------------------------------
    # The methods to be overridden.
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the media or 0."""
        return 0.

    # -----------------------------------------------------------------------

    def reset(self):
        """Re-initialize all known data."""
        try:
            self.Stop()
        except RuntimeError:
            return

        try:
            if self._media is not None:
                self._media.close()
            self._ms = PlayerState().unknown
            self._mt = PlayerType().unknown
            self._filename = None
            self._media = None
            self._start_datenow = None
            self._from_time = 0.    # position (in seconds) to start playing
            self._period = None
        except:
            pass

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load the file that filename refers to then send event.

        :param filename: (str)

        """
        value = self._load(filename)
        if value is True:
            evt = MediaEvents.MediaLoadedEvent()
            if self._period is None:
                self._period = (0., self.get_duration())
                self._from_time = 0.
        else:
            evt = MediaEvents.MediaNotLoadedEvent()

        evt.filename = filename
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        self._ms = PlayerState().stopped
        return value

    # -----------------------------------------------------------------------

    def _load(self, filename):
        """Really load all the frames of the file that filename refers to.

        :param filename: (str) Name of an audio file
        :return: (bool) True if both successfully opened and loaded.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the current range of time."""
        self._from_time = 0.
        self._period = (0., self.get_duration())
        self._seek(0.)

    # -----------------------------------------------------------------------

    def prepare_play(self, from_time=None, to_time=None):
        """Prepare to play the media stream: fix the period to play.

        :param from_time: (float) Start to play at this given time or at the current from time if None
        :param to_time: (float) Stop to play at this given time or at the current end time if None
        :return: (bool) True if the action of playing can be performed

        """
        if self._media is not None:
            self.set_period(from_time, to_time)
            if self._period[0] < self._period[1]:
                # The given period is valid
                self._from_time = self._period[0]
                self._seek(self._from_time)
            else:
                return False
        else:
            logging.error("No media file to play.")
            return False

        return self.can_play()

    # -----------------------------------------------------------------------

    def can_play(self):
        """Return True if the player is ready to start playing."""
        if self._media is None:
            return False

        can = False
        with PlayerState() as ms:
            if self._ms == ms.unknown:
                if self._mt not in (PlayerType().unknown, PlayerType().unsupported):
                    logging.error("The media stream of {:s} can't be played for "
                                  "an unknown reason.".format(self._filename))

            elif self._ms == ms.loading:
                logging.error("The media stream of {:s} can't be played; "
                              "it is still loading".format(self._filename))

            elif self._ms == ms.playing:
                logging.warning("The media stream of {:s} is already "
                                "playing.".format(self._filename))

            else:  # stopped or paused
                can = True

        return can

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play a stream in a thread.

        Start playing only is the media is currently stopped or paused.
        Start playing only if the defined period is inside or overlapping
        this audio stream AND if the the current position is inside the
        period.

        :return: (bool) True if the action of playing was started

        """
        if self.can_play() is False:
            return

        start_time = max(self._period[0], self.tell())
        if start_time < self._period[1]:
            self._th = threading.Thread(target=self._play_process, args=())
            self._ms = PlayerState().playing
            self.Start(int(self._time_delay * 1000.))
            self._start_datenow = datetime.datetime.now()
            self._th.start()

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play the stream.

        :return: (bool) True if the action of stopping was performed

        """
        if self._player is not None:
            # Stop the timer
            self.Stop()
            # Set the state
            self._ms = PlayerState().stopped
            # Stop the player
            self._stop()
            # and do other things...
            if self._th is not None:
                try:
                    self._th.join()
                except RuntimeError:
                    pass
            self.seek(self._period[0])
            self.DeletePendingEvents()  # in case of a remaining EVT_TIMER
            return True
        return False

    # -----------------------------------------------------------------------

    def _stop(self):
        """Really stop the player."""
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) True if the action of pausing was performed

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def seek(self, time_pos=0.):
        """Seek the audio stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        if self._media is None:
            return False
        if self._ms in (PlayerState().unknown, PlayerState().loading):
            return False

        time_pos = float(time_pos)
        if time_pos < 0.:
            time_pos = 0.
        if time_pos > self.get_duration():
            time_pos = self.get_duration()
        if self._period is not None:
            if time_pos > self._period[1]:
                time_pos = self._period[1]
            if time_pos < self._period[0]:
                time_pos = self._period[0]

        self._seek(time_pos)
        return True

    # -----------------------------------------------------------------------

    def _seek(self, time_pos):
        """Really do seek to the given position.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the audio stream (float)."""
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def media_tell(self):
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Manage events
    # -----------------------------------------------------------------------

    def Notify(self):
        """Override. Notify the owner of the EVT_TIMER event.

        Manage the current position in the audio stream.

        """
        # Nothing to do if we are not playing (probably paused).
        if self._ms == PlayerState().playing:
            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)
