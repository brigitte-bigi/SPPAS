# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.videodata.videoplayer.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A video player set the current image and display it with wx.

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

"""

import logging
import os
import datetime
import time
import wx

from sppas.core.config import paths
from sppas.src.videodata.video import sppasVideoReader
from sppas.src.imgdata import sppasImage

from .baseplayer import sppasBasePlayer
from .penum import PlayerState
from .penum import PlayerType

from ..windows.frame import sppasImageFrame
from ..page_editor.datactrls.videoframe import VideoAnnotationFrame
from ..page_editor.datactrls.videodatavalues import VideoDataValues
from ..page_editor.media.mediaevents import MediaEvents

# ---------------------------------------------------------------------------


class sppasVideoPlayer(sppasBasePlayer):
    """A video player based on a wx panel to display the images.

    Load, play and browse throw the video stream of a given file.

    """

    # A minimum delay to wait between too frames when playing.
    if wx.Platform == '__WXMAC__':
        WAIT_DELAY = 0.004
    elif wx.Platform == '__WXGTK__':
        WAIT_DELAY = 0.002
    else:
        # When this delay is used, notice that under Windows, the real
        # sleeping time is necessarily a multiple of 0.015.
        WAIT_DELAY = 0.008

    def __init__(self, owner, player=None):
        """Create an instance of sppasVideoPlayer.

        :param owner: (wx.Window) Owner of this class.
        :param player: (wx.Window) Frame, panel... to play the video

        """
        super(sppasVideoPlayer, self).__init__(owner)
        self._current_image = None

        # Delay in seconds to update the position value in the stream & to notify
        self._time_delay = 0.04   # corresponds to fps=25

        self._player = None
        if player is not None:
            player.Show()
            if player.IsShown():
                player.Hide()
            player.Refresh()
            self._player = player
        else:
            self._player = sppasImageFrame(
                parent=owner,   # if owner is destroyed, the frame will be too
                title="Video",
                style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT)
            self._player.SetBackgroundColour(wx.WHITE)
            self._player.Show(True)

    # -----------------------------------------------------------------------

    def close_player(self):
        if isinstance(self._player, wx.Window):
            try:
                self._player.Close()
            except RuntimeError:
                # if a window is closed even if flags to not allow window
                # closing are set, a RuntimeError would be thrown by wx,
                # ignore these errors
                pass
        self._player = None

    # -----------------------------------------------------------------------

    def _load(self, filename):
        """Open the file that filename refers to and load a buffer of frames.

        :param filename: (str) Name of a video file
        :return: (bool) True if successfully opened and loaded.

        """
        self.reset()
        self._filename = filename
        self._ms = PlayerState().loading
        loaded = False

        try:
            self._media = sppasVideoReader()
            self._media.open(filename)
            # Options to process the image with read_frame()
            self._media.set_gray(False)
            self._media.set_rgb(True)
            self._media.set_alpha(False)
            logging.debug("Video rotation: {}".format(self._media.get_rotate()))
            # Media properties
            self._ms = PlayerState().stopped
            self._mt = PlayerType().video
            loaded = True
        except Exception as e:
            logging.error("OpenCV did not opened file {:s}: {:s}".format(filename, str(e)))
            self._media = sppasVideoReader()
            self._ms = PlayerState().unknown
            self._mt = PlayerType().unknown

        # With the following, the app will crash if load() is launch into
        # a thread - tested under MacOS only:
        if loaded is True:
            if isinstance(self._player, wx.Window):
                if isinstance(self._player, VideoAnnotationFrame):
                    self._player.set_filename(file_path=filename)
                    vd = VideoDataValues()
                    vd.set_video_data(
                        framerate=self._media.get_framerate(),
                        duration=self._media.get_duration(),
                        width=self._media.get_width(),
                        height=self._media.get_height())
                    self._player.set_video_data(vd)
                self._player.Show()

            self._time_delay = 1. / self.get_framerate()
            logging.info("Video {:s} image duration: {:.3f}".format(filename, self._time_delay))

            # display a blank image in the player
            self._current_image = sppasImage(0).blank_image(w=self._media.get_width(), h=self._media.get_height())
            self.refresh_player_frame()

        return loaded

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the video.

        :return: (bool) True if the action of pausing was performed

        """
        if self._ms == PlayerState().playing:
            # stop playing
            self._ms = PlayerState().paused
            # stop the thread to prevent error:
            # "Assertion fctx->async_lock failed at libavcodec/pthread_frame.c:155"
            self._th.join()
            # get the exact moment we stopped to play
            self._from_time = self.tell()
            self._start_datenow = None
            # ensure the current frame is displayed
            self.refresh_player_frame()
            return True

        return False

    # -----------------------------------------------------------------------

    def _stop(self):
        """Stop playing of the video.

        :return: (bool) True if the action of stopping was performed

        """
        self._current_image = sppasImage(0).blank_image(w=self._media.get_width(), h=self._media.get_height())
        self.refresh_player_frame()
        return True

    # -----------------------------------------------------------------------

    def _play_process(self):
        """Run the process of playing.

        It is expected that reading a frame, converting it to an image and
        displaying it in the video frame is faster than the duration of a
        frame (1. / fps). If not, some frames can be skipped.

        """
        # The timer is already started. It's urgent to have an image...
        if self._current_image is None:
            self._current_image = sppasImage(0).blank_image(w=self._media.get_width(), h=self._media.get_height())

        self._start_datenow = datetime.datetime.now()

        fps = self._media.get_framerate()
        min_delta = 1. / (fps * 5.)

        # the position to start and to stop playing
        start_offset = self._media.tell()
        end_offset = int(self._period[1] * float(self._media.get_framerate()))
        logging.debug("  -> video player {:s} - offsets range: {}, {}"
                      "".format(self._filename, start_offset, end_offset))

        # the time when we started to play and the number of frames we displayed.
        frm = 0

        while self._media.is_opened() and self._ms == PlayerState().playing:
            # read the next frame from the file
            self._current_image = self._media.read_frame(process_image=True)
            if self._current_image is None:
                # we reached the end of the file
                self.stop()
                break
            # an image was grabbed and retrieved successfully
            # does this image is still in the defined period?
            frm += 1
            cur_offset = start_offset + frm
            if cur_offset > end_offset:
                # we reached the end of the period
                self.stop()
                break

            # if the state changed during the image was read
            if self._ms != PlayerState().playing:
                break

            # reposition in stream, or sleep
            cur_time_value = datetime.datetime.now()
            # since when the video is playing
            time_delta = cur_time_value - self._start_datenow
            delta = time_delta.total_seconds()
            # how many frames this delta is representing
            position = round(delta * float(self._media.get_framerate()))

            # Reading is too slow, frame position is in late. Go forward...
            if position > frm:
                # if the position is after the end of the video file...
                if start_offset + position > self._media.get_nframes():
                    # we reached the end of the period
                    self.stop()
                    break

                self._media.seek(start_offset + position)
                nf = position - frm   # nb of frames in late
                logging.warning("Video {:s} skipped {:d} frame(s) from {:d}. New position: {:d}".format(
                    self._filename, nf, start_offset + frm, start_offset + position
                ))
                frm = position

            # Reading is too fast, frame position is ok.
            else:
                # Wait a short time to maintain the correct fps.
                expected_time = self._start_datenow + datetime.timedelta(seconds=(float(frm) / fps))
                sppasVideoPlayer.take_a_nap(cur_time_value, expected_time, min_delta)

        # end while
        self._start_datenow = None
        self._current_image = None

    # -----------------------------------------------------------------------

    @staticmethod
    def take_a_nap(current_time, expected_time, min_delay=0.):
        """Sleep some delay to wait the expected time, if relevant.

        :param current_time: (float) Current time in seconds
        :param expected_time: (float) Expected time in seconds
        :param min_delay: (float) A minimum delay to wait in seconds
        :return: (float) Slept time

        """
        sleep_time = 0.
        if expected_time > current_time:
            # Delay between now and the expected time (in seconds)
            delta = expected_time - current_time
            delta_seconds = delta.seconds + (delta.microseconds / 1000000.)
            # Sleep time includes a delay for the system to manage the event
            # This is system-dependent.
            sleep_time = delta_seconds - sppasVideoPlayer.WAIT_DELAY
            # There's no need to sleep a too short delay
            if sleep_time > min_delay:
                # Really wait a short time
                # logging.debug("Video sleep at frame {:d} for {} seconds. "
                #              "Expected time: {}, cur time: {}".format(start_offset + frm, delta_seconds, expected_time, cur_time_value))
                time.sleep(sleep_time)
        return sleep_time

    # -----------------------------------------------------------------------

    def play_frame(self, direction: int = 1):
        """Play a single frame from the current position.

        Direction indicates which "next/previous" frame to play.

        :param direction: (int) positive value = next; negative value = previous

        """
        if direction == 0:
            return False

        frame_duration = 1. / float(self._media.get_framerate())
        current_frame_index = self._media.tell()
        current_time_value = float(current_frame_index) / float(self._media.get_framerate())
        expect_seek_at = max(0., current_time_value + (float(direction) * frame_duration))

        # skip one frame before the current one to not be one frame ahead
        expect_seek_at = expect_seek_at - frame_duration
        if expect_seek_at < 0. or expect_seek_at >= self._media.get_duration():
            logging.warning("Can't play frame of file {:s} in direction {:d}. "
                            "Time value is out of the video time range."
                            "".format(self._filename, direction))
            return False

        # seek at the correct position to be ready to read the previous frame
        self.seek(expect_seek_at)

        # read the previous frame
        previous_image = self._media.read_frame(process_image=True)
        if previous_image is None:
            # the current frame is the first frame of the video, so there is no previous frame
            # display a blank next frame
            previous_image = sppasImage(0).blank_image(w=self._media.get_width(), h=self._media.get_height())

        # read the requested frame
        current_frame_index = self._media.tell()
        self._current_image = self._media.read_frame(process_image=True)
        if self._current_image is None:
            # we reached the end of the file
            self.stop()
            return False
        # an image was grabbed and retrieved successfully

        # read the next frame
        next_image = self._media.read_frame(process_image=True)
        if next_image is None:
            # we reached the end of the file, return a blank next frame instead
            next_image = sppasImage(0).blank_image(w=self._media.get_width(), h=self._media.get_height())

        # Seeking media at the expected frame directly (no risk because current
        # state is stable), is faster than seeking with time value.
        self._media.seek(current_frame_index)

        self.refresh_player_frame(previous_image=previous_image,
                                  next_image=next_image,
                                  current_frame_index=current_frame_index)
        return True

    # -----------------------------------------------------------------------

    def refresh_player_frame(self,
                             previous_image: sppasImage = None,
                             next_image: sppasImage = None,
                             current_frame_index=-1) -> None:
        """Refresh the video frame."""
        if self._current_image is not None:
            if isinstance(self._player, VideoAnnotationFrame):
                self._player.UpdateFrames(current_image=self._current_image,
                                          current_image_index=current_frame_index,
                                          previous_image=previous_image,
                                          next_image=next_image)
            elif isinstance(self._player, sppasImageFrame):
                self._player.SetBackgroundImageArray(self._current_image)
                self._player.Refresh()

    # -----------------------------------------------------------------------

    def _seek(self, time_pos=0.):
        """Seek the video stream at the given position in time.

        :param time_pos: (float) Time in seconds

        """
        was_playing = self.is_playing()
        if was_playing is True:
            self.pause()

        # how many frames this time position is representing since the beginning
        self._from_time = float(time_pos)
        position = self._from_time * self._media.get_framerate()
        if self._period is not None:
            if self._from_time > self._period[1]:
                self.stop()

        # seek at the expected position
        try:
            self._media.seek(int(round(position, 0)))
            # continue playing if the seek was requested when playing
            if was_playing is True:
                self.play()
        except:
            # It can happen if we attempted to seek after the video length
            self.stop()
            return False

        return True

    # -----------------------------------------------------------------------

    def media_tell(self):
        return self._media.tell()

    # -----------------------------------------------------------------------

    def tell(self):
        """Return the current time position in the video stream (float).

        :return: (float) The time at the middle of the current frame

        """
        # Time value at the end of the last read frame
        offset = self._media.tell()
        if offset == 0:
            return 0.
        time_value = float(offset) / float(self._media.get_framerate())
        # Duration of a frame
        frame_duration = 1. / self._media.get_framerate()
        # Time at the middle of the last read frame
        return time_value - (frame_duration / 2.)

    # -----------------------------------------------------------------------
    # About the video
    # -----------------------------------------------------------------------

    def get_duration(self):
        """Return the duration of the loaded video (float)."""
        if self._media is None:
            return 0.
        return self._media.get_duration()

    # -----------------------------------------------------------------------

    def get_framerate(self):
        if self._media is not None:
            return self._media.get_framerate()
        return 0

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_width()

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the frames in the video."""
        if self._media is None:
            return 0
        return self._media.get_height()

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

        # Nothing to do if we are not playing
        if self._ms == PlayerState().playing:
            if self._current_image is None:
                # we reach the end of the video
                self.stop()
            else:
                # TODO: refreshing the player frame is done on the main thread,
                #  causing the UI to be unresponsive due to the time needed to
                #  refresh the frame on some systems and when displaying big
                #  images (setting a background color works in these cases)
                #  It should be done in a separated thread instead
                # FIXME: this method is continuously called when attempting to
                #  play outside of the playback interval and/or media range,
                #  causing the UI to be unresponsive in some cases like with
                #  the combination of this case and the one above
                #  A fix which could be made is to ensure we are not seeking
                #  outside of the defined period when skipping frames in the
                #  _play_process method
                self.refresh_player_frame()

            # Send the wx.EVT_TIMER event
            wx.Timer.Notify(self)

        elif self._ms != PlayerState().paused:
            self.stop()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN, name="VideoPlayer")

        # The player!
        #TOO SLOW: can't display 60 fps ->
        #self.player = sppasImageFrame(self)
        #self.ap = sppasVideoPlayer(owner=self, player=self.player)
        self.ap = sppasVideoPlayer(owner=self)

        # Actions to perform with the player
        btn2 = wx.Button(self, -1, "Play", name="btn_play")
        btn2.Enable(False)
        self.Bind(wx.EVT_BUTTON, self._on_play_ap, btn2)
        btn3 = wx.Button(self, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self._on_pause_ap, btn3)
        btn4 = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self._on_stop_ap, btn4)
        btn5 = wx.Button(self, -1, "Previous Frame")
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
        self.ap.Bind(MediaEvents.EVT_MEDIA_LOADED, self.__on_media_loaded)
        self.ap.Bind(MediaEvents.EVT_MEDIA_NOT_LOADED, self.__on_media_not_loaded)
        # Event received every 10ms (in theory) when the audio is playing
        self.Bind(wx.EVT_TIMER, self._on_timer)

        wx.CallAfter(self._do_load_file)

    # ----------------------------------------------------------------------

    def _do_load_file(self):
        self.ap.load(os.path.join(paths.samples, "faces", "video_sample.mp4"))
        #self.ap.load("/E/data/corpus/FRA/Multimodal/CLeLfPC/01_syll/syll_2_MZ_dd520f/syll_2_MZ_dd520f_front.mkv")

    # ----------------------------------------------------------------------

    def __on_media_loaded(self, event):
        wx.LogDebug("Video file loaded successfully")
        self.FindWindow("btn_play").Enable(True)
        duration = self.ap.get_duration()
        self.slider.SetRange(0, int(duration * 1000.))

        # self.ap.set_period(10., 12.)
        # self.ap.seek(10.)
        # self.slider.SetRange(10000, 12000)

    # ----------------------------------------------------------------------

    def __on_media_not_loaded(self, event):
        wx.LogError("Video file not loaded")
        self.FindWindow("btn_play").Enable(False)
        self.slider.SetRange(0, 0)

    # ----------------------------------------------------------------------

    def _on_play_ap(self, event):
        self.ap.play()

    # ----------------------------------------------------------------------

    def _on_pause_ap(self, event):
        self.ap.pause()

    # ----------------------------------------------------------------------

    def _on_stop_ap(self, event):
        self.ap.stop()
        self.slider.SetValue(0)

    # ----------------------------------------------------------------------

    def _on_next_frame_ap(self, event):
        self.ap.play_frame()
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_prev_frame_ap(self, event):
        self.ap.play_frame(direction=-1)
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))

    # ----------------------------------------------------------------------

    def _on_timer(self, event):
        time_pos = self.ap.tell()
        self.slider.SetValue(int(time_pos * 1000.))
        event.Skip()

    # ----------------------------------------------------------------------

    def _on_seek_slider(self, event):
        time_pos_ms = self.slider.GetValue()
        self.ap.seek(float(time_pos_ms) / 1000.)
        self.ap.play_frame(direction=1)
