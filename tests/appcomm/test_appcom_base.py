"""
:filename: test_appcomm_base.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the base communication class

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
import json

from sppas.ui.agnostic.appcomm.appcom_base import sppasCommunication
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommKeys
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerError
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerDataError
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerAddressError
from sppas.ui.agnostic.appcomm.appcom_base import COMM_PROTOCOL_VERSION

# ---------------------------------------------------------------------------


class TestCommunication(unittest.TestCase):

    def setUp(self):
        self.srv = sppasCommunication(host="127.0.0.1", port=8080)

    def test_host_get_set(self):
        self.srv.host = "192.168.0.2"
        self.assertEqual(self.srv.host, "192.168.0.2")
        with self.assertRaises(TypeError):
            self.srv.host = 123

    def test_port_get_set(self):
        self.srv.port = 8000
        self.assertEqual(self.srv.port, 8000)
        with self.assertRaises(TypeError):
            self.srv.port = "not_a_port"

    def test_status_property(self):
        # Test that status returns _status and cannot be set
        exc = sppasCommServerError("message")
        self.assertTrue(hasattr(exc, "status"))
        self.assertEqual(exc.status, exc._status)
        # No setter: AttributeError expected if assignment is attempted
        with self.assertRaises(AttributeError):
            exc.status = 42

    def test_server_address_error_message_and_status(self):
        host = "127.0.0.1"
        port = 8080
        exc = sppasCommServerAddressError(host, port)
        self.assertEqual(exc.status, 42)
        self.assertEqual(exc.host, host)
        self.assertEqual(exc.port, port)
        self.assertEqual(str(exc), f"':ERROR 42: Invalid host {host} or port {port}.'")

    def test_server_data_error_message_and_status(self):
        err = "Malformed packet"
        exc = sppasCommServerDataError(err)
        self.assertEqual(exc.status, 44)
        self.assertEqual(exc.error, err)
        self.assertEqual(str(exc), f"':ERROR 44: Invalid received data: {err}'")

# ---------------------------------------------------------------------------


class TestCommKeys(unittest.TestCase):

    def test_values_are_unique(self):
        values = [value for name, value in vars(sppasCommKeys).items()
                  if name.isupper() is True]
        self.assertEqual(len(values), len(set(values)))

    def test_name_of(self):
        self.assertEqual("PING", sppasCommKeys.name_of(sppasCommKeys.PING))
        self.assertEqual("ACK", sppasCommKeys.name_of(sppasCommKeys.ACK))
        # An unknown value is returned as it, for the logs
        self.assertEqual("999", sppasCommKeys.name_of(999))

# ---------------------------------------------------------------------------


class TestMessageEnvelope(unittest.TestCase):

    def test_format_message(self):
        data = sppasCommunication.format_message(sppasCommKeys.PING, "abc")
        parsed = json.loads(data)
        self.assertEqual(parsed["key"], sppasCommKeys.PING)
        self.assertEqual(parsed["value"], "abc")

    def test_format_message_unicode(self):
        data = sppasCommunication.format_message(sppasCommKeys.ACK, "éàç œ")
        self.assertTrue("éàç œ" in data)

    def test_format_message_invalid_key(self):
        with self.assertRaises(TypeError):
            sppasCommunication.format_message("PING", "abc")

    def test_parse_message(self):
        hello_value = {"source": "swapp", "version": COMM_PROTOCOL_VERSION, "port": 8888}
        data = sppasCommunication.format_message(sppasCommKeys.HELLO, hello_value)
        key, value = sppasCommunication.parse_message(data)
        self.assertEqual(key, sppasCommKeys.HELLO)
        self.assertEqual(value, hello_value)

    def test_parse_message_errors(self):
        with self.assertRaises(sppasCommServerDataError):
            sppasCommunication.parse_message(json.dumps({"value": "abc"}))
        with self.assertRaises(sppasCommServerDataError):
            sppasCommunication.parse_message(json.dumps({"key": sppasCommKeys.PING}))
        with self.assertRaises(sppasCommServerDataError):
            sppasCommunication.parse_message(json.dumps({"key": "PING", "value": ""}))
        with self.assertRaises(json.JSONDecodeError):
            sppasCommunication.parse_message("not a json")
