# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whowimgtag.handproperties.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Properties of a hand.

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
import math

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import IntervalRangeException

from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasSights

# -----------------------------------------------------------------------


class sppasHandProperties:
    """Data storage of a hand.

    Angle estimation is performed thanks to both sights S0 (wrist) and S9
    (middle finger mcp).
       - angle is 0 degree if: x0 = x9 ; y0 <= y9
       - angle is 180 degrees if: x0 = x9 ; y0 > y9
    Size estimation is performed thanks to both sights S0 and S9 too.

    Estimations from coordinates in a picture:

            A---------------------S9
            |                   /
            |               /
            |          /
            |     /
            S0

        S0 = (x0, y0)
        S9 = (x9, y9)
        A = (x0, y9)

        Let's introduce:
        - a: the distance between S0 and S9 to be estimated
        - b: the distance between A and S9: abs(y9 - y0)
        - c: the distance between A and S0: abs(x9 - x0)
        - alpha = angle A = 90 degrees
        - beta = angle S0 to be estimated

        then:
        a = sqrt(b*b - c*c) [pythagore]
        beta = arccos( (c*c + a*a - b*b) / (2*c*a) )

    """

    NUMBER_OF_SIGHTS = (4, 21)

    def __init__(self, image: sppasImage, sights: sppasSights, target_index: int):
        """The constructor of the SppasHandProperties.

        This class stores data for a hand.

        :param image: (sppasImage) The hand image associated of all data stored
        :param sights: (sppasSights) The sights annotation of the hand
        :param target_index: (int) Index of the target sight
        :raises: sppasTypeError: If the parameters have a wrong type
        :raises: IntervalRangeException: If the target index parameter is negative or too huge

        """
        # check parameters
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError(image, "sppasImage")

        if isinstance(sights, sppasSights) is False:
            raise sppasTypeError(sights, "sppasSights")

        # Declare private attributes
        self.__beta = 0
        self.__dist = 0
        self.__target = (0, 0)
        self.__distances_with_s0 = list()
        self.__angles_with_s0 = list()

        # Set the image
        self.__image = image
        # Set the sights
        self.__sights = sights

        # Set the target (x,y) from the sights
        if 0 <= target_index < len(sights):
            try:
                x, y, _, _ = sights.get_sight(target_index)
            # case if we don't have the target sights
            except IntervalRangeException:
                x, y = None, None

            self.__target = (x, y)

        else:
            raise IntervalRangeException(target_index, 0, len(sights))

        # Estimate the distance and the angle from the sights
        self.__estimation()

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def distance(self) -> int:
        """Return the [s0,s9] estimated distance value.

        :return: (int) The distance between the s0 and s9 point of the hand

        """
        return self.__dist

    # -----------------------------------------------------------------------

    def angle(self) -> int:
        """Return the default angle of the hand in the image.

        :return: (int) The beta angle

        """
        return self.__beta

    # -----------------------------------------------------------------------

    def nb_sights(self) -> int:
        """Return the number of sights of the hand.

        :return: (int) The sights length

        """
        return len(self.__sights)

    # -----------------------------------------------------------------------

    def image(self) -> sppasImage:
        """Return the image of the hand associated to the data structure.

        :return: (sppasImage) The hand image

        """
        return self.__image

    # -----------------------------------------------------------------------

    def image_size(self) -> tuple:
        """Return the image size of the hand (width, height).

        :return: (tuple) The size of the image

        """
        return self.__image.size()

    # -----------------------------------------------------------------------

    def target_coords(self) -> tuple:
        """Return coordinate (x, y) of the target point of the hand.

        :return: (tuple) The target point coordinate

        """
        return self.__target

    # -----------------------------------------------------------------------

    def get_sight(self, index: int) -> tuple:
        """Return a sight with the given index.

        :param index: (int) The index of the sight that we want
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (tuple) The coordinates of the sight

        """
        if 0 <= index < len(self.__sights):
            x, y, _, _ = self.__sights.get_sight(index)
            return x, y
        else:
            raise IntervalRangeException(index, 0, len(self.__sights))

    # -----------------------------------------------------------------------

    def get_sights(self) -> sppasSights:
        """Return the sight of the hand

        :return: (sppasSights) The sights of the hand

        """
        return self.__sights

    # -----------------------------------------------------------------------

    def set_image(self, hand_image: sppasImage) -> None:
        """Setter of the hand image (used in the program to apply the filters).

        :param hand_image: (sppasImage) The new hand image

        :raises: sppasTypeError: If the 'hand_image' parameter is not an instance of sppasImage class

        """
        if isinstance(hand_image, sppasImage) is False:
            raise sppasTypeError(hand_image, "sppasImage")

        self.__image = hand_image

    # -----------------------------------------------------------------------

    def get_distance_with_s0(self, sight_index: int) -> int:
        """Get the distance between s0 and a sight of the hand.

        :param sight_index: (int) The index of the sight
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (int) the computed distance

        """
        if sight_index < 0 or sight_index > len(self.__distances_with_s0):
            raise IntervalRangeException(sight_index, 0, len(self.__distances_with_s0))

        return self.__distances_with_s0[sight_index]

    # -----------------------------------------------------------------------

    def get_angle_with_s0(self, sight_index: int) -> int:
        """Get the angle between s0 and a sight of the hand.

        :param sight_index: (int) The index of the sight
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (int) the computed angle

        """
        if sight_index < 0 or sight_index > len(self.__angles_with_s0):
            raise IntervalRangeException(sight_index, 0, len(self.__angles_with_s0))

        return self.__angles_with_s0[sight_index]

    # -----------------------------------------------------------------------
    # STATIC METHODS
    # -----------------------------------------------------------------------

    @staticmethod
    def pythagoras(side1: float, side2: float) -> float:
        """Estimate with the Pythagoras theorem the hypotenuse of the right triangle.

        Compute the hypotenuse with the two sides passed as parameters.
        The method doesn't verify if the sides and the hypotenuse represent a right triangle or a simple triangle.

        :param side1: (float) The first side of the right triangle
        :param side2: (float) The second side of the right triangle
        :return: (float) The computed hypotenuse

        """
        return math.sqrt((side1 * side1) + (side2 * side2))

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def __estimation(self) -> None:
        """Estimate the distance and the angle of the hand shape of this class.

        :raises: sppasError: If the number sights is different of 21 or 4

        """
        x0, y0, _, _ = self.__sights.get_sight(0)

        if len(self.__sights) == 21:
            s9_x, s9_y, _, _ = self.__sights.get_sight(9)
        elif len(self.__sights) == 4:
            # To be verified.
            s9_x, s9_y, _, _ = self.__sights.get_sight(2)
        else:
            raise sppasError(f"21 or 4 sights were expected. Got {len(self.__sights)} instead.")

        # Estimate the distance between S0 and S9 points
        s0s9_x = s9_x - x0
        s0s9_y = s9_y - y0
        s0s9_dist = self.pythagoras(s0s9_x, s0s9_y)

        # Estimate the angle to put the hand to 0 degree
        bottom_number = math.sqrt(s0s9_x * s0s9_x + s0s9_y * s0s9_y)
        angle = math.degrees(math.acos(s0s9_x / bottom_number))

        if s0s9_y > 0:
            angle = -angle

        # There's no need of a high precision !
        self.__dist = int(round(s0s9_dist, 0))
        self.__beta = int(round(angle, 0))

        # compute distance and angle between all sights and s0
        for i, current_sight in enumerate(self.__sights):
            if i > 0:
                # compute distance
                sight_dist_x = current_sight[0] - x0
                sight_dist_y = current_sight[1] - y0
                sight_dist = self.pythagoras(sight_dist_x, sight_dist_y)
                self.__distances_with_s0.append(round(sight_dist, 0))
                # print(f"{current_sight} - distance between s0 and s{i}: {sight_dist}")

                # compute angle
                if i == 9:
                    self.__angles_with_s0.append(0)
                else:
                    top_number = s0s9_x*sight_dist_y - s0s9_y*sight_dist_x
                    bottom_number = s0s9_dist * sight_dist
                    sight_angle = math.degrees(math.asin(top_number / bottom_number))
                    self.__angles_with_s0.append(round(sight_angle, 0))
                    # print(f"{current_sight} - angle between s0-s9 axis and s{i}: {sight_angle}")

            # estimation for s0
            else:
                self.__distances_with_s0.append(0)
                self.__angles_with_s0.append(0)
