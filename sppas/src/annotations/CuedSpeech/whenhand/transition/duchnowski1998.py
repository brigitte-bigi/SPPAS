"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.transition.duchnowski1998.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Hand transition predictors. (Duchnowski et al. 1998) model.

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
    "The moments [D1,D2] and [M1,M2] are predicted 100ms before " \
    "the moment A1; and there's no transition time."

# ---------------------------------------------------------------------------


class WhenTransitionPredictorDuchnowski1998(BaseWhenTransitionPredictor):
    """Predict hand transition moments with (Duchnowski et al., 1998) method.

    > Paul Duchnowski, Louis D. Braida, David S. Lum, Matthew G. Sexton, Jean C. Krause, Smriti Banthia
    > AUTOMATIC GENERATION OF CUED SPEECH FOR THE DEAF: STATUS AND OUTLOOK
    > https://www.isca-speech.org/archive/pdfs/avsp_1998/duchnowski98_avsp.pdf

    In section 2.2 of this paper:
    "We found that cues are often formed before the corresponding sound is
    produced. To approximate this effect we adjusted the start times of cues
    to begin 100 ms before the boundary determined from acoustic data by the
    cue recognizer."

    Reference is:
    > Paul Duchnowski, Louis Braida, Maroula Bratakos, David Lum, Matthew Sexton, Jean Krause
    > A SPEECHREADING AID BASED ON PHONETIC ASR
    > https://isca-speech.org/archive_v0/archive_papers/icslp_1998/i98_0589.pdf

    In section 3.2 of this paper:
    "We observed that human cuers often begin to form a cue before producing
    the corresponding audible sound. To approximate this effect we adjusted
    the start times of the cues to begin 100 ms before the boundary determined
    by the cue recognizer."

    In this class, no transition time values are estimated. The returned
    intervals are [A1-0.1,A1-0.1] and [A1-0.1,A1-0.1].

    """

    def __init__(self):
        """Instantiate (Duchnowski et al. 1998) hand transition moment's predictor.

        """
        super(WhenTransitionPredictorDuchnowski1998, self).__init__()
        self._description = MSG_DESCRIPTION_DUCHNOWSKI

    # -----------------------------------------------------------------------

    def predict_position(self, **kwargs) -> tuple:
        """Predict [M1,M2] the moments when the hand is moving.

        :return: (m1: float, m2: float)

        """
        # Predict M1 - when movement started
        m1 = max(0., self.a1 - 0.100)

        # Predict M2 - when movement ended
        m2 = max(0., self.a1 - 0.100)

        return m1, m2

    # -----------------------------------------------------------------------

    def predict_shape(self, **kwargs) -> tuple:
        """Predict [D1,D2] the moments when fingers are changing.

        :return: (d1: float, d2: float)

        """
        # Predict D1 - when the shape started to change
        d1 = max(0., self.a1 - 0.100)

        # Predict D2 - when the shape is well-formed
        d2 = max(0., self.a1 - 0.100)

        return d1, d2
