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
from sppas.src.annotations.VowelFilter.vowel_profiles import VowelProfiles

# ---------------------------------------------------------------------------

# The Mahalanobis distance of a token among n ones can't be higher than
# (n-1)/sqrt(n): a small number of tokens can't have any of them further
# than the default threshold of 3 standard deviations.
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


def create_tiers(tokens, method_name=None):
    """Return the tiers with the F1 and F2 values of the given tokens.

    The tiers are the ones the Formants annotation is creating for a method,
    or the F1 and F2 ones if no method name is given.

    :param tokens: (list) List of (duration, F1, F2)
    :param method_name: (str) Name of the estimation method, or None
    :return: (sppasTier, sppasTier)

    """
    if method_name is None:
        tier_f1 = sppasTier("F1")
        tier_f2 = sppasTier("F2")
    else:
        tier_f1 = sppasTier("F1-" + method_name)
        tier_f2 = sppasTier("F2-" + method_name)
        tier_f1.set_meta("formants_estimator_method_0", method_name)
        tier_f2.set_meta("formants_estimator_method_0", method_name)

    for i, (duration, f1, f2) in enumerate(tokens):
        begin = 1. + (0.2 * i)
        location = sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(begin + duration)))

        label_f1 = sppasLabel(sppasTag(int(f1), "int"))
        label_f1.set_key("a")
        tier_f1.create_annotation(location, [label_f1])

        label_f2 = sppasLabel(sppasTag(int(f2), "int"))
        label_f2.set_key("a")
        tier_f2.create_annotation(location.copy(), [label_f2])

    return tier_f1, tier_f2

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

    def test_get_method_name(self):
        tier_f1, tier_f2 = create_tiers(create_tokens(2), "burg")
        self.assertEqual("burg", VowelFilterEstimator.get_method_name(tier_f1))
        self.assertEqual("burg", VowelFilterEstimator.get_method_name(tier_f2))

        # The F1 and F2 tiers of a single method have no name of method
        tier_f1, tier_f2 = create_tiers(create_tokens(2))
        self.assertEqual("", VowelFilterEstimator.get_method_name(tier_f1))

    # -----------------------------------------------------------------------

    def test_collect(self):
        tier_f1, tier_f2 = create_tiers(create_tokens(NB_TOKENS), "burg")
        estimator = VowelFilterEstimator()
        profiles = VowelProfiles()

        self.assertEqual(NB_TOKENS, estimator.collect(profiles, tier_f1, tier_f2))
        self.assertEqual(("a",), profiles.get_class_names())
        self.assertEqual(1, profiles.estimate())

    # -----------------------------------------------------------------------

    def test_collect_unmatched_tiers(self):
        # A token without both of its values is ignored: a method can be
        # reliable for F1 and not for F2 of a given segment.
        tier_f1, tier_f2 = create_tiers(create_tokens(NB_TOKENS), "burg")
        tier_f2.pop(0)

        estimator = VowelFilterEstimator()
        profiles = VowelProfiles()
        self.assertEqual(NB_TOKENS - 1, estimator.collect(profiles, tier_f1, tier_f2))

    # -----------------------------------------------------------------------

    def test_filter(self):
        tokens = create_tokens(NB_TOKENS)
        # An erroneous token: F1 and F2 are inverted
        tokens.append((0.073, 1800., 600.))
        tier_f1, tier_f2 = create_tiers(tokens, "burg")

        estimator = VowelFilterEstimator()
        profiles = VowelProfiles()
        estimator.collect(profiles, tier_f1, tier_f2)
        profiles.estimate()
        new_f1, new_f2, distances = estimator.filter(profiles, tier_f1, tier_f2)

        self.assertEqual(NB_TOKENS + 1, estimator.get_nb_values())
        self.assertEqual(1, estimator.get_nb_filtered())

        # The names of the created tiers are not the ones of the source
        # tiers, so that both the files can be merged.
        self.assertEqual("F1vf-burg", new_f1.get_name())
        self.assertEqual("F2vf-burg", new_f2.get_name())
        self.assertEqual("MahalanobisDist-burg", distances.get_name())

        # The erroneous value is discarded, the expected ones are kept
        self.assertEqual(NB_TOKENS + 1, len(new_f1))
        self.assertEqual(0, new_f1[NB_TOKENS].get_best_tag().get_typed_content())
        self.assertEqual(0, new_f2[NB_TOKENS].get_best_tag().get_typed_content())
        self.assertEqual(1800, tier_f1[NB_TOKENS].get_best_tag().get_typed_content())

        for i, (duration, f1, f2) in enumerate(create_tokens(NB_TOKENS)):
            self.assertEqual(int(f1), new_f1[i].get_best_tag().get_typed_content())
            self.assertEqual(int(f2), new_f2[i].get_best_tag().get_typed_content())

        # The distance of the discarded value explains why it was discarded
        self.assertGreater(distances[NB_TOKENS].get_best_tag().get_typed_content(),
                           estimator.get_threshold())

        # The metadata of the source tiers are copied
        self.assertEqual("burg", new_f1.get_meta("formants_estimator_method_0"))

    # -----------------------------------------------------------------------

    def test_filter_is_method_dependent(self):
        # The same erroneous token, estimated by two methods: it is expected
        # by the 2nd method, whose values are all higher.
        tokens = create_tokens(NB_TOKENS)
        tokens.append((0.073, 1800., 600.))
        tier_f1, tier_f2 = create_tiers(tokens, "burg")

        other_tokens = [(d, f1 + 1100., f2 - 690.) for (d, f1, f2) in create_tokens(NB_TOKENS)]
        other_tokens.append((0.073, 1800., 600.))
        other_f1, other_f2 = create_tiers(other_tokens, "praat_burg")

        estimator = VowelFilterEstimator()
        profiles = VowelProfiles()
        estimator.collect(profiles, tier_f1, tier_f2)
        estimator.collect(profiles, other_f1, other_f2)
        self.assertEqual(2, profiles.estimate())

        new_f1, new_f2, distances = estimator.filter(profiles, tier_f1, tier_f2)
        self.assertEqual(1, estimator.get_nb_filtered())
        self.assertEqual(0, new_f1[NB_TOKENS].get_best_tag().get_typed_content())

        new_f1, new_f2, distances = estimator.filter(profiles, other_f1, other_f2)
        self.assertEqual(0, estimator.get_nb_filtered())
        self.assertEqual(1800, new_f1[NB_TOKENS].get_best_tag().get_typed_content())

    # -----------------------------------------------------------------------

    def test_filter_without_distributions(self):
        # Not enough tokens to estimate a distribution: nothing is filtered
        tokens = create_tokens(2)
        tokens.append((0.073, 1800., 600.))
        tier_f1, tier_f2 = create_tiers(tokens, "burg")

        estimator = VowelFilterEstimator()
        profiles = VowelProfiles(len(tokens) + 1)
        estimator.collect(profiles, tier_f1, tier_f2)
        self.assertEqual(0, profiles.estimate())

        new_f1, new_f2, distances = estimator.filter(profiles, tier_f1, tier_f2)
        self.assertEqual(3, len(new_f1))
        self.assertEqual(0, estimator.get_nb_filtered())
        self.assertEqual(-1., distances[2].get_best_tag().get_typed_content())
