# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.tests.test_sppasHandProperties.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests for hand shapes data.

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

import unittest

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import IntervalRangeException

from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasSights

from sppas.src.annotations.CuedSpeech.whowtag.handproperties import sppasHandProperties

# ---------------------------------------------------------------------------


class TestHandProperties(unittest.TestCase):
    """This class is a unit test class to the SppasHandProperties class."""

    def setUp(self) -> None:
        self.img = sppasImage(0).blank_image(w=320, h=200)

        self.sights = sppasSights(4)
        self.sights.set_sight(0, 250, 400)  # S0 = (250, 400)
        self.sights.set_sight(1, 300, 200)  # S9 = (300, 200)
        self.sights.set_sight(2, 300, 200)
        self.sights.set_sight(3, 300, 200)

    # ---------------------------------------------------------------------------
    # Tests Exceptions
    # ---------------------------------------------------------------------------

    def test_negative_target_index(self):
        with self.assertRaises(IntervalRangeException):
            sppasHandProperties(self.img, self.sights, -3)

    # ---------------------------------------------------------------------------

    def test_too_huge_target_index(self):
        with self.assertRaises(IntervalRangeException):
            # exception raise because target index > len(sights)
            sppasHandProperties(self.img, self.sights, 5)

    # ---------------------------------------------------------------------------

    def test_incorrect_nb_sights(self):
        self.sights = sppasSights(16)

        with self.assertRaises(sppasError):
            sppasHandProperties(self.img, self.sights, 1)

    # ---------------------------------------------------------------------------
    # Tests Static Methods
    # ---------------------------------------------------------------------------

    def test_pythagoras(self):
        side1 = 3
        side2 = 4

        # classic case
        # result expend : 3² + 4² = 25 => square_root(25) = 5
        self.assertEqual(5, sppasHandProperties.pythagoras(side1, side2))

        # test sides order doesn't change the result
        self.assertEqual(sppasHandProperties.pythagoras(side1, side2), sppasHandProperties.pythagoras(side2, side1))

    # ---------------------------------------------------------------------------
    # Tests Getters & Estimation
    # ---------------------------------------------------------------------------

    def test_getters(self):
        # Variables initialization
        img_width = self.img.width
        img_height = self.img.height
        target_sight = 1

        hand_properties = sppasHandProperties(self.img, self.sights, target_sight)

        # test image getter
        self.assertEqual(self.img, hand_properties.image())

        # test image size getter
        self.assertEqual(img_width, hand_properties.image_size()[0])  # with test
        self.assertEqual(img_height, hand_properties.image_size()[1])  # height test
        self.assertEqual((img_width, img_height), hand_properties.image_size())  # tuple test

        # test number of sights
        self.assertEqual(len(self.sights), hand_properties.nb_sights())

        # test target sight coordinates
        self.assertEqual(self.sights.get_sight(target_sight)[:2], hand_properties.target_coords())

    # ---------------------------------------------------------------------------

    def test_distance_estimation(self):
        hand_properties = sppasHandProperties(self.img, self.sights, 1)

        # first case
        self.assertEqual(206, hand_properties.distance())

        # change sights coordinates
        self.sights.set_sight(1, 200, 200)
        self.sights.set_sight(2, 200, 200)
        self.sights.set_sight(3, 200, 200)

        hand_properties = sppasHandProperties(self.img, self.sights, 1)

        # second case
        self.assertEqual(206, hand_properties.distance())
