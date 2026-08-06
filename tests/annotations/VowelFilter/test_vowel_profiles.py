"""
:filename: tests.annotations.VowelFilter.test_vowel_profiles.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the feature distributions of the vowels.

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

from sppas.src.annotations.VowelFilter.vowel_profiles import VowelProfiles

# ---------------------------------------------------------------------------


class TestVowelProfiles(unittest.TestCase):
    """Test of the distributions of the acoustic features of the vowels.

    """

    def setUp(self):
        # Tokens of the class "a" of the method "burg": duration, F1, F2.
        self.vectors = [
            [0.080, 700., 1300.],
            [0.090, 715., 1350.],
            [0.070, 690., 1250.],
            [0.085, 705., 1310.],
            [0.075, 710., 1290.]
        ]

    # -----------------------------------------------------------------------

    def test_add_token(self):
        profiles = VowelProfiles()
        self.assertEqual(0, len(profiles))
        self.assertEqual(0, profiles.get_nb_tokens("a", "burg"))

        profiles.add_token("a", "burg", self.vectors[0])
        self.assertEqual(1, profiles.get_nb_tokens("a", "burg"))
        self.assertEqual(0, profiles.get_nb_tokens("a", "praat_burg"))
        self.assertEqual(0, profiles.get_nb_tokens("i", "burg"))
        self.assertEqual(("a",), profiles.get_class_names())

        # A profile is not estimated when adding a token
        self.assertEqual(0, len(profiles))

        with self.assertRaises(ValueError):
            profiles.add_token("a", "burg", list())

    # -----------------------------------------------------------------------

    def test_estimate_not_enough_tokens(self):
        profiles = VowelProfiles()
        for vector in self.vectors[:VowelProfiles.MIN_TOKENS-1]:
            profiles.add_token("a", "burg", vector)

        self.assertEqual(0, profiles.estimate())
        self.assertIsNone(profiles.get_distance("a", "burg", self.vectors[0]))

    # -----------------------------------------------------------------------

    def test_estimate_singular_matrix(self):
        # All the tokens are identical: the covariance matrix is singular
        profiles = VowelProfiles()
        for i in range(VowelProfiles.MIN_TOKENS + 1):
            profiles.add_token("a", "burg", [0.080, 700., 1300.])

        self.assertEqual(0, profiles.estimate())
        self.assertIsNone(profiles.get_distance("a", "burg", self.vectors[0]))

    # -----------------------------------------------------------------------

    def test_get_distance(self):
        profiles = VowelProfiles()
        for vector in self.vectors:
            profiles.add_token("a", "burg", vector)
        self.assertEqual(1, profiles.estimate())

        # A token far from the expected values of its class
        far = profiles.get_distance("a", "burg", [0.080, 300., 2500.])
        # A token close to the expected values of its class
        close = profiles.get_distance("a", "burg", [0.080, 700., 1300.])
        self.assertGreater(far, close)

        # No distance if the class or the method is unknown
        self.assertIsNone(profiles.get_distance("i", "burg", self.vectors[0]))
        self.assertIsNone(profiles.get_distance("a", "autocorrelation", self.vectors[0]))

        # The dimension of the vector must match the one of the profile
        with self.assertRaises(ValueError):
            profiles.get_distance("a", "burg", [700., 1300.])

    # -----------------------------------------------------------------------

    def test_estimate_each_method(self):
        # Distributions are not shared by the methods
        profiles = VowelProfiles()
        for vector in self.vectors:
            profiles.add_token("a", "burg", vector)
            profiles.add_token("a", "autocorrelation", [vector[0], vector[1] + 200., vector[2]])

        self.assertEqual(2, profiles.estimate())
        self.assertEqual(("a",), profiles.get_class_names())

        vector = [0.080, 900., 1300.]
        self.assertGreater(profiles.get_distance("a", "burg", vector),
                           profiles.get_distance("a", "autocorrelation", vector))
