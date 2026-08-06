# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.VowelFilter.vowel_profiles.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Distributions of the acoustic features of the vowels of a corpus.

.. _This file is part of SPPAS: <https://sppas.org/>
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

from __future__ import annotations
import logging

from sppas.src.calculus import fmean
from sppas.src.calculus import lcovariance
from sppas.src.calculus import mahalanobis
from sppas.src.calculus.calculusexc import VectorsError

# ---------------------------------------------------------------------------


class VowelProfiles:
    """Feature distributions of the vowels, one for each class and method.

    A profile is the mean vector and the covariance matrix of the feature
    vectors of all the tokens sharing both the same vowel class and the same
    estimation method. Distributions are not comparable from a method to
    another one: an estimation method has its own profile of each class.

    Profiles are estimated on a whole set of tokens, then the distance of
    any token to the profile of its class is the number of standard
    deviations between the token and the expected values of the class.

    :example:
    >>> profiles = VowelProfiles()
    >>> profiles.add_token("a", "burg", [0.08, 700., 1300.])
    >>> profiles.estimate()
    >>> profiles.get_distance("a", "burg", [0.08, 900., 1300.])

    """

    # Minimum number of tokens to estimate a profile. The covariance matrix
    # of a space of d dimensions is singular with less than d+1 observations.
    MIN_TOKENS = 4

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a VowelProfiles instance without any token."""
        # Feature vectors of the tokens. Key is (class name, method name):
        self.__vectors = dict()

        # Mean vector and covariance matrix. Key is (class name, method name):
        self.__profiles = dict()

    # -----------------------------------------------------------------------

    def add_token(self, class_name: str, method_name: str, vector: list) -> None:
        """Add the feature vector of a token of the given class and method.

        :param class_name: (str) Name of the vowel class of the token
        :param method_name: (str) Name of the method the features come from
        :param vector: (list) Feature values of the token
        :raises: ValueError: The given vector is empty

        """
        if len(vector) == 0:
            raise ValueError("A non-empty vector of features was expected.")

        key = (class_name, method_name)
        if key not in self.__vectors:
            self.__vectors[key] = list()
        self.__vectors[key].append(vector)

    # -----------------------------------------------------------------------

    def estimate(self) -> int:
        """Estimate the profile of each class and each method.

        A profile is estimated only if the class has enough tokens and if
        their covariance matrix can be inverted. No profile means that no
        distance can be estimated, so that no token of the class is filtered.

        :return: (int) Number of estimated profiles

        """
        self.__profiles = dict()

        for key in self.__vectors:
            class_name, method_name = key
            vectors = self.__vectors[key]

            if len(vectors) < VowelProfiles.MIN_TOKENS:
                logging.info(f"No profile for the class {class_name} of the method "
                             f"{method_name}: {len(vectors)} tokens only.")
                continue

            dimension = len(vectors[0])
            mean = [fmean([vector[i] for vector in vectors]) for i in range(dimension)]
            covariance = lcovariance(vectors)

            # A singular covariance matrix can't be inverted, so no distance
            # can be estimated with such a profile.
            try:
                mahalanobis(mean, mean, covariance)
            except VectorsError:
                logging.info(f"No profile for the class {class_name} of the method "
                             f"{method_name}: the covariance matrix is singular.")
                continue

            self.__profiles[key] = (mean, covariance)

        return len(self.__profiles)

    # -----------------------------------------------------------------------

    def get_distance(self, class_name: str, method_name: str, vector: list) -> float:
        """Return the distance of a token to the profile of its class.

        The returned distance is the number of standard deviations between
        the given features and the mean ones of the class.

        :param class_name: (str) Name of the vowel class of the token
        :param method_name: (str) Name of the method the features come from
        :param vector: (list) Feature values of the token
        :raises: ValueError: The dimension of the vector does not match the profile
        :return: (float|None) Distance to the profile, or None if no profile

        """
        key = (class_name, method_name)
        if key not in self.__profiles:
            return None

        mean, covariance = self.__profiles[key]
        if len(vector) != len(mean):
            raise ValueError("Expected a vector of dimension {:d}. Got {:d} instead."
                             "".format(len(mean), len(vector)))

        return mahalanobis(vector, mean, covariance)

    # -----------------------------------------------------------------------

    def get_nb_tokens(self, class_name: str, method_name: str) -> int:
        """Return the number of added tokens of a class and a method.

        :param class_name: (str) Name of the vowel class of the tokens
        :param method_name: (str) Name of the method the features come from
        :return: (int)

        """
        key = (class_name, method_name)
        if key not in self.__vectors:
            return 0

        return len(self.__vectors[key])

    # -----------------------------------------------------------------------

    def get_class_names(self) -> tuple:
        """Return the sorted names of the classes with at least one token."""
        names = list()
        for class_name, method_name in self.__vectors:
            if class_name not in names:
                names.append(class_name)

        return tuple(sorted(names))

    # -----------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of estimated profiles."""
        return len(self.__profiles)
