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
        method_names = VowelFilterEstimator.get_method_names(tier_f1)
        classifier = VowelClassifier(syll_tier)

        nb_tokens = 0
        for class_name, vectors in self.__get_tokens(tier_f1, tier_f2, classifier, method_names):
            for i, vector in enumerate(vectors):
                if vector is None:
                    continue
                self.__profiles.add_token(class_name, method_names[i], vector)
                nb_tokens += 1

        return nb_tokens

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
        method_names = VowelFilterEstimator.get_method_names(tier_f1)
        classifier = VowelClassifier(syll_tier)

        new_f1 = VowelFilterEstimator.__create_tier("F1", tier_f1)
        new_f2 = VowelFilterEstimator.__create_tier("F2", tier_f2)
        distances_tier = VowelFilterEstimator.__create_tier("MahalanobisDist", tier_f1)

        self.__nb_values = 0
        self.__nb_filtered = 0

        tokens = self.__get_tokens(tier_f1, tier_f2, classifier, method_names)
        for i, (class_name, vectors) in enumerate(tokens):
            if len(vectors) == 0:
                continue

            values_f1, values_f2, distances = self.__filter_token(class_name, vectors, method_names)
            VowelFilterEstimator.__append_annotations(
                new_f1, new_f2, distances_tier, tier_f1[i], tier_f2[i],
                values_f1, values_f2, distances)

        return new_f1, new_f2, distances_tier

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
        names = list()
        i = 0
        name = tier.get_meta("formants_estimator_method_0", default="")
        while len(name) > 0:
            names.append(name)
            i += 1
            name = tier.get_meta("formants_estimator_method_{:d}".format(i), default="")

        if len(names) == 0:
            # The tier was not created by the Formants annotation. The number
            # of values of an annotation is then the number of methods.
            for ann in tier:
                labels = ann.get_labels()
                if len(labels) > 0:
                    names = ["method_{:d}".format(j) for j in range(len(labels[0]))]
                    break

        return tuple(names)

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
        values_f1 = list()
        values_f2 = list()
        distances = list()

        for i, vector in enumerate(vectors):
            if vector is None:
                # The method didn't estimate any value for this token.
                values_f1.append(0)
                values_f2.append(0)
                distances.append(-1.)
                continue

            self.__nb_values += 1
            distance = self.__profiles.get_distance(class_name, method_names[i], vector)

            if distance is None:
                # No distribution to compare this token with.
                values_f1.append(int(vector[1]))
                values_f2.append(int(vector[2]))
                distances.append(-1.)

            elif distance > self.__threshold:
                self.__nb_filtered += 1
                values_f1.append(0)
                values_f2.append(0)
                distances.append(round(distance, 3))

            else:
                values_f1.append(int(vector[1]))
                values_f2.append(int(vector[2]))
                distances.append(round(distance, 3))

        return values_f1, values_f2, distances

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

        tokens = list()

        for ann_f1, ann_f2 in zip(tier_f1, tier_f2):
            labels_f1 = ann_f1.get_labels()
            labels_f2 = ann_f2.get_labels()
            if len(labels_f1) == 0 or len(labels_f2) == 0:
                tokens.append(("", list()))
                continue

            # Two methods sharing the same value are stored into a single
            # tag, so that no value can be assigned to its method.
            if len(labels_f1[0]) != len(method_names) or len(labels_f2[0]) != len(method_names):
                logging.warning("Ignored the token at {:s}: {:d} values instead of the "
                                "{:d} expected ones."
                                "".format(str(ann_f1.get_location()),
                                          len(labels_f1[0]), len(method_names)))
                tokens.append(("", list()))
                continue

            class_name = classifier.get_class(ann_f1)
            begin = ann_f1.get_lowest_localization().get_midpoint()
            end = ann_f1.get_highest_localization().get_midpoint()
            duration = end - begin

            vectors = list()
            for (tag_f1, score_f1), (tag_f2, score_f2) in zip(labels_f1[0], labels_f2[0]):
                f1 = tag_f1.get_typed_content()
                f2 = tag_f2.get_typed_content()
                # A value of zero is the one the Formants annotation is
                # assigning when a method didn't estimate any value.
                if f1 == 0 or f2 == 0:
                    vectors.append(None)
                else:
                    vectors.append([duration, float(f1), float(f2)])

            tokens.append((class_name, vectors))

        return tokens

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_tier(tier_name: str, source_tier: sppasTier) -> sppasTier:
        """Return a new tier with the metadata of the given one.

        :param tier_name: (str) Name of the tier to create
        :param source_tier: (sppasTier) Tier the metadata are copied from
        :return: (sppasTier)

        """
        tier = sppasTier(tier_name)
        for key in source_tier.get_meta_keys():
            if tier.get_meta(key, default=None) is None:
                tier.set_meta(key, source_tier.get_meta(key))
        tier.set_media(source_tier.get_media())

        return tier

    # -----------------------------------------------------------------------

    @staticmethod
    def __append_annotations(new_f1: sppasTier, new_f2: sppasTier, distances_tier: sppasTier,
                             ann_f1, ann_f2, values_f1: list, values_f2: list,
                             distances: list) -> None:
        """Append the filtered values of a token to the given tiers.

        Like the Formants annotation does, no annotation is created if none
        of the methods has a value to store.

        """
        nb_kept = 0
        for value_f1, value_f2 in zip(values_f1, values_f2):
            if value_f1 != 0 and value_f2 != 0:
                nb_kept += 1
        if nb_kept == 0:
            return

        phoneme = ann_f1.get_labels()[0].get_key()

        label_f1 = sppasLabel([sppasTag(v, "int") for v in values_f1])
        label_f1.set_key(phoneme)
        new_f1.create_annotation(ann_f1.get_location().copy(), [label_f1])

        label_f2 = sppasLabel([sppasTag(v, "int") for v in values_f2])
        label_f2.set_key(phoneme)
        new_f2.create_annotation(ann_f2.get_location().copy(), [label_f2])

        label_distances = sppasLabel([sppasTag(d, "float") for d in distances])
        label_distances.set_key(phoneme)
        distances_tier.create_annotation(ann_f1.get_location().copy(), [label_distances])
