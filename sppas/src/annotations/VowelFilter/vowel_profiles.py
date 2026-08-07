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
from sppas.src.calculus import lunbiasedcovariance
from sppas.src.calculus import mahalanobis
from sppas.src.calculus.calculusexc import VectorsError

# ---------------------------------------------------------------------------


class VowelProfiles:
    """Feature distributions of the vowels, one for each class and method.

    A profile is the mean vector and the covariance matrix of the feature
    vectors of all the tokens sharing the same file, the same vowel class and
    the same estimation method. A file is a speech style of a speaker, and
    distributions are not comparable from a method to another one: a profile
    is then estimated for each file, class and method.

    Profiles are estimated on a whole set of tokens, then the distance of
    any token to the profile of its class is the number of standard
    deviations between the token and the expected values of the class.

    A class requires a minimum number of tokens to be estimated. Whatever
    this given number, a class with no more tokens than the dimensions of
    the space has no profile: its covariance matrix can't be inverted.

    :example:
    >>> profiles = VowelProfiles()
    >>> profiles.add_token("a", "burg", [0.08, 700., 1300.])
    >>> profiles.estimate()
    >>> profiles.get_distance("a", "burg", [0.08, 900., 1300.])

    """

    # Default number of tokens a class requires to estimate its profile
    MIN_TOKENS = 3

    # A profile can't be estimated with less tokens than this value
    LOWEST_MIN_TOKENS = 2

    # -----------------------------------------------------------------------

    def __init__(self, min_tokens: int = MIN_TOKENS):
        """Create a VowelProfiles instance without any token.

        :param min_tokens: (int) Number of tokens a class requires

        """
        # Feature vectors of the tokens. Key is (class name, method name):
        self.__vectors = dict()

        # Mean vector and covariance matrix. Key is (class name, method name):
        self.__profiles = dict()

        # Number of tokens a class requires to estimate its profile:
        self.__min_tokens = VowelProfiles.MIN_TOKENS
        self.set_min_tokens(min_tokens)

    # -----------------------------------------------------------------------

    def get_min_tokens(self) -> int:
        """Return the number of tokens a class requires to be estimated."""
        return self.__min_tokens

    # -----------------------------------------------------------------------

    def set_min_tokens(self, value: int) -> None:
        """Set the number of tokens a class requires to estimate its profile.

        :param value: (int) Number of tokens, at least 2
        :raises: TypeError: Given value is not an integer.
        :raises: ValueError: Given value is lower than the lowest accepted one.

        """
        self.__min_tokens = VowelProfiles.check_min_tokens(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def check_min_tokens(value: int) -> int:
        """Return the given number of tokens if a profile can be estimated with.

        :param value: (int) Number of tokens, at least 2
        :raises: TypeError: Given value is not an integer.
        :raises: ValueError: Given value is lower than the lowest accepted one.
        :return: (int) The given number of tokens

        """
        if isinstance(value, int) is False:
            raise TypeError(f"Given value {value} is not an integer.")
        if value < VowelProfiles.LOWEST_MIN_TOKENS:
            raise ValueError(f"Given value must be at least "
                             f"{VowelProfiles.LOWEST_MIN_TOKENS}. Got {value} instead.")

        return value

    # -----------------------------------------------------------------------

    def add_token(self, file_id: str, class_name: str, method_name: str, vector: list) -> None:
        """Add the feature vector of a token of the given file, class and method.

        :param file_id: (str) Identifier of the file the token comes from
        :param class_name: (str) Name of the vowel class of the token
        :param method_name: (str) Name of the method the features come from
        :param vector: (list) Feature values of the token
        :raises: ValueError: The given vector is empty

        """
        if len(vector) == 0:
            raise ValueError("A non-empty vector of features was expected.")

        _key = (file_id, class_name, method_name)
        if _key not in self.__vectors:
            self.__vectors[_key] = list()
        self.__vectors[_key].append(vector)

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
            _file_id, _class_name, _method_name = key
            _profile = self.__estimate_profile(self.__vectors[key])
            if _profile is None:
                logging.info(f"No profile for the class {_class_name} of the method "
                             f"{_method_name} in {_file_id}.")
                continue

            self.__profiles[key] = _profile

        return len(self.__profiles)

    # -----------------------------------------------------------------------

    def __are_enough(self, vectors: list) -> bool:
        """Return True if the vectors can estimate a profile of their class.

        :param vectors: (list) Feature vectors of the tokens of a class
        :return: (bool)

        """
        if len(vectors) < self.__min_tokens:
            logging.info("{:d} tokens only.".format(len(vectors)))
            return False

        # The covariance matrix of a space of d dimensions is singular with
        # d vectors or less. Inverting it then returns rounding errors instead
        # of raising an error, so that the estimated distances are meaningless.
        _dimension = len(vectors[0])
        if len(vectors) <= _dimension:
            logging.info("{:d} tokens only for a space of {:d} dimensions."
                         "".format(len(vectors), _dimension))
            return False

        return True

    # -----------------------------------------------------------------------

    def __estimate_profile(self, vectors: list) -> tuple:
        """Return the mean vector and the covariance matrix of the vectors.

        Nothing is returned if there's not enough vectors or if their
        covariance matrix is singular, i.e. it can't be inverted. Such a
        matrix of a space of d dimensions requires at least d+1 vectors.

        :param vectors: (list) Feature vectors of the tokens of a class
        :return: (tuple|None) Mean vector and covariance matrix

        """
        if self.__are_enough(vectors) is False:
            return None

        _dimension = len(vectors[0])
        _mean = [fmean([vector[i] for vector in vectors]) for i in range(_dimension)]
        _covariance = lunbiasedcovariance(vectors)

        try:
            mahalanobis(_mean, _mean, _covariance)
        except VectorsError:
            logging.info("The covariance matrix is singular.")
            return None

        return _mean, _covariance

    # -----------------------------------------------------------------------

    def get_distance(self, file_id: str, class_name: str, method_name: str, vector: list) -> float:
        """Return the distance of a token to the profile of its class.

        The returned distance is the number of standard deviations between
        the given features and the mean ones of the class.

        :param file_id: (str) Identifier of the file the token comes from
        :param class_name: (str) Name of the vowel class of the token
        :param method_name: (str) Name of the method the features come from
        :param vector: (list) Feature values of the token
        :raises: ValueError: The dimension of the vector does not match the profile
        :return: (float|None) Distance to the profile, or None if no profile

        """
        _key = (file_id, class_name, method_name)
        if _key not in self.__profiles:
            return None

        _mean, _covariance = self.__profiles[_key]
        if len(vector) != len(_mean):
            raise ValueError("Expected a vector of dimension {:d}. Got {:d} instead."
                             "".format(len(_mean), len(vector)))

        # The covariance matrix is invertible, but it can be ill-conditioned:
        # the distance of a token is then not reliable enough to be used.
        try:
            return mahalanobis(vector, _mean, _covariance)
        except VectorsError:
            logging.info(f"No reliable distance for a token of the class "
                         f"{class_name} of the method {method_name} in {file_id}.")

        return None

    # -----------------------------------------------------------------------

    def get_nb_tokens(self, file_id: str, class_name: str, method_name: str) -> int:
        """Return the number of added tokens of a file, a class and a method.

        :param file_id: (str) Identifier of the file the tokens come from
        :param class_name: (str) Name of the vowel class of the tokens
        :param method_name: (str) Name of the method the features come from
        :return: (int)

        """
        _key = (file_id, class_name, method_name)
        if _key not in self.__vectors:
            return 0

        return len(self.__vectors[_key])

    # -----------------------------------------------------------------------

    def get_class_names(self) -> tuple:
        """Return the sorted names of the classes with at least one token."""
        _names = list()
        for file_id, class_name, method_name in self.__vectors:
            if class_name not in _names:
                _names.append(class_name)

        return tuple(sorted(_names))

    # -----------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of estimated profiles."""
        return len(self.__profiles)
