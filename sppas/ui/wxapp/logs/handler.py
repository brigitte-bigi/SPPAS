# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.phoenix.logs.handler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A log handler for all messages of SPPAS (both logging and wx.Log).

.. _This file is part of SPPAS: http://sppas.org/
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
import wx.lib.newevent

from sppas.core.coreutils import msg
from ..events import sppasLoggingEvent

# ----------------------------------------------------------------------------


# match between wx log levels and python log level names
match_levels = {
    wx.LOG_FatalError: 'CRITICAL',
    wx.LOG_Error: 'ERROR',
    wx.LOG_Warning: 'WARNING',
    wx.LOG_Info: 'INFO',
    wx.LOG_Message: 'INFO',
    wx.LOG_Debug: 'DEBUG'
}

# ----------------------------------------------------------------------------


MSG_HEADER_LOG = msg("Log Window", "ui")
MSG_ACTION_CLEAR = msg("Clear", "ui")
MSG_ACTION_SAVE = msg("Save", "ui")
MSG_ACTION_SEND = msg("Send feedback", "ui")
MSG_ADD_COMMENT = msg("Add comments here", "ui")

# ----------------------------------------------------------------------------


def log_level_to_wx(log_level):
    """Convert a python logging log level to a wx one.

    From python logging log levels:

        50 - CRITICAL
        40 - ERROR
        30 - WARNING
        20 - INFO
        10 - DEBUG
        0 - NOTSET

    To wx log levels:

        0 - LOG_FatalError 	program can’t continue, abort immediately
        1 - LOG_Error 	a serious error, user must be informed about it
        2 - LOG_Warning user is normally informed about it but may be ignored
        3 - LOG_Message normal message (i.e. normal output of a non GUI app)
        4 - LOG_Status 	informational: might go to the status line of GUI app
        5 - LOG_Info 	informational message (a.k.a. ‘Verbose’)
        6 - LOG_Debug 	never shown to the user, disabled in release mode
        7 - LOG_Trace 	trace messages are also only enabled in debug mode
        8 - LOG_Progress 	used for progress indicator (not yet)
        100 - LOG_User 	user defined levels start here
        10000 LOG_Max

    :param log_level: (int) python logging log level
    :returns: (int) wx log level

    """
    if log_level == logging.CRITICAL:
        return wx.LOG_Message
    if log_level <= 10:
        return wx.LOG_Debug
    if log_level <= 20:
        return wx.LOG_Info
    if log_level <= 30:
        return wx.LOG_Warning
    if log_level <= 40:
        return wx.LOG_Error
    return wx.LOG_FatalError

# ---------------------------------------------------------------------------


class sppasHandlerToWx(logging.Handler):
    """Logging handler class which sends log strings to a wx object.

    """

    def __init__(self, wx_dest=None):
        """Initialize the handler.

        :param wx_dest: (wx.Window) destination object to post the event to

        """
        super(sppasHandlerToWx, self).__init__()

        if isinstance(wx_dest, wx.Window) is False:
            raise TypeError('Expected a wx.Window but got {} instead.'
                            ''.format(type(wx_dest)))
        self.wx_dest = wx_dest

    # -----------------------------------------------------------------------

    def flush(self):
        """Override. Do nothing for this handler."""
        pass

    # -----------------------------------------------------------------------

    def emit(self, record):
        """Override. Emit a record.

        IMPORTANT: The record message can't contain the '%' character!
        It makes the application crashing... So, any record with a '%'
        is ignored.

        :param record: (logging.LogRecord)

        """
        if '%' in record.msg:
            return

        try:
            # the log event sends the record to the destination wx object
            event = sppasLoggingEvent(-1)
            event.SetRecord(record)
            wx.PostEvent(self.wx_dest, event)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
