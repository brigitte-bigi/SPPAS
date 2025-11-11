# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.angle.unified.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Large amount of observed values for hand angles. Answer the "Where?" question.

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

MSG_DESCRIPTION_UNIFIED = \
    "The angles were observed on 3722 pictures of CLeLfPC corpus."

# ---------------------------------------------------------------------------


class WhereAnglePredictorUnified(BaseWhereAnglePredictor):
    """Predict hand angles with expert rules based on observed values.

    This model was created from observed values in a corpus.
    - Collected data: 3769 values
    - Filtered data: 3722 values (outliers removed)

    Statistics by Hand Position
    - b : Mean = 64.29, Std Dev = 7.87
    - c : Mean = 61.34, Std Dev = 7.37
    - m : Mean = 62.58, Std Dev = 8.12
    - s : Mean = 68.49, Std Dev = 11.07
    - t : Mean = 54.02, Std Dev = 9.96
    => The position is strongly correlated to the angle.

    Statistics by Hand Shape
    - 1 : Mean = 63.37, Std Dev = 11.85
    - 2 : Mean = 64.03, Std Dev = 10.54
    - 3 : Mean = 65.73, Std Dev = 10.89
    - 4 : Mean = 66.25, Std Dev = 11.50
    - 5 : Mean = 62.38, Std Dev = 10.01
    - 6 : Mean = 65.04, Std Dev = 12.08
    - 7 : Mean = 60.59, Std Dev = 11.59
    - 8 : Mean = 60.98, Std Dev = 9.50
    => The shape has no impact on the angle value.

    Statistics by Speaker
    - AM: Mean = 63.86, Std Dev = 12.91
    - CH: Mean = 73.80, Std Dev = 10.41
    - LM: Mean = 61.72, Std Dev = 7.35
    - ML: Mean = 56.81, Std Dev = 5.88
    - VT: Mean = 65.60, Std Dev = 11.10
    => There is a speaker effect, but it should be accounted for to create
    a general model.

    Statistics by Condition
    - syll: Mean = 61.17, Std Dev = 8.68
    - word: Mean = 58.30, Std Dev = 12.72
    - sent: Mean = 64.88, Std Dev = 10.05
    - text: Mean = 66.11, Std Dev = 10.49
    => The condition affects the angle, possibly by influencing movement
    precision; so it should be accounted for to create a general model.

    """

    def __init__(self):
        """Instantiate a custom hand angle predictor.

        """
        super(WhereAnglePredictorUnified, self).__init__()
        self._description = MSG_DESCRIPTION_UNIFIED
        self._radius = 5

    # -----------------------------------------------------------------------
    # Override.
    # -----------------------------------------------------------------------

    def _calculate_angle_n(self) -> int:
        """Calculate the angle at the neutral position.

        :return: (int) angle in degrees

        """
        return 45

    # -----------------------------------------------------------------------

    def _calculate_angle_b(self) -> int:
        """Calculate the angle at the cheek bone position.

        :return: (int) angle in degrees

        """
        return 63

    # -----------------------------------------------------------------------

    def _calculate_angle_c(self) -> int:
        """Calculate the angle at the chin position.

        :return: (int) angle in degrees

        """
        return 57

    # -----------------------------------------------------------------------

    def _calculate_angle_m(self) -> int:
        """Calculate the angle at the mouse position.

        :return: (int) angle in degrees

        """
        return 60

    # -----------------------------------------------------------------------

    def _calculate_angle_s(self) -> int:
        """Calculate the angle at the side position.

        :return: (int) angle in degrees

        """
        return 70

    # -----------------------------------------------------------------------

    def _calculate_angle_t(self) -> int:
        """Calculate the angle at the throat position.

        :return: (int) angle in degrees

        """
        return 50
