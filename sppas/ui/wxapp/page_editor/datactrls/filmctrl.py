# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.datactrls.filmctrl.py
:author:   Audric V
:contact:  contact@sppas.org
:summary:  Viewer of frames of a video in the visible part of in the editor.

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

Viewer of frames of a video in the visible part of in the editor.

"""

import logging

import wx

from sppas.ui.wxapp.page_editor.datactrls.videodatavalues import VideoDataValues
from sppas.ui.wxapp.windows import sppasDCWindow, sppasStaticText

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

MIN_PANEL_WIDTH_TO_DRAW = 5
MIN_PANEL_HEIGHT_TO_DRAW = 3
MIN_FRAME_WIDTH = 5
MIN_DURATION_TO_DRAW = 0.02
DEFAULT_PEN_WIDTH = 1
FRAME_BORDER_COLOUR = wx.Colour(50, 135, 80)
FRAME_FILL_COLOUR = wx.Colour(50, 70, 80)

# -----------------------------------------------------------------------


class SppasFilmWindow(sppasDCWindow):
    """Viewer of frames of a video in the visible part of in the editor."""

    # -----------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------

    def __init__(self,
                 parent: wx.Window,
                 id: str = wx.ID_ANY,
                 pos: wx.Position = wx.DefaultPosition,
                 size: wx.Size = wx.DefaultSize,
                 style: int = wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name: str = "film_panel"):
        super(SppasFilmWindow, self).__init__(parent, id, pos, size, style, name)
        
        # Period of time to draw (in seconds)
        self.__period = (0., 0.)
        # the number of pixels to represent 1 second of time
        self._pxframe = 0.

        # An instance of VideoDataValues()
        self._video_data = None

        self._frames_period_start = -1.
        self._frames_period_end = -1.

        self._pen_width = DEFAULT_PEN_WIDTH
        self._vert_border_width = 0
        self._horiz_border_width = self._pen_width * 2
        
        self.SetBorderColour(FRAME_BORDER_COLOUR)

        self.Bind(wx.EVT_SIZE, self._on_size)

    # -----------------------------------------------------------------------

    def SetPenWidth(self, value: int) -> None:
        value = int(value)
        if value < 1:
            value = 1
        if value > 20:
            value = 20
        self._pen_width = value
        self._horiz_border_width = value * 2

    # -----------------------------------------------------------------------
    # Getters/setters (public and private)
    # -----------------------------------------------------------------------

    def get_visible_period(self) -> (float, float):
        """Return (begin, end) time values of the period to draw."""
        return self.__period[0], self.__period[1]

    # -----------------------------------------------------------------------

    def set_visible_period(self, start: float, end: float) -> bool:
        """Set the period to draw (seconds).

        Do not re-draw the window, but update the tooltip with the new visible
        period.

        :param start: (float) Start time value (seconds)
        :param end: (float) End time value (seconds)
        :return: (bool) whether the period changed

        """
        start = float(start)
        end = float(end)
        if start != self.__period[0] or end != self.__period[1]:
            self.__period = (start, end)
            duration = end - start
            if duration < MIN_DURATION_TO_DRAW:
                logging.warning("Period {:f}-{:f} is not large enough to draw film.".format(start, end))
                self._pxframe = 0.
            else:
                x, y, w, h = self.GetContentRect()
                self._pxframe = float(w) / duration
            return True
        return False

    # -----------------------------------------------------------------------

    def get_sel_frames_period(self) -> (float, float):
        """Return the period of time of the 3 displayed frames."""
        return self._frames_period_start, self._frames_period_end

    # -----------------------------------------------------------------------

    def set_sel_frames_period(self, start: float, end: float) -> None:
        """Set the period of time of the 3 displayed frames.
        
        :param start: (float) Start time in seconds or -1.
        :param end: (float) End time in seconds or -1.
        
        """
        self._frames_period_start = start
        self._frames_period_end = end

    # -----------------------------------------------------------------------

    def set_video_data(self, video_data: VideoDataValues) -> None:
        """Set the video data to use.

        :param video_data: (VideoDataValues) the video data to use

        """
        self._video_data = video_data

    # -----------------------------------------------------------------------
    # Draw methods (public and protected)
    # -----------------------------------------------------------------------

    def GetContentRect(self) -> (int, int, int, int):
        """Override. Adjust the width with the period to draw."""
        x, y, w, h = sppasDCWindow.GetContentRect(self)
        if self._video_data is None:
            return x, y, w, h
        video_duration = self._video_data.duration

        if video_duration < self.__period[1]:
            total_visible = self.__period[1] - self.__period[0]
            video_visible = video_duration - self.__period[0]
            w = int((w * video_visible) / total_visible)

        return x, y, w, h

    # -----------------------------------------------------------------------

    def DrawContent(self, dc: wx.DC, gc: wx.GCDC) -> None:
        if self.__is_invalid_data_present() is True:
            return

        x, y, w, h = self.GetContentRect()

        if w < MIN_PANEL_WIDTH_TO_DRAW or h < MIN_PANEL_HEIGHT_TO_DRAW:
            return

        time_range = self.__period[1] - self.__period[0]
        if time_range <= 0:
            return

        frame_duration = 1. / self._video_data.framerate
        frame_size = int(w * frame_duration / time_range)

        # whether the frame size is large enough to draw each frame
        is_frame_size_large_enough = frame_size >= MIN_FRAME_WIDTH

        # if the frame size is not large enough to draw each frame, we want to draw a single rectangle instead
        # we have to draw it before we draw the selected frames one, otherwise the selected frames rectangle wouldn't
        # be visible
        if is_frame_size_large_enough is False:
            # set the correct color
            dc.SetBrush(wx.Brush(FRAME_BORDER_COLOUR, wx.BRUSHSTYLE_SOLID))

            dc.DrawRectangle(x=x, y=self._horiz_border_width, width=w, height=h)

        # draw only a rectangle of the selected frames period if this period is in the range of the visible one
        if self._frames_period_start < self.__period[1] and self._frames_period_end > self.__period[0]:
            # set the correct colors
            dc.SetPen(wx.Pen(FRAME_FILL_COLOUR, self._pen_width))
            dc.SetBrush(wx.Brush(FRAME_FILL_COLOUR, wx.BRUSHSTYLE_SOLID))

            self.__draw_selected_frames_rectangle(w=w, period=time_range, dc=dc, h=h)

        # if the frame size is large enough, draw frames
        if is_frame_size_large_enough is True:
            # set the correct colors
            dc.SetPen(wx.Pen(FRAME_BORDER_COLOUR, self._pen_width))
            dc.SetBrush(wx.Brush(FRAME_FILL_COLOUR, wx.BRUSHSTYLE_TRANSPARENT))

            self.__draw_individual_frames(dc=dc, frame_duration=frame_duration, w=w, h=h)

    # -----------------------------------------------------------------------

    def __is_invalid_data_present(self) -> bool:
        # draw only lines and/or rectangles if we have enough size and duration, and if video frame rate and visible
        # part are known and valid

        # we can't use pxframe in the cases where invalid or unknown data is passed, as pxframe assignment only checks
        # the length of the period shown
        return self._video_data is None or self._pxframe == 0. or self._video_data.duration <= 0. \
            or self._video_data.framerate <= 0. \
            or (self.__period[0] < 0. or self.__period[0] > self._video_data.duration) \
            or (self.__period[1] <= 0. or self.__period[1] > self._video_data.duration)

    # -----------------------------------------------------------------------

    def __draw_selected_frames_rectangle(self, w: float, period: float, dc: wx.DC, h: float) -> None:
        rectangle_start = max(self._frames_period_start, self.__period[0])
        rectangle_end = min(self._frames_period_end, self.__period[1])

        duration_start = rectangle_start - self.__period[0]
        duration_end = rectangle_end - self.__period[0]

        # convert times into pixels
        rectangle_start_width = int(round(w * duration_start / period, 0))
        rectangle_end_width = int(round(w * duration_end / period, 0))

        dc.DrawRectangle(x=rectangle_start_width,
                         y=self._horiz_border_width,
                         width=rectangle_end_width - rectangle_start_width,
                         height=h)

    # -----------------------------------------------------------------------

    def __draw_individual_frames(self, dc: wx.DC, frame_duration: float, w: int, h: int) -> None:
        # draw lines corresponding to frame separators

        h_with_horizontal_border = h + self._horiz_border_width * 2

        # draw first vertical line(s)
        initial_duration_drawn = self.__draw_first_frame_lines(frame_duration=frame_duration,
                                                               dc=dc,
                                                               h_with_horizontal_border=h_with_horizontal_border,
                                                               w=w)
        if initial_duration_drawn < 0.:
            # if initial_duration_drawn is negative, this means that we can draw only the initial line and nothing else
            return

        self.__draw_second_until_last_visible_frame_lines(duration_drawn=initial_duration_drawn,
                                                          frame_duration=frame_duration,
                                                          w=w,
                                                          dc=dc,
                                                          h_with_horizontal_border=h_with_horizontal_border)

    # -----------------------------------------------------------------------

    def __draw_first_frame_lines(self,
                                 frame_duration: float,
                                 dc: wx.DC,
                                 h_with_horizontal_border: int,
                                 w: int) -> float:
        # calculate the decimal value of the previous frame of the visible period's start
        # this is required to know if we draw a line at the beginning of the film and
        # where to draw the line representing the end of the frame
        pf_start_period_absolute_index = self.__period[0] / frame_duration

        # draw a line at the beginning only if the start position is a frame start
        # TODO: check if we need to improve the condition, by rounding values for instance
        if pf_start_period_absolute_index % 1 == 0:
            dc.DrawLine(x1=0, y1=0, x2=0, y2=h_with_horizontal_border)

        # get the previous frame time by using the integer value of the previous frame absolute index
        # and by multiplying by the frame duration
        previous_frame_index = int(pf_start_period_absolute_index)
        previous_frame_time = previous_frame_index * frame_duration

        # calculate the time shown
        duration_not_shown = self.__period[0] - previous_frame_time
        duration_shown = frame_duration - duration_not_shown

        # check if the duration between the start visible position and the next frame is fully inside the visible part
        # return a negative value if that's not the case, which should be handled by not drawing anything more
        if duration_shown > self.__period[1]:
            return -1.

        # calculate the line position x coordinate
        period_shown = self.__period[1] - self.__period[0]
        first_frame_end_line_pos_x = int(round(w * duration_shown / period_shown, 0))

        # draw the line
        dc.DrawLine(x1=first_frame_end_line_pos_x, y1=0, x2=first_frame_end_line_pos_x, y2=h_with_horizontal_border)

        return duration_shown

    # -----------------------------------------------------------------------

    def __draw_second_until_last_visible_frame_lines(self,
                                                     duration_drawn: float,
                                                     frame_duration: float,
                                                     w: int,
                                                     dc: wx.DC,
                                                     h_with_horizontal_border: int) -> None:
        period_shown = self.__period[1] - self.__period[0]
        while duration_drawn < period_shown:
            # calculate the time of line with a new frame
            duration_with_new_frame = duration_drawn + frame_duration

            if duration_with_new_frame > period_shown:
                # we are on the last frame and drawing completely the frame overlaps the range selected, so we don't
                # need to draw anything else
                return

            # calculate the line position x coordinate
            line_with_new_frame_pos_x = int(round(w * duration_with_new_frame / period_shown, 0))

            # draw the line
            dc.DrawLine(x1=line_with_new_frame_pos_x, y1=0, x2=line_with_new_frame_pos_x, y2=h_with_horizontal_border)

            duration_drawn = duration_with_new_frame

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    # noinspection PyUnusedLocal
    def _on_size(self, event: wx.Event) -> None:
        """Our size changed. We need to re-estimate pxframe before re-draw."""
        x, y, w, h = self.GetContentRect()
        prev_pxframe = self._pxframe
        duration = self.__period[1] - self.__period[0]
        middle = duration / 2.
        if duration < 0.02:
            self._pxframe = 0.
        else:
            self._pxframe = float(w) / duration

        # Re-draw only if the new pxframe is significantly different
        delay = middle - self.__period[0]
        x_old = x + int(delay * prev_pxframe)
        x_new = x + int(delay * self._pxframe)
        if x_old != x_new:
            self.Refresh()

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    """Test panel for SppasFilmWindow."""

    def __init__(self, parent: wx.Window):
        super(TestPanel, self).__init__(parent=parent,
                                        style=wx.BORDER_NONE | wx.WANTS_CHARS,
                                        name="Test SppasFilmWindow")
        self.__create_content()
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)

    # -----------------------------------------------------------------------

    def __create_content(self) -> None:
        sizer = wx.GridSizer(cols=1, vgap=0, hgap=0)

        self.__create_films_with_full_rectangle(sizer)
        self.__create_films_with_incomplete_rectangle(sizer)
        self.__create_films_with_not_visible_or_missing_rectangle(sizer)
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def __create_films_with_full_rectangle(self, sizer: wx.Sizer) -> None:
        # film panel with start matching a frame begin and sel_frames period fully inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="start_begin_frame_film_panel_full_rectangle",
            descriptive_text_label_name="start_begin_frame_descriptive_text_label",
            descriptive_text="Film panel with a visible start period at the beginning of a frame, "
                             "sel_frames period fully inside the visible part",
            pen_width=3,
            visible_period=(0, 0.18),
            sel_frames_period=(0.0, 0.12),
            framerate=25,
            duration=2.3,
            sizer=sizer)

        # film panel with start not matching a frame begin and sel_frames period fully inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="start_not_begin_frame_film_panel_full_rectangle",
            descriptive_text_label_name="start_not_begin_frame_descriptive_text_label",
            descriptive_text="Film panel with a visible start period not at the beginning of a frame, "
                             "sel_frames period fully inside the visible part",
            pen_width=4,
            visible_period=(0.03, 0.18),
            sel_frames_period=(0.04, 0.16),
            framerate=25,
            duration=1.23,
            sizer=sizer)

        # film panel with end matching a frame end and sel_frames period fully inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="end_end_frame_film_panel_full_rectangle",
            descriptive_text_label_name="end_end_frame_descriptive_text_label",
            descriptive_text="Film panel with a visible end period at the end of a frame, "
                             "sel_frames period fully inside the visible part",
            pen_width=6,
            visible_period=(0.03, 0.20),
            sel_frames_period=(0.04, 0.16),
            framerate=25,
            duration=12.3,
            sizer=sizer)

        # film panel with end not matching a frame end and sel_frames period fully inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="end_end_frame_film_panel_full_rectangle",
            descriptive_text_label_name="end_end_frame_full_rectangle_label",
            descriptive_text="Film panel with a visible end period not at the end of a frame, "
                             "sel_frames period fully inside the visible part",
            pen_width=4,
            visible_period=(0.03, 0.17),
            sel_frames_period=(0.04, 0.16),
            framerate=25,
            duration=21.3,
            sizer=sizer)

    # -----------------------------------------------------------------------

    def __create_films_with_incomplete_rectangle(self, sizer: wx.Sizer) -> None:
        # film panel with start matching a frame begin and sel_frames period partially inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="start_begin_frame_film_panel_incomplete_rectangle",
            descriptive_text_label_name="start_begin_frame_incomplete_rectangle_label",
            descriptive_text="Film panel with a visible start period at the beginning of a frame, "
                             "sel_frames period partially inside the visible part",
            pen_width=2,
            visible_period=(0.04, 0.12),
            sel_frames_period=(0.10, 0.14),
            framerate=50,
            duration=34.6,
            sizer=sizer)

        # film panel with start not matching a frame begin and sel_frames period partially inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="start_not_begin_frame_film_panel_incomplete_rectangle",
            descriptive_text_label_name="start_not_begin_frame_incomplete_rectangle_label",
            descriptive_text="Film panel with a visible start period not at the beginning of a frame, "
                             "sel_frames period partially inside the visible part",
            pen_width=4,
            visible_period=(0.05, 0.11),
            sel_frames_period=(0.02, 0.06),
            framerate=50,
            duration=44.4,
            sizer=sizer)

        # film panel with end matching a frame end and sel_frames period partially inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="end_end_frame_film_panel_incomplete_rectangle",
            descriptive_text_label_name="end_end_frame_incomplete_rectangle_label",
            descriptive_text="Film panel with a visible end period at the end of a frame, "
                             "sel_frames period partially inside the visible part",
            pen_width=2,
            visible_period=(0.07, 0.12),
            sel_frames_period=(0.10, 0.14),
            framerate=50,
            duration=34.6,
            sizer=sizer)

        # film panel with end not matching a frame end and sel_frames period partially inside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="end_not_end_frame_film_panel_incomplete_rectangle",
            descriptive_text_label_name="end_not_end_frame_incomplete_rectangle_label",
            descriptive_text="Film panel with a visible end period not at the end of a frame, "
                             "sel_frames period partially inside the visible part",
            pen_width=2,
            visible_period=(0.03, 0.13),
            sel_frames_period=(0.10, 0.14),
            framerate=50,
            duration=23.8,
            sizer=sizer)

    # -----------------------------------------------------------------------

    def __create_films_with_not_visible_or_missing_rectangle(self, sizer: wx.Sizer) -> None:
        # film panel with sel_frames period outside the visible part
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="film_panel_outside_rectangle",
            descriptive_text_label_name="film_panel_outside_rectangle_label",
            descriptive_text="Film panel with a sel_frames period outside the visible part",
            pen_width=5,
            visible_period=(1.02, 1.67),
            sel_frames_period=(0.10, 0.14),
            framerate=50,
            duration=23.8,
            sizer=sizer)

        # film panel with no/invalid sel_frames period
        self.__create_descriptive_text_and_film_panel_and_add_to_sizer(
            panel_name="film_panel_no_rectangle",
            descriptive_text_label_name="film_panel_no_rectangle_label",
            descriptive_text="Film panel with no/invalid sel_frames period",
            pen_width=2,
            visible_period=(3.45, 3.51),
            sel_frames_period=(-2.3, -8.78),
            framerate=50,
            duration=23.8,
            sizer=sizer)

    # -----------------------------------------------------------------------

    def __create_descriptive_text_and_film_panel_and_add_to_sizer(self,
                                                                  panel_name: str,
                                                                  descriptive_text_label_name: str,
                                                                  descriptive_text: str,
                                                                  pen_width: int,
                                                                  visible_period: (float, float),
                                                                  sel_frames_period: (float, float),
                                                                  framerate: int,
                                                                  duration: float,
                                                                  sizer: wx.Sizer) -> None:
        descriptive_text_label = sppasStaticText(parent=self,
                                                 name=descriptive_text_label_name,
                                                 label=descriptive_text,
                                                 style=wx.ALIGN_CENTRE_HORIZONTAL)
        film_panel = SppasFilmWindow(parent=self, name=panel_name)
        film_panel.SetPenWidth(pen_width)
        film_panel.set_visible_period(start=visible_period[0], end=visible_period[1])
        film_panel.set_sel_frames_period(start=sel_frames_period[0], end=sel_frames_period[1])

        video_data_values = VideoDataValues()
        video_data_values.framerate = framerate
        video_data_values.duration = duration
        film_panel.set_video_data(video_data_values)

        sizer.Add(window=descriptive_text_label, flags=wx.SizerFlags(0).Expand())
        sizer.Add(window=film_panel, flags=wx.SizerFlags(1).Expand())
