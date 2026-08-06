# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.VowelFilter.vowel_filter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Filtering of the erroneous formant values of a corpus.

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

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from .vowel_classifier import VowelClassifier
from .vowel_profiles import VowelProfiles

# ---------------------------------------------------------------------------


class VowelFilterEstimator:
    """Estimator of the erroneous formant values of a corpus.

    The tokens of all the files are collected, then their feature
    distributions are estimated, then each file can be filtered: a formant
    value is discarded if its token is further than a given number of
    standard deviations from the expected values of its class.

    Estimating the distributions requires a large number of tokens: the
    Mahalanobis distance of a token among n ones can't be higher than
    (n-1)/sqrt(n), so that a small corpus can't have any token further
    than the default threshold of 3 standard deviations.

    :example:
    >>> estimator = VowelFilterEstimator()
    >>> estimator.collect(tier_f1, tier_f2)
    >>> estimator.estimate()
    >>> f1, f2, distances = estimator.filter(tier_f1, tier_f2)

    """

    def __init__(self, threshold: float = 3.):
        """Create a VowelFilterEstimator instance.

        :param threshold: (float) Maximum number of standard deviations

        """
        # Feature distributions of all the collected tokens:
        self.__profiles = VowelProfiles()

        # Maximum distance of a token to the profile of its class:
        self.__threshold = 3.
        self.set_threshold(threshold)

        # Number of estimated and filtered values of the last filtered tiers:
        self.__nb_values = 0
        self.__nb_filtered = 0

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_threshold(self) -> float:
        """Return the maximum distance of a token to the profile."""
        return self.__threshold

    # -----------------------------------------------------------------------

    def set_threshold(self, value: float) -> None:
        """Set the maximum distance of a token to the profile of its class.

        :param value: (float) Number of standard deviations
        :raises: TypeError: Given value is not a number.
        :raises: ValueError: Given value is not a positive number.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError(f"Given value {value} is not a number.")
        if value <= 0.:
            raise ValueError(f"Given value must be a positive number. Got {value} instead.")

        self.__threshold = float(value)

    # -----------------------------------------------------------------------

    def get_class_names(self) -> tuple:
        """Return the names of the classes of the collected tokens."""
        return self.__profiles.get_class_names()

    # -----------------------------------------------------------------------

    def get_nb_values(self) -> int:
        """Return the number of estimated values of the last filtered tiers."""
        return self.__nb_values

    # -----------------------------------------------------------------------

    def get_nb_filtered(self) -> int:
        """Return the number of discarded values of the last filtered tiers."""
        return self.__nb_filtered

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def collect(self, tier_f1: sppasTier, tier_f2: sppasTier, syll_tier: sppasTier = None) -> int:
        """Add the features of the vowels of a file to the distributions.

        :param tier_f1: (sppasTier) Tier with F1 values
        :param tier_f2: (sppasTier) Tier with F2 values
        :param syll_tier: (sppasTier) Tier with time-aligned syllables, or None
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (int) Number of added tokens

        """
        _method_names = VowelFilterEstimator.get_method_names(tier_f1)
        _classifier = VowelClassifier(syll_tier)

        _nb_tokens = 0
        for class_name, vectors in self.__get_tokens(tier_f1, tier_f2, _classifier, _method_names):
            for i, vector in enumerate(vectors):
                if vector is None:
                    continue
                self.__profiles.add_token(class_name, _method_names[i], vector)
                _nb_tokens += 1

        return _nb_tokens

    # -----------------------------------------------------------------------

    def estimate(self) -> int:
        """Estimate the distributions of the collected tokens.

        :return: (int) Number of estimated distributions

        """
        return self.__profiles.estimate()

    # -----------------------------------------------------------------------

    def filter(self, tier_f1: sppasTier, tier_f2: sppasTier, syll_tier: sppasTier = None) -> tuple:
        """Discard the erroneous formant values of a file.

        A value is discarded by assigning it a zero, like the Formants
        annotation is doing when a method didn't estimate any value, so
        that the values of the other methods are preserved.

        :param tier_f1: (sppasTier) Tier with F1 values
        :param tier_f2: (sppasTier) Tier with F2 values
        :param syll_tier: (sppasTier) Tier with time-aligned syllables, or None
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (sppasTier, sppasTier, sppasTier) Filtered F1, F2 and distances

        """
        _method_names = VowelFilterEstimator.get_method_names(tier_f1)
        _classifier = VowelClassifier(syll_tier)
        _new_f1, _new_f2, _distances_tier = VowelFilterEstimator.__create_tiers(tier_f1, tier_f2)

        self.__nb_values = 0
        self.__nb_filtered = 0

        _tokens = self.__get_tokens(tier_f1, tier_f2, _classifier, _method_names)
        for i, (class_name, vectors) in enumerate(_tokens):
            if len(vectors) == 0:
                continue

            _values_f1, _values_f2, _distances = self.__filter_token(class_name, vectors, _method_names)
            VowelFilterEstimator.__append_annotations(
                _new_f1, _new_f2, _distances_tier, tier_f1[i], tier_f2[i],
                _values_f1, _values_f2, _distances)

        return _new_f1, _new_f2, _distances_tier

    # -----------------------------------------------------------------------

    @staticmethod
    def get_method_names(tier: sppasTier) -> tuple:
        """Return the name of the method of each value of the annotations.

        The Formants annotation is storing the names of its enabled methods
        into the metadata of the tier, and one value of each of them into
        the labels of its annotations.

        :param tier: (sppasTier) Tier with formant values
        :return: (tuple) Name of the method of each value

        """
        _names = list()
        i = 0
        _name = tier.get_meta("formants_estimator_method_0", default="")
        while len(_name) > 0:
            _names.append(_name)
            i += 1
            _name = tier.get_meta("formants_estimator_method_{:d}".format(i), default="")

        if len(_names) == 0:
            # The tier was not created by the Formants annotation. The number
            # of values of an annotation is then the number of methods.
            for ann in tier:
                _labels = ann.get_labels()
                if len(_labels) > 0:
                    _names = ["method_{:d}".format(j) for j in range(len(_labels[0]))]
                    break

        return tuple(_names)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __filter_token(self, class_name: str, vectors: list, method_names: tuple) -> tuple:
        """Return the kept values and the distance of a token, for each method.

        :param class_name: (str) Name of the vowel class of the token
        :param vectors: (list) Feature vector of each method, or None
        :param method_names: (tuple) Name of the method of each value
        :return: (list, list, list) F1 values, F2 values and distances

        """
        _values_f1 = list()
        _values_f2 = list()
        _distances = list()

        for i, vector in enumerate(vectors):
            _f1, _f2, _distance = self.__filter_value(class_name, method_names[i], vector)
            _values_f1.append(_f1)
            _values_f2.append(_f2)
            _distances.append(_distance)

        return _values_f1, _values_f2, _distances

    # -----------------------------------------------------------------------

    def __filter_value(self, class_name: str, method_name: str, vector: list) -> tuple:
        """Return the kept values and the distance of a token of a method.

        :param class_name: (str) Name of the vowel class of the token
        :param method_name: (str) Name of the method the features come from
        :param vector: (list) Feature vector of the method, or None
        :return: (int, int, float) F1 value, F2 value and distance

        """
        if vector is None:
            # The method didn't estimate any value for this token.
            return 0, 0, -1.

        self.__nb_values += 1
        _distance = self.__profiles.get_distance(class_name, method_name, vector)

        if _distance is None:
            # No distribution to compare this token with.
            return int(vector[1]), int(vector[2]), -1.

        if _distance > self.__threshold:
            self.__nb_filtered += 1
            return 0, 0, round(_distance, 3)

        return int(vector[1]), int(vector[2]), round(_distance, 3)

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_tokens(tier_f1: sppasTier, tier_f2: sppasTier, classifier: VowelClassifier,
                     method_names: tuple) -> list:
        """Return the class name and the feature vectors of each token.

        A token has one feature vector for each method: its duration, its F1
        and its F2 values. The vector of a method is None if this latter
        didn't estimate any value for the token.

        :param tier_f1: (sppasTier) Tier with F1 values
        :param tier_f2: (sppasTier) Tier with F2 values
        :param classifier: (VowelClassifier) To get the class of the tokens
        :param method_names: (tuple) Name of the method of each value
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (list) List of (class name, list of vectors)

        """
        if len(tier_f1) != len(tier_f2):
            raise ValueError("Expected the same number of F1 and F2 values. "
                             "Got {:d} and {:d} instead."
                             "".format(len(tier_f1), len(tier_f2)))

        _tokens = list()

        for ann_f1, ann_f2 in zip(tier_f1, tier_f2):
            _vectors = VowelFilterEstimator.__get_vectors(ann_f1, ann_f2, len(method_names))
            if len(_vectors) == 0:
                _tokens.append(("", list()))
            else:
                _tokens.append((classifier.get_class(ann_f1), _vectors))

        return _tokens

    # -----------------------------------------------------------------------

    @staticmethod
    def __is_valid_token(ann_f1, ann_f2, nb_methods: int) -> bool:
        """Return True if each value of a token can be assigned to its method.

        :param ann_f1: (sppasAnnotation) Annotation with the F1 values
        :param ann_f2: (sppasAnnotation) Annotation with the F2 values
        :param nb_methods: (int) Expected number of values
        :return: (bool)

        """
        _labels_f1 = ann_f1.get_labels()
        _labels_f2 = ann_f2.get_labels()
        if len(_labels_f1) == 0 or len(_labels_f2) == 0:
            return False

        # Two methods sharing the same value are stored into a single tag,
        # so that no value can be assigned to its method.
        if len(_labels_f1[0]) != nb_methods or len(_labels_f2[0]) != nb_methods:
            logging.warning("Ignored the token at {:s}: {:d} values instead of the "
                            "{:d} expected ones."
                            "".format(str(ann_f1.get_location()),
                                      len(_labels_f1[0]), nb_methods))
            return False

        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_vectors(ann_f1, ann_f2, nb_methods: int) -> list:
        """Return the feature vector of each method of a token.

        An empty list is returned if the values of the token can't be
        assigned to their method.

        :param ann_f1: (sppasAnnotation) Annotation with the F1 values
        :param ann_f2: (sppasAnnotation) Annotation with the F2 values
        :param nb_methods: (int) Expected number of values
        :return: (list) Feature vector of each method, or None

        """
        if VowelFilterEstimator.__is_valid_token(ann_f1, ann_f2, nb_methods) is False:
            return list()

        _labels_f1 = ann_f1.get_labels()
        _labels_f2 = ann_f2.get_labels()
        _duration = (ann_f1.get_highest_localization().get_midpoint() -
                     ann_f1.get_lowest_localization().get_midpoint())

        _vectors = list()
        for (tag_f1, score_f1), (tag_f2, score_f2) in zip(_labels_f1[0], _labels_f2[0]):
            _f1 = tag_f1.get_typed_content()
            _f2 = tag_f2.get_typed_content()
            # A value of zero is the one the Formants annotation is
            # assigning when a method didn't estimate any value.
            if _f1 == 0 or _f2 == 0:
                _vectors.append(None)
            else:
                _vectors.append([_duration, float(_f1), float(_f2)])

        return _vectors

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_tiers(tier_f1: sppasTier, tier_f2: sppasTier) -> tuple:
        """Return the three tiers of the result, with the source metadata.

        :param tier_f1: (sppasTier) Tier with F1 values
        :param tier_f2: (sppasTier) Tier with F2 values
        :return: (sppasTier, sppasTier, sppasTier) F1, F2 and distances

        """
        return (VowelFilterEstimator.__create_tier("F1", tier_f1),
                VowelFilterEstimator.__create_tier("F2", tier_f2),
                VowelFilterEstimator.__create_tier("MahalanobisDist", tier_f1))

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_tier(tier_name: str, source_tier: sppasTier) -> sppasTier:
        """Return a new tier with the metadata of the given one.

        :param tier_name: (str) Name of the tier to create
        :param source_tier: (sppasTier) Tier the metadata are copied from
        :return: (sppasTier)

        """
        _tier = sppasTier(tier_name)
        for key in source_tier.get_meta_keys():
            if _tier.get_meta(key, default=None) is None:
                _tier.set_meta(key, source_tier.get_meta(key))
        _tier.set_media(source_tier.get_media())

        return _tier

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_annotations(new_f1: sppasTier, new_f2: sppasTier, distances_tier: sppasTier,
                             ann_f1, ann_f2, values_f1: list, values_f2: list,
                             distances: list) -> None:
        """Append the filtered values of a token to the given tiers.

        Like the Formants annotation does, no annotation is created if none
        of the methods has a value to store.

        """
        _nb_kept = 0
        for value_f1, value_f2 in zip(values_f1, values_f2):
            if value_f1 != 0 and value_f2 != 0:
                _nb_kept += 1
        if _nb_kept == 0:
            return

        _phoneme = ann_f1.get_labels()[0].get_key()

        _label_f1 = sppasLabel([sppasTag(v, "int") for v in values_f1])
        _label_f1.set_key(_phoneme)
        new_f1.create_annotation(ann_f1.get_location().copy(), [_label_f1])

        _label_f2 = sppasLabel([sppasTag(v, "int") for v in values_f2])
        _label_f2.set_key(_phoneme)
        new_f2.create_annotation(ann_f2.get_location().copy(), [_label_f2])

        _label_distances = sppasLabel([sppasTag(d, "float") for d in distances])
        _label_distances.set_key(_phoneme)
        distances_tier.create_annotation(ann_f1.get_location().copy(), [_label_distances])
