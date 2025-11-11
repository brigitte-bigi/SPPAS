"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.whereangles.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: CS Hand angle coordinates predictor. Answer the "Where?" question.

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

from __future__ import annotations

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.calculus import observed_angle

from .angles import WhereAnglesPredictor

# ---------------------------------------------------------------------------


class sppasWhereAnglesPredictor:
    """Predict the angle of the wrist at all vowel positions.

    Create a tier indicating the angles.

    """

    def __init__(self, predictor_version=WhereAnglesPredictor.DEFAULT_VERSION):
        """Create a new instance of angles predictor.

        """
        # Predictor system. Use the default number of sights.
        self.__predictor = WhereAnglesPredictor(predictor_version)

    # -----------------------------------------------------------------------

    def version_numbers(self) -> list:
        """Return the whole list of supported version numbers."""
        return self.__predictor.version_numbers()

    # -----------------------------------------------------------------------

    def get_version_number(self) -> int:
        """Return the version number of the selected predictor (int)."""
        return self.__predictor.get_version_number()

    # -----------------------------------------------------------------------

    def set_version_number(self, version_number: int) -> None:
        """Change the predictor version number.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number

        """
        self.__predictor.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def get_use_face(self) -> bool:
        """Return True if the hand angle must be corrected by the one of the face."""
        return self.__predictor.use_face

    def set_use_face(self, value: bool) -> None:
        """The angle of the hand is corrected by the one of the face or not.

        :param value: (bool) True if the angle of the hand has to be corrected.

        """
        self.__predictor.use_face = value

    # -----------------------------------------------------------------------

    def hand_angles(self, tier_pos: sppasTier, face_sights: sppasTier = None):
        """Predict the angles for the given vowels.

        Notice that the coordinates of the position can have negative values.

        :param tier_pos: (sppasTier) Coordinates of the vowel positions.
        :param face_sights: (sppasTier) Sights of the face corresponding to each vowel.
        :return: (sppasTier) tier with name 'CS-HandAngle'

        """
        # Estimate the angles of the hand
        angles = self.__eval_hand_angle(tier_pos, face_sights)

        # Turn the list into a tier
        angles_tier = sppasTier("CS-HandAngle")
        for ann, angle in zip(tier_pos, angles):
            loc = ann.get_location().copy()
            tag = sppasTag(angle, tag_type="int")
            angles_tier.create_annotation(loc, sppasLabel(tag))

        return angles_tier

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __eval_hand_angle(self, hand_pos_probas, face_sights):
        """Return angle of the hand for each ann in given tier.

        :param hand_pos_probas: (sppasTier) Coordinates of the vowel positions.
        :param face_sights: (sppasTier) Sights of the face corresponding to each vowel.
        :return: (list) Angle values -- one for each ann in given tier.

        """
        angles = list()

        for i in range(len(hand_pos_probas)):

            # Extract information from the given tier
            cur_vowels = list()
            cur_probas = list()
            for label in hand_pos_probas[i].get_labels():
                for tag, score in label:
                    cur_vowels.append(tag.get_content())
                    cur_probas.append(score)

            face_angle = 90
            if face_sights is not None:
                _, _, sights = face_sights[i]
                face_angle = observed_angle((sights.x(8), sights.y(8)), (sights.x(27), sights.y(27)))

            # Predict the angle for all the vowels
            self.__predictor.predict_angle_values(cur_vowels)

            if len(cur_vowels) == 1:
                # The hand is at a target position.
                # Store the angle for the only one vowel
                angles.append(self.__predictor.get_angle(cur_vowels[0], face_angle))

            elif len(cur_vowels) == 2:
                # The hand is moving from a position to another one.
                # Get the destination angle and estimate the diff
                angle1 = self.__predictor.get_angle(cur_vowels[0], face_angle)
                angle2 = self.__predictor.get_angle(cur_vowels[1], face_angle)
                da = angle2 - angle1
                # Estimate the new angle by using the probabilities
                na = angle1 + int(float(da) * cur_probas[1])
                angles.append(na)

        return angles
