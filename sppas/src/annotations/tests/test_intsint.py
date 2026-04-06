# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.tests.test_intsint.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of INTSINT automatic annotation.

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

from sppas.src.annotations.Intsint import Intsint
from sppas.src.annotations.Intsint import sppasIntsint

# ---------------------------------------------------------------------------


class TestIntsint(unittest.TestCase):
    """Test of the class Intsint."""

    def setUp(self):
        self.anchors = [(0.1, 240), (0.4, 340), (0.6, 240), (0.7, 286)]

    def test_intsint(self):
        result = Intsint().annotate(self.anchors)
        self.assertEqual(len(self.anchors), len(result))
        self.assertEqual(['M', 'T', 'L', 'H'], result)

        with self.assertRaises(IOError):
            Intsint().annotate([(0.1, 240)])

    def test_sppasintsint(self):
        si = sppasIntsint()
        # to be continued...
