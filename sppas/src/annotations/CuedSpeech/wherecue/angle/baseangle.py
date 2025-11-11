# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.angle.baseangle.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base for hand angle predictors. Answer the "Where?" question.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######  ########  ########     ###     ######
    ##    ## ##     ## ##     ##   ## ##   ##    ##     the automatic
    ##       ##     ## ##     ##  ##   ##  ##            annotation
     ######  ########  ########  ##     ##  ######        and
          ## ##        ##        #########       ##        analysis
    ##    ## ##        ##        ##     ## ##    ##         of speech
     ######  ##        ##        ##     ##  ######

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from sppas.core.coreutils import sppasKeyError
from sppas.core.coreutils import IntervalRangeException

# ---------------------------------------------------------------------------


MSG_DESCRIPTION_BASE = "The hand angles are always predicted the same whatever the vowel."

# ---------------------------------------------------------------------------


class BaseWhereAnglePredictor(object):
    """Base class to predict the angle of the hand.

    Currently, 5 vowel positions are possible, and they are associated to
    only one angle value.
    For English langage, this will have to be changed because some vowels have
    a movement effect: side-forward, side-down.

    Angle value is given relatively to the horizontal axis, like in the
    following unit circle:

                     90°
                     |
                     |
        180° ------- + ------- 0°
                     |
                     |
                    270°
                    -90°

    """

    MAX_RADIUS = 20

    def __init__(self):
        """Instantiate a hand angle's predictor.

        """
        # Short description of the angle prediction method
        self._description = MSG_DESCRIPTION_BASE

        # Predicted angles for each position
        self._vowels = dict()

        # Vagueness. Angle is more or less this value in degrees.
        self._radius = 10

        # Map the hand angle estimation method to a vowel code.
        self.__vowel_mapping = {
            'b': self._calculate_angle_b,
            'c': self._calculate_angle_c,
            'm': self._calculate_angle_m,
            's': self._calculate_angle_s,
            't': self._calculate_angle_t,
            'n': self._calculate_angle_n
        }

    # -----------------------------------------------------------------------

    def vowel_codes(self) -> tuple:
        """Return the list of vowel codes the class can calculate hand angles for."""
        return tuple(self.__vowel_mapping.keys())

    # -----------------------------------------------------------------------

    def get_radius(self) -> int:
        """Vagueness of angle value."""
        return self._radius

    def set_radius(self, r: int):
        """Fix a new radius value.

        :param r: (int) The new radius value between 0 and MAX_RADIUS.
        :raises: ValueError: Invalid given radius value.

        """
        r = int(r)
        if r < 0 or r > self.MAX_RADIUS:
            raise IntervalRangeException(r, 0, BaseWhereAnglePredictor.MAX_RADIUS)
        self._radius = r

    radius = property(get_radius, set_radius)

    # -----------------------------------------------------------------------

    def get_angle(self, vowel: str = 'n') -> tuple:
        """Return the angle at a given position.

        :param vowel: (char) Vowel position name. If unknown, 'n' is used instead.
        :return: (int)
        :raises: sppasKeyError: Invalid given vowel code.

        """
        if vowel in self._vowels:
            return self._vowels[vowel]
        raise sppasKeyError(vowel, "Predicted Angles")

    # -----------------------------------------------------------------------

    def predict_angle_values(self, vowels=('n', )) -> None:
        """Estimate the angle of the hand for all the given positions.

        It uses predefined angles and stores them in a dictionary.

        :param vowels: (tuple) List of vowel position names. If unknown, 'n' is used instead.
        :raises: sppasKeyError: Invalid given vowel code.

        """
        self.check(vowels)

        self._vowels = dict()
        codes = self.vowel_codes()
        for vowel in vowels:
            if vowel not in codes:
                raise sppasKeyError(vowel, "Position Code")
            # Calculate the angles and store into the dict
            self._vowels[vowel] = self.__vowel_mapping[vowel]()

    # -----------------------------------------------------------------------

    def check(self, vowels: list):
        """Check if the given vowel codes are valid.

        :param vowels: (list of characters)
        :raises: sppasKeyError: Invalid given vowel code.

        """
        codes = self.vowel_codes()
        for vowel in vowels:
            if vowel not in codes:
                raise sppasKeyError(vowel, "Position Code")

    # -----------------------------------------------------------------------
    # To be overridden
    # -----------------------------------------------------------------------

    def _calculate_angle_n(self) -> int:
        """To be overridden. Calculate the angle at the neutral position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_b(self) -> int:
        """To be overridden. Calculate the angle at the cheek bone position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_c(self) -> int:
        """To be overridden. Calculate the angle at the chin position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_m(self) -> int:
        """To be overridden. Calculate the angle at the mouse position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_s(self) -> int:
        """To be overridden. Calculate the angle at the side position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_t(self) -> int:
        """To be overridden. Calculate the angle at the throat position.

        :return: (int) angle in degrees

        """
        return 60
