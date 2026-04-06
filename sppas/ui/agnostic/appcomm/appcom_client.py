"""
:filename: sppas.ui.agnostic.appcomm_client.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A client able to communicate on a socket to an app server.

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
import socket
import json

from sppas.core import sppasTypeError

from .appcom_base import sppasCommunication
from .appcom_base import sppasCommServerError

# ---------------------------------------------------------------------------


class sppasCommClient(sppasCommunication):
    """Socket client.

    """

    def __init__(self, host: str, port: int):
        """Initialize client with all parameters.

        :param host: (str) Host IP address
        :param port: (int) Port number

        """
        super().__init__(host, port)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_request(key: str, value) -> str:
        """Create a serialized JSON allowing to send data to the server.

        :param key: (str) The action to be performed by the server
        :param value: (any) A serializable object
        :raises: sppasError: Invalid argument
        :return: (str) The ready-to-send JSON string.

        """
        if isinstance(key, str) is False:
            raise sppasTypeError("str", type(key))

        data = dict()
        data["key"] = key
        data["value"] = value

        return json.dumps(data, ensure_ascii=False)

    # -----------------------------------------------------------------------

    def request(self, data: str) -> str:
        """Send a request to the server and return its response.

        :param data: (str) The data to send to the server.
        :return: (str) The response from the server.

        """
        client_socket = None
        try:
            # Create a socket to communicate with the server
            client_socket = socket.socket()

            # Connect to the server
            client_socket.connect((self.host, self.port))

            # Send the audio filename to the server
            client_socket.sendall(data.encode(encoding="utf-8"))
            client_socket.shutdown(socket.SHUT_WR)

            # Receive the transcribed text from the server
            # response = client_socket.recv(8192).decode()
            response_bytes = b""
            while True:
                packet = client_socket.recv(8192)
                if not packet:
                    break
                response_bytes += packet
            response = response_bytes.decode(encoding="utf-8", errors="replace")

            # Close connection
            client_socket.close()

        except Exception as e:
            # Ensure the socket is always closed
            if client_socket:
                client_socket.close()

            # Handle any exception that occurs
            raise sppasCommServerError(str(e))

        # Return the server's response
        return response
