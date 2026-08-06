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


def write_formants_file(filename, tokens, method_names=("burg",)):
    """Create a file with F1/F2 values, like the Formants annotation does.

    Each token is a tuple with a duration and the F1 and F2 values of each
    of the given methods.

    :param filename: (str) Name of the file to write
    :param tokens: (list) List of (duration, F1 values, F2 values)
    :param method_names: (tuple) Name of the estimation methods

    """
    tier_f1 = sppasTier("F1")
    tier_f2 = sppasTier("F2")
    for i, name in enumerate(method_names):
        tier_f1.set_meta("formants_estimator_method_{:d}".format(i), name)
        tier_f2.set_meta("formants_estimator_method_{:d}".format(i), name)

    for i, (duration, values_f1, values_f2) in enumerate(tokens):
        begin = 1. + (0.2 * i)
        location = sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(begin + duration)))

        label_f1 = sppasLabel([sppasTag(int(v), "int") for v in values_f1])
        label_f1.set_key("a")
        tier_f1.create_annotation(location, [label_f1])

        label_f2 = sppasLabel([sppasTag(int(v), "int") for v in values_f2])
        label_f2.set_key("a")
        tier_f2.create_annotation(location.copy(), [label_f2])

    trs = sppasTranscription("Formants")
    trs.append(tier_f1)
    trs.append(tier_f2)
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

        # All the tokens of the expected values are kept
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[0])
        self.assertEqual(NB_TOKENS, len(tier_f1))
        self.assertEqual(NB_TOKENS, len(tier_f2))
        self.assertEqual(NB_TOKENS, len(tier_dist))

        # The erroneous token is discarded. Only one method is enabled, so
        # no value at all is remaining for this token: like the Formants
        # annotation does, no annotation is created.
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[1])
        self.assertEqual(4, len(tier_f1))
        self.assertEqual(4, len(tier_f2))

        # The kept tokens are the expected ones, with their values unchanged
        for i, (duration, f1, f2) in enumerate(create_tokens(4)):
            self.assertEqual(int(f1), tier_f1[i].get_labels()[0][0][0].get_typed_content())
            self.assertEqual(int(f2), tier_f2[i].get_labels()[0][0][0].get_typed_content())
            self.assertEqual("a", tier_f1[i].get_labels()[0].get_key())

    # -----------------------------------------------------------------------

    def test_filtering_is_method_dependent(self):
        # Two methods: the 2nd one estimated an erroneous value of the last
        # token, the 1st one estimated the expected values. The two methods
        # can't share a value: it would be stored into a single tag.
        filename = os.path.join(self.folder, "twomethods-formants.xra")
        tokens = [(d, [f1, f1 + 7.], [f2, f2 + 11.]) for (d, f1, f2) in create_tokens(NB_TOKENS)]
        tokens.append((0.073, [700., 1800.], [1300., 600.]))
        write_formants_file(filename, tokens, method_names=("burg", "autocorrelation"))

        ann = sppasVowelFilter()
        out_files = ann.batch_processing([[filename]])
        self.assertEqual(1, len(out_files))

        # The token is kept: one of its methods has an expected value
        tier_f1, tier_f2, tier_dist = self.__read_result(out_files[0])
        self.assertEqual(NB_TOKENS + 1, len(tier_f1))

        # The value of the 1st method is kept, the one of the 2nd is filtered
        label_f1 = tier_f1[NB_TOKENS].get_labels()[0]
        self.assertEqual(700, label_f1[0][0].get_typed_content())
        self.assertEqual(0, label_f1[1][0].get_typed_content())

        label_f2 = tier_f2[NB_TOKENS].get_labels()[0]
        self.assertEqual(1300, label_f2[0][0].get_typed_content())
        self.assertEqual(0, label_f2[1][0].get_typed_content())

        # One distance for each method, and the filtered one is the highest
        label_dist = tier_dist[NB_TOKENS].get_labels()[0]
        self.assertEqual(2, len(label_dist))
        self.assertGreater(label_dist[1][0].get_typed_content(),
                           label_dist[0][0].get_typed_content())

    # -----------------------------------------------------------------------

    @staticmethod
    def __read_result(filename):
        """Return the three tiers of a file created by the annotation."""
        parser = sppasTrsRW(filename)
        trs = parser.read()

        return (trs.find("F1"),
                trs.find("F2"),
                trs.find("MahalanobisDist"))
