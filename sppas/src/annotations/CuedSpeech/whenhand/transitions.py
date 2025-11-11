# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transitions.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transitions predictors. Answer the "When?" question.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

import logging

from sppas.core.coreutils import sppasKeyError

from .transition import BaseWhenTransitionPredictor
from .transition import WhenTransitionPredictorDuchnowski1998
from .transition import WhenTransitionPredictorDuchnowski2000
from .transition import WhenTransitionPredictorAttina
from .transition import WhenTransitionPredictorRules
from .transition import WhenTransitionPredictorRevisedRules
from .whenhandexc import sppasCuedPredictorError

# ---------------------------------------------------------------------------


class WhenTransitionPredictor(object):
    """Hand transitions predictor for both hand shape and hand position.

    There are several solutions to estimate transition intervals. These
    solutions make use of A1-A3 values, i.e., the 'begin' and 'end' time
    values of a key interval:

                        A1             A2             A3
                        | ---- C ----- | ----- V ---- |
                        | ---- C -------------------- |
                        | -------------------- V -----|

    Five solutions are implemented in the form of generator classes predicting the
    transition intervals [M1, M2] and [D1, D2]:

    Implemented predictors will predict:

    - the moments [M1, M2] when the hand is moving from a previous position to
      the current one (the vowel);
    - the moments [D1, D2] when the hand is changing from a previous shape to
      the current one (the consonant).

    Implemented models are:

    - model 0 (Base): moments at the same time as the key
    - model 1 (Duchnowski et al. 1998): moments M1-M2 are both 100ms before the key
    - model 2 (Duchnowski et al. 2000): moment M2 100ms before the key, M1-M2 transition is 150ms
    - model 3 (Attina, 2005): moments proportional to key duration
    - model 4 (custom rules): custom rules based on our expertise in coding.
    - model 5 (revised rules): revised rules based on observed values in CleLfPC dataset.

    """

    # A dictionary to associate a version number and a class to instantiate.
    HAND_TRANSITIONS = dict()
    HAND_TRANSITIONS[0] = BaseWhenTransitionPredictor
    HAND_TRANSITIONS[1] = WhenTransitionPredictorDuchnowski1998
    HAND_TRANSITIONS[2] = WhenTransitionPredictorDuchnowski2000
    HAND_TRANSITIONS[3] = WhenTransitionPredictorAttina
    HAND_TRANSITIONS[4] = WhenTransitionPredictorRules
    HAND_TRANSITIONS[5] = WhenTransitionPredictorRevisedRules

    # The default version number used to define a prediction system.
    DEFAULT = 4

    # -----------------------------------------------------------------------

    @staticmethod
    def version_numbers() -> list:
        """Return the whole list of supported version numbers."""
        return list(WhenTransitionPredictor.HAND_TRANSITIONS.keys())

    # -----------------------------------------------------------------------

    def __init__(self, version_number: int = DEFAULT):
        """Create a hand transitions predictor.

        :param version_number: (int) Version of the predictor system ranging (0-3).

        """
        self.__predictor = None
        self.__version = WhenTransitionPredictor.DEFAULT
        self.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def get_a1a3_avg_duration(self) -> float:
        """Return the average of stored [A1;A3] durations or the fixed one.

        If there's not enough known [A1;A3] durations, the fixed value is
        returned.

        """
        return self.__predictor.get_a1a3_avg_duration()

    # -----------------------------------------------------------------------

    def get_version_number(self) -> int:
        """Return the version number of the selected predictor (int)."""
        return self.__version

    # -----------------------------------------------------------------------

    def set_version_number(self, version_number: int) -> None:
        """Change the predictor version number.

        It invalidates the current values of A1 and A3.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number

        """
        authorized = self.version_numbers()
        try:
            v = int(version_number)
            if v not in authorized:
                raise sppasKeyError(str(authorized), version_number)
        except ValueError:
            logging.error("Hand transition: invalid predictor version {}. "
                          "Expected one of: {}".format(version_number, authorized))
            raise sppasKeyError(str(authorized), version_number)

        # The given version is correct.
        self.__version = v
        self.__predictor = WhenTransitionPredictor.HAND_TRANSITIONS[self.__version]()

    # -----------------------------------------------------------------------

    def set_a(self, a1: float, a3: float, store: bool = True) -> None:
        """Set [A1,A3] the moments of the sounds of a newly observed key.

        Instantiate the predictor with the given interval:

            - a1 - when the 1st phoneme of the key starts in the audio;
            - a3 - when the 2nd phoneme of the key ends in the audio.

        :param a1: (float) Start time value of a key
        :param a3: (float) End time value of a key
        :param store: (bool) Store the a1 and a3 values into a list
        :raises: sppasTypeError: one of a1 or a3 is not a float
        :raises: RangeBoundsException: if a3 is lesser than a1
        :raises: sppasCuedPredictorError: No predictor system is defined

        """
        if self.__predictor is None:
            raise sppasCuedPredictorError
        self.__predictor.set_key_interval(a1, a3, store)

    # -----------------------------------------------------------------------

    def reset_key_intervals(self):
        """Forget the stored A1,A3 moments."""
        self.__predictor.reset_key_intervals()

    # -----------------------------------------------------------------------

    def predict_m(self, **kwargs) -> tuple:
        """Predict [M1,M2] the moments when the hand is moving.

        Make use of the defined predictor and estimates the position
        transition moments:

            - Predict M1 - when leaving the current position
            - Predict M2 - when arrived to the expected position

        Neutral means it's not a phoneme: the key is 0-n.
        A nil shape means it's a key of type -V.

        Depending on the predictor, possible arguments are:

         - rank: (int) The rank of the key after a silence (sil=0, 1st key=1, ...)
         - is_nil_shape: (bool) The shape is nil, i.e. there's no consonant in the syllable (N-V)

        :return: tuple(float, float) The interval [M1,M2] or (0.,0.)
        :raises: sppasCuedPredictorError: No predictor defined.

        """
        if self.__predictor is None:
            raise sppasCuedPredictorError
        return self.__predictor.predict_position(**kwargs)

    # -----------------------------------------------------------------------

    def predict_d(self, **kwargs) -> tuple:
        """Predict [D1,D2] the moments when fingers are changing.

        Make use of the defined predictor and estimates the shape transition
        moments:

            - Predict D1 - when starting to move fingers
            - Predict D2 - when ending to move fingers

        Depending on the predictor, possible arguments are:
         - rank: (int) The rank of the key after a silence (sil=0, 1st key=1, ...)
         - is_nil_shape: (bool) The shape is nil, i.e. there's no consonant in the syllable (N-V)

        :return: tuple(float, float) The interval [D1,D2] or (0.,0.)
        :raises: sppasCuedPredictorError: No predictor defined.

        """
        if self.__predictor is None:
            raise sppasCuedPredictorError
        return self.__predictor.predict_shape(**kwargs)
