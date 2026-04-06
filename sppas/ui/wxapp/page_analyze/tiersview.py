# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_analyze.tiersview.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Views of annotations of a tier.

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

Each tier is displayed in a ListCtrl.
Organize the view of each tier in a notebook.

"""

import wx

from sppas.ui.wxapp.windows.dialogs import sppasDialog
from sppas.ui.wxapp.windows.book import sppasNotebook
from sppas.ui.wxapp.panel_shared.tierlist import sppasTierListCtrl

# ---------------------------------------------------------------------------


class sppasTiersViewDialog(sppasDialog):
    """A dialog with a notebook to display each tier in a listctrl.

    Returns wx.ID_OK if ShowModal().

    """

    def __init__(self, parent, tiers, title="Tiers View"):
        """Create a dialog to display tiers.

        :param parent: (wx.Window)
        :param tiers: (List of sppasTier)

        """
        super(sppasTiersViewDialog, self).__init__(
            parent=parent,
            title=title,
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP,
            name="tiersview_dialog")

        self._create_content(tiers)
        self.CreateActions([wx.ID_OK])

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.CenterOnParent()
        self.FadeIn()

    # -----------------------------------------------------------------------

    def _create_content(self, tiers):
        """Create the content of the message dialog."""
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        for tier in tiers:
            page = sppasTierListCtrl(notebook, tier, "")
            notebook.AddPage(page, tier.get_name())
        self.SetContent(notebook)
