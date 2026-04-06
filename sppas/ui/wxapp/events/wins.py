# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.wins.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Custom events for windows: moved, selected, ...

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


class sppasWindowSelectedEvent(wx.PyCommandEvent):
    """Class for an event sent when the window is selected.

    The binder of this event is EVT_WINDOW_SELECTED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasWindowSelectedEvent, self).__init__(sb.EVT_WINDOW_SELECTED.typeId, event_id)
        self.__selected = False

    # -----------------------------------------------------------------------

    def SetSelected(self, value):
        """Set the window status as selected or not.

        :param value: (bool) True if the window is selected, False otherwise.

        """
        value = bool(value)
        self.__selected = value

    # -----------------------------------------------------------------------

    def GetSelected(self):
        """Return the window status as True if selected.

        :returns: (bool)

        """
        return self.__selected

    # -----------------------------------------------------------------------

    Selected = property(GetSelected, SetSelected)

# ---------------------------------------------------------------------------


class sppasWindowFocusedEvent(wx.PyCommandEvent):
    """Class for an event sent when the window is focused.

    The binder of this event is EVT_WINDOW_FOCUSED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasWindowFocusedEvent, self).__init__(sb.EVT_WINDOW_FOCUSED.typeId, event_id)
        self.__focused = False

    # -----------------------------------------------------------------------

    def SetFocused(self, value):
        """Set the window status as focused or not.

        :param value: (bool) True if the window is focused, False otherwise.

        """
        value = bool(value)
        self.__focused = value

    # -----------------------------------------------------------------------

    def GetFocused(self):
        """Return the window status as True if selected.

        :returns: (bool)

        """
        return self.__focused

    # -----------------------------------------------------------------------

    Focused = property(GetFocused, SetFocused)

# ---------------------------------------------------------------------------


class sppasWindowMovedEvent(wx.PyCommandEvent):
    """Class for an event sent when the window is moved.

    The binder of this event is EVT_WINDOW_MOVED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasWindowMovedEvent, self).__init__(sb.EVT_WINDOW_MOVED.typeId, event_id)
        self.__position = None

    # -----------------------------------------------------------------------

    def GetObjPosition(self):
        """Return the object relative position when the event is sent."""
        return self.__position

    # -----------------------------------------------------------------------

    def SetObjPosition(self, pos):
        """Set the object relative position when the event is sent."""
        self.__position = pos

# ---------------------------------------------------------------------------


class sppasWindowResizedEvent(wx.PyCommandEvent):
    """Class for an event sent when the window is resized.

    The binder of this event is EVT_WINDOW_RESIZED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasWindowResizedEvent, self).__init__(sb.EVT_WINDOW_RESIZED.typeId, event_id)
        self.__position = None
        self.__size = None

    # -----------------------------------------------------------------------

    def GetObjPosition(self):
        """Return the object relative position when the event is sent."""
        return self.__position

    # -----------------------------------------------------------------------

    def SetObjPosition(self, pos):
        """Set the object relative position when the event is sent."""
        self.__position = pos

    # -----------------------------------------------------------------------

    def GetObjSize(self):
        """Return the object size when the event is sent."""
        return self.__size

    # -----------------------------------------------------------------------

    def SetObjSize(self, size):
        """Set the object size when the event is sent."""
        self.__size = size

# ---------------------------------------------------------------------------


class sppasButtonPressedEvent(wx.PyCommandEvent):
    """Class for an event sent when a check/radio/toggle button is pressed.

    The binder of this event is EVT_BUTTON_PRESSED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasButtonPressedEvent, self).__init__(sb.EVT_BUTTON_PRESSED.typeId, event_id)
        self.__pressed = False

    # -----------------------------------------------------------------------

    def SetPressed(self, value):
        """Set the window status as selected or not.

        :param value: (bool) True if the window is selected, False otherwise.

        """
        value = bool(value)
        self.__pressed = value

    # -----------------------------------------------------------------------

    def GetPressed(self):
        """Return the window status as True if selected.

        :returns: (bool)

        """
        return self.__pressed

    # -----------------------------------------------------------------------

    Pressed = property(GetPressed, SetPressed)
