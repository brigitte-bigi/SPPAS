# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.position.observed.py
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

MSG_DESCRIPTION_OBSERVED = \
    "The positions were observed on 25 selected pictures of CLeLfPC corpus."

# ---------------------------------------------------------------------------


class WherePositionPredictorObserved(BaseWherePositionPredictor):
    """Predict the coordinates of vowels from 2D sights.

    Extend the base class to predict the coordinates of vowels from 2D sights.
    It overrides methods to provide specific calculations for different vowel
    positions based on facial landmarks.

    It adds the calculation of a radius for each vowel: it allows to define
    an area in which the target is acceptable.

    Observed values are for each measured key on 5 professional cuers:
        1 ; b ; 64 ; 375
        2 ; b ; 141 ; 425
        6 ; b ; 60 ; 370
        7 ; b ; 145 ; 339
        8 ; b ; -15 ; 397
        3 ; c ; 349 ; 836
        4 ; c ; 461 ; 967
        5 ; c ; 393 ; 944
        6 ; c ; 499 ; 927
        7 ; c ; 488 ; 904
        1 ; m ; 309 ; 710
        4 ; m ; 215 ; 742
        5 ; m ; 233 ; 653
        6 ; m ; 213 ; 656
        8 ; m ; 304 ; 713
        2 ; s ; -337 ; 753
        3 ; s ; -622 ; 726
        4 ; s ; -453 ; 667
        6 ; s ; -331 ; 774
        7 ; s ; -415 ; 370
        1 ; t ; 543 ; 1429
        3 ; t ; 339 ; 1305
        4 ; t ; 505 ; 1382
        5 ; t ; 448 ; 1272
        6 ; t ; 434 ; 1573

    Average and standard deviations:
        - b : mean(79.0, 381.2), stdev(66.37, 32.07)
        - c : mean(438.0, 915.6), stdev(64.61, 50.12)
        - m : mean(254.8, 694.8), stdev(47.87, 38.87)
        - s : mean(-431.6, 658.0), stdev(118.38, 165.93)
        - t : mean(453.8, 1392.2), stdev(77.75, 118.53)

    """

    def __init__(self, nb_sights=68):
        super(WherePositionPredictorObserved, self).__init__(nb_sights)
        self._description = MSG_DESCRIPTION_OBSERVED

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
        x = self._x(4) - ((abs(self._x(36) - self._x(0))) // 20)
        y = self._y(1) + int((abs(self._y(2) - self._y(1))) / 1.6)
        r = int(0.044 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_c(self) -> tuple:
        """Override. Calculate the position of the chin vowel.

        :return: (tuple) coordinates and radius of the chin vowel

        """
        x = self._x(8) - int((abs(self._x(8) - self._x(6))) / 3.8)
        y = self._y(8) - int(abs(self._y(8) - self._y(57)) // 3.)
        r = int(0.059 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_m(self) -> tuple:
        """Override. Calculate the position of the mouth vowel.

        :return: (tuple) coordinates and radius of the mouth vowel

        """
        x = self._x(48) - int(abs(self._x(48) - self._x(4)) / 4.5)
        y = self._y(60) + abs(self._y(60) - self._y(4))
        r = int(0.044 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_s(self) -> tuple:
        """Override. Calculate the position of the side vowel.

        :return: (tuple) coordinates and radius of the side vowel

        """
        x = self._x(0) - int(abs(self._x(8) - self._x(0)) * 0.85)
        y = self._y(4) - int(abs(self._y(4) - self._y(3)) / 3.2)
        r = int(0.14 * self._radius_ratio())
        return x, y, r

    # -----------------------------------------------------------------------

    def _calculate_vowel_t(self) -> tuple:
        """Override. Calculate the position of the throat vowel.

        :return: (tuple) coordinates and radius of the throat vowel

        """
        x = self._x(8) - int((abs(self._x(8) - self._x(6))) / 5.2)
        y = self._y(8) + int(0.8 * float(abs(self._y(8) - self._y(33))))
        r = int(0.1 * self._radius_ratio())
        return x, y, r
