"""
:filename: test_appcomm_server.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the server able to communicate on a socket to an app client.

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

from sppas.ui.agnostic.appcomm.appcom_base import sppasCommServerDataError
from sppas.ui.agnostic.appcomm.appcom_server import sppasCommServer

# ---------------------------------------------------------------------------


class TestServerCommunication(unittest.TestCase):

    def setUp(self):
        self.srv = sppasCommServer(host="127.0.0.1", port=8080)

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


# ---------------------------------------------------------------------------


class TestServer(unittest.TestCase):

    def test_parse_received_data(self):
        server = sppasCommServer("127.0.0.1", 1234)

        valid_data = json.dumps({
            "key": "audio",
            "value": ["16000", "2", "stream"]
        })
        key, value = server._parse_received_data(valid_data)
        self.assertEqual(key, "audio")
        self.assertEqual(value, ["16000", "2", "stream"])

        missing_key = json.dumps({"value": "abc"})
        with self.assertRaises(sppasCommServerDataError):
            server._parse_received_data(missing_key)

        missing_value = json.dumps({"key": "audio"})
        with self.assertRaises(sppasCommServerDataError):
            server._parse_received_data(missing_value)

        empty_key = json.dumps({"key": "", "value": "abc"})
        with self.assertRaises(sppasCommServerDataError):
            server._parse_received_data(empty_key)

    def test_process_received_data_stop(self):
        server = sppasCommServer("127.0.0.1", 1234)
        data_stop = json.dumps({"key": "0", "value": ""})
        result = server._process_received_data(data_stop)
        self.assertEqual(result, "__STOP__")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
