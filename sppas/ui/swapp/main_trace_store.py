"""
:filename: sppas.ui.swapp.main_trace_store.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The shared store of the trace/info records of SPPAS.

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
import time
import threading
from datetime import datetime

from sppas.core.config import sppasHeartbeat
from sppas.core.coreutils import sppasLogFile

# ---------------------------------------------------------------------------


class swappTraceStore:
    """Store the trace/info records of the SPPAS components.

    The swapp server is the collector of the traces of all the SPPAS
    components: its own python logging feeds the store with a local
    handler, and the wx interface feeds it through the communication
    socket. The store replaces the wx log window: it is the single place
    where the useful trace/info messages are accumulated, then displayed
    by the trace page, saved into the log files, or sent with a feedback.

    Each record is a dict with the keys: "created" (float), "levelno" (int),
    "levelname" (str), "source" (str), "origin" (str), "message" (str).

    The "origin" distinguishes the useful/important messages of the API
    from the secondary messages of the interfaces.

    """

    # The origin of a record: the API or an interface.
    API_ORIGIN = "api"
    UI_ORIGIN = "ui"

    def __init__(self):
        """Create a swappTraceStore instance.

        The store starts with the standard header of the SPPAS log files.

        """
        # Appends come from the HTTPD threads and from the socket thread.
        self.__lock = threading.Lock()
        self.__records = list()
        self.__header = sppasLogFile.get_header()
        self.__logfile = sppasLogFile(pattern="log")
        # Time of the last heartbeat of the trace page, or None if never.
        self.__viewer = sppasHeartbeat(max_age=40.)

    # -----------------------------------------------------------------------

    @staticmethod
    def origin_of(pathname: str, logger_name: str = "") -> str:
        """Return the origin of a log record: the API or an interface.

        The distinction is made without modifying the existing code: the
        records coming from the 'sppas/ui' sources are interface messages,
        the other ones are API messages. A named logger starting with
        "swapp" also indicates an interface message.

        :param pathname: (str) Full pathname of the source file of the record.
        :param logger_name: (str) Name of the logger which emitted the record.
        :return: (str) API_ORIGIN or UI_ORIGIN

        """
        if logger_name.startswith("swapp") is True:
            return swappTraceStore.UI_ORIGIN

        normalized = pathname.replace("\\", "/")
        if "/ui/" in normalized:
            return swappTraceStore.UI_ORIGIN

        return swappTraceStore.API_ORIGIN

    # -----------------------------------------------------------------------

    def append(self, levelno: int, levelname: str, message: str,
               source: str, origin: str, created: float | None = None) -> None:
        """Append a record to the store.

        :param levelno: (int) Python logging level number
        :param levelname: (str) Python logging level name
        :param message: (str) The message of the record
        :param source: (str) The process the record comes from: "swapp" or "wxapp"
        :param origin: (str) API_ORIGIN or UI_ORIGIN
        :param created: (float) Time of the record, or None for now

        """
        if created is None:
            created = time.time()
        record = {
            "created": created,
            "levelno": levelno,
            "levelname": levelname,
            "source": source,
            "origin": origin,
            "message": message
        }
        with self.__lock:
            self.__records.append(record)

    # -----------------------------------------------------------------------

    def get_records(self, min_level: int = 0, origin: str | None = None) -> list:
        """Return a copy of the stored records.

        :param min_level: (int) Return only the records of at least this level.
        :param origin: (str) Return only the records of this origin, or None for all.
        :return: (list) List of dict records.

        """
        with self.__lock:
            records = list()
            for record in self.__records:
                if record["levelno"] < min_level:
                    continue
                if origin is not None and record["origin"] != origin:
                    continue
                records.append(dict(record))
            return records

    # -----------------------------------------------------------------------

    def get_header(self) -> str:
        """Return the header of the store."""
        return self.__header

    # -----------------------------------------------------------------------

    def viewer_ping(self) -> None:
        """Store the time of the last sign of life of the trace page.

        The trace page sends a periodic heartbeat: the server knows if the
        single tab displaying the traces is currently open.

        """
        self.__viewer.ping()

    # -----------------------------------------------------------------------

    def viewer_alive(self, max_age: float = 40.) -> bool:
        """Return True if the trace page gave a recent sign of life.

        :param max_age: (float) Maximum age of the last heartbeat, in seconds.
        :return: (bool) True if the last heartbeat is younger than max_age.

        """
        return self.__viewer.alive(max_age)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_record(record: dict) -> str:
        """Return one record formatted as a single line of plain text.

        :param record: (dict) A record, as stored and returned by this class.
        :return: (str) The formatted line, without a trailing newline.

        """
        when = datetime.fromtimestamp(record["created"])
        return "{:s} [{:s}] ({:s}/{:s}) {:s}".format(
            when.strftime("%Y-%m-%d %H:%M:%S"),
            record["levelname"],
            record["source"],
            record["origin"],
            record["message"])

    # -----------------------------------------------------------------------

    def serialize_records(self, min_level: int = 0, origin: str | None = None) -> str:
        """Return the formatted records as text, without the header.

        :param min_level: (int) Serialize only the records of at least this level.
        :param origin: (str) Serialize only the records of this origin, or None for all.
        :return: (str) The formatted records, one per line.

        """
        lines = [self.format_record(r) for r in self.get_records(min_level, origin)]
        return "\n".join(lines) + "\n"

    # -----------------------------------------------------------------------

    def serialize(self, min_level: int = 0) -> str:
        """Return the header and the formatted records, as text.

        :param min_level: (int) Serialize only the records of at least this level.
        :return: (str) The full trace content.

        """
        return self.__header + self.serialize_records(min_level)

    # -----------------------------------------------------------------------

    def clear(self) -> None:
        """Delete all the records and re-generate the header."""
        with self.__lock:
            self.__records = list()
            self.__header = sppasLogFile.get_header()

    # -----------------------------------------------------------------------

    def save(self) -> str:
        """Save the trace into the current log file, then clear the store.

        This is the behavior of the "Save" action of the former wx log
        window: the content is written, the store re-starts empty and the
        next save will use an incremented filename.

        :return: (str) The saved filename.

        """
        filename = self.__logfile.get_filename()
        with open(filename, "w") as file_descriptor:
            file_descriptor.write(self.serialize())
        self.clear()
        self.__logfile.increment()
        return filename
