# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_analyze.basefilelist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class to diaplay the content of a file as a list.

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

import random
import os
import wx
import wx.lib.scrolledpanel as sc

from sppas.core.config import paths

from ..events import sppasActionEvent
from ..windows.panels import sppasPanel
from ..windows.panels import sppasCollapsiblePanel

# ----------------------------------------------------------------------------


class sppasFileSummaryPanel(sppasCollapsiblePanel):
    """Panel to display a summary of the content of a file.

    """

    def __init__(self, parent, filename, name="file_panel"):
        super(sppasFileSummaryPanel, self).__init__(
            parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            label=filename,
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.BORDER_NONE,
            name=name)

        self._dirty = False
        self._filename = filename

        # Background color range
        self._rgb1 = (255, 200, 200)
        self._rgb2 = (255, 150, 150)
        self._tools_bg_color = None

        # Create the GUI
        self._create_content()

        # Look&feel
        try:
            settings = wx.GetApp().settings
            self.SetForegroundColour(settings.fg_color)
            self.SetFont(settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the filename this panel is displaying."""
        return self._filename

    # ------------------------------------------------------------------------

    def set_filename(self, name):
        """Set a new name to the file.

        :param name: (str) Name of a file. It is not verified.

        """
        self._filename = name
        self.SetLabel(name)
        self._dirty = True

    # ------------------------------------------------------------------------

    def is_modified(self):
        """Return True if the content of the file has changed."""
        return self._dirty

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        # The name of the file is Bold
        f = wx.Font(font.GetPointSize(),
                    font.GetFamily(),
                    font.GetStyle(),
                    wx.FONTWEIGHT_BOLD,
                    font.GetUnderlined(),
                    font.GetFaceName())
        sppasCollapsiblePanel.SetFont(self, f)
        self.GetPane().SetFont(font)
        self.Layout()

    # -----------------------------------------------------------------------

    def SetRandomColours(self):
        """Set background and foreground colors from our range of rgb colors."""
        # Fix the color of the background
        r = random.randint(min(self._rgb1[0], self._rgb2[0]), max(self._rgb1[0], self._rgb2[0]))
        g = random.randint(min(self._rgb1[1], self._rgb2[1]), max(self._rgb1[1], self._rgb2[1]))
        b = random.randint(min(self._rgb1[2], self._rgb2[2]), max(self._rgb1[2], self._rgb2[2]))
        color = wx.Colour(r, g, b)

        if (r + g + b) > 384:
            self._tools_bg_color = color.ChangeLightness(95)
        else:
            self._tools_bg_color = color.ChangeLightness(105)

        # Set the BG color to the panel itself and to its children
        wx.Panel.SetBackgroundColour(self, color)
        self._child_panel.SetBackgroundColour(color)
        self._tools_panel.SetBackgroundColour(self._tools_bg_color)

        # Set the FG color to the panel itself and to its children
        min_i = min(self._rgb1 + self._rgb2 + (150,))
        fg = wx.Colour(r - min_i, g - min_i, b - min_i)
        self._child_panel.SetForegroundColour(fg)
        self._tools_panel.SetForegroundColour(fg)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def notify(self, action):
        wx.LogDebug("{:s} notifies its parent {:s} of action {:s}."
                    "".format(self.GetName(), self.GetParent().GetName(), action))
        evt = sppasActionEvent(self.GetId())
        evt.SetEventObject(self)
        evt.SetAction(action)
        wx.PostEvent(self.GetParent(), evt)

# ---------------------------------------------------------------------------


class TestSummaryPanel(sppasFileSummaryPanel):

    FILENAME = os.path.join(paths.samples, "samples-fra", "F_F_B003_P8.wav")

    def __init__(self, parent):
        super(TestSummaryPanel, self).__init__(
            parent,
            TestSummaryPanel.FILENAME)
        self.Collapse(False)

    def _create_content(self):
        # Child panel
        panel = sppasPanel(self)
        st = wx.StaticText(panel, -1, self.get_filename(), pos=(10, 100))
        sz = st.GetBestSize()
        panel.SetSize((sz.width + 20, sz.height + 20))
        self.SetPane(panel)

# ---------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Base FileSummary View")

        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(10):
            panel = TestSummaryPanel(self)
            r = (i+1)*5
            g = (i+1)*15
            b = (i+1)*25
            panel.SetMinSize(wx.Size(-1, 128))
            panel.GetPane().SetBackgroundColour(wx.Colour(r, g, b))
            sizer.Add(panel, 0, wx.EXPAND, 10)
            self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnCollapseChanged, panel)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnCollapseChanged(self, evt=None):
        panel = evt.GetEventObject()
        self.ScrollChildIntoView(panel)

    def OnSize(self, evt):
        self.Layout()
        self.Refresh()
