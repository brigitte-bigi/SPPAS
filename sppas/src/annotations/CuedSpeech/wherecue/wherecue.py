# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.wherecue.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  CS Hand coordinates predictor. Answer the "Where?" question.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

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

    ---------------------------------------------------------------------

"""

import logging

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTranscription
from sppas.src.imgdata import sppasSights
from sppas.src.annotations.FaceSights import sppasSightsVideoReader

from ..whatkey import CuedSpeechCueingRules

from .faceheight import sppasFaceHeightGenerator
from .positions import WhereVowelPositionsPredictor
from .angles import WhereAnglesPredictor
from .wherepositions import sppasWherePositionsPredictor
from .whereangles import sppasWhereAnglesPredictor
from .targetprobas import TargetProbabilitiesEstimator

# ---------------------------------------------------------------------------


class sppasWhereCuePredictor(object):
    """Create a tier indicating the position of 2 points of the hand.

    Predict the position of points S0 and S9 of an hand relatively to
    sights of a face.

    """

    def __init__(self,
                 pos_predictor_version: int = WhereVowelPositionsPredictor.DEFAULT_VERSION,
                 angle_predictor_version: int = WhereAnglesPredictor.DEFAULT_VERSION,
                 cue_rules: CuedSpeechCueingRules = CuedSpeechCueingRules()):
        """Create a new instance.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        if isinstance(cue_rules, CuedSpeechCueingRules) is False:
            raise sppasTypeError("cue_rules", "CuedSpeechCueingRules")

        # Default number of faces per second
        self.__fps = 50

        # Prediction system for the coordinates of the vowel positions
        self.__pos_predictor = sppasWherePositionsPredictor(pos_predictor_version)

        # Prediction system for the angle of the wrist/arm
        self.__angle_predictor = sppasWhereAnglesPredictor(angle_predictor_version)

        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = None

        # A temporary solution, during the period the Proof of Concept
        # is turned into a stable and clean program.
        self.__gentargets = TargetProbabilitiesEstimator()

        # Assign the cue rules
        self.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def get_wherepositionpredictor_versions(self) -> list:
        """Return the list of version numbers of the vowel positions generator system."""
        return self.__pos_predictor.version_numbers()

    # -----------------------------------------------------------------------

    def get_whereanglepredictor_versions(self) -> list:
        """Return the list of version numbers of the angles generation system."""
        return self.__angle_predictor.version_numbers()

    # -----------------------------------------------------------------------

    def get_wherepositionpredictor_version(self) -> int:
        """Return the version number of the vowel positions prediction system."""
        return self.__pos_predictor.get_version_number()

    # -----------------------------------------------------------------------

    def get_whereanglepredictor_version(self) -> int:
        """Return the version number of the angle prediction system."""
        return self.__angle_predictor.get_version_number()

    # -----------------------------------------------------------------------

    def set_wherepositionpredictor_version(self, version_number: int) -> None:
        """Change the vowel position predictor version number.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number

        """
        self.__pos_predictor.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def set_whereanglepredictor_version(self, version_number: int) -> None:
        """Change the angle predictor version number.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number

        """
        self.__angle_predictor.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechCueingRules) -> None:
        """Set new rules.

        :param cue_rules: (CuedSpeechCueingRules) Rules and codes for vowel positions and hand shapes
        :raises: sppasTypeError: given parameter is not CuedSpeechCueingRules

        """
        if isinstance(cue_rules, CuedSpeechCueingRules) is False:
            raise sppasTypeError("cue_rules", "CuedSpeechCueingRules")

        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = cue_rules

        # A temporary solution, during the period this Proof of Concept
        # is turned into a stable and clean program.
        self.__gentargets.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------
    # Predictors options
    # -----------------------------------------------------------------------

    def get_angle_use_face(self) -> bool:
        """Return True if the hand angle must be corrected by the one of the face."""
        return self.__angle_predictor.get_use_face()

    def set_angle_use_face(self, value: bool) -> None:
        """The angle of the hand is corrected by the one of the face or not.

        :param value: (bool) True if the angle of the hand has to be corrected.

        """
        self.__angle_predictor.set_use_face(value)

    # -----------------------------------------------------------------------
    # Predictor
    # -----------------------------------------------------------------------

    def predict_where(self, file_sights, tier_pos_transitions, tier_shapes_transitions):
        """Prodict where to cue, hand angle and hand size from face sights.

        :param file_sights: (str) Filename with 68 sights of a face for each image of a video
        :param tier_pos_transitions: (sppasTier) Predicted hand position transitions
        :param tier_shapes_transitions: (sppasTier) Predicted hand shapes transitions
        :return: (sppasTranscription)

        """
        # Load the list of sights of the 1st face from the given file
        face_sights = self._load_sights(file_sights, kid_index=0)

        # Fix the video fps -- used to define length of a queue to smooth coords
        self.__set_fps(face_sights)

        # Predict the size of the hand, for each face in the list
        tier_sizes = sppasFaceHeightGenerator(face_sights).face_height(fps=self.__fps)

        # Predict position of all vowels for each face in the list
        self.__pos_predictor.set_sights(face_sights)
        tier_pos_coords = self.__pos_predictor.vowels_coords(self.__cued.get_vowels_codes(), smooth_len=self.__fps//5)

        # Discretize the position and shape transitions to get position and
        # shape probabilities, for each face in the list
        tier_pos_probas = self.__gentargets.positions_discretization(tier_pos_coords, tier_pos_transitions)
        tier_shp_probas = self.__gentargets.shapes_discretization(tier_pos_coords, tier_shapes_transitions)

        # Predict coordinated of the target point, for each face in the list
        tier_target_coords = self.__gentargets.hands_to_target_coords(tier_pos_probas, tier_pos_coords)

        # Predict the angle of the arm, for each face in the list
        tier_angles = self.__angle_predictor.hand_angles(tier_pos_probas, face_sights)

        # Create an object to store all these results
        trs = sppasTranscription("WhereToCue")
        trs.append(tier_pos_coords)      # CS-VowelsCoords
        trs.append(tier_shp_probas)      # CS-PosProbas
        trs.append(tier_pos_probas)      # CS-ShapeProbas
        trs.append(tier_angles)          # CS-HandAngle
        trs.append(tier_sizes)           # CS-FaceSize
        trs.append(tier_target_coords)   # CS-TargetCoords

        return trs

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _load_sights(self, filename: str, kid_index: int = 0) -> list:
        """Load a filename and store the sights of a given kid.

        The returned data is a list of tuples with:

        - at index 0: midpoint time value
        - at index 1: radius time value
        - at index 2: the 68 sights of a face

        :param filename: (str) Filename of the XRA/CSV with sights
        :param kid_index: (int) index of the kid to get sights
        :raises: sppasWhereCuedSightsValueError: there are sights but there are not of the expected size
        :raises: Exception:
        :return: (list)

        """
        # Sights of each image previously estimated on a video
        # Open the file with sights coordinates dans load all its data
        data = sppasSightsVideoReader(filename)
        cur_sights = self.__get_current_sights(data, kid_index)

        # Fill-in the data with sights of the given kid
        data_sights = list()
        for i, kids_sights in enumerate(data.sights):
            midpoint = data.midpoints[i]
            if midpoint is None:
                # This should never happen... but we can never say never...
                raise Exception("No time point value at index {:d}.".format(i))

            # Get the current sights [only if available]
            if 0 < len(kids_sights) <= kid_index + 1:
                s = kids_sights[kid_index]
                if s is not None:
                    cur_sights = s
                else:
                    logging.warning("No estimated sights at frame number {:d} for kid {:d}."
                                    "".format(i + 1, kid_index))
            else:
                logging.warning("No estimated sights at frame number {:d} for kid {:d}."
                                "".format(i + 1, kid_index))

            # Append the sights to the data
            data_sights.append((midpoint, data.radius[i], cur_sights))

        return data_sights

    # -----------------------------------------------------------------------

    def __set_fps(self, data_sights: list) -> None:
        """Fix the video frames-per-seconds value."""
        if len(data_sights) == 0:
            self.__fps = 50
        else:
            first_midpoint = data_sights[0][0]
            self.__fps = int(1. / first_midpoint)
            logging.debug(f"Video fps={self.__fps}")

    # -----------------------------------------------------------------------

    def __get_current_sights(self, data: sppasSightsVideoReader, kid_index: int) -> sppasSights:
        """Return the sights at given index.

        :param data: (sppasSightsVideoReader) Video reader with sights
        :param kid_index: (int) index of the kid to get sights
        :raises: sppasWhereCuedSightsValueError: there are sights but there are not of the expected size
        :raises: Exception:

        """
        # Get the first set of sights for the given kid and check dimension
        cur_sights = sppasSights()
        for i, kids_sights in enumerate(data.sights):
            if 0 < len(kids_sights) <= kid_index + 1:
                cur_sights = kids_sights[kid_index]
                if cur_sights is not None:
                    break

        return cur_sights
