"""
:filename: test_trace_store.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the socket communication of swapp with the other UI.

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

from sppas.ui.agnostic import sppasCommKeys
from sppas.ui.agnostic import COMM_PROTOCOL_VERSION

from sppas.ui.swapp.main_comm import sppasWappCommServer
from sppas.ui.swapp.wappcore.wappsg import wapp_wxstate

# ---------------------------------------------------------------------------


class TestInterlocutorGone(unittest.TestCase):
    """What happens to the state when the other UI does not answer."""

    def setUp(self):
        # A port nothing is listening to: a push to it fails, exactly as it
        # does when the wx interface crashed.
        self.server = sppasWappCommServer("127.0.0.1", 61999)
        self.hello = {"source": "wxapp", "version": COMM_PROTOCOL_VERSION,
                      "port": 61998}

    def tearDown(self):
        wapp_wxstate.running = False

    # -----------------------------------------------------------------------

    def test_hello_registers(self):
        """The handshake registers the interlocutor and the shared state."""
        self.server._prepare_response(sppasCommKeys.HELLO, self.hello)
        self.assertEqual(self.hello, self.server.get_interlocutor())
        self.assertTrue(wapp_wxstate.running)

    def test_bye_unregisters(self):
        """The announced shutdown un-registers it."""
        self.server._prepare_response(sppasCommKeys.HELLO, self.hello)
        self.server._prepare_response(sppasCommKeys.BYE, None)
        self.assertIsNone(self.server.get_interlocutor())
        self.assertFalse(wapp_wxstate.running)

    def test_push_to_a_gone_interlocutor(self):
        """An interlocutor which does not answer is un-registered too.

        This is the crash of the wx interface: no BYE is ever sent, and the
        state it left behind must not outlive it.

        """
        self.server._prepare_response(sppasCommKeys.HELLO, self.hello)
        self.assertTrue(wapp_wxstate.running)

        # Nothing is listening on the announced port: the push fails
        self.server.push(sppasCommKeys.SHOW_PAGE, "page_files")

        self.assertIsNone(self.server.get_interlocutor())
        self.assertFalse(wapp_wxstate.running)

    def test_push_without_interlocutor(self):
        """Without any interlocutor, a push is dropped and nothing raises."""
        self.server.push(sppasCommKeys.SHOW_PAGE, "page_files")
        self.assertIsNone(self.server.get_interlocutor())
