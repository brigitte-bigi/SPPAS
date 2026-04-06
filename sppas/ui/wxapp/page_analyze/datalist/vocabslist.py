# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_analyze.datalist.vocabslist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A class to display a summary of a list of controlled vocabularies.

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

from sppas.ui.wxapp.windows.panels import sppasPanel
from .baseobjlist import BaseObjectListCtrl

# ---------------------------------------------------------------------------


class CtrlVocabListCtrl(BaseObjectListCtrl):
    """A panel to display a list of controlled vocabs.

    """

    def __init__(self, parent, objects, name="vocabs_listctrl"):
        super(CtrlVocabListCtrl, self).__init__(parent, objects, name=name)

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create columns to display the tiers."""
        self.AppendColumn("type", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(50))
        self.AppendColumn("name", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(200))
        self.AppendColumn("description", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(80))
        self.AppendColumn("id", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(220))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state."""
        if obj.get_id() in self._trss:
            index = self._trss.index(obj.get_id())
            self.SetItem(index, 0, "Vocab")
            self.SetItem(index, 1, obj.get_name())
            self.SetItem(index, 2, obj.get_description())
            self.SetItem(index, 3, obj.get_id())
            self.RefreshItem(index)

    # ------------------------------------------------------------------------

    def __item_selected(self, event):
        index = event.GetIndex()
        self.Select(index, on=False)
