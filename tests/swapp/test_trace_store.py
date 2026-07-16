"""
:filename: test_trace_store.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the shared trace store and its logging handler

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

from sppas.ui.swapp.swapp_trace_store import swappTraceStore
from sppas.ui.swapp.swapp_trace_handler import swappTraceHandler

# ---------------------------------------------------------------------------


class TestTraceStore(unittest.TestCase):

    def setUp(self):
        self.store = swappTraceStore()

    def test_origin_of_api(self):
        origin = swappTraceStore.origin_of("/D/Projects/sppas-code/sppas/src/anndata/aio/xra.py")
        self.assertEqual(origin, swappTraceStore.API_ORIGIN)
        origin = swappTraceStore.origin_of("/D/Projects/sppas-code/sppas/core/config/appcfg.py")
        self.assertEqual(origin, swappTraceStore.API_ORIGIN)

    def test_origin_of_ui_from_pathname(self):
        origin = swappTraceStore.origin_of("/D/Projects/sppas-code/sppas/ui/swapp/main_app.py")
        self.assertEqual(origin, swappTraceStore.UI_ORIGIN)
        # Windows-style pathname
        origin = swappTraceStore.origin_of("C:\\sppas\\ui\\wxapp\\main_app.py")
        self.assertEqual(origin, swappTraceStore.UI_ORIGIN)

    def test_origin_of_ui_from_logger_name(self):
        origin = swappTraceStore.origin_of("/whatever/path.py", "swapp")
        self.assertEqual(origin, swappTraceStore.UI_ORIGIN)

    def test_append_and_get_records(self):
        self.store.append(logging.INFO, "INFO", "a message", "swapp", "api")
        self.store.append(logging.DEBUG, "DEBUG", "a detail", "wxapp", "ui")
        records = self.store.get_records()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["message"], "a message")
        self.assertEqual(records[1]["source"], "wxapp")

    def test_get_records_min_level(self):
        self.store.append(logging.DEBUG, "DEBUG", "a detail", "swapp", "api")
        self.store.append(logging.ERROR, "ERROR", "a problem", "swapp", "api")
        records = self.store.get_records(min_level=logging.INFO)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["levelname"], "ERROR")

    def test_serialize(self):
        self.store.append(logging.INFO, "INFO", "a message", "swapp", "api")
        content = self.store.serialize()
        self.assertTrue(content.startswith(self.store.get_header()))
        self.assertIn("[INFO] (swapp/api) a message", content)

    def test_clear(self):
        self.store.append(logging.INFO, "INFO", "a message", "swapp", "api")
        self.store.clear()
        self.assertEqual(len(self.store.get_records()), 0)
        self.assertTrue(self.store.serialize().startswith(self.store.get_header()))

# ---------------------------------------------------------------------------


class TestTraceHandler(unittest.TestCase):

    def setUp(self):
        self.store = swappTraceStore()
        self.handler = swappTraceHandler(self.store)

    @staticmethod
    def record(pathname, levelno, message, name=""):
        return logging.LogRecord(
            name=name, level=levelno, pathname=pathname,
            lineno=1, msg=message, args=None, exc_info=None)

    def test_emit_appends_api_record(self):
        self.handler.emit(TestTraceHandler.record(
            "/sppas/src/annotations/align.py", logging.INFO, "aligned"))
        records = self.store.get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["origin"], swappTraceStore.API_ORIGIN)
        self.assertEqual(records[0]["source"], "swapp")

    def test_emit_appends_ui_record(self):
        self.handler.emit(TestTraceHandler.record(
            "/sppas/ui/swapp/main_app.py", logging.WARNING, "careful"))
        records = self.store.get_records()
        self.assertEqual(records[0]["origin"], swappTraceStore.UI_ORIGIN)

    def test_emit_excludes_comm_below_warning(self):
        self.handler.emit(TestTraceHandler.record(
            "/sppas/ui/agnostic/appcomm/appcom_server.py", logging.DEBUG, "received data"))
        self.handler.emit(TestTraceHandler.record(
            "/sppas/ui/swapp/main_comm.py", logging.INFO, "interlocutor registered"))
        self.assertEqual(len(self.store.get_records()), 0)

    def test_emit_keeps_comm_warning(self):
        self.handler.emit(TestTraceHandler.record(
            "/sppas/ui/swapp/main_comm.py", logging.WARNING, "HELLO received without a port"))
        self.assertEqual(len(self.store.get_records()), 1)
