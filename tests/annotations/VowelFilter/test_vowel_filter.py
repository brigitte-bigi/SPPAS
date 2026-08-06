"""
:filename: tests.annotations.VowelFilter.test_vowel_filter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the estimator of the erroneous formant values.

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

from sppas.src.annotations.VowelFilter.vowel_filter import VowelFilterEstimator

# ---------------------------------------------------------------------------

# The Mahalanobis distance of a token among n ones can't be higher than
# (n-1)/sqrt(n): a small number of tokens can't have any of them further
# than the default threshold of 3 standard deviations.
NB_TOKENS = 40

# ---------------------------------------------------------------------------


def create_tiers(tokens, method_names=("burg",)):
    """Return the tiers with the F1 and F2 values of the given tokens.

    :param tokens: (list) List of (duration, F1 values, F2 values)
    :param method_names: (tuple) Name of the estimation methods
    :return: (sppasTier, sppasTier)

    """
    tier_f1 = sppasTier("F1")
    tier_f2 = sppasTier("F2")
    for i, name in enumerate(method_names):
        tier_f1.set_meta("formants_estimator_method_{:d}".format(i), name)

    for i, (duration, values_f1, values_f2) in enumerate(tokens):
        begin = 1. + (0.2 * i)
        location = sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(begin + duration)))

        label_f1 = sppasLabel([sppasTag(int(v), "int") for v in values_f1])
        label_f1.set_key("a")
        tier_f1.create_annotation(location, [label_f1])

        label_f2 = sppasLabel([sppasTag(int(v), "int") for v in values_f2])
        label_f2.set_key("a")
        tier_f2.create_annotation(location.copy(), [label_f2])

    return tier_f1, tier_f2

# ---------------------------------------------------------------------------


def create_tokens(nb_tokens):
    """Return a list of (duration, [F1], [F2]) of expected values of a vowel."""
    tokens = list()
    for i in range(nb_tokens):
        tokens.append((0.070 + 0.001 * (i % 7),
                       [690. + 3. * (i % 11)],
                       [1280. + 5. * (i % 13)]))

    return tokens

# ---------------------------------------------------------------------------


class TestVowelFilterEstimator(unittest.TestCase):
    """Test of the estimator of the erroneous formant values.

    """

    def test_threshold(self):
        estimator = VowelFilterEstimator()
        self.assertEqual(3., estimator.get_threshold())

        estimator = VowelFilterEstimator(2.5)
        self.assertEqual(2.5, estimator.get_threshold())

        with self.assertRaises(ValueError):
            estimator.set_threshold(-1.)
        with self.assertRaises(TypeError):
            estimator.set_threshold("2.5")

    # -----------------------------------------------------------------------

    def test_get_method_names(self):
        tier_f1, tier_f2 = create_tiers(create_tokens(2))
        self.assertEqual(("burg",), VowelFilterEstimator.get_method_names(tier_f1))

        # No metadata: the number of values is the number of methods
        self.assertEqual(("method_0",), VowelFilterEstimator.get_method_names(tier_f2))

    # -----------------------------------------------------------------------

    def test_collect(self):
        tier_f1, tier_f2 = create_tiers(create_tokens(NB_TOKENS))
        estimator = VowelFilterEstimator()

        self.assertEqual(NB_TOKENS, estimator.collect(tier_f1, tier_f2))
        self.assertEqual(("a",), estimator.get_class_names())
        self.assertEqual(1, estimator.estimate())

    # -----------------------------------------------------------------------

    def test_collect_invalid_tiers(self):
        tier_f1, tier_f2 = create_tiers(create_tokens(NB_TOKENS))
        tier_f2.pop(0)

        estimator = VowelFilterEstimator()
        with self.assertRaises(ValueError):
            estimator.collect(tier_f1, tier_f2)

    # -----------------------------------------------------------------------

    def test_filter(self):
        tokens = create_tokens(NB_TOKENS)
        # An erroneous token: F1 and F2 are inverted
        tokens.append((0.073, [1800.], [600.]))
        tier_f1, tier_f2 = create_tiers(tokens)

        estimator = VowelFilterEstimator()
        estimator.collect(tier_f1, tier_f2)
        estimator.estimate()
        new_f1, new_f2, distances = estimator.filter(tier_f1, tier_f2)

        self.assertEqual(NB_TOKENS + 1, estimator.get_nb_values())
        self.assertEqual(1, estimator.get_nb_filtered())

        # Only one method: the erroneous token has no remaining value, so
        # that no annotation is created for it.
        self.assertEqual(NB_TOKENS, len(new_f1))
        self.assertEqual(NB_TOKENS, len(new_f2))
        self.assertEqual(NB_TOKENS, len(distances))

        # The metadata of the source tiers are copied
        self.assertEqual("burg", new_f1.get_meta("formants_estimator_method_0"))

    # -----------------------------------------------------------------------

    def test_filter_without_distributions(self):
        # Not enough tokens to estimate a distribution: nothing is filtered
        tokens = create_tokens(2)
        tokens.append((0.073, [1800.], [600.]))
        tier_f1, tier_f2 = create_tiers(tokens)

        estimator = VowelFilterEstimator()
        estimator.collect(tier_f1, tier_f2)
        self.assertEqual(0, estimator.estimate())

        new_f1, new_f2, distances = estimator.filter(tier_f1, tier_f2)
        self.assertEqual(3, len(new_f1))
        self.assertEqual(0, estimator.get_nb_filtered())
        self.assertEqual(-1., distances[2].get_labels()[0][0][0].get_typed_content())
