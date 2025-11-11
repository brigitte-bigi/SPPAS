# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.angle.observed.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A few observed values for hand angles. Answer the "Where?" question.

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

    -------------------------------------------------------------------------

"""

from __future__ import annotations

from .baseangle import BaseWhereAnglePredictor


# ---------------------------------------------------------------------------

MSG_DESCRIPTION_RULES = \
    "The angles were observed on 25 selected pictures of CLeLfPC corpus."

# ---------------------------------------------------------------------------


class WhereAnglePredictorObserved(BaseWhereAnglePredictor):
    """Predict hand angles with experts rules.

    Observed values are for each measured key on 5 professional cuers:
        1 ; b ; 53
        2 ; b ; 73
        6 ; b ; 57
        7 ; b ; 63
        8 ; b ; 62
        3 ; c ; 64
        4 ; c ; 69
        5 ; c ; 52
        6 ; c ; 51
        7 ; c ; 59
        1 ; m ; 55
        4 ; m ; 56
        5 ; m ; 62
        6 ; m ; 39
        8 ; m ; 70
        2 ; s ; 73
        3 ; s ; 93
        4 ; s ; 90
        6 ; s ; 80
        7 ; s ; 85
        1 ; t ; 48
        3 ; t ; 52
        4 ; t ; 42
        5 ; t ; 57
        6 ; t ; 44

    Average and standard deviations:
    - b: 62.0  (5.3)
    - c: 59.0  (6.0)
    - m: 56.4  (7.7)
    - t: 48.6  (4.7)
    - s: 83.0  (5.0)

    """

    def __init__(self):
        """Instantiate a custom hand angle predictor.

        """
        super(WhereAnglePredictorObserved, self).__init__()
        self._description = MSG_DESCRIPTION_RULES
        self._radius = 5

    # -----------------------------------------------------------------------
    # Override.
    # -----------------------------------------------------------------------

    def _calculate_angle_n(self) -> int:
        """Calculate the angle at the neutral position.

        :return: (int) angle in degrees

        """
        return 50

    # -----------------------------------------------------------------------

    def _calculate_angle_b(self) -> int:
        """Calculate the angle at the cheek bone position.

        :return: (int) angle in degrees

        """
        return 62

    # -----------------------------------------------------------------------

    def _calculate_angle_c(self) -> int:
        """Calculate the angle at the chin position.

        :return: (int) angle in degrees

        """
        return 59

    # -----------------------------------------------------------------------

    def _calculate_angle_m(self) -> int:
        """Calculate the angle at the mouse position.

        :return: (int) angle in degrees

        """
        return 56

    # -----------------------------------------------------------------------

    def _calculate_angle_s(self) -> int:
        """Calculate the angle at the side position.

        :return: (int) angle in degrees

        """
        return 83

    # -----------------------------------------------------------------------

    def _calculate_angle_t(self) -> int:
        """Calculate the angle at the throat position.

        :return: (int) angle in degrees

        """
        return 49
