# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.gauge.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: a gauge not built on native controls but is self-drawn.

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

import wx

from .basedcwindow import sppasDCWindow

# ---------------------------------------------------------------------------


class sppasGauge(sppasDCWindow):
    """A window imitating a slider but with the same look on all platforms.

    Non-interactive: show values but can't be moved with the mouse.

    """

    def __init__(self, parent, id=wx.ID_ANY,
                 range=100,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
                 name="gauge_panel"):
        """Create a self-drawn window to display a gauge value into a range.

        """
        super(sppasGauge, self).__init__(parent, id, pos=pos, size=size, style=style, name=name)
        self._start = 0
        self._end = range
        self.__pos = 0
        self._vert_border_width = 0
        self._horiz_border_width = 0
        self._min_width = 48
        self.__label = ""

    # -----------------------------------------------------------------------

    def set_label(self, entry):
        """Set the label string to display at left of the gauge."""
        self.__label = str(entry)

    # -----------------------------------------------------------------------

    def get_range(self):
        """Return the (start, end) values."""
        return self._start, self._end

    # -----------------------------------------------------------------------

    def set_range(self, start, end):
        """Fix the range of values the slider is considering.

        Do not refresh.

        :param start: (float)
        :param end: (float)
        :return: (float) current position: either the current one, start or end.

        """
        start = float(start)
        end = float(end)
        if start > end:
            raise ValueError("Start {} can't be greater then end {}".format(start, end))
        self._start = start
        self._end = end

        # question: do we have to adjust pos automatically??
        # if self.__pos < self._start:
        #     self.__pos = self._start
        # if self.__pos > self._end:
        #     self.__pos = self._end

    # -----------------------------------------------------------------------

    def get_value(self):
        """Return the current position value."""
        return self.__pos

    # -----------------------------------------------------------------------

    def set_value(self, pos):
        """Fix the current position value.

        Do not refresh.

        :param pos: (float) A position in the current range.
        :return: (float) current position: either the given one, start or end.

        """
        pos = float(pos)
        self.__pos = pos

        if self.__pos < self._start:
            self.__pos = self._start
        if self.__pos > self._end:
            self.__pos = self._end
        return self.__pos

    # -----------------------------------------------------------------------

    def DrawContent(self, dc, gc):
        """Override."""
        x, y, w, h = self.GetContentRect()
        # Draw background
        brush = wx.Brush(wx.Colour(235, 235, 245), wx.BRUSHSTYLE_SOLID)
        dc.SetBrush(brush)
        pen = wx.Pen(wx.Colour(235, 235, 245), 1, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)
        dc.DrawRectangle(0, 0, w, h)

        # Estimate the width to fill in
        range = self._end - self._start
        ratio = float(self.__pos) / float(range)
        fill_w = int(float(w) * ratio)

        # Fill in...
        brush = wx.Brush(wx.Colour(35, 50, 90), wx.BRUSHSTYLE_SOLID)
        dc.SetBrush(brush)
        pen = wx.Pen(wx.Colour(35, 50, 90), 1, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)
        dc.DrawRectangle(0, 0, fill_w, h)
        # Draw the value of the current position at left or at right
        pos_x = 0
        total_dur = self._end - self._start
        pos_dur = self.__pos - self._start
        if total_dur > 0.:
            ratio = pos_dur / total_dur
            pos_x = w * ratio

        # Draw the value
        if len(self.__label) > 0:
            tw, th = self.get_text_extend(dc, gc, self.__label)
            font = self.GetFont()
            gc.SetFont(font)
            dc.SetFont(font)
            dc.SetTextForeground(wx.Colour(128, 128, 128))
            dc.DrawText(self.__label, 2, (h - th) // 2)

# ----------------------------------------------------------------------------
# Panel for tests
# ----------------------------------------------------------------------------


class TestPanel(wx.Panel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Gauge")

        s1 = sppasGauge(self, pos=(0, 0), size=wx.Size(120, 20), name="s1")

        s2 = sppasGauge(self, pos=(0, 50), size=wx.Size(120, 20), name="s2")
        s2.SetForegroundColour(wx.Colour(208, 200, 166))
        s2.set_range(0, 10)
        s2.set_value(6)
        s1.set_label("6%")

        s3 = sppasGauge(self, style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_SIMPLE, name="s3")
        s3.set_range(0, 3245)
        s3.set_value(4567)
        s3.set_label("a custom label...")

        s4 = sppasGauge(self, name="s4")
        s4.set_range(0, 345)
        s4.set_value(56)

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(s1, 0, wx.EXPAND)
        s.Add(s2, 0, wx.EXPAND)
        s.Add(s3, 1, wx.EXPAND)
        s.Add(s4, 1, wx.EXPAND)
        self.SetSizer(s)
