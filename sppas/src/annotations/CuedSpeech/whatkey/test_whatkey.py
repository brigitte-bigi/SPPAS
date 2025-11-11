# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.test_whatkey.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unittests for Cued Speech keys predictor.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

    ---------------------------------------------------------------------

"""

import unittest
import os.path

from sppas.core.config import paths
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from .whatkeyexc import sppasCuedRulesValueError
from .whatkeyexc import sppasCuedRulesMinValueError
from .whatkeyexc import sppasCuedRulesMaxValueError
from .keysrules import CuedSpeechCueingRules
from .phonestokeys import CuedSpeechKeys
from .whatkey import sppasWhatKeyPredictor

# ---------------------------------------------------------------------------

# French
FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")
# American English
ENG_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-eng.txt")

# ---------------------------------------------------------------------------


class TestWhatKeyExceptions(unittest.TestCase):
    """Test the exceptions of the 'whatkey' package."""

    def test_min_value_error(self):
        try:
            raise sppasCuedRulesMinValueError("abcd")
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasCuedRulesMinValueError))
            self.assertTrue("1321" in str(e))
            self.assertTrue(1321, e.status)

    def test_value_error(self):
        try:
            raise sppasCuedRulesValueError("abcd")
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasCuedRulesValueError))
            self.assertTrue("1322" in str(e))
            self.assertTrue(1322, e.status)

    def test_max_value_error(self):
        try:
            raise sppasCuedRulesMaxValueError("abcd")
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasCuedRulesMaxValueError))
            self.assertTrue("1323" in str(e))
            self.assertTrue(1323, e.status)

# ---------------------------------------------------------------------------


class TestWhatKeyCueingRules(unittest.TestCase):
    """Test the base class for any cueing rule system. """

    def test_init(self):
        # No file is defined
        rules = CuedSpeechCueingRules()
        self.assertIsNone(rules.get_key("p"))
        self.assertIsNone(rules.get_key("#"))
        self.assertEqual(rules.get_class("p"), CuedSpeechCueingRules.NEUTRAL_CLASS)
        self.assertEqual(rules.get_class("#"), CuedSpeechCueingRules.NEUTRAL_CLASS)
        self.assertEqual(rules.get_class("cnone"), "N")
        self.assertEqual(rules.get_class("vnone"), "N")
        self.assertEqual(rules.get_class("cnil"), "N")
        self.assertEqual(rules.get_class("vnil"), "N")

        self.assertEqual(rules.get_key("cnone"), "0")
        self.assertEqual(rules.get_key("vnone"), "n")
        self.assertIsNone(rules.get_key("cnil"))
        self.assertIsNone(rules.get_key("vnil"))

        # A wrong file is given
        with self.assertRaises(IOError):
            rules = CuedSpeechCueingRules("toto.txt")

        # An expected file is given
        rules = CuedSpeechCueingRules(FRA_KEYS)
        self.assertEqual(rules.get_class("#"), CuedSpeechCueingRules.NEUTRAL_CLASS)
        self.assertEqual(rules.get_class("e"), "V")
        self.assertEqual(rules.get_class("p"), "C")
        self.assertEqual(rules.get_class("fp"), CuedSpeechCueingRules.NEUTRAL_CLASS)

        self.assertEqual(rules.get_key("p"), "1")
        self.assertEqual(rules.get_key("e"), "t")   # throat
        self.assertEqual(rules.get_key("E"), "c")   # chin
        self.assertEqual(rules.get_key("2"), "b")   # cheek bone
        self.assertEqual(rules.get_key("#"), None)
        self.assertEqual(rules.get_key("fp"), None)

    # -----------------------------------------------------------------------

    def test_load(self):
        rules = CuedSpeechCueingRules()

        # Wrong filename
        with self.assertRaises(IOError):
            rules.load("toto.txt")

        # No rule defined in the file
        result = rules.load(os.path.abspath(__file__))
        self.assertFalse(result)
        self.assertEqual(rules.get_shape_target(""), CuedSpeechCueingRules.SHAPE_TARGET)

        # A well-formed file
        result = rules.load(FRA_KEYS)
        self.assertTrue(result)
        self.assertEqual(rules.get_class("p"), "C")
        self.assertEqual(rules.get_class("e"), "V")
        self.assertEqual(rules.get_class("cnil"), "N")
        self.assertEqual(rules.get_class("vnil"), "N")
        # unknown vowel
        self.assertEqual(rules.get_class("aU"), "N")

        self.assertEqual(rules.get_key("p"), "1")
        self.assertEqual(rules.get_key("e"), "t")
        self.assertIsNone(rules.get_key("aU"))
        self.assertEqual(rules.get_key("cnil"), "5")
        self.assertEqual(rules.get_key("vnil"), "s")

        self.assertIsNone(rules.get_key("%"))

        # Defined targets
        self.assertEqual(rules.get_shape_target("0"), 5)
        self.assertEqual(rules.get_shape_target("1"), 8)
        self.assertEqual(rules.get_shape_target("2"), 12)
        # Undefined target
        self.assertEqual(rules.get_shape_target("a"), CuedSpeechCueingRules.SHAPE_TARGET)

    # -----------------------------------------------------------------------

    def test_getters(self):
        rules = CuedSpeechCueingRules(FRA_KEYS)
        self.assertEqual(rules.get_nil_vowel(), "s")
        self.assertEqual(rules.get_nil_consonant(), "5")

        self.assertEqual(CuedSpeechCueingRules().get_neutral_consonant(), "0")
        self.assertEqual(CuedSpeechCueingRules().get_neutral_vowel(), "n")

        # Defined targets
        self.assertEqual(rules.get_shape_target("2"), 12)
        # Undefined target
        self.assertEqual(rules.get_shape_target("a"), CuedSpeechCueingRules.SHAPE_TARGET)

        # get target from phoneme
        self.assertEqual(rules.get_phon_target("p"), 8)
        self.assertEqual(rules.get_phon_target("S"), 8)
        self.assertEqual(rules.get_phon_target("g"), 12)
        self.assertEqual(rules.get_phon_target("m"), 12)
        self.assertEqual(rules.get_phon_target("a"), CuedSpeechCueingRules.SHAPE_TARGET)

    # -----------------------------------------------------------------------

    def test_get_diphthong_key(self):
        rules = CuedSpeechCueingRules(ENG_KEYS)

        key = rules.get_diphthong_key("aI")
        self.assertEqual(key, ('s', 't'))

        # Given entry is not a diphthong
        self.assertIsNone(rules.get_diphthong_key("E"))
        self.assertIsNone(rules.get_diphthong_key("p"))

    def test_get_key(self):
        rules = CuedSpeechCueingRules(ENG_KEYS)
        # Given entry is a known phoneme
        key = rules.get_key("@U")
        self.assertEqual(key, "sf")
        key = rules.get_key("D")
        self.assertEqual(key, "2")
        key = rules.get_key("I")
        self.assertEqual(key, "t")

        # Given entry is a known diphthong
        key = rules.get_key("aI")
        self.assertEqual(key, ('s', 't'))

        # Given entry is unknown
        self.assertIsNone(rules.get_diphthong_key(""))
        self.assertIsNone(rules.get_diphthong_key("o"))

    # -----------------------------------------------------------------------

    def test_syll_to_key(self):

        # French well-formed syllables (C-V or C- or -V)
        rules = CuedSpeechCueingRules(FRA_KEYS)

        keys = rules.syll_to_key("p-")
        self.assertEqual(("1", "s"), keys)

        keys = rules.syll_to_key("-a")
        self.assertEqual(("5", "s"), keys)

        keys = rules.syll_to_key("p-a")
        self.assertEqual(("1", "s"), keys)

        keys = rules.syll_to_key("p")
        self.assertEqual(("1", "s"), keys)

        keys = rules.syll_to_key("a")
        self.assertEqual(("5", "s"), keys)

        # Unknown phonemes

        # badly-formed syllables
        with self.assertRaises(ValueError):
            rules.syll_to_key("-")

        with self.assertRaises(ValueError):
            rules.syll_to_key("%")

        with self.assertRaises(ValueError):
            rules.syll_to_key("%-")

        with self.assertRaises(ValueError):
            rules.syll_to_key("-%")

        with self.assertRaises(ValueError):
            rules.syll_to_key("p-a-p")

        with self.assertRaises(ValueError):
            rules.syll_to_key("p-p")

        with self.assertRaises(ValueError):
            rules.syll_to_key("a-a")

        with self.assertRaises(ValueError):
            rules.syll_to_key("a-p")

        with self.assertRaises(ValueError):
            rules.syll_to_key("")

        # English well-formed syllables (C-V or C- or -V)
        rules = CuedSpeechCueingRules(ENG_KEYS)

        keys = rules.syll_to_key("p-")
        self.assertEqual(("1", "s"), keys)

        keys = rules.syll_to_key("p-E")
        self.assertEqual(("1", "c"), keys)

        keys = rules.syll_to_key("p-aI")
        self.assertEqual((("1", "s"), ('5', 't')), keys)

    # -----------------------------------------------------------------------

    def test_get_vowels_codes(self):
        rules = CuedSpeechCueingRules()
        vowels = rules.get_vowels_codes()
        self.assertEqual(len(vowels), 1)  # neutral=n
        self.assertTrue('n' in vowels)

        rules.load(FRA_KEYS)
        fra_vowels = rules.get_vowels_codes()
        self.assertEqual(len(fra_vowels), 6)  # neutral=n and 5 positions
        self.assertTrue('n' in fra_vowels)
        self.assertEqual(fra_vowels, ['n', 't', 's', 'm', 'c', 'b'])

        rules.load(ENG_KEYS)
        eng_vowels = rules.get_vowels_codes()
        self.assertEqual(len(eng_vowels), 7)  # neutral=n and 6 positions
        self.assertTrue('n' in eng_vowels)
        self.assertEqual(eng_vowels, ['n', 't', 'sf', 'sd', 's', 'm', 'c'])

    # -----------------------------------------------------------------------

    def test_get_consonants_codes(self):
        rules = CuedSpeechCueingRules()
        cons = rules.get_consonants_codes()
        self.assertEqual(len(cons), 1)  # neutral=0
        self.assertTrue('0' in cons)

        rules.load(FRA_KEYS)
        fra_cons = rules.get_consonants_codes()
        self.assertEqual(len(fra_cons), 9)  # neutral and 8 shapes
        self.assertEqual(fra_cons, [str(i) for i in range(9)])

        rules.load(ENG_KEYS)
        eng_cons = rules.get_consonants_codes()
        self.assertEqual(len(eng_cons), 9)  # neutral and 8 shapes
        self.assertEqual(eng_cons, [str(i) for i in range(9)])

# ---------------------------------------------------------------------------


class TestWhatCuedSpeechKeys(unittest.TestCase):
    """Test the syllabification when applying rules to a sequence of phonemes."""

    def setUp(self):
        self.lfpc = CuedSpeechKeys(FRA_KEYS)
        self.csa = CuedSpeechKeys(ENG_KEYS)

    # -----------------------------------------------------------------------

    def test_annotate_breaks(self):
        phonemes = list()
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["#"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["fp"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, list())

        # Unknown phoneme
        phonemes = ["%"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, list())

    # -----------------------------------------------------------------------

    def test_annotate_consonants(self):
        phonemes = ["p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["s", "p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1)])

        phonemes = ["s", "p", "p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (2, 2)])

        phonemes = ["s", "p", "#", "p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (3, 3)])

        phonemes = ["#", "s", "p", "#", "p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 2), (4, 4)])

        phonemes = ["#", "s", "p", "a", "s"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 3), (4, 4)])

    # -----------------------------------------------------------------------

    def test_annotate_vowels(self):
        phonemes = ["a"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["a", "e"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1)])

        phonemes = ["a", "e", "u"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (2, 2)])

        phonemes = ["a", "e", "#", "u"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (1, 1), (3, 3)])

        phonemes = ["#", "a", "e", "#", "u"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 2), (4, 4)])

    # -----------------------------------------------------------------------

    def test_annotate_unknown(self):
        # Unknown phonemes are not coded!
        phonemes = ["X"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, list())

        phonemes = ["a", "X"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0)])

        phonemes = ["a", "X", "a"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 0), (2, 2)])

        phonemes = ["#", "s", "p", "%", "p"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(1, 1), (2, 2), (4, 4)])

    # -----------------------------------------------------------------------

    def test_syllabify(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 1), (2, 3), (4, 4)])

        phonemes = ['b', 'O~', '#', 'Z', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 1), (3, 4), (5, 5)])

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 1), (3, 4), (5, 5)])

        phonemes = ['b', 'O~', '%', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        self.assertEqual(sgmts, [(0, 1), (3, 3), (4, 4)])

    # -----------------------------------------------------------------------

    def test_phonetize(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "b-O~.Z-u.R-vnil")

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "b-O~.Z-u.R-vnil")

        phonemes = ['O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "cnil-O~.Z-u.R-vnil")

        phonemes = ["s", "p", "a", "s"]
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "s-vnil.p-a.s-vnil")

        phonemes = ['b', 'O~', '%', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        self.assertEqual(phons, "b-O~.cnil-u.R-vnil")

    # -----------------------------------------------------------------------

    def test_keys(self):
        phonemes = ['b', 'O~', 'Z', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lfpc.keys_phonetized(phons)
        self.assertEqual(keys, "4-m.1-c.3-s")

        phonemes = ['b', 'O~', 'fp', 'Z', 'u', 'R', "#"]
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lfpc.keys_phonetized(phons)
        self.assertEqual(keys, "4-m.1-c.3-s")

        phonemes = ["s", "p", "a", "s"]
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lfpc.keys_phonetized(phons)
        self.assertEqual(keys, "3-s.1-s.3-s")

        phonemes = ['b', 'O~', '%', 'u', 'R']
        sgmts = self.lfpc.syllabify(phonemes)
        phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        keys = self.lfpc.keys_phonetized(phons)
        self.assertEqual(keys, "4-m.5-c.3-s")

        phonemes = ['m', 'aI', 'h', 'aU', 's']
        sgmts = self.csa.syllabify(phonemes)
        phons = self.csa.phonetize_syllables(phonemes, sgmts)
        keys = self.csa.keys_phonetized(phons)
        self.assertEqual(keys, "5-s.5-t.3-s.5-t.3-s")

# ---------------------------------------------------------------------------


class TestWhatKeysPredictor(unittest.TestCase):
    """Test cued speech generation of a tier."""

    def setUp(self):
        self.rules = CuedSpeechKeys(FRA_KEYS)
        self.lpc = sppasWhatKeyPredictor(self.rules)

        self.tier = sppasTier("PhonAlign")
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(0.), sppasPoint(0.2))),
            sppasLabel(sppasTag("#")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(0.2), sppasPoint(0.6))),
            sppasLabel(sppasTag("v")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(0.6), sppasPoint(2.))),
            sppasLabel(sppasTag("#")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(2.8))),
            sppasLabel(sppasTag("j")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(2.8), sppasPoint(3.9))),
            sppasLabel(sppasTag("o")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(3.9), sppasPoint(4.))),
            sppasLabel(sppasTag("+")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
            sppasLabel(sppasTag("l")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
            sppasLabel(sppasTag("E")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(7.5))),
            sppasLabel(sppasTag("t")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(7.5), sppasPoint(10.))),
            sppasLabel(sppasTag("#")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(10.), sppasPoint(11.))),
            sppasLabel(sppasTag("v")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(11.), sppasPoint(12.))),
            sppasLabel(sppasTag("i")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(12.), sppasPoint(14.2))),
            sppasLabel(sppasTag("#")))

    # -----------------------------------------------------------------------

    def test_phons_to_key_predictor(self):
        # Create the key segments. There are 5 keys in the example: v-jo-lE-t-vi
        result_phons = self.lpc.phons_to_segments(self.tier)
        self.assertEqual(len(result_phons), 5)

        # Convert the key segments to cued code
        result_keys, result_class, _ = self.lpc.segments_to_keys(
            result_phons, self.tier.get_first_point(), self.tier.get_last_point())
        self.assertEqual(len(result_keys), len(result_class))
        for ann1, ann2 in zip(result_keys, result_class):
            labels = ann1.get_labels()
            self.assertTrue(len(labels), 2)
            labels = ann2.get_labels()
            self.assertTrue(len(labels), 2)
            self.assertTrue(labels[0].get_best().get_content() in ('C', 'N'))
            self.assertTrue(labels[1].get_best().get_content() in ('V', 'N'))
        self.assertEqual(len(result_keys), 9)

        # Vowel keys
        self.assertEqual('0', result_keys[0].get_labels()[0].get_best().get_content())
        self.assertEqual('2', result_keys[1].get_labels()[0].get_best().get_content())
        self.assertEqual('0', result_keys[2].get_labels()[0].get_best().get_content())
        self.assertEqual('8', result_keys[3].get_labels()[0].get_best().get_content())
        self.assertEqual('6', result_keys[4].get_labels()[0].get_best().get_content())
        self.assertEqual('5', result_keys[5].get_labels()[0].get_best().get_content())
        self.assertEqual('0', result_keys[6].get_labels()[0].get_best().get_content())
        self.assertEqual('2', result_keys[7].get_labels()[0].get_best().get_content())
        self.assertEqual('0', result_keys[8].get_labels()[0].get_best().get_content())

        # Consonant keys
        self.assertEqual('n', result_keys[0].get_labels()[1].get_best().get_content())
        self.assertEqual('s', result_keys[1].get_labels()[1].get_best().get_content())
        self.assertEqual('s', result_keys[2].get_labels()[1].get_best().get_content())
        self.assertEqual('s', result_keys[3].get_labels()[1].get_best().get_content())
        self.assertEqual('c', result_keys[4].get_labels()[1].get_best().get_content())
        self.assertEqual('s', result_keys[5].get_labels()[1].get_best().get_content())
        self.assertEqual('n', result_keys[6].get_labels()[1].get_best().get_content())
        self.assertEqual('m', result_keys[7].get_labels()[1].get_best().get_content())
        self.assertEqual('n', result_keys[8].get_labels()[1].get_best().get_content())
