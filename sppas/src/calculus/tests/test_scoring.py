# -*- coding:utf-8 -*-
"""
:filename: sppas.src.calculus.tests.test_scoring.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for scoring calculus

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

from sppas.src.calculus.scoring.kappa import sppasKappa

# ---------------------------------------------------------------------------


class TestVectorKappa(unittest.TestCase):

    def setUp(self):
        self.p = [(1.0, 0.0), (0.0, 1.0), (0.0, 1.0), (1.0, 0.0), (1.0, 0.0)]
        self.q = [(1.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 0.0), (1.0, 0.0)]

    def test_kappa(self):
        kappa = sppasKappa(self.p, self.q)
        self.assertTrue(kappa.check())  # check both p and q
        self.assertFalse(kappa.check_vector([(0., 1.), (0., 1., 0.)]))
        self.assertFalse(kappa.check_vector([(0.0, 0.1)]))
        v = kappa.evaluate()
        self.assertEqual(0.54545, round(v, 5))

    def test_kappa3(self):
        p = [(1., 0., 0.), (0., 0., 1.), (0., 1., 0.), (1., 0., 0.), (0., 0., 1.)]
        q = [(0., 0., 1.), (0., 0., 1.), (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)]
        kappa = sppasKappa(p, q)
        v = kappa.evaluate()
        self.assertEqual(0.0625, round(v, 5))
