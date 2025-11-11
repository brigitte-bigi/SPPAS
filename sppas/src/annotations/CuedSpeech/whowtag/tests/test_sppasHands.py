# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.tests.test_sppasHands.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests for hand shapes math calcul data.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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
from sppas.core.coreutils import sppasIOError
from sppas.src.imgdata import sppasImage

from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag.handsset import sppasHandsSet

# ---------------------------------------------------------------------------

FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")
HANDS_FILES_PREFIX = "brigitte"

# ---------------------------------------------------------------------------


class TestHands(unittest.TestCase):
    """This class is a unit test class to the SppasHands class."""

    def setUp(self) -> None:
        self.hands = sppasHandsSet(CuedSpeechKeys(FRA_KEYS))

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def test_image(self):
        # None because we don't yet load images
        self.assertIsNone(self.hands.image("2"))

        self.hands.load(HANDS_FILES_PREFIX)

        # None because wrong index given
        self.assertIsNone(self.hands.image("45"))

        # correct index
        self.assertIsInstance(self.hands.image("2"), sppasImage)

    # ---------------------------------------------------------------------------

    def test_target_coords(self):
        # None because we don't yet load images
        self.assertIsNone(self.hands.target_coords("2"))

        self.hands.load(HANDS_FILES_PREFIX)

        # None because wrong index given
        self.assertIsNone(self.hands.target_coords("45"))

        # correct index
        coordinates = self.hands.target_coords("2")
        self.assertIsInstance(coordinates, tuple)
        self.assertIsInstance(coordinates[0], int)
        self.assertIsInstance(coordinates[1], int)

    # ---------------------------------------------------------------------------

    def test_distance(self):
        # 0 because we don't yet load images
        self.assertEqual(0, self.hands.distance("2"))

        self.hands.load(HANDS_FILES_PREFIX)

        # 0 because wrong index given
        self.assertEqual(0, self.hands.distance("45"))

        # correct index
        self.assertEqual(681, self.hands.distance("2"))

    # ---------------------------------------------------------------------------
    # Methods
    # ---------------------------------------------------------------------------

    def test_len_method_overloading(self):
        # check length before load images
        self.assertEqual(0, len(self.hands))

        # check length after loaded the 9 hands shapes images
        self.hands.load(HANDS_FILES_PREFIX)
        self.assertEqual(9, len(self.hands))

    # ---------------------------------------------------------------------------

    def test_load_method(self):
        # wrong prefix cases
        with self.assertRaises(sppasIOError):
            self.hands.load("wrong-prefix")

        # correct cases
        nb_hands_loaded = self.hands.load(HANDS_FILES_PREFIX)
        self.assertEqual(9, nb_hands_loaded)  # For French language, we have 9 hand shapes
