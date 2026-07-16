"""
:filename: sppas.ui.agnostic.appcomm.appcom_loghandler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A logging handler sending the records on the communication socket.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

from __future__ import annotations
import logging
import threading

from .appcom_base import sppasCommKeys
from .appcom_client import sppasCommClient

# ---------------------------------------------------------------------------


class sppasCommLogHandler(logging.Handler):
    """Send the python logging records on the communication socket.

    The handler is added to the root logger of a process -- the wx
    interface -- so that its records reach the collector of the traces:
    the swapp server. Each record is sent as a TRACE message, serialized
    with the fields the collector needs to classify and store it.

    The handler is tolerant: when the server is not listening, the record
    is dropped silently. It never logs by itself, and a re-entrancy guard
    protects against the records the sending could produce: without it,
    such a record would be sent in its turn, endlessly.

    """

    def __init__(self, host: str, port: int, source: str):
        """Create a sppasCommLogHandler instance.

        :param host: (str) Host IP address of the collector server
        :param port: (int) Port number of the collector server
        :param source: (str) Name of the process the records come from, e.g. "wxapp"

        """
        super(sppasCommLogHandler, self).__init__()
        self.__host = host
        self.__port = port
        self.__source = source
        self.__local = threading.local()

    # -----------------------------------------------------------------------

    @staticmethod
    def format_value(record: logging.LogRecord, source: str) -> dict:
        """Return the TRACE payload of a record.

        :param record: (logging.LogRecord) The record to serialize.
        :param source: (str) Name of the process the record comes from.
        :return: (dict) The JSON-serializable value of the TRACE message.

        """
        return {
            "created": record.created,
            "levelno": record.levelno,
            "levelname": record.levelname,
            "pathname": record.pathname,
            "name": record.name,
            "message": record.getMessage(),
            "source": source
        }

    # -----------------------------------------------------------------------

    def emit(self, record: logging.LogRecord) -> None:
        """Override. Send the given record to the collector server.

        :param record: (logging.LogRecord) The record to send.

        """
        if getattr(self.__local, "emitting", False) is True:
            return

        self.__local.emitting = True
        try:
            client = sppasCommClient(self.__host, self.__port)
            request = client.format_request(
                sppasCommKeys.TRACE,
                sppasCommLogHandler.format_value(record, self.__source))
            client.request(request)
        except Exception:
            # No collector server listening: the record is dropped.
            pass
        finally:
            self.__local.emitting = False
