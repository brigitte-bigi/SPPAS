# -*- coding:utf-8 -*-
"""
:filename: sppas.src.annotations.tests.test_repet.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Repetitions automatic annotation.

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

import os
import unittest

from sppas.core.config import paths

from ..SelfRepet.datastructs import DataSpeaker
from ..SelfRepet.detectrepet import SelfRepetition
from ..OtherRepet.detectrepet import OtherRepetition

# ---------------------------------------------------------------------------

STOP_LIST = ["ah", "aller", "alors", "après", "avec", "avoir", "bon", "ce", "comme", "c'est", "dans", "de", "de+le", "dire", "donc", "eeh", "eh", "en", "en_fait", "et", "etc", "euh", "hein", "heu", "hum", "hm", "il", "le", "lui", "là", "mais", "meuh", "mh", "mhmh", "mmh", "moi", "mon", "ne", "non", "null", "on", "ou", "ouais", "oui", "où", "pas", "peu", "pf", "pff", "plus", "pour", "quand", "que", "qui", "quoi", "se", "si", "sur", "tout", "très", "un", "voilà", "voir", "y", "à", "ça", "être"]
STOP_LIST_FRA = os.path.join(paths.resources, "vocab", "fra.stp")


# ---------------------------------------------------------------------------

#

#
class TestRepetitions(unittest.TestCase):

    def test_longest(self):
        r = SelfRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertEqual(r.get_longest(0, d1), 0)   # tok1 is repeated
        self.assertEqual(r.get_longest(1, d1), -1)  # tok2 is not repeated
        d1 = DataSpeaker(["tok1", "tok2", "tok2"])
        self.assertEqual(r.get_longest(0, d1), -1)  # tok1 is repeated
        self.assertEqual(r.get_longest(1, d1), 1)   # tok2 is repeated
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        self.assertEqual(r.get_longest(0, d1), 2)   # tok1 & tok2 & tok2 are repeated
        self.assertEqual(r.get_longest(1, d1), 2)   # tok2 & tok2 are repeated
        self.assertEqual(r.get_longest(2, d1), 2)   # tok2 is repeated
        self.assertEqual(r.get_longest(3, d1), -1)  # tok2 is not repeated
        self.assertEqual(r.get_longest(4, d1), 4)   # euh is repeated
        self.assertEqual(r.get_longest(5, d1), -1)  # tok1 is not repeated
        d1 = DataSpeaker(["tok1", "*", "tok2", "tok1"])
        self.assertEqual(r.get_longest(0, d1), 0)   # tok1 is repeated

    def test_select_self_repetition(self):
        r = SelfRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok1"])
        self.assertIsNone(r.get_source())
        self.assertEqual(r.select(0, 0, d1), 1)  # tok1 is stored
        self.assertEqual(r.get_source(), (0, 0))

        r = SelfRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        n = r.get_longest(0, d1)  # n=2
        self.assertEqual(r.select(0, n, d1), 3)   # "tok1 tok2 tok2" is a source
        self.assertEqual(r.get_source(), (0, 2))
        n = r.get_longest(4, d1)  # n=4
        self.assertEqual(r.select(4, n, d1), 5)   # "euh" is not accepted as source
        self.assertEqual(r.get_source(), (0, 2))

        r = SelfRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "euh", "euh", "euh", "tok2", "euh", "*", "tok1"])
        n = r.get_longest(0, d1)  # n=3
        self.assertEqual(r.select(0, n, d1), 4)  # "tok1 euh euh euh" is a source
        self.assertEqual(r.get_source(), (0, 3))

        r = SelfRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "euh", "euh", "euh", "tok2", "euh"])
        n = r.get_longest(1, d1)  # n=3
        self.assertEqual(r.select(1, n, d1), 4)  # "euh euh euh" is not accepted as source
        self.assertIsNone(r.get_source())

    def test_select_other_repetition(self):
        r = OtherRepetition(['euh'])
        d1 = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "blah", "tok1", "blah"])
        d2 = DataSpeaker(["tok1", "euh", "euh", "tok1", "tok2", "euh"])
        n = r.get_longest(1, d1, d2)
        self.assertEqual(r.select(0, n, d1, d2), 4)
        self.assertEqual(r.get_source(), (0, 3))

    def test_find_echos(self):
        pass
        # TODO

    def test_detect_sr(self):
        d = DataSpeaker(["tok1", "tok2", "tok2", "tok2", "euh", "tok1", "euh"])
        r = SelfRepetition(['euh'])
        r.detect(d)
        self.assertEqual(r.get_source(), (0, 2))
        self.assertEqual(len(r.get_echos()), 2)
        self.assertTrue((3, 3) in r.get_echos())
        self.assertTrue((5, 5) in r.get_echos())

        d = DataSpeaker(["sur", "la", "bouffe", "#", "après", "etc", "la",
                         "etc", "#", "etc", "bouffe", "etc"])
        r = SelfRepetition(STOP_LIST)
        r.detect(d, limit=3)
        self.assertEqual(r.get_source(), (1, 2))

    def test_detect_or(self):

        r = OtherRepetition(STOP_LIST)
        s_AB = "le petit feu de artifice ouais ce être le tout petit truc là"
        s_CM = "le feu # ah le petit machin de ouais ouais ouais ouais ouais " \
               "d'accord ouais + ouais ouais ouais ouais + hum hum ouais hum " \
               "hum @@ # ouais # ouais ouais ouais ouais + hum # ouais oui " \
               "oui ce être pas le le ouais ah ouais ouais @@"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, d_CM, 15)
        self.assertEqual(r.get_source(), (0, 3))
        self.assertTrue((4, 5) in r.get_echos())  # le petit
        self.assertTrue((1, 1) in r.get_echos())  # feu
        self.assertTrue((7, 7) in r.get_echos())  # de

        s_AB = "ils voulaient qu'on fasse un feu d'artifice en_fait dans un " \
               "voy- un foyer un foyer catho un foyer de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, d_CM, 10)
        self.assertEqual(r.get_source(), (4, 6))

        s_AB = "en_fait dans un voy- un foyer un foyer catho un foyer " \
               "de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, d_CM, 10)
        self.assertEqual(r.get_source(), (4, 7))
        self.assertEqual(len(r.get_echos()), 1)
        self.assertTrue((5, 6) in r.get_echos())  # un foyer

        s_AB = "catho un foyer de bonnes soeurs"
        s_CM = "un feu d'artifice # dans un foyer de bonnes soeurs"
        d_AB = DataSpeaker(s_AB.split())
        d_CM = DataSpeaker(s_CM.split())
        r.detect(d_AB, d_CM, 10)
        self.assertEqual(r.get_source(), (1, 5))
        self.assertEqual(len(r.get_echos()), 1)
        self.assertTrue((5, 9) in r.get_echos())  # un foyer
