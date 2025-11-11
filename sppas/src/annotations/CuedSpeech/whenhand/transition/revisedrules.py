# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.revisedrules.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictor: a custom revised RBS model.

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

from .basewhen import BaseWhenTransitionPredictor

# ---------------------------------------------------------------------------

MSG_DESCRIPTION_RULES = \
    "The moments [D1,D2] and [M1,M2] are with some custom rules made by " \
    "experts and updated after the analyses of CleLfPC transitions."

# ---------------------------------------------------------------------------


class WhenTransitionPredictorRevisedRules(BaseWhenTransitionPredictor):
    """Predict hand transition moments with a revised rule-based system.

    The system implements the following rules to estimate [M1;M2]:
    - The structure of the key matters.
    - M2 is before A1, like in (Duchnowski et al. 1998) but not that much
    - The position transition of the first key after a silence (from neutral)
      is very early before the sound. The M2 of the 2nd key of a speech segment
      is also earlier than the next ones.
    - The position transition from the last key of a speech segment to the
      neutral one (to a long silence), is delayed. See predict_pos_to_neutral().
    - They are estimated proportionally to the average duration of *observed*
      A1A3 intervals.

    """

    def __init__(self):
        """Instantiate a custom hand transition moment's predictor.

        """
        super(WhenTransitionPredictorRevisedRules, self).__init__()
        self._description = MSG_DESCRIPTION_RULES

    # -----------------------------------------------------------------------
    # Predict the position transition
    # -----------------------------------------------------------------------

    def predict_position(self, rank: int = 4, **kwargs) -> tuple:
        """Predict [M1;M2] the moments when the hand is moving.

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :return: (m1: float, m2: float)

        """
        rank = int(rank)

        if rank == 0:
            # Transition from a facial key to the neutral position.
            return self._predict_pos_to_neutral()

        if rank == 1:
            # Transition from neutral to the 1st facial key.
            return self._predict_pos_from_neutral()

        # Transition to any key inside a speech segment.
        m1, m2 = self._predict_pos_generic(rank, **kwargs)

        # Do not go too far away...
        # The transition to the key must be completed before the end of the
        # corresponding pronounced sounds, i.e. before A3.
        m2 = min(m2, self.a3)
        m1 = min(m1, m2)

        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_to_neutral(self) -> tuple:
        """Predict [M1;M2] for a destination key NN.

        This transition is delayed compared to the other ones.

        :return: tuple(float, float)

        """
        a3a1 = self.get_static_duration()
        m1a1 = a3a1 * 0.1
        m2a1 = a3a1 * 1.25
        m1 = max(0., self.a1 - m1a1)
        m2 = max(m1, self.a1 + m2a1)

        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_from_neutral(self) -> tuple:
        """Predict [M1;M2] from a silence to the first key on the face.

        This transition is anticipated compared to the other ones.

        :return: tuple(float, float)

        """
        a3a1 = self.get_a1a3_avg_duration()
        m1a1 = max(0.600, a3a1 * 1.60)
        m2a1 = min(0.150, a3a1 * 0.10)

        m1 = max(0., self.a1 - m1a1)
        m2 = max(m1, self.a1 - m2a1)

        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_generic(self, rank: int = 3,
                             is_nil_shape: bool = False,
                             is_nil_pos: bool = False,
                             **kwargs) -> tuple:
        """Predict [M1;M2] for a destination key 'C', 'V' or 'CV'.

        Prediction algorithm is as follows:
        >    if 'C':
        >         m1 = a1 - (a3a1 * 1.60)
        >         m2 = a1 - (a3a1 * 0.30)
        >     elif 'V':
        >         m1 = a1 - (a3a1 * 2.40)
        >         m2 = a1 - (a3a1 * 0.60)
        >     else:
        >         m1 = a1 - (a3a1 * 0.80)
        >         if 2nd_key:
        >             m2 = a1
        >         else
        >             m2 = a1 + (a3a1 * 0.11)

        :param rank: (int) Rank of the key into the speech segment
        :param is_nil_shape: (bool) True is the key is of the form "-V", i.e. no consonant
        :param is_nil_pos: (bool) True is the key is of the form "C-", i.e. no vowel
        :raises: ValueError: invalid rank. It must be > 1.
        :return: tuple(float, float)

        """
        if all((is_nil_shape, is_nil_pos)) is True:
            raise ValueError("For the generic prediction, nil_shape and nil_pos can't "
                             "be both True together.")
        if rank < 2:
            raise ValueError("For the generic prediction, rank must be >= 2.")

        a3a1 = self.get_a1a3_avg_duration()
        if is_nil_pos is True:
            # Key structure is C-.
            m1a1 = max(0.500, a3a1 * 1.60)
            m2a1 = a3a1 * -0.30

        elif is_nil_shape is True:
            # Key structure is '-V'.
            m1a1 = max(0.600, a3a1 * 2.40)
            m2a1 = a3a1 * -0.60

        else:
            m1a1 = max(0.350, a3a1 * 0.80)
            if rank == 2:
                # Second sounding segment after a silence.
                m2a1 = 0.
            else:
                m2a1 = a3a1 * 0.11

        # Both M1 and M2 are before A1.
        m1 = max(0., self.a1 - m1a1)
        m2 = max(m1, self.a1 + m2a1)

        return m1, m2


    # -----------------------------------------------------------------------
    # Predict the shape transition
    # -----------------------------------------------------------------------

    def predict_shape(self, rank: int = 3,
                            is_nil_shape: bool = False,
                            is_nil_pos: bool = False,
                            **kwargs) -> tuple:
        """Predict [D1;D2] the moments when fingers are changing.

        It is considered but not proved that:

        - D1 is after M1; and
        - D2 is before M2;
        - [D1;D2] is a relative fast change and must occur asap.

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :param is_nil_shape: (bool) True is the key is of the form "-V", i.e. no consonant
        :param is_nil_pos: (bool) True is the key is of the form "C-", i.e. no vowel
        :return: (d1: float, d2: float)

        """
        if rank == 0:
            # Both the target position and the target shape are neutral.
            return self._predict_shp_to_neutral()

        elif rank == 1:
            # First sounding segment after a silence.
            return self._predict_shp_from_neutral()

        else:
            a3a1 = self.get_a1a3_avg_duration()
            if is_nil_pos is True:
                # Key structure is C-.
                d1a1 = a3a1 * 1.15 #max(0.450, )
                d2a1 = a3a1 * -0.55

            elif is_nil_shape is True:
                # Key structure is '-V'.
                d1a1 = max(0.400, a3a1 * 1.80)
                d2a1 = a3a1 * -1.20

            else:
                if rank == 2:
                    # Second sounding segment after a silence.
                    d1a1 = a3a1 * 0.8
                    d2a1 = a3a1 * -0.6
                else:
                    d1a1 = a3a1 * 0.65
                    d2a1 = a3a1 * -0.4

            # Both D1 and D2 are before A1.
            d1 = max(0., self.a1 - d1a1)
            d2 = max(d1, self.a1 + d2a1)

            return d1, d2

    # -----------------------------------------------------------------------

    def _predict_shp_to_neutral(self) -> tuple:
        """Predict [D1;D2] for a destination key NN.

        [A1;A3] is a silence, so the transition is from a previous sounded key
        (CV, -V or C-) to the neutral one.

        :return: tuple(float, float)

        """
        a3a1 = self.get_static_duration()
        d1 = self.a1 + (a3a1 * 0.4)
        d2 = self.a1 + (a3a1 * 0.7)
        return d1, d2

    # -----------------------------------------------------------------------

    def _predict_shp_from_neutral(self) -> tuple:
        """Predict [D1;D2] from a key NN to a facial one.

        :return: tuple(float, float)

        """
        a3a1 = self.get_a1a3_avg_duration()
        d1a1 = a3a1 * 1.30
        d2a1 = a3a1 * 0.90

        d1 = max(0., self.a1 - d1a1)
        d2 = max(d1, self.a1 - d2a1)
        return d1, d2
