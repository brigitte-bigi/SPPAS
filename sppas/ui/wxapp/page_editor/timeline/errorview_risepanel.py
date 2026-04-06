# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.timeline.errorview_risepanel.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  View panel to display an error message instead of a file content.

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

from sppas.ui import _
from sppas.ui.wxapp.windows import sppasPanel
from sppas.ui.wxapp.windows import sppasTextCtrl

from .baseview_risepanel import sppasFileViewPanel


# ----------------------------------------------------------------------------
# List of displayed messages:


MSG_ERROR = _("The file {:s} can't be displayed by this view.")
MSG_UNK = _("Unknown error.")

# ---------------------------------------------------------------------------


class ErrorViewPanel(sppasFileViewPanel):
    """Display an error message instead of the content of a file.

    """

    def __init__(self, parent, filename=None, name="errview_risepanel"):
        super(ErrorViewPanel, self).__init__(parent, filename=filename, name=name)
        self.Expand()

        # Background color range - orange to red.
        self._rgb1 = (250, 190, 180)
        self._rgb2 = (255, 210, 200)
        self.SetRandomColours()

    # -----------------------------------------------------------------------
    # Override from the parent
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the panel."""
        style = wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH | \
                wx.TE_PROCESS_ENTER | wx.TE_BESTWRAP | wx.TE_NO_VSCROLL
        txtview = sppasTextCtrl(self, style=style)
        txtview.SetFont(wx.GetApp().settings.mono_text_font)
        txtview.SetEditable(False)
        self.SetPane(txtview)

        self.set_error_message(MSG_UNK)

    # -----------------------------------------------------------------------

    def set_error_message(self, error_message):
        """Set the error message to be displayed.

        :param error_message: (str)

        """
        message = "\n{}\n{}".format(MSG_ERROR.format(self._filename), error_message)

        txtview = self.GetPane()
        txtview.SetValue(message)

        # required under Windows
        txtview.SetStyle(0, len(message), txtview.GetDefaultStyle())

        # Search for the height of the text
        nblines = len(error_message.split("\n")) + 1
        view_height = self.get_font_height() * nblines

        txtview.SetMinSize(wx.Size(sppasPanel.fix_size(420), int(view_height) + 6))

# ---------------------------------------------------------------------------


class TestPanel(sppasPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="ErrorView RisePanel")

        p1 = ErrorViewPanel(self, filename="Path/to/a/file.ext")
        p2 = ErrorViewPanel(self, filename="Path to another file")
        p3 = ErrorViewPanel(self, filename="Path to another file")
        p4 = ErrorViewPanel(self, filename="Path to another file")

        p1.set_error_message("This is an error message to explain why the"
                             " file is not properly displayed.")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(p1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
        s.Add(p2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
        s.Add(p3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
        s.Add(p4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
        self.SetSizer(s)
