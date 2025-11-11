# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_annotate.annotevent.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Events of the page to annotate of the GUI

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

import wx.lib.newevent

EVT_ANNOT_PAGE_CHANGE = wx.PyEventBinder(wx.NewEventType(), 1)


class sppasAnnotBookPageChangeEvent(wx.PyCommandEvent):
    """Class for an event sent when an action requires to change the page.

    The binder of this event is EVT_PAGE_CHANGE.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasAnnotBookPageChangeEvent, self).__init__(EVT_ANNOT_PAGE_CHANGE.typeId, event_id)
        self.__to_page = ""
        self.__fct = ""
        self.__args = None

    # -----------------------------------------------------------------------

    def SetToPage(self, value):
        """Set the name of the destination page of the book.

        :param value: (str) Name of a page.

        """
        self.__to_page = str(value)

    # -----------------------------------------------------------------------

    def GetToPage(self):
        """Return the name of the destination page of the book.

        :returns: (str)

        """
        return self.__to_page

    # -----------------------------------------------------------------------

    def SetFctName(self, name):
        """Name of a function the destination page has to launch.

        :param name: (str) Name of a function of the destination page.

        """
        self.__fct = str(name)

    # -----------------------------------------------------------------------

    def GetFctName(self):
        """Return the name of the function the destination page will run.

        :returns: (str) Empty string if no function

        """
        return self.__fct

    # -----------------------------------------------------------------------

    def SetFctArgs(self, args):
        """Arguments for the function.

        :param args: ()

        """
        self.__args = args

    # -----------------------------------------------------------------------

    def GetFctArgs(self):
        """Return the arguments for the function the destination page will run.

        :returns: () None if no arguments

        """
        return self.__args
