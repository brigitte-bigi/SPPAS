# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.vowels.baseposition.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base for vowels positions predictors. Answer the "Where?" question.

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
import logging

from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasKeyError
from sppas.src.imgdata import sppasSights

from .facesights import FaceTwoDim

# ---------------------------------------------------------------------------


MSG_DESCRIPTION_BASE = \
    ("The vowel positions are always predicted at the same coordinates "
     "and relatively to sights of the face. ")

# ---------------------------------------------------------------------------


class BaseWherePositionPredictor:
    """Base class to predict vowel positions around the face.

    The vowel positions are considered targets in the hand trajectory.
    Currently, 5 vowel positions are possible and they have only one coordinate.
    For English language, this will have to be changed because some vowels have
    a movement effect: side-forward, side-down.

    """

    def __init__(self, nb_sights=68):
        """Instantiate a vowel position's predictor.

        :param nb_sights: (int) Number of face sights. Must match the one of FaceTwoDim().
        :raises: NotImplementedError: given nb sights is not supported.
        :raises: sppasTypeError: given nb sights is not of 'int' type.

        """
        # Short description of the position prediction method
        self._description = MSG_DESCRIPTION_BASE

        # The sights of a face at a given moment
        self.__sights = None
        # The reference face, in a 1000x1000 pixels image.
        self._f2 = FaceTwoDim()

        try:
            nb_sights = int(nb_sights)
        except ValueError:
            raise sppasTypeError(type(nb_sights), "int")
        nb_sights = int(nb_sights)
        if nb_sights != self._f2.dim:
            raise NotImplementedError(
                "The support for vowel prediction with {:d} sights is not "
                "implemented yet. Expected {:d}.".format(nb_sights, self._f2.dim))

        # Predicted vowels from the given sights
        self._vowels = dict()

        # Map the vowel code to the method to be used for the calculation
        # of its position. It should contain all vowels for all languages.
        self.__vowel_mapping = {
            'b': self._calculate_vowel_b,
            'c': self._calculate_vowel_c,
            'm': self._calculate_vowel_m,
            's': self._calculate_vowel_s,
            'sf': self._calculate_vowel_sf,
            'sd': self._calculate_vowel_sd,
            't': self._calculate_vowel_t,
            'n': self._calculate_vowel_n
        }

    # -----------------------------------------------------------------------

    def vowel_codes(self) -> tuple:
        """Return the list of vowel codes the class can calculate position."""
        return tuple(self.__vowel_mapping.keys())

    # -----------------------------------------------------------------------

    def get_sights_dim(self) -> int:
        """Return the number of sights this predictor was trained for."""
        return self._f2.dim

    # -----------------------------------------------------------------------

    def set_sights_and_predict_coords(self, sights: sppasSights | None = None, vowels: tuple | None = None) -> None:
        """Set the sights of a face and predict all vowel positions.

        If no sights are provided, it uses default sights. It validates the
        input type and the number of sights before setting them and predicting
        vowel coordinates.

        :param sights: (sppasSights | None)
        :param vowels: (tuple | None) List of vowel position names. Default is all known ones.
        :raises: sppasTypeError: given parameter is not a sppasSights type.
        :raises: NotImplementedError: not the expected number of sights

        """
        if sights is None:
            self.__sights = self._f2.sights
        else:
            if isinstance(sights, sppasSights) is False:
                raise sppasTypeError(type(sights), "sppasSights")
            if len(sights) != self._f2.dim:
                raise NotImplementedError(
                    "The support for vowel prediction with {:d} sights is not "
                    "implemented yet. Expected {:d}.".format(len(sights), self._f2.dim))
            self.__sights = sights

        if vowels is None:
            vowels = self.vowel_codes()
        self.predict_vowels_coords(vowels)

    # -----------------------------------------------------------------------

    def get_vowel_coords(self, vowel: str = 'n') -> tuple:
        """Return the absolute position of the given vowel.

        Estimated relatively to the sights of a face. Sights must be set
        before using this method.

        :param vowel: (char) Vowel position name. If unknown, 'n' is used instead.
        :return: tuple(x, y, r) with point coordinates and radius
        :raises: sppasKeyError: Invalid given vowel code.

        """
        if vowel in self._vowels:
            return self._vowels[vowel]
        raise sppasKeyError(vowel, "Predicted Vowels")

    # -----------------------------------------------------------------------

    def predict_vowels_coords(self, vowels: tuple = ('n', )) -> None:
        """Estimate the absolute position of all the requested vowels.

        Estimate the absolute positions of specified vowels relative to the
        sights of a face. It uses predefined coordinates and calculations
        to determine these positions and stores them in a dictionary.
        Sights must be set before using this method.

        :param vowels: (tuple) List of vowel position names. If unknown, 'n' is used instead.
        :raises: sppasKeyError: Invalid given vowel code.

        """
        self.check(vowels)

        self._vowels = dict()
        for vowel in vowels:
            # Calculate the coordinates and store into the dict
            try:
                self._vowels[vowel] = self.__vowel_mapping[vowel]()
            except NotImplementedError:
                logging.warning(f"No vowel position calculation for vowel '{vowel}'")
                pass

    # -----------------------------------------------------------------------
    
    def check(self, vowels: tuple):
        """Check if the given vowel codes are valid.

        :param vowels: (tuple) The character codes of vowels
        :raises: sppasKeyError: Invalid given vowel code.

        """
        if self.__sights is None:
            logging.warning("Attempting to predict vowel positions but no sights were defined.")
            self.set_sights_and_predict_coords()

        codes = self.vowel_codes()
        for vowel in vowels:
            if vowel not in codes:
                raise sppasKeyError(vowel, "Vowel Position Code")

    # -----------------------------------------------------------------------
    # To be overridden
    # -----------------------------------------------------------------------

    def _calculate_vowel_n(self) -> tuple:
        """To be overridden. Calculate the position of the neutral position.

        :return: (tuple) coordinates and radius of the neutral position

        """
        x = self._x(8)
        y = self._y(8) + 4 * (self._y(8) - self._y(57))
        return x, y, 0

    # -----------------------------------------------------------------------

    def _calculate_vowel_b(self) -> tuple:
        """To be overridden. Calculate the position of a cheek bone vowel.

        :return: (tuple) coordinates and radius of the cheek bone vowel

        """
        x = self._x(4) + ((abs(self._x(36) - self._x(0))) // 2)
        y = self._y(1) - ((abs(self._y(1) - self._y(0))) // 3)
        return x, y, 0

    # -----------------------------------------------------------------------

    def _calculate_vowel_c(self) -> tuple:
        """To be overridden. Calculate the position of a chin vowel.

        :return: (tuple) coordinates and radius of the chin vowel

        """
        x = self._x(8)
        y = self._y(8) - (abs(self._y(8) - self._y(57)) // 5)
        return x, y, 0

    # -----------------------------------------------------------------------

    def _calculate_vowel_m(self) -> tuple:
        """To be overridden. Calculate the position of a mouth vowel.

        :return: (tuple) coordinates and radius of the mouth vowel

        """
        x = self._x(48) - (abs(self._x(48) - self._x(4)) // 4)
        y = self._y(60)
        return x, y, 0

    # -----------------------------------------------------------------------

    def _calculate_vowel_s(self) -> tuple:
        """To be overridden. Calculate the position of a side vowel.

        :return: (tuple) coordinates and radius of the side vowel

        """
        x = self._x(0) - ((2 * abs(self._x(8) - self._x(0))) // 3)
        y = self._y(4) - (abs(self._y(4) - self._y(3)) // 2)
        return x, y, 0

    # -----------------------------------------------------------------------

    def _calculate_vowel_sf(self) -> tuple:
        """To be overridden. Calculate the position of a side-forward vowel.

        :return: (tuple) coordinates and radius of the side-forward vowel

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _calculate_vowel_sd(self) -> tuple:
        """To be overridden. Calculate the position of a side-down vowel.

        :return: (tuple) coordinates and radius of the side-down vowel

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _calculate_vowel_t(self) -> tuple:
        """To be overridden. Calculate the position of a throat vowel.

        :return: (tuple) coordinates and radius of the throat vowel

        """
        x = self._x(8)
        y = self._y(8) + int(1.2 * float(abs(self._y(8) - self._y(57))))
        return x, y, 0

    # -----------------------------------------------------------------------
    # Private area
    # -----------------------------------------------------------------------

    def _x(self, idx) -> int:
        return self.__sights.x(idx)

    def _y(self, idx) -> int:
        return self.__sights.y(idx)

    def _radius_ratio(self) -> float:
        """Return the width/height ratio of the face sights."""
        return (float(self._x(16) - self._x(0)) +
                (float(self._y(8) - self._y(27)))) / 1.85
