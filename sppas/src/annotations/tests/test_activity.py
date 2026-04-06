# -*- coding: utf8 -*-
"""
:filename: sppas.src.annotations.tests.test_activity.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Activity automatic annotation.

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

from sppas.core.config import symbols
from sppas.src.anndata import sppasTranscription

from sppas.src.annotations.Activity.activity import Activity

# ---------------------------------------------------------------------------


class TestActivity(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create(self):

        # create an instance with the default symbols
        a = Activity()
        for s in symbols.all:
            self.assertTrue(s in a)
        self.assertTrue(symbols.unk in a)
        self.assertEqual(len(a), len(symbols.all))

        # try to add again the same symbols - they won't
        for s in symbols.all:
            a.append_activity(s, symbols.all[s])
        self.assertEqual(len(a), len(symbols.all))

    def test_get_tier(self):
        a = Activity()
        trs = sppasTranscription()

        # Test with an empty Tokens tier
        tier = trs.create_tier('TokensAlign')
        tmin = trs.get_min_loc()
        tmax = trs.get_max_loc()

        tier = a.get_tier(tier, tmin, tmax)
        self.assertEqual(len(tier), 0)

        # now, test with a real TokensTier
        # ...
