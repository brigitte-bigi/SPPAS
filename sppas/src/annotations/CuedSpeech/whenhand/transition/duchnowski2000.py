# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.duchnowski2000.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictors. (Duchnowski et al. 2000) model.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

from .basewhen import BaseWhenTransitionPredictor

# ---------------------------------------------------------------------------


MSG_DESCRIPTION_DUCHNOWSKI = \
    "The moments D2 and M2 are predicted 100ms before the moment A1;" \
    "and both the shape and position transitions duration are 150ms."

# ---------------------------------------------------------------------------


class WhenTransitionPredictorDuchnowski2000(BaseWhenTransitionPredictor):
    """Predict hand transition moments with (Duchnowski et al., 2000) method.

    > Paul Duchnowski, David S. Lum, Jean C. Krause, Matthew G. Sexton,
    > Maroula S. Bratakos, and Louis D. Braida
    > Development of Speechreading Supplements Based in Automatic Speech Recognition
    > IEEE Transactions on Biomedical Engineering, vol. 47, no. 4, pp. 487-496, 2000.
    > doi: 10.1109/10.828148.

    In section III.C (page 491) of this paper:
    "The 'dynamic' display used heuristic rules to apportion cue display time
    between time paused at target positions and time spent in transition
    between these positions. Typically, 150 ms was allocated to the transition
    provided the hand could pause at the target position for at least 100 ms.
    The movement between target positions was, thus, smooth unless the cue was
    short, in which case it would tend to resemble the original 'static'
    display."

    The 'static' system mentioned here is their previous system with no
    transition duration described in (Duchnowski et al., 1998).

    """

    def __init__(self):
        """Instantiate (Duchnowski et al. 2000) hand transition moment's predictor.

        """
        super(WhenTransitionPredictorDuchnowski2000, self).__init__()
        self._description = MSG_DESCRIPTION_DUCHNOWSKI

    # -----------------------------------------------------------------------

    def predict_position(self, **kwargs) -> tuple:
        """Predict [M1,M2] the moments when the hand is moving.

        :return: (m1: float, m2: float)

        """
        # Predict M1 - when movement started
        m1 = max(0., self.a1 - 0.250)

        # Predict M2 - when movement ended
        m2 = max(0., self.a1 - 0.100)

        return m1, m2

    # -----------------------------------------------------------------------

    def predict_shape(self, **kwargs) -> tuple:
        """Predict [D1,D2] the moments when fingers are changing.

        :return: (d1: float, d2: float)

        """
        # Predict D1 - when the shape started to change
        d1 = max(0., self.a1 - 0.250)

        # Predict D2 - when the shape is well-formed
        d2 = max(0., self.a1 - 0.100)

        return d1, d2
