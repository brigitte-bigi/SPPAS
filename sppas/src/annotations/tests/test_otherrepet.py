# -*- coding: utf8 -*-
"""
:filename: sppas.src.annotations.tests.test_otherrepet.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Other-Repetitions automatic annotation.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

from ..SelfRepet.datastructs import DataSpeaker
from ..OtherRepet.rules import OtherRules
from ..OtherRepet.detectrepet import OtherRepetition

# ---------------------------------------------------------------------------


class TestOtherRules(unittest.TestCase):

    def test_rule_strict(self):
        r = OtherRules(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok3", "euh", "ok"])
        d2 = DataSpeaker(["bla", "tok1", "tok2"])
        d3 = DataSpeaker(["bla", "tok1", "tok2", "tok3"])
        d4 = DataSpeaker(["tok1", "euh", "tok2", "tok3"])
        self.assertFalse(r.rule_strict(0, 1, d1, d2))
        self.assertFalse(r.rule_strict(0, 2, d1, d2))
        self.assertTrue(r.rule_strict(0, 2, d1, d3))
        self.assertFalse(r.rule_strict(0, 2, d1, d4))

    def test_find_echos(self):
        r = OtherRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok3", "euh", "ok"])
        d2 = DataSpeaker(["bla", "tok1", "tok2", "euh", "oui", "tok1"])
        r.detect(d1, d2)
        self.assertEqual(r.get_source(), (0, 1))
        d1 = DataSpeaker(["a", "x1", "x2", "x3", "euh", "ok"])
        d2 = DataSpeaker(["x2", "blabla", "x3", "x2", "x1", "yep", "oui", "x2", "ya", "x1"])
        r.detect(d1, d2)
        self.assertEqual((1, 3), r.get_source())
        self.assertEqual([0, 2, 3, 4, 7, 9], r.get_all_echos())
        self.assertEqual([(2, 4)], r.get_echos())
