# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_analyze.errfilelist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: ErrorViewPanel to display an error message instead of the content.

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
import wx
import wx.lib.scrolledpanel as sc

from sppas.ui import _
from ..windows import sppasPanel
from ..windows import sppasTextCtrl

from .basefilelist import sppasFileSummaryPanel


# ----------------------------------------------------------------------------
# List of displayed messages:


MSG_ERROR = _("The file {:s} can't be displayed by this tool.")
MSG_UNK = _("Unknown error.")

# ---------------------------------------------------------------------------


class ErrorFileSummaryPanel(sppasFileSummaryPanel):
    """Display an error message instead of the summary of a file.

    """

    def __init__(self, parent, filename, name="errlist_panel"):
        super(ErrorFileSummaryPanel, self).__init__(parent, filename, name)
        self.Bind(wx.EVT_BUTTON, self.__process_tool_event)
        self.Collapse(False)
        self.SetRandomColours()

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        self.AddButton("close", direction=1)

        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        txtview = sppasTextCtrl(self, style=style, name="msg_textctrl")
        txtview.SetFont(wx.GetApp().settings.mono_text_font)
        txtview.SetEditable(False)
        self.set_error_message(MSG_UNK)
        self.SetPane(txtview)
        txtview.Bind(wx.EVT_MOUSEWHEEL, self._process_wheel)

    def _process_wheel(self, event):
        """An attempt to ignore event.

        This is an attempt to make the parent ScrolledPanel scrolling
        when mouse wheel on the text.

        """
        logging.debug(" -- txt mouse wheel event")
        wx.PostEvent(self.GetParent(), event)
        event.Skip()
        # ... should be turned into "EVT_SCROLL???"

    # -----------------------------------------------------------------------

    def set_error_message(self, error_message):
        """Set the error message to be displayed.

        :param error_message: (str)

        """
        message = MSG_ERROR.format(self._filename) + "\n" + error_message
        txtview = self.FindWindow("msg_textctrl")
        txtview.SetValue(message)

        # required under Windows
        txtview.SetStyle(0, len(message), txtview.GetDefaultStyle())

        # Search for the height of the text
        nblines = len(message.split("\n")) + 1  # add one for a margin...
        view_height = float(self.get_font_height()) * 1.1 * float(nblines)
        txtview.SetMinSize(wx.Size(sppasPanel.fix_size(420), int(view_height)))

    # -----------------------------------------------------------------------

    def __process_tool_event(self, event):
        """Process a button event from the tools.

        :param event: (wx.Event)

        """
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "close":
            self.notify("close")

        else:
            event.Skip()

# ---------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):
    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="Test Error View")

        s = wx.BoxSizer(wx.VERTICAL)
        for i in range(10):
            p = ErrorFileSummaryPanel(self, filename="Wrong/Path/to/a/file.ext")
            p.set_error_message("This is an error message to explain why the"
                                " file is not properly displayed.")
            s.Add(p, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(s)
        self.SetAutoLayout(True)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
