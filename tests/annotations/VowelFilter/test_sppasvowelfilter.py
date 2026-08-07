"""
:filename: tests.annotations.VowelFilter.test_sppasvowelfilter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the filtering of the erroneous formant values.

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
import os
import shutil
import tempfile

from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from sppas.src.annotations.VowelFilter.sppasvowelfilter import sppasVowelFilter

# ---------------------------------------------------------------------------

# Number of tokens the distributions are estimated with. The Mahalanobis
# distance of a token of a sample of n tokens can't be higher than
# (n-1)/sqrt(n): a small sample can't have any token further than the
# default threshold of 3 standard deviations.
NB_TOKENS = 40

# ---------------------------------------------------------------------------


def create_tokens(nb_tokens):
    """Return a list of (duration, F1, F2) of expected values of a vowel."""
    tokens = list()
    for i in range(nb_tokens):
        tokens.append((0.070 + 0.001 * (i % 7),
                       690. + 3. * (i % 11),
                       1280. + 5. * (i % 13)))

    return tokens

# ---------------------------------------------------------------------------


def create_tier(tier_name, method_names):
    """Return an empty tier with the metadata of the given methods."""
    tier = sppasTier(tier_name)
    for i, name in enumerate(method_names):
        tier.set_meta("formants_estimator_method_{:d}".format(i), name)

    return tier

# ---------------------------------------------------------------------------


def append_values(tier, location, values):
    """Append an annotation with the given values of a vowel 'a'."""
    label = sppasLabel([sppasTag(int(v), "int") for v in values])
    label.set_key("a")
    tier.create_annotation(location.copy(), [label])

# ---------------------------------------------------------------------------


def write_formants_file(filename, tokens, method_names=("burg",)):
    """Create a file with F1/F2 values, like the Formants annotation does.

    The values of all the methods are stored into the F1 and F2 tiers. Each
    method also has its own tiers, except if only one method is given: its
    tiers would be identical to the F1 and F2 ones.

    :param filename: (str) Name of the file to write
    :param tokens: (list) List of (duration, F1 values, F2 values)
    :param method_names: (tuple) Name of the estimation methods

    """
    trs = sppasTranscription("Formants")
    tier_f1 = create_tier("F1", method_names)
    tier_f2 = create_tier("F2", method_names)
    trs.append(tier_f1)
    trs.append(tier_f2)

    method_tiers = dict()
    if len(method_names) > 1:
        for name in method_names:
            method_tiers[name] = (create_tier("F1-" + name, [name]),
                                  create_tier("F2-" + name, [name]))
            trs.append(method_tiers[name][0])
            trs.append(method_tiers[name][1])

    for i, (duration, values_f1, values_f2) in enumerate(tokens):
        begin = 1. + (0.2 * i)
        location = sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(begin + duration)))

        append_values(tier_f1, location, values_f1)
        append_values(tier_f2, location, values_f2)

        for j, name in enumerate(method_names):
            if name in method_tiers:
                append_values(method_tiers[name][0], location, [values_f1[j]])
                append_values(method_tiers[name][1], location, [values_f2[j]])

    parser = sppasTrsRW(filename)
    parser.write(trs)

# ---------------------------------------------------------------------------


class TestSppasVowelFilter(unittest.TestCase):
    """Test of the filtering of the erroneous formant values of a corpus.

    """

    def setUp(self):
        self.folder = tempfile.mkdtemp()

        # A file with the expected values of the vowel: the distributions
        # are mainly estimated with these tokens.
        self.expected_filename = os.path.join(self.folder, "expected-formants.xra")
        tokens = [(d, [f1], [f2]) for (d, f1, f2) in create_tokens(NB_TOKENS)]
        write_formants_file(self.expected_filename, tokens)

        # A file with 4 expected tokens and an erroneous one: F1 and F2 are
        # inverted, like a formant jump does.
        self.erroneous_filename = os.path.join(self.folder, "erroneous-formants.xra")
        tokens = [(d, [f1], [f2]) for (d, f1, f2) in create_tokens(4)]
        tokens.append((0.073, [1800.], [600.]))
        write_formants_file(self.erroneous_filename, tokens)

    # -----------------------------------------------------------------------

    def tearDown(self):
        shutil.rmtree(self.folder)

    # -----------------------------------------------------------------------

    def test_options(self):
        ann = sppasVowelFilter()
        self.assertEqual(3., ann.get_threshold())
        self.assertEqual(False, ann.get_coda())
        self.assertEqual("-vfilter", ann.get_output_pattern())
        self.assertEqual(["-formants", "-syll"], ann.get_input_patterns())

        ann.set_threshold(2.5)
        self.assertEqual(2.5, ann.get_threshold())
        ann.set_coda(True)
        self.assertEqual(True, ann.get_coda())

        with self.assertRaises(ValueError):
            ann.set_threshold(0.)
        with self.assertRaises(TypeError):
            ann.set_threshold("2.5")

    # -----------------------------------------------------------------------

    def test_no_file(self):
        ann = sppasVowelFilter()
        self.assertEqual(list(), ann.batch_processing(list()))

    # -----------------------------------------------------------------------

    def test_batch_processing(self):
        ann = sppasVowelFilter()
        out_files = ann.batch_processing([[self.expected_filename],
                                          [self.erroneous_filename]])
        self.assertEqual(2, len(out_files))

        # Only one method: the F1 and F2 tiers are the filtered ones
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[0], "")
        self.assertEqual(NB_TOKENS, len(tier_f1))
        self.assertEqual(NB_TOKENS, len(tier_f2))
        self.assertEqual(NB_TOKENS, len(tier_dist))

        # The erroneous value is discarded, the expected ones are kept
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[1], "")
        self.assertEqual(5, len(tier_f1))
        self.assertEqual(0, tier_f1[4].get_best_tag().get_typed_content())
        self.assertEqual(0, tier_f2[4].get_best_tag().get_typed_content())
        self.assertGreater(tier_dist[4].get_best_tag().get_typed_content(), 3.)

        for i, (duration, f1, f2) in enumerate(create_tokens(4)):
            self.assertEqual(int(f1), tier_f1[i].get_best_tag().get_typed_content())
            self.assertEqual(int(f2), tier_f2[i].get_best_tag().get_typed_content())
            self.assertEqual("a", tier_f1[i].get_labels()[0].get_key())

    # -----------------------------------------------------------------------

    def test_filtering_is_method_dependent(self):
        # Two methods: the 2nd one estimated an erroneous value of the last
        # token, the 1st one estimated the expected values.
        filename = os.path.join(self.folder, "twomethods-formants.xra")
        tokens = [(d, [f1, f1 + 7.], [f2, f2 + 11.]) for (d, f1, f2) in create_tokens(NB_TOKENS)]
        tokens.append((0.073, [700., 1800.], [1300., 600.]))
        write_formants_file(filename, tokens, method_names=("burg", "autocorrelation"))

        ann = sppasVowelFilter()
        out_files = ann.batch_processing([[filename]])
        self.assertEqual(1, len(out_files))

        # The value of the 1st method is kept, the one of the 2nd is discarded
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[0], "-burg")
        self.assertEqual(NB_TOKENS + 1, len(tier_f1))
        self.assertEqual(700, tier_f1[NB_TOKENS].get_best_tag().get_typed_content())
        self.assertEqual(1300, tier_f2[NB_TOKENS].get_best_tag().get_typed_content())

        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[0], "-autocorrelation")
        self.assertEqual(0, tier_f1[NB_TOKENS].get_best_tag().get_typed_content())
        self.assertEqual(0, tier_f2[NB_TOKENS].get_best_tag().get_typed_content())
        self.assertGreater(tier_dist[NB_TOKENS].get_best_tag().get_typed_content(), 3.)

    # -----------------------------------------------------------------------

    def test_reference_tiers_are_not_filtered(self):
        # The F1 and F2 tiers are storing the values of both methods into
        # alternative tags: they are neither filtered nor copied.
        filename = os.path.join(self.folder, "twomethods-formants.xra")
        tokens = [(d, [f1, f1 + 7.], [f2, f2 + 11.]) for (d, f1, f2) in create_tokens(NB_TOKENS)]
        write_formants_file(filename, tokens, method_names=("burg", "autocorrelation"))

        ann = sppasVowelFilter()
        out_files = ann.batch_processing([[filename]])

        parser = sppasTrsRW(out_files[0])
        trs = parser.read()
        self.assertIsNone(trs.find("F1"))
        self.assertIsNone(trs.find("F2"))
        self.assertEqual(6, len(trs))

    # -----------------------------------------------------------------------

    @staticmethod
    def __read_result(filename, method_suffix):
        """Return the three tiers of a method of a file created by the annotation."""
        parser = sppasTrsRW(filename)
        trs = parser.read()

        return (trs.find("F1" + method_suffix),
                trs.find("F2" + method_suffix),
                trs.find("MahalanobisDist" + method_suffix))
