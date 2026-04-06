# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_analyze.datalist.tierslist.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A class to display a summary of a list of tiers.

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


class TiersListCtrl(BaseObjectListCtrl):
    """A panel to display a list of tiers.

    """

    def __init__(self, parent, objects, name="tiers_listctrl"):
        super(TiersListCtrl, self).__init__(parent, objects, name=name)

    # ------------------------------------------------------------------------

    def _create_columns(self):
        """Create columns to display the tiers."""
        self.AppendColumn("type", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(50))
        self.AppendColumn("name", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(160))
        self.AppendColumn("len", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(30))
        self.AppendColumn("loctype", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(50))
        self.AppendColumn("begin", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(40))
        self.AppendColumn("end", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(40))
        self.AppendColumn("tagtype", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(40))
        self.AppendColumn("tagged", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(30))
        self.AppendColumn("id", format=wx.LIST_FORMAT_LEFT, width=sppasPanel.fix_size(240))

    # ------------------------------------------------------------------------

    def update_item(self, obj):
        """Update information of an object, except its state.

        :param obj: (sppasTier)

        """
        if obj.is_point() is True:
            tier_type = "Point"
        elif obj.is_interval():
            tier_type = "Interval"
        elif obj.is_disjoint():
            tier_type = "Disjoint"
        else:  # probably an empty tier
            tier_type = "Unknown"

        if obj.is_empty() is True:
            begin = " ... "
            end = " ... "
        else:
            begin = str(obj.get_first_point().get_midpoint())
            end = str(obj.get_last_point().get_midpoint())

        if obj.is_string() is True:
            tier_tag_type = "String"
        elif obj.is_int() is True:
            tier_tag_type = "Integer"
        elif obj.is_float() is True:
            tier_tag_type = "Float"
        elif obj.is_bool() is True:
            tier_tag_type = "Bool"
        else:
            tier_tag_type = "Unknown"

        if obj.get_id() in self._trss:
            index = self._trss.index(obj.get_id())
            self.SetItem(index, 0, "Tier")
            self.SetItem(index, 1, obj.get_name())
            self.SetItem(index, 2, str(len(obj)))
            self.SetItem(index, 3, tier_type)
            self.SetItem(index, 4, begin)
            self.SetItem(index, 5, end)
            self.SetItem(index, 6, tier_tag_type)
            self.SetItem(index, 7, str(obj.get_nb_filled_labels()))
            self.SetItem(index, 8, obj.get_id())
            self.RefreshItem(index)

            state = obj.get_meta("private_checked", "False")
            if state == "True":
                self.Select(index, on=1)
