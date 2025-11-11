# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.position.customs.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Predict the vowel positions from given sights.

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

from .baseposition import BaseWherePositionPredictor

# ---------------------------------------------------------------------------

MSG_DESCRIPTION_CUSTOMS = \
    "The positions were fixed by Cued Speech experts."

# ---------------------------------------------------------------------------


class WherePositionPredictorCustoms(BaseWherePositionPredictor):
    """Predict the coordinates of vowels from 2D sights.

    Extend the base class to predict the coordinates of vowels from 2D sights.
    It overrides methods to provide specific calculations for different vowel
    positions based on facial landmarks.

    It adds the calculation of a radius for each vowel: it allows to define
    an area in which the target is acceptable.

    """

    def __init__(self, nb_sights=68):
        super(WherePositionPredictorCustoms, self).__init__(nb_sights)
        self._description = MSG_DESCRIPTION_CUSTOMS

    # -----------------------------------------------------------------------
    # Overridden
    # -----------------------------------------------------------------------

    def _calculate_vowel_n(self) -> tuple:
        """Override. Calculate the position of the neutral vowel.

        :return: (tuple) coordinates and radius of the neutral vowel

        """
        x = self._x(8) - ((abs(self._x(8) - self._x(7))) // 4)
        y = self._y(8) + 4 * (self._y(8) - self._y(57))
        r = int(0.2 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_b(self) -> tuple:
        """Override. Calculate the position of the cheek bone vowel.

        :return: (tuple) coordinates and radius of the cheek bone vowel

        """
        x = self._x(4) + ((abs(self._x(36) - self._x(0))) // 6)
        y = self._y(1)
        r = int(0.114 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_c(self) -> tuple:
        """Override. Calculate the position of the chin vowel.

        :return: (tuple) coordinates and radius of the chin vowel

        """
        x = self._x(8)
        y = self._y(8) - (abs(self._y(8) - self._y(57)) // 5)
        r = int(0.062 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_m(self) -> tuple:
        """Override. Calculate the position of the mouth vowel.

        :return: (tuple) coordinates and radius of the mouth vowel

        """
        x = self._x(48) - (abs(self._x(48) - self._x(4)) // 4)
        y = self._y(60)
        r = int(0.094 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_s(self) -> tuple:
        """Override. Calculate the position of the side vowel.

        :return: (tuple) coordinates and radius of the side vowel

        """
        x = self._x(0) - ((2 * abs(self._x(8) - self._x(0))) // 3)
        y = self._y(4)
        r = int(0.18 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_t(self) -> tuple:
        """Override. Calculate the position of the throat vowel.

        :return: (tuple) coordinates and radius of the throat vowel

        """
        x = self._x(8)
        y = self._y(8) + int(1.2 * float(abs(self._y(8) - self._y(57))))
        r = int(0.14 * self._radius_ratio())
        return x, y, r
