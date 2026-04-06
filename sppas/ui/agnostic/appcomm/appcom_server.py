"""
:filename: sppas.ui.agnostic.appcomm_server.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Server able to communicate to a client (receive request, send response).

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
import json
import socket

from .appcom_base import sppasCommunication
from .appcom_base import sppasCommServerDataError
from .appcom_base import sppasCommServerAddressError

# ---------------------------------------------------------------------------


class sppasCommServer(sppasCommunication):
    """Manage a socket connection and answer to client requests.

    The server listens to a TCP socket for incoming requests, performs
    the requested action using the configured engines, and returns results
    to the client.

    The server can be stopped by calling the shutdown() method from another
    thread or process.
    By sending the special key number "0" from a client, the server closes
    the connection.

    The server expects data in JSON format, as follows:
        {
            "key": "<str>",     # Required. Any string.
            "value": "<str>"    # Any serialized information.
        }

    """

    def __init__(self, host: str, port: int):
        """Initialize sppasCommServer with all parameters.

        :param host: (str) Host IP address
        :param port: (int) Port number

        """
        super().__init__(host, port)

        # Server is running by default
        self.__running = True

    # -----------------------------------------------------------------------

    def shutdown(self) -> None:
        """Request a graceful server shutdown (stop the next loop)."""
        self.__running = False


    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def start(self) -> None:
        """Start the server for client requests.

        :raises: OSError:
        :raises: json.JSONDecodeError:
        :raises: ImportError: Speech-to-text can't be imported.

        """
        logging.info(f"Server starting on {self.host}:{self.port}")
        server_socket = self._create_socket(time_out=1)
        logging.info(" ... Socket successfully created.")

        try:
            while self.__running:
                try:
                    conn, address = server_socket.accept()
                except socket.timeout:
                    continue
                logging.info(f"Server connected from: {address}")

                data = b""
                while True:
                    packet = conn.recv(8192)
                    if not packet:
                        break
                    data += packet
                data = data.decode()
                logging.debug(f" ... Server received data of length={len(data)}")

                response = " ... Connection established."
                error = None

                if isinstance(data, str) is True and len(data) > 0:
                    # Parse the received data and prepare the response for the client
                    try:
                        response = self._process_received_data(data)
                        # Check for stop message
                        if response == "__STOP__":
                            logging.info(" ... Server received close command.")
                            conn.close()
                            break
                    except Exception as e:
                        error = f"Server received invalid data: {str(e)}"
                else:
                    error = (f"Server received empty data or data of an invalid type: "
                             f"{str(type(data))}")

                if error is not None:
                    conn.send(error.encode())
                else:
                    # Response may be str or already bytes depending on the service output.
                    conn.send(response if isinstance(response, bytes) else response.encode())

                conn.close()
                logging.info("Connection closed.")
        finally:
            # Always executed, even on exception
            logging.info("Server stopped.")
            server_socket.close()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _create_socket(self, time_out: int | None = 600) -> socket.socket:
        """Create and configure a socket for server-client communication.

        :param time_out: (int or None) The timeout duration in seconds.
        :return: (socket) Server socket object.
        :raises: socket.timeout: The server socket timed out.
        :raises: socket.error: A socket error occurred.
        :raises: ValueError: Invalid host or port.

        """
        server_socket = socket.socket()

        # Use explicit check for clarity
        if isinstance(self.host, str) is False or isinstance(self.port, int) is False:
            raise sppasCommServerAddressError(host=self.host, port=self.port)

        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        if time_out is not None:
            server_socket.settimeout(time_out)

        return server_socket

    # -----------------------------------------------------------------------

    def _process_received_data(self, data: str) -> str:
        """Parse received data from server and launch the expected service.

        :param data: (str) The received data -- JSON.
        :return: (str) The response from the service(s)
        :raises: JSONDecodeError: The received data can't be parsed.

        """
        # Received data are supposed to be in JSON format
        key, value = self._parse_received_data(data)
        logging.info(f" ... Server received key: {key}")

        # Analyze action and ask for the relevant services
        if key == "0":
            return "__STOP__"

        return self._prepare_response(key, value)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_received_data(data: str) -> (str, str):
        """Parse received data from server and launch the expected service.

        :param data: (str) The received data -- JSON.
        :return: (str) The response from the service(s)
        :raises: JSONDecodeError: The received data can't be parsed.

        """
        # Received data are supposed to be in JSON format
        parsed = json.loads(data)

        # Get the name of the action to perform
        if "key" not in parsed:
            raise sppasCommServerDataError("'key' key missing in received data.")
        if "value" not in parsed:
            raise sppasCommServerDataError("'value' key missing in received data.")

        if len(parsed["key"]) == 0:
            raise sppasCommServerDataError("key can't be empty in received data.")

        return parsed["key"], parsed["value"]

    # -----------------------------------------------------------------------
    # To be overridden by the app.
    # -----------------------------------------------------------------------

    def _prepare_response(self, key: str, value: str) -> str:
        """To be overridden. Prepare response to send data to server.

        :param key: (str) The key sent by the client.
        :param value: (str) The value sent by the client.
        :return: (str) The response to the client.

        """
        return "0"
