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
        self.assertEqual(0, profiles.get_nb_tokens("spk1", "a", "burg"))

        profiles.add_token("spk1", "a", "burg", self.vectors[0])
        self.assertEqual(1, profiles.get_nb_tokens("spk1", "a", "burg"))
        self.assertEqual(0, profiles.get_nb_tokens("spk1", "a", "praat_burg"))
        self.assertEqual(0, profiles.get_nb_tokens("spk1", "i", "burg"))
        self.assertEqual(("a",), profiles.get_class_names())

        # A profile is not estimated when adding a token
        self.assertEqual(0, len(profiles))

        with self.assertRaises(ValueError):
            profiles.add_token("spk1", "a", "burg", list())

    # -----------------------------------------------------------------------

    def test_min_tokens(self):
        profiles = VowelProfiles()
        self.assertEqual(VowelProfiles.MIN_TOKENS, profiles.get_min_tokens())

        profiles = VowelProfiles(5)
        self.assertEqual(5, profiles.get_min_tokens())
        profiles.set_min_tokens(VowelProfiles.LOWEST_MIN_TOKENS)
        self.assertEqual(VowelProfiles.LOWEST_MIN_TOKENS, profiles.get_min_tokens())

        with self.assertRaises(ValueError):
            profiles.set_min_tokens(VowelProfiles.LOWEST_MIN_TOKENS - 1)
        with self.assertRaises(TypeError):
            profiles.set_min_tokens(3.5)

    # -----------------------------------------------------------------------

    def test_estimate_not_enough_tokens(self):
        # The class has less tokens than the required number of them
        profiles = VowelProfiles(len(self.vectors) + 1)
        for vector in self.vectors:
            profiles.add_token("spk1", "a", "burg", vector)

        self.assertEqual(0, profiles.estimate())
        self.assertIsNone(profiles.get_distance("spk1", "a", "burg", self.vectors[0]))

    # -----------------------------------------------------------------------

    def test_estimate_not_enough_tokens_for_the_dimensions(self):
        # As many tokens as the dimensions of the space: the covariance
        # matrix is singular, whatever the required number of tokens.
        profiles = VowelProfiles(VowelProfiles.LOWEST_MIN_TOKENS)
        for vector in self.vectors[:3]:
            profiles.add_token("spk1", "a", "burg", vector)

        self.assertEqual(0, profiles.estimate())
        self.assertIsNone(profiles.get_distance("spk1", "a", "burg", self.vectors[0]))

    # -----------------------------------------------------------------------

    def test_estimate_singular_matrix(self):
        # All the tokens are identical: the covariance matrix is singular
        profiles = VowelProfiles()
        for i in range(VowelProfiles.MIN_TOKENS + 2):
            profiles.add_token("spk1", "a", "burg", [0.080, 700., 1300.])

        self.assertEqual(0, profiles.estimate())
        self.assertIsNone(profiles.get_distance("spk1", "a", "burg", self.vectors[0]))

    # -----------------------------------------------------------------------

    def test_get_distance(self):
        profiles = VowelProfiles()
        for vector in self.vectors:
            profiles.add_token("spk1", "a", "burg", vector)
        self.assertEqual(1, profiles.estimate())

        # A token far from the expected values of its class
        far = profiles.get_distance("spk1", "a", "burg", [0.080, 300., 2500.])
        # A token close to the expected values of its class
        close = profiles.get_distance("spk1", "a", "burg", [0.080, 700., 1300.])
        self.assertGreater(far, close)

        # No distance if the class or the method is unknown
        self.assertIsNone(profiles.get_distance("spk1", "i", "burg", self.vectors[0]))
        self.assertIsNone(profiles.get_distance("spk1", "a", "autocorrelation", self.vectors[0]))

        # The dimension of the vector must match the one of the profile
        with self.assertRaises(ValueError):
            profiles.get_distance("spk1", "a", "burg", [700., 1300.])

    # -----------------------------------------------------------------------

    def test_estimate_each_file(self):
        # A file is a speech style of a speaker: distributions are not
        # shared by the files, even for the same class and method.
        profiles = VowelProfiles()
        for vector in self.vectors:
            profiles.add_token("spk1", "a", "burg", vector)
            profiles.add_token("spk2", "a", "burg", [vector[0], vector[1] + 200., vector[2]])

        self.assertEqual(2, profiles.estimate())
        self.assertEqual(("a",), profiles.get_class_names())
        self.assertEqual(len(self.vectors), profiles.get_nb_tokens("spk1", "a", "burg"))

        vector = [0.080, 900., 1300.]
        self.assertGreater(profiles.get_distance("spk1", "a", "burg", vector),
                           profiles.get_distance("spk2", "a", "burg", vector))

    # -----------------------------------------------------------------------

    def test_estimate_each_method(self):
        # Distributions are not shared by the methods
        profiles = VowelProfiles()
        for vector in self.vectors:
            profiles.add_token("spk1", "a", "burg", vector)
            profiles.add_token("spk1", "a", "autocorrelation", [vector[0], vector[1] + 200., vector[2]])

        self.assertEqual(2, profiles.estimate())
        self.assertEqual(("a",), profiles.get_class_names())

        vector = [0.080, 900., 1300.]
        self.assertGreater(profiles.get_distance("spk1", "a", "burg", vector),
                           profiles.get_distance("spk1", "a", "autocorrelation", vector))
