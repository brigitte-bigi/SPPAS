# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.splash.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A window to display a gauge progress.

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

"""

import wx

# ---------------------------------------------------------------------------


class sppasGauge(wx.Window):
    """Mimics a gauge with a ClientDC: no events are used.

    """

    def __init__(self, parent, id=-1,
                 range=100,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE | wx.TRANSPARENT_WINDOW | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.FULL_REPAINT_ON_RESIZE,
                 name="sppasgauge"):
        """Initialize a new sppasGauge instance.

        :param parent: Parent window. Must not be None.
        :param id:     A value of -1 indicates a default value.
        :param pos:    If the position (-1, -1) is specified
                       then a default position is chosen.
        :param size:   If the default size (-1, -1) is specified
                       then a default size is chosen.
        :param style:  often LC_REPORT
        :param name:   Window name.

        """
        super(sppasGauge, self).__init__(parent, id, pos, size, style, name)
        self.__range = int(range)
        self.__value = 0
        self.gc = wx.ClientDC(self)
        self.Show(True)

    # -----------------------------------------------------------------------

    def GetRange(self):
        """Return the max range value."""
        return self.__range

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        """Set the value of the gauge.

        :param value: (int)

        """
        value = int(value)
        if value < 0:
            value = 0
        if value > self.__range:
            value = self.__range

        self.__value = value
        self.Draw()

    # -----------------------------------------------------------------------

    def Draw(self):
        """Draw the gauge in the ClientDC."""
        w, h = self.GetSize()

        # Draw background
        brush = wx.Brush(wx.Colour(235, 235, 245), wx.BRUSHSTYLE_SOLID)
        self.gc.SetBrush(brush)
        pen = wx.Pen(wx.Colour(235, 235, 245), 1, wx.PENSTYLE_SOLID)
        self.gc.SetPen(pen)
        self.gc.DrawRectangle(0, 0, w, h)

        # Estimate the width to fill in
        ratio = float(self.__value) / float(self.__range)
        fill_w = int(float(w) * ratio)

        # Fill in...
        brush = wx.Brush(wx.Colour(35, 50, 90), wx.BRUSHSTYLE_SOLID)
        self.gc.SetBrush(brush)
        pen = wx.Pen(wx.Colour(35, 50, 90), 1, wx.PENSTYLE_SOLID)
        self.gc.SetPen(pen)
        self.gc.DrawRectangle(0, 0, fill_w, h)
