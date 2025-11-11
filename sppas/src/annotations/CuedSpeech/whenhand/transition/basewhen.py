# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.basewhen.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Base for hand transition predictors. Answer the "When?" question.

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

from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import RangeBoundsException
from sppas.core.coreutils import IntervalRangeException

# ---------------------------------------------------------------------------


MSG_DESCRIPTION_BASE = \
    "The moments [D1,D2] and [M1,M2] are predicted at" \
    "the moment A1. It means there's no transition time."

# ---------------------------------------------------------------------------


class BaseWhenTransitionPredictor(object):
    """Base class to predict hand transition moments [D1,D2] and [M1,M2].

    A Cued Speech key is defined as follows:

            A1             A2             A3
            | ---- C ----- | ----- V ---- |
            | ---- C -------------------- |
            | -------------------- V -----|

    - A1 is the start time value of the first phoneme of the key;
    - A3 is the end time value of the second phoneme of the key.

    The system aims to predict both the interval [M1,M2], the moments the hand
    is moving from its previous position to the one of the key, and interval
    [D1,D2], the moments the fingers are changing from the previous shape to
    the one of the key.

    In this base class, no transition time values are estimated. The returned
    intervals are [A1,A1] and [A1,A1]. It corresponds to the system presented
    in (Bratakos et al., 1998):
    "Appearance of the cue typically began at the frame corresponding to the
    start of the consonant segment in the acoustic waveform and was maintained
    until the end of the following vowel segment (for CV combinations) or of the
    consonant segment (for consonants occurring alone)."

    Reference is:
    >Maroula S. Bratakos, Paul Duchnowski and Louis D. Braida
    >Toward the Automatic Generation of Cued Speech
    >Cued Speech Journal, vol. VI, pp 1-37, 1998.

    :Example:
    >>> p = BaseWhenTransitionPredictor()
    >>> p.set_key_interval(2.3, 2.8)
    >>> p.a1
    2.3
    >>> p.a3
    2.8
    >>> m1, m2 = p.predict_position()
    >>> print(m1)
    2.3
    >>> print(m2)
    2.3
    >>> d1, d2 = p.predict_shape()
    >>> print(d1)
    2.3
    >>> print(d2)
    2.3
    >>> p.get_static_duration()      # a default key duration
    0.3

    All given intervals [A1;A3] are stored until the reset method is invoked.
    Their average value can be estimated with 'get_a1a3_avg_duration()' method.

    :Example:
    >>> p = BaseWhenTransitionPredictor()
    >>> p.set_key_interval(2., 3.)   # duration is 1.
    >>> p.set_key_interval(3., 5.)   # duration is 2.
    >>> p.get_a1a3_avg_duration()    # average is 1.5
    1.5

    """

    # Based on the observed durations in 5 topics of CLeLfPC corpus.
    # See B. Bigi (2023) https://hal.science/hal-04081282
    DEFAULT_KEY_DURATION = 0.3

    def __init__(self):
        """Instantiate a hand transition moment's predictor.

        """
        # Short description of the transition prediction method
        self._description = MSG_DESCRIPTION_BASE
        # Given [A1;A3] values
        self.__a1 = None
        self.__a3 = None
        # Average duration of a key. Fixed or to be evaluated with [A1;A3]
        self.__avg = BaseWhenTransitionPredictor.DEFAULT_KEY_DURATION
        self.__dur = list()

    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------

    def get_key_interval(self) -> tuple:
        """Return [A1;A3] the moments of the sounds of the last key.

        :return: tuple(a1,a3) if a1 and a3 are known or (0.,0.) if unknown

        """
        if self.__a1 is None:
            return 0., 0.
        return self.__a1, self.__a3

    # -----------------------------------------------------------------------

    def set_key_interval(self, a1: float, a3: float, store: bool = True) -> None:
        """Set [A1;A3] the moments of the sounds of the key.

        Given a1 value represents when the 1st phoneme of the key starts in
        the audio, and a3 represents when the 2nd phoneme of the key ends in
        the audio.

        :param a1: (float) Start time value of a key
        :param a3: (float) End time value of a key
        :param store: (bool) Store the a1 and a3 values into a list
        :raises: sppasTypeError: one of a1 or a3 is not a float
        :raises: RangeBoundsException: if a3 is lesser than a1

        """
        try:
            a1 = float(a1)
        except ValueError:
            raise sppasTypeError(type(a1), "float")
        try:
            a3 = float(a3)
        except ValueError:
            raise sppasTypeError(type(a3), "float")

        if a3 < a1:
            raise RangeBoundsException(a1, a3)

        self.__a1 = a1
        self.__a3 = a3
        if store is True:
            self.__dur.append(a3-a1)

    # -----------------------------------------------------------------------

    def reset_key_intervals(self) -> None:
        """Forget the stored A1-A3 durations."""
        self.__dur = list()

    # -----------------------------------------------------------------------

    def get_a1(self) -> float:
        """Return the lastly given A1 time value.

        :raises: ValueError: Unknown A1 value.

        """
        if self.__a1 is None:
            raise ValueError("Interval [A1;A3] un-defined. A1 un-defined.")
        return self.__a1

    a1 = property(get_a1, None)

    def get_a3(self) -> float:
        """Return the lastly given A3 time value.

        :raises: ValueError: Unknown A3 value.

        """
        if self.__a1 is None:
            raise ValueError("Interval [A1;A3] un-defined. A3 un-defined.")
        return self.__a3

    a3 = property(get_a3, None)

    # -----------------------------------------------------------------------

    def get_static_duration(self) -> float:
        """Return the duration of a key."""
        return self.__avg

    def set_static_duration(self, duration: float) -> None:
        """Set the duration of a key.

        :param duration: (float) Fixed duration of a key.
        :raises: sppasTypeError: if given duration can't be a float.
        :raises: IntervalRangeException: if given duration is < 0.1 or > 1.0.

        """
        try:
            duration = float(duration)
        except ValueError:
            raise sppasTypeError(type(duration), "float")
        if 0.1 <= duration <= 1.0:
            self.__avg = duration
        else:
            raise IntervalRangeException(duration, 0.1, 1.0)

    # -----------------------------------------------------------------------

    def get_a1a3_avg_duration(self) -> float:
        """Return the average of stored [A1;A3] durations or the fixed one.

        :return: (float) Average value or if there's not enough known [A1;A3] durations, the fixed value is returned.

        """
        if len(self.__dur) < 2:
            # Not enough values to estimate properly an average duration
            return self.__avg
        elif len(self.__dur) < 3:
            # Close to enough values to estimate properly an average duration
            return (sum(self.__dur) + self.__avg) / float(len(self.__dur) + 1)
        else:
            return sum(self.__dur) / float(len(self.__dur))

    # -----------------------------------------------------------------------

    def get_description(self) -> str:
        """Return a brief description of the transition estimation method."""
        return self._description

    # -----------------------------------------------------------------------

    def predict_position(self, **kwargs) -> tuple:
        """Predict [M1, M2] the moments when the hand is moving.

        Predict M1 - when leaving the current position
        Predict M2 - when arrived to the expected position

        :return: tuple(m1: float, m2: float)

        """
        if self.__a1 is None:
            raise ValueError("Interval [A1;A3] un-defined.")
        return self.__a1, self.__a1

    # -----------------------------------------------------------------------

    def predict_shape(self, **kwargs) -> tuple:
        """Predict [D1, D2] the moments when fingers are changing.

        Predict D1 - when fingers are starting to move
        Predict D2 - when fingers finished representing the expected shape

        :return: tuple(d1: float, d2: float)

        """
        if self.__a1 is None:
            raise ValueError("Interval [A1;A3] un-defined.")
        return self.__a1, self.__a1
