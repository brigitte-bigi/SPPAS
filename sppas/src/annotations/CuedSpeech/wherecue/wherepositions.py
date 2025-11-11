# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.wherepositions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: CS vowel coordinates predictor. Answer the "Where?" question.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

    ---------------------------------------------------------------------

"""

from __future__ import annotations
from collections import deque

from sppas.src.calculus import fmean
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasPoint

from .wherecueexc import sppasWhereCuedSightsValueError
from .positions import WhereVowelPositionsPredictor

# ---------------------------------------------------------------------------


class sppasWherePositionsPredictor(object):
    """Predict the position of all the vowels from sights in a file.

    Create a tier indicating the position of CS vowels.

    """

    def __init__(self, predictor_version=WhereVowelPositionsPredictor.DEFAULT_VERSION):
        """Create a new instance of vowels predictor.

        """
        # Predictor system. Use the default number of sights.
        self.__predictor = WhereVowelPositionsPredictor(predictor_version)

        # The sight' values of a single kid in all images
        self.__data_sights = list()

    # -----------------------------------------------------------------------

    def version_numbers(self) -> list:
        """Return the whole list of supported version numbers."""
        return self.__predictor.version_numbers()

    # -----------------------------------------------------------------------

    def get_version_number(self) -> int:
        """Return the version number of the selected predictor (int)."""
        return self.__predictor.get_version_number()

    # -----------------------------------------------------------------------

    def set_version_number(self, version_number: int) -> None:
        """Change the predictor version number.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number

        """
        self.__predictor.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def get_nb_sights(self) -> int:
        """Return the number of sights."""
        return len(self.__data_sights)

    # -----------------------------------------------------------------------

    def set_sights(self, data_sights: list) -> None:
        """Load a filename and store the sights of a given kid.

        The given data is a list of tuples with:

        - at index 0: midpoint time value
        - at index 1: radius time value
        - at index 2: the 68 sights of a face

        :param data_sights: (list) List of sights of a face
        :raises: TypeError: if data_sights is not a list
        :raises: TypeError: if data_sights is not a list of tuples
        :raises: sppasWhereCuedSightsValueError: there are sights but there are not of the expected size

        """
        if isinstance(data_sights, (list, tuple)) is True:
            for s in data_sights:
                if isinstance(s, (tuple, list)) is False or len(s) != 3:
                    raise TypeError("Invalid item in the list of sights: {:s}".format(str(s)))
                cur_sights = s[2]
                if cur_sights is not None and len(cur_sights) != self.__predictor.get_sights_dim():
                    # there are sights but there are not of the expected size
                    raise sppasWhereCuedSightsValueError(self.__predictor.get_sights_dim(),
                                                         len(cur_sights))

            # Sights of each image previously estimated on a video
            self.__data_sights = data_sights
        else:
            raise TypeError("Invalid given sights. Expected a list. Got {:s}".format(str(type(data_sights))))

    # -----------------------------------------------------------------------

    def vowels_coords(self, vowels: list, smooth_len: int = 20):
        """Predict the coordinates of the given vowels.

        Notice that the coordinates of the position can have negative values.

        The 'smooth_len' variable is used to smooth the coordinates in order to
        eliminate micro-movements caused by the imprecision in detecting points
        and facial movements, preventing any visible 'shaking'.

        :param smooth_len: (int) Length of the queue used to smooth coords.
        :param vowels: (None | list) List of the vowel codes to predict.
        :return: (sppasTier) tier with name 'CS-VowelsCoords'

        """
        # The tier to be returned
        tier = sppasTier("CS-VowelsCoords")
        if vowels is None:
            vowels = self.__predictor.vowel_codes()

        # The (x, y, r) coords of each vowel in the last past 'fps' images.
        # This queue is used to store the last estimated vowels coords and
        # to smooth the current vowel position before adding into the tier.
        points_x = dict()
        points_y = dict()
        points_r = dict()
        for vowel in vowels:
            points_x[vowel] = deque(maxlen=smooth_len)
            points_y[vowel] = deque(maxlen=smooth_len)
            points_r[vowel] = deque(maxlen=smooth_len)

        # Let's go
        for midpoint, radius, sights in self.__data_sights:
            self.__predictor.set_sights_and_predict_coords(sights, vowels)
            labels = list()
            for vowel in vowels:
                if vowel in self.__predictor.vowel_codes():
                    # get the predicted position (x,y) and a radius value
                    x, y, r = self.__predictor.get_vowel_coords(vowel)

                    # add into the queue and get the smoothed value
                    x = self.__append_and_smooth(points_x[vowel], x)
                    y = self.__append_and_smooth(points_y[vowel], y)
                    r = self.__append_and_smooth(points_r[vowel], r)

                    # format the output result: a set of labels, one for each vowel.
                    tag = sppasTag((x, y, r), tag_type="point")
                    label = sppasLabel(tag)
                    label.set_key(vowel)
                    labels.append(label)

            # Save the coordinates of vowels into an annotation
            loc = sppasLocation(sppasPoint(midpoint, radius))
            tier.create_annotation(loc, labels)

        return tier

    # ----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    @staticmethod
    def __append_and_smooth(deck: deque, value: int):
        """Append into the queue and return the smoothed value.

        """
        # Append the real value into the queue
        deck.append(value)
        # Estimate the smoothed value: average of values in the queue
        if len(deck) > 1:
            return int(fmean(deck))
        return value
