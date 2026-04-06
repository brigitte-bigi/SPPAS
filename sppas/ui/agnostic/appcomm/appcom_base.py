"""
:filename: sppas.ui.agnostic.appcom_base.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class to communicate on a socket between swapp and wxapp.

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

from sppas.core import sppasError

# ---------------------------------------------------------------------------


class sppasCommServerError(sppasError):
    """Raised when a socket is not listening."""

    def __init__(self, error) -> None:
        self._status = 40
        self.parameter = f":ERROR 40: Server error: {error}"
        self.error = error

# ---------------------------------------------------------------------------


class sppasCommServerAddressError(sppasError):
    """Raised when a socket error occurs."""

    def __init__(self, host: str, port) -> None:
        self._status = 42
        self.parameter = f":ERROR 42: Invalid host {host} or port {port}."
        self.host = host
        self.port = port

# ---------------------------------------------------------------------------


class sppasCommServerDataError(sppasError):
    """Raised when received data are not valid"""

    def __init__(self, error) -> None:
        self._status = 44
        self.parameter = f":ERROR 44: Invalid received data: {error}"
        self.error = error

# ---------------------------------------------------------------------------


class sppasCommunication:
    """Base class for communication in a socket.

    """

    def __init__(self, host: str, port: int):
        """Initialize sppasCommunication with all parameters.

        :param host: (str) Host IP address
        :param port: (int) Port number

        """
        # Server address
        self.__host = ""
        self.__port = 0
        self.set_host(host)
        self.set_port(port)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    # -------------------- HOST --------------------

    def get_host(self) -> str:
        """Get the host IP address."""
        return self.__host

    def set_host(self, value: str) -> None:
        """Set the host IP address."""
        if isinstance(value, str) is False:
            raise TypeError("host must be a string")
        self.__host = value

    host = property(get_host, set_host)

    # -------------------- PORT --------------------

    def get_port(self) -> int:
        """Get the port number."""
        return self.__port

    def set_port(self, value: int) -> None:
        """Set the port number."""
        if isinstance(value, int) is False:
            raise TypeError("port must be an integer")
        self.__port = value

    port = property(get_port, set_port)

