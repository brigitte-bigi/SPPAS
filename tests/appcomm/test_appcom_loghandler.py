"""
:filename: test_appcom_loghandler.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the logging handler sending records on the socket

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

import unittest
import logging

from sppas.ui.agnostic.appcomm.appcom_loghandler import sppasCommLogHandler

# ---------------------------------------------------------------------------


class TestCommLogHandler(unittest.TestCase):

    @staticmethod
    def record(message, levelno=logging.INFO):
        return logging.LogRecord(
            name="", level=levelno, pathname="/sppas/src/module.py",
            lineno=1, msg=message, args=None, exc_info=None)

    def test_format_value(self):
        record = TestCommLogHandler.record("a message", logging.WARNING)
        value = sppasCommLogHandler.format_value(record, "wxapp")
        self.assertEqual(value["levelno"], logging.WARNING)
        self.assertEqual(value["levelname"], "WARNING")
        self.assertEqual(value["pathname"], "/sppas/src/module.py")
        self.assertEqual(value["message"], "a message")
        self.assertEqual(value["source"], "wxapp")
        self.assertEqual(value["created"], record.created)

    def test_emit_without_server_is_tolerant(self):
        # Port 1 is never listening: the record must be dropped silently.
        handler = sppasCommLogHandler("127.0.0.1", 1, "wxapp")
        handler.emit(TestCommLogHandler.record("a message"))
        # No exception raised: the test passes by reaching this point.
        self.assertTrue(True)
