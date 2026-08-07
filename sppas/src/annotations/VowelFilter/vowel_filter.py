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
        """Add the features of the vowels of a pair of tiers to the distributions.

        :param tier_f1: (sppasTier) Tier with the F1 values of a method
        :param tier_f2: (sppasTier) Tier with the F2 values of a method
        :param syll_tier: (sppasTier) Tier with time-aligned syllables, or None
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (int) Number of added tokens

        """
        _method_name = VowelFilterEstimator.get_method_name(tier_f1)
        _classifier = VowelClassifier(syll_tier)

        _nb_tokens = 0
        for class_name, vector in self.__get_tokens(tier_f1, tier_f2, _classifier):
            if vector is None:
                continue
            self.__profiles.add_token(class_name, _method_name, vector)
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
        """Discard the erroneous formant values of a pair of tiers.

        A value is discarded by assigning it a zero, like the Formants
        annotation is doing when a method didn't estimate any value.

        :param tier_f1: (sppasTier) Tier with the F1 values of a method
        :param tier_f2: (sppasTier) Tier with the F2 values of a method
        :param syll_tier: (sppasTier) Tier with time-aligned syllables, or None
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (sppasTier, sppasTier, sppasTier) Filtered F1, F2 and distances

        """
        _method_name = VowelFilterEstimator.get_method_name(tier_f1)
        _classifier = VowelClassifier(syll_tier)
        _new_f1, _new_f2, _distances_tier = VowelFilterEstimator.__create_tiers(tier_f1, tier_f2)

        self.__nb_values = 0
        self.__nb_filtered = 0

        _tokens = self.__get_tokens(tier_f1, tier_f2, _classifier)
        for i, (class_name, vector) in enumerate(_tokens):
            if vector is None:
                continue

            _f1, _f2, _distance = self.__filter_value(class_name, _method_name, vector)
            VowelFilterEstimator.__append_annotations(
                _new_f1, _new_f2, _distances_tier, tier_f1[i], tier_f2[i], _f1, _f2, _distance)

        return _new_f1, _new_f2, _distances_tier

    # -----------------------------------------------------------------------

    @staticmethod
    def get_method_name(tier: sppasTier) -> str:
        """Return the name of the estimation method of the given tier.

        The Formants annotation is naming the tier of a method after this
        latter, i.e. "F1-burg", and it is also storing this name into the
        metadata of the tier.

        :param tier: (sppasTier) Tier with the formant values of a method
        :return: (str) Name of the method, or an empty string

        """
        _name = tier.get_name()
        if _name.startswith("F1-") is True or _name.startswith("F2-") is True:
            return _name[3:]

        return tier.get_meta("formants_estimator_method_0", default="")

    # -----------------------------------------------------------------------
    # Private
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
    def __get_tokens(tier_f1: sppasTier, tier_f2: sppasTier, classifier: VowelClassifier) -> list:
        """Return the class name and the feature vector of each token.

        The feature vector of a token is its duration, its F1 and its F2
        values. It is None if the method didn't estimate any value.

        :param tier_f1: (sppasTier) Tier with the F1 values of a method
        :param tier_f2: (sppasTier) Tier with the F2 values of a method
        :param classifier: (VowelClassifier) To get the class of the tokens
        :raises: ValueError: The tiers don't have the same number of annotations
        :return: (list) List of (class name, vector)

        """
        if len(tier_f1) != len(tier_f2):
            raise ValueError("Expected the same number of F1 and F2 values. "
                             "Got {:d} and {:d} instead."
                             "".format(len(tier_f1), len(tier_f2)))

        _tokens = list()

        for ann_f1, ann_f2 in zip(tier_f1, tier_f2):
            _vector = VowelFilterEstimator.__get_vector(ann_f1, ann_f2)
            if _vector is None:
                _tokens.append(("", None))
            else:
                _tokens.append((classifier.get_class(ann_f1), _vector))

        return _tokens

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_vector(ann_f1, ann_f2) -> list:
        """Return the feature vector of a token: duration, F1 and F2 values.

        :param ann_f1: (sppasAnnotation) Annotation with the F1 value
        :param ann_f2: (sppasAnnotation) Annotation with the F2 value
        :return: (list|None) Feature vector, or None if there's no value

        """
        _labels_f1 = ann_f1.get_labels()
        _labels_f2 = ann_f2.get_labels()
        if len(_labels_f1) == 0 or len(_labels_f2) == 0:
            return None

        _f1 = _labels_f1[0].get_best().get_typed_content()
        _f2 = _labels_f2[0].get_best().get_typed_content()

        # A value of zero is the one the Formants annotation is assigning
        # when a method didn't estimate any value.
        if _f1 == 0 or _f2 == 0:
            return None

        _duration = (ann_f1.get_highest_localization().get_midpoint() -
                     ann_f1.get_lowest_localization().get_midpoint())

        return [_duration, float(_f1), float(_f2)]

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_tiers(tier_f1: sppasTier, tier_f2: sppasTier) -> tuple:
        """Return the three tiers of the result, with the source metadata.

        The filtered tiers are named like the source ones, and the tier of
        the distances is named after the method of these latter.

        :param tier_f1: (sppasTier) Tier with the F1 values of a method
        :param tier_f2: (sppasTier) Tier with the F2 values of a method
        :return: (sppasTier, sppasTier, sppasTier) F1, F2 and distances

        """
        _method_name = VowelFilterEstimator.get_method_name(tier_f1)
        _dist_name = "MahalanobisDist"
        if len(_method_name) > 0 and tier_f1.get_name().startswith("F1-") is True:
            _dist_name = "MahalanobisDist-" + _method_name

        return (VowelFilterEstimator.__create_tier(tier_f1.get_name(), tier_f1),
                VowelFilterEstimator.__create_tier(tier_f2.get_name(), tier_f2),
                VowelFilterEstimator.__create_tier(_dist_name, tier_f1))

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
                             ann_f1, ann_f2, value_f1: int, value_f2: int,
                             distance: float) -> None:
        """Append the filtered values of a token to the given tiers.

        A discarded value is stored as a zero, like the Formants annotation
        is doing, and its distance is kept to explain why it was discarded.

        """
        _phoneme = ann_f1.get_labels()[0].get_key()

        _label_f1 = sppasLabel(sppasTag(value_f1, "int"))
        _label_f1.set_key(_phoneme)
        new_f1.create_annotation(ann_f1.get_location().copy(), [_label_f1])

        _label_f2 = sppasLabel(sppasTag(value_f2, "int"))
        _label_f2.set_key(_phoneme)
        new_f2.create_annotation(ann_f2.get_location().copy(), [_label_f2])

        _label_distance = sppasLabel(sppasTag(distance, "float"))
        _label_distance.set_key(_phoneme)
        distances_tier.create_annotation(ann_f1.get_location().copy(), [_label_distance])
