"""
:filename: sppas.ui.swapp.main_comm.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The communication server of the web application.

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

from sppas.src.wkps.wio import sppasWJSON
from sppas.ui.agnostic import sppasCommServer
from sppas.ui.agnostic import sppasCommClient
from sppas.ui.agnostic import sppasCommKeys
from sppas.ui.agnostic import sppasCommServerError

from .wappsg import wapp_wkps
from .wappsg import wapp_wxstate
from .wappsg import wapp_trace
from .wappsg import notify_wkp_changed
from .swapp_trace_store import swappTraceStore

# ---------------------------------------------------------------------------


class sppasWappCommServer(sppasCommServer):
    """The interlocutor of the wx UI, on the swapp side.

    Receive the messages the wx UI sends on the socket. The HELLO message
    registers the interlocutor -- in particular the port of its own
    communication server: it is what makes the full-duplex possible, with
    the send() method creating a client toward that port.

    """

    def __init__(self, host: str, port: int):
        """Create the communication server of the web application.

        :param host: (str) Host IP address
        :param port: (int) Port number

        """
        super(sppasWappCommServer, self).__init__(host, port)
        # The interlocutor declared by the last received HELLO, or None.
        # Keys: "source" (str), "version" (int), "port" (int).
        self.__interlocutor = None

    # -----------------------------------------------------------------------

    def get_interlocutor(self) -> dict | None:
        """Return the registered interlocutor, or None.

        :return: (dict|None) The value of the last received HELLO message.

        """
        return self.__interlocutor

    # -----------------------------------------------------------------------

    def send(self, key: int, value) -> str:
        """Send a message to the registered interlocutor.

        :param key: (int) One of the sppasCommKeys constants
        :param value: (any) A JSON-serializable object
        :raises: sppasCommServerError: No interlocutor, or sending failed.
        :return: (str) The response of the interlocutor -- JSON envelope.

        """
        if self.__interlocutor is None:
            raise sppasCommServerError("No registered interlocutor to send to.")

        client = sppasCommClient(self.host, self.__interlocutor["port"])
        request = client.format_request(key, value)
        return client.request(request)

    # -----------------------------------------------------------------------

    def _prepare_response(self, key: int, value) -> str:
        """Override. Register the interlocutor and answer the messages.

        The HELLO and BYE messages register/un-register the interlocutor.
        The WKP_CHANGED message stores the received workspace into the
        shared state -- the workspaces manager of the web application.

        :param key: (int) One of the sppasCommKeys constants, sent by the client.
        :param value: (any) The value sent by the client.
        :return: (str) The response to the client, in the shared JSON envelope.

        """
        if key == sppasCommKeys.HELLO:
            if isinstance(value, dict) is True and "port" in value:
                self.__interlocutor = value
                logging.info(f"Interlocutor registered: {value}")
                # The shared state allows the Dashboard to disable the launch
                # of a second wx instance: only one is allowed.
                if value.get("source", "") == "wxapp":
                    wapp_wxstate.running = True
                # The interlocutor starts with its own workspace: publish the
                # shared one, so that both UIs work on the same data.
                notify_wkp_changed()
            else:
                logging.warning(f"HELLO received without a port. Not registered: {value}")

        if key == sppasCommKeys.BYE:
            self.__interlocutor = None
            wapp_wxstate.running = False
            logging.info("Interlocutor un-registered.")

        if key == sppasCommKeys.WKP_CHANGED:
            wjson = sppasWJSON()
            wjson.parse(value)
            wapp_wkps.data = wjson
            logging.info("Workspace received and stored into the shared state.")
            return self.format_message(sppasCommKeys.ACK, "Workspace stored.")

        if key == sppasCommKeys.TRACE:
            if isinstance(value, dict) is True:
                wapp_trace.append(
                    value.get("levelno", 0),
                    value.get("levelname", ""),
                    value.get("message", ""),
                    value.get("source", "wxapp"),
                    swappTraceStore.origin_of(value.get("pathname", ""), value.get("name", "")),
                    value.get("created"))
            return self.format_message(sppasCommKeys.ACK, "Trace stored.")

        return super(sppasWappCommServer, self)._prepare_response(key, value)

    # -----------------------------------------------------------------------

    def push(self, key: int, value) -> None:
        """Push an event to the registered interlocutor, if any.

        Tolerant version of send(): when there is no interlocutor -- the
        other UI is not running -- the event is dropped, with a log only.
        This is the observer the application subscribes to the notifier.

        :param key: (int) One of the sppasCommKeys constants
        :param value: (any) A JSON-serializable object

        """
        try:
            self.send(key, value)
            logging.debug(f"Event {sppasCommKeys.name_of(key)} pushed to the interlocutor.")
        except sppasCommServerError as e:
            logging.info(f"Event {sppasCommKeys.name_of(key)} not pushed: {e}")
