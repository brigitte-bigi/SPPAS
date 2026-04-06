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

from sppas.ui.agnostic.appcomm.appcom_base import sppasCommunication
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerError
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerDataError
from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerAddressError

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
