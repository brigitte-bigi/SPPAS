# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.events.actions.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Custom action events used when an action has to be performed.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

from .binder import sb

# ---------------------------------------------------------------------------


class sppasActionEvent(wx.PyCommandEvent):
    """Class for an event sent when an action is requested.

    The binder of this event is EVT_ACTION.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasActionEvent, self).__init__(sb.EVT_ACTION.typeId, event_id)
        self.__action = ""

    # -----------------------------------------------------------------------

    def SetAction(self, value):
        """Set the action name.

        :param value: (str)

        """
        value = str(value)
        self.__action = value

    # -----------------------------------------------------------------------

    def GetAction(self):
        """Return the action name.

        :returns: (name)

        """
        return self.__action

    # -----------------------------------------------------------------------

    action = property(GetAction, SetAction)

# ---------------------------------------------------------------------------


class sppasActionFileEvent(wx.PyCommandEvent):
    """Class for an event sent when an action on a file is requested.

    The binder of this event is EVT_ACTION_FILE.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasActionFileEvent, self).__init__(sb.EVT_ACTION_FILE.typeId, event_id)
        self.__action = ""
        self.__file = ""

    # -----------------------------------------------------------------------

    def SetAction(self, value):
        """Set the action name.

        :param value: (str)

        """
        value = str(value)
        self.__action = value

    # -----------------------------------------------------------------------

    def GetAction(self):
        """Return the action name.

        :returns: (name)

        """
        return self.__action

    # -----------------------------------------------------------------------

    def SetFilename(self, value):
        """Set the action filename.

        :param value: (str)

        """
        value = str(value)
        self.__file = value

    # -----------------------------------------------------------------------

    def GetFilename(self):
        """Return the action filename.

        :returns: (name)

        """
        return self.__file

    # -----------------------------------------------------------------------

    action = property(GetAction, SetAction)
    filename = property(GetFilename, SetFilename)
