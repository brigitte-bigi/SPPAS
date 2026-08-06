"""
:filename: tests.annotations.VowelFilter.test_vowel_classifier.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the class name of the vowels to be filtered.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from sppas.src.annotations.VowelFilter.vowel_classifier import VowelClassifier

# ---------------------------------------------------------------------------


def create_interval(begin, end):
    """Return a location of an interval between the two given times."""
    return sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(end)))

# ---------------------------------------------------------------------------


class TestVowelClassifier(unittest.TestCase):
    """Test of the class names assigned to the vowels.

    """

    def setUp(self):
        # A tier with the F1 values of two vowels, like the Formants
        # annotation is creating: the phoneme is the key of the label.
        self.tier_f1 = sppasTier("F1")

        label = sppasLabel(sppasTag(700, "int"))
        label.set_key("a")
        self.tier_f1.create_annotation(create_interval(1., 1.1), [label])

        label = sppasLabel(sppasTag(350, "int"))
        label.set_key("i")
        self.tier_f1.create_annotation(create_interval(1.3, 1.4), [label])

        # A tier with two syllables: the 1st vowel is followed by a coda,
        # the 2nd one is closing its syllable.
        self.tier_syll = sppasTier("Syllables")
        self.tier_syll.create_annotation(create_interval(1., 1.2),
                                         sppasLabel(sppasTag("a-b")))
        self.tier_syll.create_annotation(create_interval(1.3, 1.4),
                                         sppasLabel(sppasTag("i")))

    # -----------------------------------------------------------------------

    def test_class_of_phoneme(self):
        classifier = VowelClassifier()
        self.assertEqual("a", classifier.get_class(self.tier_f1[0]))
        self.assertEqual("i", classifier.get_class(self.tier_f1[1]))

    # -----------------------------------------------------------------------

    def test_class_without_phoneme(self):
        tier = sppasTier("F1")
        tier.create_annotation(create_interval(1., 1.1), [sppasLabel(sppasTag(700, "int"))])
        tier.create_annotation(create_interval(1.3, 1.4))

        classifier = VowelClassifier()
        self.assertEqual("", classifier.get_class(tier[0]))
        self.assertEqual("", classifier.get_class(tier[1]))

    # -----------------------------------------------------------------------

    def test_class_of_phoneme_and_position(self):
        classifier = VowelClassifier(self.tier_syll)
        self.assertEqual("a" + VowelClassifier.CODA_SYMBOL,
                         classifier.get_class(self.tier_f1[0]))
        self.assertEqual("i" + VowelClassifier.OPEN_SYMBOL,
                         classifier.get_class(self.tier_f1[1]))

    # -----------------------------------------------------------------------

    def test_class_of_vowel_out_of_syllables(self):
        # The vowel is not inside a syllable: its position is unknown
        tier = sppasTier("F1")
        label = sppasLabel(sppasTag(700, "int"))
        label.set_key("a")
        tier.create_annotation(create_interval(4., 4.1), [label])

        classifier = VowelClassifier(self.tier_syll)
        self.assertEqual("a", classifier.get_class(tier[0]))

    # -----------------------------------------------------------------------

    def test_invalid_syllables(self):
        with self.assertRaises(TypeError):
            VowelClassifier("Syllables")

        tier = sppasTier("Points")
        tier.create_annotation(sppasLocation(sppasPoint(1.)), sppasLabel(sppasTag("a")))
        with self.assertRaises(TypeError):
            VowelClassifier(tier)
