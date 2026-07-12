# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.events.mains.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Main custom events for the app.

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

import logging
import wx

from sppas.core.coreutils import sppasTypeError
from sppas.src.wkps import sppasWorkspace

from .binder import sb

# ---------------------------------------------------------------------------


class sppasLoggingEvent(wx.PyCommandEvent):
    """Class for an event sent when there's a logging message.

    The binder of this event is EVT_LOGGING.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasLoggingEvent, self).__init__(sb.EVT_LOGGING.typeId, event_id)
        self.__record = logging.LogRecord("", 0, "", 0, "", None, None)

    # -----------------------------------------------------------------------

    def SetRecord(self, record):
        """Set the logging record.

        https://docs.python.org/3/library/logging.html#logging.LogRecord

        :param record: (logging.LogRecord) see logging documentation

        """
        if isinstance(record, logging.LogRecord) is False:
            raise sppasTypeError("LogRecord", type(record))
        self.__record = record

    # -----------------------------------------------------------------------

    def GetRecord(self):
        """Return the logging record.

        :returns: (logging.LogRecord)

        """
        return self.__record

    # -----------------------------------------------------------------------

    record = property(GetRecord, SetRecord)

# ---------------------------------------------------------------------------


class sppasDataChangedEvent(wx.PyCommandEvent):
    """Class for an event sent when there's changes on the workspace.

    The binder of this event is EVT_DATA_CHANGED.

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasDataChangedEvent, self).__init__(sb.EVT_DATA_CHANGED.typeId, event_id)
        self.__workspace = None

    # -----------------------------------------------------------------------

    def SetWorkspace(self, data):
        """Set the stored data.

        :param data: (logging.LogRecord)

        """
        if isinstance(data, sppasWorkspace) is False:
            raise sppasTypeError("sppasWorkspace", type(data))
        self.__workspace = data

    # -----------------------------------------------------------------------

    def GetWorkspace(self):
        """Return the data.

        :returns: (sppasWorkspace)

        """
        return self.__workspace

    # -----------------------------------------------------------------------

    workspace = property(GetWorkspace, SetWorkspace)

# ---------------------------------------------------------------------------


class sppasCommMessageEvent(wx.PyCommandEvent):
    """Class for an event sent when a message is received on the socket.

    The binder of this event is EVT_COMM_MESSAGE. The event carries the
    (key, value) of a message received from the other UI (swapp), exactly
    as parsed from the shared JSON envelope (see sppasCommKeys).

    """

    def __init__(self, event_id):
        """Default class constructor.

        :param event_id: the event identifier.

        """
        super(sppasCommMessageEvent, self).__init__(sb.EVT_COMM_MESSAGE.typeId, event_id)
        self.__key = -1
        self.__value = None

    # -----------------------------------------------------------------------

    def SetKey(self, key):
        """Set the key of the received message.

        :param key: (int) One of the sppasCommKeys constants

        """
        if isinstance(key, int) is False:
            raise sppasTypeError("int", type(key))
        self.__key = key

    # -----------------------------------------------------------------------

    def GetKey(self):
        """Return the key of the received message.

        :returns: (int)

        """
        return self.__key

    # -----------------------------------------------------------------------

    key = property(GetKey, SetKey)

    # -----------------------------------------------------------------------

    def SetValue(self, value):
        """Set the value of the received message.

        :param value: (any) The JSON-parsed value of the message

        """
        self.__value = value

    # -----------------------------------------------------------------------

    def GetValue(self):
        """Return the value of the received message.

        :returns: (any)

        """
        return self.__value

    # -----------------------------------------------------------------------

    value = property(GetValue, SetValue)
