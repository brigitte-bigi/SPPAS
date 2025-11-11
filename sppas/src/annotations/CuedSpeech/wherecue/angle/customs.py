# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.angle.customs.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Manual values for hand angles. Answer the "Where?" question.

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

MSG_DESCRIPTION_CUSTOMS = \
    "The angles were fixed by Cued Speech experts."

# ---------------------------------------------------------------------------


class WhereAnglePredictorCustoms(BaseWhereAnglePredictor):
    """Predict hand angles with experts rules.

    """

    def __init__(self):
        """Instantiate a custom hand angle predictor.

        """
        super(WhereAnglePredictorCustoms, self).__init__()
        self._description = MSG_DESCRIPTION_CUSTOMS
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
        return 75

    # -----------------------------------------------------------------------

    def _calculate_angle_c(self) -> int:
        """Calculate the angle at the chin position.

        :return: (int) angle in degrees

        """
        return 67

    # -----------------------------------------------------------------------

    def _calculate_angle_m(self) -> int:
        """Calculate the angle at the mouse position.

        :return: (int) angle in degrees

        """
        return 73

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
        return 58

