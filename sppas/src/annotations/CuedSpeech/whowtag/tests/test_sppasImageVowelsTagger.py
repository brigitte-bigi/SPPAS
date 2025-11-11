# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.tests.test_sppasImageVowelsTagger.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests for vowels tag on an image.

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
from sppas.src.imgdata import sppasImage
from sppas.src.anndata import sppasFuzzyPoint

from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag.whowimgtag.imgpostag import sppasImageVowelPosTagger

# ---------------------------------------------------------------------------

FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")

# ---------------------------------------------------------------------------


class TestImageVowelsTagger(unittest.TestCase):
    """This class is a unit test class to the sppasImageVowelsTagger class."""

    def setUp(self) -> None:
        self.img = sppasImage(filename=os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png"))
        self.cues = CuedSpeechKeys(FRA_KEYS)

        self.image_vowels_tagger = sppasImageVowelPosTagger(self.cues)

    # ---------------------------------------------------------------------------
    # Getters
    # ---------------------------------------------------------------------------

    def test_vowel_text_getter(self):
        # empty string because negative index
        self.assertEqual("", self.image_vowels_tagger.get_vowel_text(-5))

        # empty string because too huge index (index out of bounds)
        self.assertEqual("", self.image_vowels_tagger.get_vowel_text(100000))

        # correct cases
        vowel_index = 3
        vowel_text_expected = self.cues.get_vowels_codes()[vowel_index]

        self.assertEqual(vowel_text_expected, self.image_vowels_tagger.get_vowel_text(vowel_index))

    # ---------------------------------------------------------------------------

    def test_vowel_color_getter(self):
        default_return_value = (128, 128, 128)

        # negative index cases
        self.assertEqual(default_return_value, self.image_vowels_tagger.get_vowel_color(-5))

        # too huge index cases (index out of bounds)
        self.assertEqual(default_return_value, self.image_vowels_tagger.get_vowel_color(1000))

        # correct cases
        """
        - Key of vowels "n" is grey   (128, 128, 128)
        - Key of vowels "t" is green  (0, 175, 0)
        - Key of vowels "s" is blue   (0, 128, 255)
        - Key of vowels "m" is red    (205, 0, 0)
        - Key of vowels "c" is orange (255, 128, 0)
        - Key of vowels "b" is pink   (200, 0, 100)
        """
        vowels_color = [(128, 128, 128), (0, 175, 0), (0, 128, 255), (205, 0, 0), (255, 128, 0), (200, 0, 100)]

        for i in range(len(vowels_color)):
            self.assertEqual(vowels_color[i], self.image_vowels_tagger.get_vowel_color(i))

    # ---------------------------------------------------------------------------
    # Methods
    # ---------------------------------------------------------------------------

    def test_tag_vowel(self):
        f1 = sppasFuzzyPoint((500, 400), 30)
        f2 = sppasFuzzyPoint((600, 400), 30)
        f3 = sppasFuzzyPoint((700, 400), 30)
        f4 = sppasFuzzyPoint((800, 400), 30)
        f5 = sppasFuzzyPoint((900, 400), 30)
        f6 = sppasFuzzyPoint((1000, 400), 30)

        # first cases with vowel name option disabled
        img_copy = self.img.copy()

        img_copy = self.image_vowels_tagger.slap_on(img_copy, [None, f1, None, f2])
        img_copy.write("test_tag_vowel_without_vowel_name.jpg")

        # second cases with vowel name option activated
        img_copy = self.img.copy()
        self.image_vowels_tagger.enable_vowel_name()

        img_copy = self.image_vowels_tagger.slap_on(img_copy, [f1, f2, f3, f4, f5, f6])
        img_copy.write("test_tag_vowel_with_vowel_name.jpg")
