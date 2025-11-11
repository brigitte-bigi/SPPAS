# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.resources.tests.test_hand.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests class of the sppasHandResource class.

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

from sppas.core.coreutils import NegativeValueError
from sppas.core.coreutils import IndexRangeException

from sppas.src.resources.hand import sppasHandResource

# ----------------------------------------------------------------------------


class TestHandResource(unittest.TestCase):

    def setUp(self):
        self.__handResource = sppasHandResource()

    # ----------------------------------------------------------------------------
    # Test Getters
    # ----------------------------------------------------------------------------

    def test_identifiers_getter(self):
        # not yet loaded
        self.assertEqual(list(), self.__handResource.get_hand_sets_identifiers())

        self.__handResource.load_hand_set("cartoonhandcue")
        self.assertEqual(["cartoonhandcue"], self.__handResource.get_hand_sets_identifiers())

        self.__handResource.load_hand_set("brigitte")
        self.assertEqual(["cartoonhandcue", "brigitte"], self.__handResource.get_hand_sets_identifiers())

    # ----------------------------------------------------------------------------

    def test_images_getter(self):
        # test get images for hands set not loaded
        self.assertIsNone(self.__handResource.get_hand_images("brigitte"))

        self.__handResource.load_hand_set("brigitte")

        self.assertIsNone(self.__handResource.get_hand_images("cartoonhandcue"))

        # test get images for hands set loaded
        images = self.__handResource.get_hand_images("brigitte")
        self.assertIsNotNone(images)
        self.assertEqual(9, len(images))

        for img_path in images:
            self.assertTrue(os.path.exists(img_path))

    # ----------------------------------------------------------------------------

    def test_sights_list_getter(self):
        # test get sights for hands set not loaded
        self.assertIsNone(self.__handResource.get_hands_sights("brigitte"))

        self.__handResource.load_hand_set("brigitte")

        self.assertIsNone(self.__handResource.get_hands_sights("cartoonhandcue"))

        # test get images for hands set loaded
        sights = self.__handResource.get_hands_sights("brigitte")
        self.assertIsNotNone(sights)
        self.assertEqual(9, len(sights))

        for current_sights_path in sights:
            self.assertTrue(os.path.exists(current_sights_path))

    # ----------------------------------------------------------------------------

    def test_hand_shape_getter(self):
        # tests wrong index value
        with self.assertRaises(NegativeValueError):
            self.__handResource.get_shape("brigitte", -8)

        with self.assertRaises(IndexRangeException):
            self.__handResource.get_shape("brigitte", 1000)

        # test get hand shape for hands set not loaded
        self.assertIsNone(self.__handResource.get_sights("brigitte", 3))
        self.__handResource.load_hand_set("brigitte")
        self.assertIsNone(self.__handResource.get_shape("cartoonhandcue", 3))

        # test get hand shape for hands set loaded
        hand_shape = self.__handResource.get_shape("brigitte", 3)
        self.assertIsNotNone(hand_shape)
        self.assertTrue(os.path.exists(hand_shape))

    # ----------------------------------------------------------------------------

    def test_sights_getter(self):
        # tests wrong index value
        with self.assertRaises(NegativeValueError):
            self.__handResource.get_shape("brigitte", -1)

        with self.assertRaises(IndexRangeException):
            self.__handResource.get_shape("brigitte", 10)

        # test get shape sights for hands set not loaded
        self.assertIsNone(self.__handResource.get_sights("brigitte", 2))
        self.__handResource.load_hand_set("brigitte")
        self.assertIsNone(self.__handResource.get_shape("cartoonhandcue", 2))

        # test get shape sights for hands set loaded
        shape_sights = self.__handResource.get_shape("brigitte", 2)
        self.assertIsNotNone(shape_sights)
        self.assertTrue(os.path.exists(shape_sights))

    # ----------------------------------------------------------------------------
    # Test Public Methods
    # ----------------------------------------------------------------------------

    def test_clear_method(self):
        # we load resources
        self.__handResource.automatic_loading()
        self.assertNotEqual(0, len(self.__handResource))

        # we clear them
        self.__handResource.clear_hands_resources()
        self.assertEqual(0, len(self.__handResource))

    # ----------------------------------------------------------------------------

    def test_automatic_loading_method(self):
        self.assertEqual(0, len(self.__handResource))

        self.__handResource.automatic_loading()

        self.assertEqual(1, len(self.__handResource))
        self.assertEqual(["brigitte"], self.__handResource.get_hand_sets_identifiers())

        self.assertEqual(9, len(self.__handResource.get_hand_images("brigitte")))
        self.assertEqual(9, len(self.__handResource.get_hands_sights("brigitte")))

    # ----------------------------------------------------------------------------

    def test_load_hand_set_method(self):
        self.assertIsNone(self.__handResource.get_hand_images("brigitte"))

        self.__handResource.load_hand_set("brigitte")

        self.assertEqual(1, len(self.__handResource))
        self.assertEqual(["brigitte"], self.__handResource.get_hand_sets_identifiers())
        self.assertEqual(9, len(self.__handResource.get_hand_images("brigitte")))
        self.assertEqual(9, len(self.__handResource.get_hands_sights("brigitte")))

    # ----------------------------------------------------------------------------

    def test_len_method(self):
        # 0 because we don't yet loaded resources
        self.assertEqual(0, len(self.__handResource))

        # load one hands set, so len = 1
        self.__handResource.load_hand_set("brigitte")
        self.assertEqual(1, len(self.__handResource))

        # load another hands set, so len = 2
        self.__handResource.load_hand_set("laurent")
        self.assertEqual(2, len(self.__handResource))

        # clear and automatic load after, so len = 2 (only 2 hands sets in the resource/cuedspeech folder)
        self.__handResource.clear_hands_resources()
        self.__handResource.automatic_loading()
        self.assertEqual(2, len(self.__handResource))
