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
import socket
import threading

from .appcom_base import sppasCommunication
from .appcom_base import sppasCommKeys
from .appcom_base import sppasCommServerAddressError
from .appcom_base import COMM_PROTOCOL_VERSION

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
        # Set when the socket is created and the server accepts: whoever
        # announces itself before that would not be reachable yet.
        self.__ready = threading.Event()

    # -----------------------------------------------------------------------

    def shutdown(self) -> None:
        """Request a graceful server shutdown (stop the next loop)."""
        self.__running = False
        self.__ready.clear()

    # -----------------------------------------------------------------------

    def wait_ready(self, timeout: float = 5.) -> bool:
        """Wait until this server is listening.

        :param timeout: (float) Maximum waiting time, in seconds
        :return: (bool) True if the server is listening

        """
        return self.__ready.wait(timeout)


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
        self.__ready.set()

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

                response = self.format_message(sppasCommKeys.ACK, "Connection established.")
                stop_requested = False

                if isinstance(data, str) is True and len(data) > 0:
                    # Parse the received data and prepare the response for the client
                    try:
                        response = self._process_received_data(data)
                        # Check for stop message
                        if response == "__STOP__":
                            logging.info(" ... Server received close command.")
                            stop_requested = True
                            response = self.format_message(sppasCommKeys.ACK, "Server is stopping.")
                    except Exception as e:
                        response = self.format_message(
                            sppasCommKeys.ERROR,
                            f"Server received invalid data: {str(e)}")
                else:
                    response = self.format_message(
                        sppasCommKeys.ERROR,
                        f"Server received empty data or data of an invalid type: "
                        f"{str(type(data))}")

                # Response may be str or already bytes depending on the service output.
                conn.send(response if isinstance(response, bytes) else response.encode())

                conn.close()
                logging.info("Connection closed.")

                if stop_requested is True:
                    break
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
        """Parse received data and launch the expected service.

        :param data: (str) The received data -- JSON.
        :return: (str) The response from the service(s)
        :raises: sppasCommServerDataError: Invalid message envelope.
        :raises: JSONDecodeError: The received data can't be parsed.

        """
        # Received data are supposed to be in the shared JSON envelope
        key, value = self.parse_message(data)
        logging.info(f" ... Server received key: {sppasCommKeys.name_of(key)}")

        # Analyze action and ask for the relevant services
        if key == sppasCommKeys.STOP:
            return "__STOP__"

        return self._prepare_response(key, value)

    # -----------------------------------------------------------------------
    # To be overridden by the app.
    # -----------------------------------------------------------------------

    def _prepare_response(self, key: int, value) -> str:
        """To be overridden. Prepare the response to send to the client.

        :param key: (int) One of the sppasCommKeys constants, sent by the client.
        :param value: (any) The value sent by the client.
        :return: (str) The response to the client, in the shared JSON envelope.

        """
        if key == sppasCommKeys.PING:
            return self.format_message(sppasCommKeys.ACK, {"version": COMM_PROTOCOL_VERSION})

        if key == sppasCommKeys.HELLO:
            # The interlocutor announced itself: value = {"source", "version", "port"}
            logging.info(f" ... Handshake received: {value}")
            return self.format_message(sppasCommKeys.ACK, {"version": COMM_PROTOCOL_VERSION})

        if key == sppasCommKeys.BYE:
            logging.info(f" ... The interlocutor announced its shutdown: {value}")
            return self.format_message(sppasCommKeys.ACK, "Goodbye.")

        return self.format_message(sppasCommKeys.ERROR, f"Unknown message key: {key}")
