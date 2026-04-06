"""
:filename: test_appcomm_client.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the client able to communicate on a socket to an app server.

 _This file is part of SPPAS: https://sppas.org/
.
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

import json
import unittest

from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerError
from sppas.ui.agnostic.appcomm.appcom_client import sppasCommClient

# ---------------------------------------------------------------------------


class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = sppasCommClient(host="127.0.0.1", port=5678)

    def test_host_port_setter_getter(self):
        self.assertEqual(self.client.host, "127.0.0.1")
        self.client.host = "localhost"
        self.assertEqual(self.client.host, "localhost")
        with self.assertRaises(TypeError):
            self.client.host = 42

        self.assertEqual(self.client.port, 5678)
        self.client.port = 1234
        self.assertEqual(self.client.port, 1234)
        with self.assertRaises(TypeError):
            self.client.port = "bad"

    def test_format_request_json_value(self):
        req = self.client.format_request("audio", ["16000", "2", "stream"])
        parsed = json.loads(req)
        self.assertEqual(parsed["key"], "audio")
        self.assertEqual(parsed["value"], ["16000", "2", "stream"])

    def test_format_request_rejects_bytes(self):
        with self.assertRaises(TypeError):
            self.client.format_request("audio", b"ABCDEF")

    def test_format_request_invalid_key(self):
        with self.assertRaises(Exception):
            self.client.format_request(2, ["x"])

    def test_request_connection_error(self):
        data = self.client.format_request("2", ["test"])
        with self.assertRaises(sppasCommServerError):
            self.client.request(data)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
