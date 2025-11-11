# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.customtrees.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictors. Custom decision tree model.

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
    "The moments [D1,D2] and [M1,M2] are estimated with a decision tree"\
    "to be defined."

# ---------------------------------------------------------------------------


class WhenTransitionPredictorRules(BaseWhenTransitionPredictor):
    """Predict hand transition moments with a decision tree system.

    TO BE IMPLEMENTED.

    """

    # Delay when silence
    DELAY = 0.5

    def __init__(self):
        """Instantiate a custom hand transition moment's predictor.

        """
        super(WhenTransitionPredictorRules, self).__init__()
        self._description = MSG_DESCRIPTION_RULES

    # -----------------------------------------------------------------------
    # Predict the position transition
    # -----------------------------------------------------------------------

    def predict_position(self, rank: int = 4,
                         is_nil_shape: bool = False,
                         is_same: bool = False, **kwargs) -> tuple:
        """Predict [M1,M2] the moments when the hand is moving.

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :param is_nil_shape: (bool) The shape is a neutral one (no consonant)
        :param is_same: (bool) The current key is the same as the previous one
        :return: (m1: float, m2: float)

        """
        # A supposed lesser duration if same key
        coefficient = 1.
        if is_same is True:
            coefficient = 0.8

        if rank == 0:
            # Both the position and the shape are neutral. Key is NN.
            m1, m2 = self._predict_pos_to_neutral()
        elif rank == 1:
            # The 1st key after a long silence (from the neutral position).
            m1, m2 = self._predict_pos_from_neutral()
        else:
            if is_nil_shape is False:
                m1, m2 = self._predict_pos_with_shape(rank, coefficient)
            else:
                m1, m2 = self._predict_pos_no_shape(rank, coefficient)

        # Do not go too far away...
        m2 = min(m2, self.a3)
        m1 = min(m1, m2)

        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_to_neutral(self) -> tuple:
        """Predict (m1, m2) for a destination key NN from a CV or C- or -V key.

        [A1,A3] is a silence, so the transition is from a previous sounded key
        (CV, -V or C-) to the neutral one.

        """
        delay = WhenTransitionPredictorRules.DELAY
        a3a1 = self.a3 - self.a1
        m1 = min(self.a1 + (delay // 4), self.a1 + (a3a1 * 0.2))
        m2 = min(m1 + delay, m1 + (a3a1 * 0.6))
        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_from_neutral(self) -> tuple:
        """Predict (m1, m2) for a destination key CV, C- or -V from neutral.

        [A1,A3] is the first sounding segment after a silence.

        """
        a3a1 = self.a3 - self.a1
        a1m2 = a3a1 * 0.
        m2 = self.a1 + a1m2
        m2m1 = a3a1 * 1.60
        m1 = max(0., m2 - m2m1)
        return m1, m2

    # -----------------------------------------------------------------------

    def _predict_pos_with_shape(self, rank: int = 3, coefficient: float = 1.) -> tuple:
        """Predict (m1, m2) for a destination key CV or C-."""
        a3a1 = self.a3 - self.a1

        # This is a CV key
        if rank == 2:
            # The 2nd key after a silence. It is also reaching the
            # target earlier than the other keys.
            a1m2 = a3a1 * 0.
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.82 * coefficient
        elif rank == 3:
            # The 3rd key after a silence. It is also reaching the
            # target earlier than the other keys.
            a1m2 = a3a1 * 0.10
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.72 * coefficient
        else:
            # (Attina, 2005) both page 136 and page 117:
            # in a CV key, M2 is 10% later than A1
            a1m2 = a3a1 * 0.10
            # (Attina, 2005) page 136: in a CV key, M2 is 62-65% of A1A3
            # but page 117: in a CV key, M2 is 60% of A1A3
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.62 * coefficient

        return max(0., self.a1 - m1a1), m2

    # -----------------------------------------------------------------------

    def _predict_pos_no_shape(self, rank: int = 3, coefficient: float = 1.) -> tuple:
        """Predict (m1, m2) for a destination key -V."""
        a3a1 = self.a3 - self.a1

        # This is a -V key.
        # The 1st key after a silence starts before
        if rank == 2:
            a1m2 = a3a1 * 0.02
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.72 * coefficient
        elif rank == 3:
            a1m2 = a3a1 * 0.08
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.62 * coefficient
        else:
            # (Attina, 2005) page 117:
            # in a -V key, M2 is 21% later than A1
            a1m2 = a3a1 * 0.21
            # (Attina, 2005) page 117: in a -V key, M2 is 46% of A1A3
            m2 = max(0., self.a1 + a1m2)
            m1a1 = a3a1 * 0.46 * coefficient

        return max(0., self.a1 - m1a1), m2

    # -----------------------------------------------------------------------
    # Predict the shape transition
    # -----------------------------------------------------------------------

    def predict_shape(self, rank: int = 3, is_nil_shape: bool = False,
                      m1: float = None, m2: float = None, **kwargs) -> tuple:
        """Predict [D1,D2] the moments when fingers are changing.

        :param rank: (int) The rank of the key. 0=silence, 1=1st key after a silence, etc.
        :param is_nil_shape: (bool) The shape is a neutral one (no consonant)
        :param m1: (float) The M1 value
        :param m2: (float) The M2 value
        :return: (d1: float, d2: float)

        """
        a3a1 = self.a3 - self.a1
        delay = WhenTransitionPredictorRules.DELAY

        # Predict D1 - when the shape started to change
        if rank == 0:
            # Both the position and the shape are neutral.
            # [a1-a3] is a (long) silence, so after speech
            d1 = min(self.a1 + (delay // 4), self.a1 + (a3a1 * 0.2))
            d2 = min(d1 + delay, d1 + (a3a1 * 0.4))

        else:
            if rank == 1:
                # The 1st key after a silence. It seems that the shape
                # is formed very early before the phoneme starts;
                # d2 must be (clearly) before m2
                d2 = self.a1 - (d // 2)
                d2d1 = a3a1 * 1.02
                # d1 must be after m1
                d1 = max(0., min(m1 + (delay // 5), d2 - d2d1))

            elif rank == 2:
                # The 2nd key after a silence. It is also reaching the
                # target earlier than the other keys.
                d2 = self.a1 - (d // 4)
                d2d1 = a3a1 * 0.72
                d1 = max(0., d2 - d2d1)

            else:
                # (Attina 2005) page 136:
                # in a CV key, D2 is 1% before A1
                if is_nil_shape is False:
                    # (Attina 2005) page 136:
                    # In the tested version (ALPC, August 2022): a1d2 = a3a1 * 0.01
                    # Transition was finishing too late... Adjusted is:
                    a1d2 = a3a1 * 0.10
                    d2d1 = a3a1 * 0.46
                else:
                    # (Attina 2005) page 136:
                    # In the tested version (ALPC, August 2022): a1d2 = a3a1 * 0.11
                    # Transition was finishing too late... Adjusted is:
                    a1d2 = a3a1 * 0.21
                    # but we adjust transition duration because d1 must be after m1
                    d2d1 = a3a1 * 0.39
                d2 = max(0., self.a1 - a1d2)
                d1 = max(0., d2 - d2d1)

            # But... reduce d2 when [d1, d2] is very long...
            d2d1 = d2 - d1
            if d2d1 > WhenTransitionPredictorRules.DELAY:
                reduce = a3a1 * 0.05
                d2 = max(d1, d2 - reduce)

        # Do not go too far away...
        d2 = min(d2, self.a3)
        # Do not end shape transition after position transition
        if m2 is not None:
            d2 = min(d2, m2)
        d1 = min(d1, d2)
        # Do not start shape transition before position transition
        if m1 is not None:
            d1 = max(d1, m1)
            d2 = max(d1, d2)

        return d1, d2
