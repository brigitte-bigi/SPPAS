# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.attina.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictor based on (Attina, 2005) model.

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


MSG_DESCRIPTION_ATTINA = \
    "The moments [M1,M2] and [D1,D2] are estimated proportionally " \
    "to the mean duration of [A1,A3], before the key. "

# ---------------------------------------------------------------------------


class WhenTransitionPredictorAttina(BaseWhenTransitionPredictor):
    """Predict hand transition moments with (Attina, 2005) method.

    > Virginie Attina Dubesset (2005)
    > La langue française parlée complétée (LPC) : production et perception.
    > PhD Thesis of INPG Grenoble, France.
    > Page 117, page 136 and page 148
    > https://tel.archives-ouvertes.fr/file/index/docid/384080/filename/these_attina.pdf

    See page 112 (Experiment 1, no shape change, position changes, CV syllables):

        - The average key duration is 399.5ms
        - M1A1: mean duration is 239 ms (std is 87ms)  => 60%
        - A1M2: mean duration is 37 ms (std is 76ms)   => 9%

    See page 113 (Experiment 1, no shape change, position changes, V syllables):

        - The average key duration is 383.6ms
        - M1A1: mean duration is 183 ms (std is 79ms)  => 47%
        - A1M2: mean duration is 84 ms (std is 64ms)   => 22%

    Both results are summarized in the scheme page 117.

    See page 118 (Experiment 2, shape changes, position doesn't), results page 123-124:

        - The average CV key duration is 275ms
        - D1A1: mean duration is 124 ms (std is 34ms)
        - A1D2: mean duration is 46 ms (std is 35ms)

    See page 119 (Experiment 2, both shape/position change), results page 124-

        - The average CV key duration is 316.3ms
        - D1A1: mean duration is 171 ms (std is 48ms)    => 54%
        - A1D2: mean duration is -3 ms (std is 45ms)     => 0%
        - M1A1: mean duration is 205 ms (std is 54.5ms)  => 65%
        - A1M2: mean duration is 33 ms (std is 50ms)     => 10%

    Both results are summarized in the scheme page 128.

    A general synchronization scheme is proposed page 136 with percentages
    instead of durations; and extended to 3 more speakers page 148.

    The percentages implemented in this class are related to an average
    key duration of 399.5ms (Experiment 1).

    """

    def __init__(self):
        """Instantiate (Attina, 2005) hand transition moment's predictor.

        """
        super(WhenTransitionPredictorAttina, self).__init__()
        self._description = MSG_DESCRIPTION_ATTINA

        # Percentages implemented in this class are related to an average
        # key duration of 399.5ms (Experiment 1).
        self.set_static_duration(0.4)

    # -----------------------------------------------------------------------

    def predict_position(self, is_nil_shape: bool = False, **kwargs) -> tuple:
        """Predict [M1,M2] the moments when the hand is moving.

        To predict M2:
            - if CV key: both page 136 and page 117, M2 is 10% later than A1.
            - if -V key: page 117, M2 is 21% later than A1.
            - if C- key: no information. CV key case is used.

        To predict M1:
            - if CV key: page 136 M1 is 62-65% of A1A3, but page 117, M1 is 60% of A1A3
            - if -V key: page 117, M1 is 46% of A1A3
            - if C- key: no information. CV key case is used.

        :param is_nil_shape: (bool) True is the key is of the form "-V", i.e. no consonant
        :return: tuple(m1: float, m2: float)

        """
        a3a1 = self.get_a1a3_avg_duration()

        if is_nil_shape is False:  # key is CV or C-
            # Both page 136 and page 117, in a CV key, M2 is 10% later than A1.
            # Page 148, the 3 speakers are at 6%, 10% and 18%.
            a1m2 = a3a1 * 0.10
            # At page 136, in a CV key, M1 is 62-65% of A1A3, but page 117,
            # in a CV key, M1 is 60% of A1A3. Speakers of page 148 are 60%,
            # 61% and 63%. So 62% is a good value.
            m1a1 = a3a1 * 0.62
        else:  # key is -V
            # In page 117, in a -V key, M2 is 21% later than A1.
            a1m2 = a3a1 * 0.21
            # In page 117, in a -V key, M1 is 46% of A1A3.
            m1a1 = a3a1 * 0.46

        # M1 is before A1.
        m1 = max(0., self.a1 - m1a1)
        # M2 is after A1.
        m2 = self.a1 + a1m2

        return m1, m2

    # -----------------------------------------------------------------------

    def predict_shape(self, is_nil_shape: bool = False, **kwargs) -> tuple:
        """Predict [D1,D2] the moments when fingers are changing.

        D1 and D2 are predicted from the key duration only. Following the
        model proposed page 136:

        - D2 is right before A1 (1%).
        - Estimating D1D2 interval, which is 55% of A3A1, gives D1 position
          related to D2.

        :return: (d1: float, d2: float)

        """
        a3a1 = self.get_a1a3_avg_duration()

        # D1 is 54% of A1A3 before A1.
        if is_nil_shape is False:
            d2d1 = a3a1 * 0.54
        else:
            # Improvised value... because not in the reference
            d2d1 = a3a1 * 0.36

        d1 = max(0., self.a1 - d2d1)
        d2 = self.a1

        return d1, d2
