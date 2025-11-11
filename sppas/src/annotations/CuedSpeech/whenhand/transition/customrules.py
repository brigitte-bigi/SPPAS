# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.customs.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictor: a custom RBS model.

.. _This file is part of SPPAS: <https://sppas.org/>
..
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from .basewhen import BaseWhenTransitionPredictor

# ---------------------------------------------------------------------------

MSG_DESCRIPTION_RULES = \
    "The moments [D1,D2] and [M1,M2] are with some custom rules made by " \
    "experts."

# ---------------------------------------------------------------------------


class WhenTransitionPredictorRules(BaseWhenTransitionPredictor):
    """Predict hand transition moments with a rule-based system.

    It is inspired from the synchronization model in Attina (2005) and the
    automatic system in (Duchnowski et al. 2000).
    It is also inspired by (Bratakos et al., 1998): "A critical delay
    to display the hand cue is +165ms. The max delay is +100ms.
    A non-significant delay is +33ms.":

    > Maroula S. Bratakos, Paul Duchnowski and Louis D. Braida
    > Toward the Automatic Generation of Cued Speech
    > Cued Speech Journal VI 1998 p1-37.
    > (c) 1998 National Cued Speech Association, Inc.

    The system implements the following rules to estimate [M1;M2]:
    - Like (Duchnowski et al. 1998), the structure of the key does not matter.
    - M2 is before A1, like in (Duchnowski et al. 1998) but not that much
    - The position transition of the first key after a silence (from neutral)
      is very early before the sound. The 2nd key of a speech segment
       is also proportionally earlier than the next ones. See predict_pos_generic().
    - The position transition from the last key of a speech segment to the
      neutral one (to a long silence), is delayed. See predict_pos_to_neutral().
    - They are estimated proportionally to the average duration of *observed*
      A1A3 intervals.

    """

    def __init__(self):
        """Instantiate a custom hand transition moment's predictor.

        """
        super(WhenTransitionPredictorRules, self).__init__()
        self._description = MSG_DESCRIPTION_RULES

    # -----------------------------------------------------------------------
    # Predict the position transition
    # -----------------------------------------------------------------------

    def predict_position(self, rank: int = 4, **kwargs) -> tuple:
        """Predict [M1;M2] the moments when the hand is moving.

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :return: (m1: float, m2: float)

        """
        if rank == 0:
            # Transition to the neutral position.
            return self._predict_pos_to_neutral()

        # Transition to any key inside a speech segment.
        m1, m2 = self._predict_pos_generic(rank)

        # Do not go too far away...
        # The transition to the key must be completed before the end of the
        # corresponding pronounced sounds, so before A3.
        m2 = min(m2, self.a3)
        m1 = min(m1, m2)

        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_to_neutral(self) -> tuple:
        """Predict [M1;M2] for a destination key NN.

        [A1;A3] is a silence, so the transition is from a previous sounded key
        (CV, -V or C-) to the neutral one. This transition is delayed compared
        to the other ones.

        :return: tuple(float, float)

        """
        a3a1 = self.get_static_duration()
        m1 = self.a1 + (a3a1 * 0.2)
        m2 = m1 + (a3a1 * 0.8)
        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_generic(self, rank: int = 3) -> tuple:
        """Predict [M1;M2] for a destination key CV or C-.

        SPPAS 4.22, which was evaluated at ALPC 2024, was:
            - m2a1 = a3a1 * 0.05
            - m1a1 =
                if rank == 1: m1a1 = max(0.500, a3a1 * 1.25)
                if rank == 2: m1a1 = max(0.250, a3a1)
                else: a3a1 * 0.9

        m2a1 is a compromise value between the 100ms before a1 of (Duchnowski
        et al., 2000), and the 10% after a1 of (Attina, 2005).

        :param rank: (int) Rank of the key into the speech segment
        :return: tuple(float, float)

        """
        a3a1 = self.get_a1a3_avg_duration()

        if rank == 1:
            # First sounding segment after a silence. Movement is anticipated.
            m1a1 = max(0.500, a3a1 * 1.40)
            m2a1 = min(0.150, a3a1 * 0.20)

        elif rank == 2:
            # Second sounding segment after a silence.
            m1a1 = max(0.350, a3a1 * 1.15)
            m2a1 = min(0.150, a3a1 * 0.15)

        elif rank == 3:
            # Third sounding segment after a silence.
            m1a1 = max(0.250, a3a1)
            m2a1 = min(0.100, a3a1 * 0.10)

        else:
            m1a1 = a3a1 * 0.9
            m2a1 = a3a1 * 0.05

        # Both M1 and M2 are before A1.
        m1 = max(0., self.a1 - m1a1)
        m2 = max(m1, self.a1 - m2a1)

        return m1, m2

    # -----------------------------------------------------------------------
    # Predict the shape transition
    # -----------------------------------------------------------------------

    def predict_shape(self, rank: int = 3, **kwargs) -> tuple:
        """Predict [D1;D2] the moments when fingers are changing.

        It is considered but not proved that:

        - D1 is after M1; and
        - D2 is before M2;
        - [D1;D2] is a relative fast change and must occur asap.

        SPPAS 4.22, which was evaluated at ALPC 2024, was:
            - d2a1 = a3a1 * 0.4
             - d1a1 =
             if rank == 1: d1a1 = max(0.500, a3a1 * 1.25)
             if rank == 2: d1a1 = max(0.250, a3a1)
             else: d1a1 = a3a1 * 0.7

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :return: (d1: float, d2: float)

        """
        a3a1 = self.get_a1a3_avg_duration()

        if rank == 0:
            # Both the target position and the target shape are neutral.
            return self._predict_shp_to_neutral()

        elif rank == 1:
            # First sounding segment after a silence.
            d1a1 = max(0.450, a3a1 * 1.1)
            d2a1 = a3a1 * 0.8

        elif rank == 2:
            # Second sounding segment after a silence.
            d1a1 = max(0.300, a3a1 * 0.95)
            d2a1 = a3a1 * 0.65

        elif rank == 3:
            # Third sounding segment after a silence.
            d1a1 = max(0.200, a3a1 * 0.8)
            d2a1 = a3a1 * 0.5

        else:
            d1a1 = a3a1 * 0.7
            d2a1 = a3a1 * 0.4

        # Both D1 and D2 are before A1.
        d1 = max(0., self.a1 - d1a1)
        d2 = max(d1, self.a1 - d2a1)

        return d1, d2

    # -----------------------------------------------------------------------

    def _predict_shp_to_neutral(self) -> tuple:
        """Predict [D1;D2] for a destination key NN.

        [A1;A3] is a silence, so the transition is from a previous sounded key
        (CV, -V or C-) to the neutral one.

        :return: tuple(float, float)

        """
        a3a1 = self.get_static_duration()
        d1 = self.a1 + (a3a1 * 0.3)
        d2 = d1 + (a3a1 * 0.4)
        return d1, d2
