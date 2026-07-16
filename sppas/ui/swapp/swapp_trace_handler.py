"""
:filename: sppas.ui.swapp.swapp_trace_handler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The logging handler feeding the shared trace store.

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

from .swapp_trace_store import swappTraceStore

# ---------------------------------------------------------------------------


class swappTraceHandler(logging.Handler):
    """Redirect the python logging records to the shared trace store.

    The handler is added to the root logger of the swapp server process:
    it makes the server the collector of its own traces. The records are
    classified with the origin_of() method of the store.

    Anti-noise: the records of the communication modules below the
    WARNING level are excluded from the store. Each message received on
    the socket -- including every TRACE sent by the wx interface --
    produces its own debug and info records: storing them would drown
    the useful trace. They remain visible on the standard error, like
    any other record.

    """

    # The modules whose records below WARNING are excluded from the store.
    COMM_MODULES = ("appcom", "main_comm")

    def __init__(self, store: swappTraceStore):
        """Create a swappTraceHandler instance.

        :param store: (swappTraceStore) The store to feed with the records.

        """
        super(swappTraceHandler, self).__init__()
        self.__store = store

    # -----------------------------------------------------------------------

    def emit(self, record: logging.LogRecord) -> None:
        """Override. Append the given record to the store.

        :param record: (logging.LogRecord) The record to append.

        """
        try:
            if record.levelno < logging.WARNING:
                for module_name in swappTraceHandler.COMM_MODULES:
                    if module_name in record.pathname:
                        return

            origin = swappTraceStore.origin_of(record.pathname, record.name)
            self.__store.append(
                record.levelno,
                record.levelname,
                record.getMessage(),
                "swapp",
                origin,
                record.created)
        except Exception:
            self.handleError(record)
