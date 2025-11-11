# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.tests.test_sppasImageHandTagger.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests for tag images with cued speech hand (or badge).

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
from sppas.core.coreutils import sppasError
from sppas.src.imgdata import sppasImage
from sppas.src.anndata import sppasFuzzyPoint

from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag.whowimgtag.imghandtag import sppasImageHandTagger

# ---------------------------------------------------------------------------

FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")
HANDS_SET_PREFIX = "brigitte"

# ---------------------------------------------------------------------------


class TestImageHandTagger(unittest.TestCase):
    """This class is a unit test class to the SppasImageHandTagger class."""

    def setUp(self) -> None:
        self.cues = CuedSpeechKeys(FRA_KEYS)
        self.img = sppasImage(filename=os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png"))
        self.image_hand_tagger = sppasImageHandTagger(self.cues)

    # ---------------------------------------------------------------------------
    # Getters & Setters
    # ---------------------------------------------------------------------------

    def test_vowel_rank_getter(self):
        # invalid vowel cases
        self.assertEqual(-1, self.image_hand_tagger.get_vowel_rank("g"))

        # correct cases
        vowels_code = ["n", "b", "c", "s", "m", "t"]  # french vowels

        for current_code in vowels_code:
            index_expected = self.cues.get_vowels_codes().index(current_code)
            self.assertEqual(index_expected, self.image_hand_tagger.get_vowel_rank(current_code))

    # ---------------------------------------------------------------------------

    def test_enable_hand_mode(self):
        # never crash cases
        self.image_hand_tagger.enable_hand_mode(False)

        # activate hand mode cases, but we don't load any hand
        with self.assertRaises(sppasError):
            self.image_hand_tagger.enable_hand_mode()

        # activate hand mode cases, with hands loaded
        self.image_hand_tagger.load_hands(HANDS_SET_PREFIX)

        self.image_hand_tagger.enable_hand_mode()

    # ---------------------------------------------------------------------------

    def test_load_hands(self):
        success = self.image_hand_tagger.load_hands(HANDS_SET_PREFIX)
        self.assertTrue(success)
        self.image_hand_tagger.enable_hand_mode()  # no error raises

    # ---------------------------------------------------------------------------
    # Tag Methods
    # ---------------------------------------------------------------------------

    def test_badge_tag(self):
        shapes = list()
        target_points = list()

        # first badge
        shapes.append(("n", 1))
        target_points.append((sppasFuzzyPoint((100, 250), 20), 1))

        # second badge
        shapes.append(("b", 0.7))  # decrease the shape proba => text less weight
        target_points.append((sppasFuzzyPoint((200, 300), 30), 0.5))  # decrease the point proba => circle outline less black

        # tag and save the image
        img_tag = self.image_hand_tagger.slap_on(self.img, shapes, target_points)
        img_tag.write("test_img_tag_badge.png")

    # ---------------------------------------------------------------------------

    def test_hand_tag(self):
        self.image_hand_tagger.load_hands(HANDS_SET_PREFIX)
        self.image_hand_tagger.enable_hand_mode()

        img_tag = self.image_hand_tagger.slap_on(self.img, [(str(self.image_hand_tagger.get_vowel_rank("t")), 1)],
                                                 [(sppasFuzzyPoint((300, 333), 20), 0.9)])
        img_tag.write("test_img_tag_hand.png")
