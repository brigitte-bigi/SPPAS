"""
:filename: sppas.tests.config.test_heartbeat.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the last sign of life of an interlocutor.

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
import time

from sppas.core.config import sppasHeartbeat

# ---------------------------------------------------------------------------


class TestHeartbeat(unittest.TestCase):

    def test_without_any_sign(self):
        """Nothing was ever heard: the interlocutor is not there."""
        beat = sppasHeartbeat()
        self.assertFalse(beat.alive())
        self.assertIsNone(beat.age())

    def test_ping(self):
        """A sign of life is recent by definition."""
        beat = sppasHeartbeat(max_age=40.)
        beat.ping()
        self.assertTrue(beat.alive())
        self.assertTrue(beat.age() < 1.)

    def test_too_old(self):
        """A sign older than the age is not a sign any more."""
        beat = sppasHeartbeat(max_age=0.05)
        beat.ping()
        self.assertTrue(beat.alive())
        time.sleep(0.1)
        self.assertFalse(beat.alive())
        # the age is given whatever the answer
        self.assertTrue(beat.age() > 0.05)

    def test_max_age_of_the_call(self):
        """The age of the call wins over the one of the creation."""
        beat = sppasHeartbeat(max_age=0.01)
        beat.ping()
        self.assertTrue(beat.alive(max_age=40.))
        self.assertEqual(0.01, beat.get_max_age())

    def test_forget(self):
        """The announced end drops the last sign."""
        beat = sppasHeartbeat()
        beat.ping()
        beat.forget()
        self.assertFalse(beat.alive())
        self.assertIsNone(beat.age())
