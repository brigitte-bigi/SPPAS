"""
:filename: test_appcomm_notify.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the application events notifier

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

from sppas.ui.agnostic.appcomm.appcom_notify import sppasCommNotifier

# ---------------------------------------------------------------------------


class TestCommNotifier(unittest.TestCase):

    def setUp(self):
        self.notifier = sppasCommNotifier()
        self.received = list()

    def __observer(self, key, value):
        self.received.append((key, value))

    def test_notify_without_observer(self):
        # Nothing happens, no exception raised
        self.notifier.notify(20, {"a": 1})

    def test_subscribe_and_notify(self):
        self.notifier.subscribe(self.__observer)
        self.notifier.notify(20, {"a": 1})
        self.assertEqual([(20, {"a": 1})], self.received)

    def test_subscribe_twice(self):
        self.notifier.subscribe(self.__observer)
        self.notifier.subscribe(self.__observer)
        self.notifier.notify(20, {"a": 1})
        self.assertEqual([(20, {"a": 1})], self.received)

    def test_subscribe_invalid_observer(self):
        with self.assertRaises(TypeError):
            self.notifier.subscribe("not a callable")

    def test_unsubscribe(self):
        self.notifier.subscribe(self.__observer)
        self.notifier.unsubscribe(self.__observer)
        self.notifier.notify(20, {"a": 1})
        self.assertEqual([], self.received)

    def test_unsubscribe_unknown_observer(self):
        # Ignored, no exception raised
        self.notifier.unsubscribe(self.__observer)

    def test_notify_invalid_key(self):
        with self.assertRaises(TypeError):
            self.notifier.notify("20", {"a": 1})
