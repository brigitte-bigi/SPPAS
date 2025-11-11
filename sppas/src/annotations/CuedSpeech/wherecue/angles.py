"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.angles.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Predict hand angles for given shapes.

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

from __future__ import annotations
import logging

from sppas.core.coreutils import sppasTypeError

from .basepredictor import BaseWhereModelPredictor
from .angle import BaseWhereAnglePredictor
from .angle import WhereAnglePredictorObserved
from .angle import WhereAnglePredictorCustoms
from .angle import WhereAnglePredictorUnified

# ---------------------------------------------------------------------------


class WhereAnglesPredictor(BaseWhereModelPredictor):
    """Predict the angle of the wrist/arm.

    """

    # The default version number used to define a prediction system.
    DEFAULT_VERSION = 3

    # -----------------------------------------------------------------------

    def __init__(self, version_number: int = DEFAULT_VERSION):
        """Create a hand transitions predictor.

        :param version_number: (int) Version of the predictor system ranging (0-3).

        """
        super(WhereAnglesPredictor, self).__init__()

        # A dictionary to associate a version number and a class to instantiate.
        self._models[0] = BaseWhereAnglePredictor
        self._models[1] = WhereAnglePredictorCustoms
        self._models[2] = WhereAnglePredictorObserved
        self._models[3] = WhereAnglePredictorUnified

        # Set the model and version from the given version number
        self.set_version_number(version_number)

        # Options of this class:
        self.__use_face = False

    # -----------------------------------------------------------------------

    def get_use_face(self) -> bool:
        """Return True if the hand angle must be corrected by the one of the face."""
        return self.__use_face

    def set_use_face(self, value: bool) -> None:
        """Set if the angle of the hand has to be corrected by the one of the face.

        :param value: (bool) True if the angle of the hand has to be corrected.

        """
        self.__use_face = bool(value)

    use_face = property(get_use_face, set_use_face)

    # -----------------------------------------------------------------------

    def predict_angle_values(self, vowels=('n', )) -> None:
        """Estimate the angle of the wrist for all vowels.

        Estimate the angle in degrees of the wrist for specified vowels,
        and stores them in a dictionary of the predictor.

        :param vowels: (tuple) List of vowel position names. If unknown, 'n' is used instead.
        :raises: sppasKeyError: Invalid given vowel code.

        """
        self._model.predict_angle_values(vowels)

    # -----------------------------------------------------------------------

    def get_angle(self, vowel: str = 'n', face_angle: int = 90) -> int:
        """Return the angle of the wrist at the given vowel.

        :param vowel: (char) Vowel position name. If unknown, 'n' is used instead.
        :param face_angle: (int) Angle value of the face
        :return: (int) angle in degrees
        :raises: sppasKeyError: Invalid given vowel code.

        """
        value = self._model.get_angle(vowel)
        if self.__use_face is True and face_angle is not None:
            try:
                face_angle = int(face_angle)
            except ValueError:
                raise sppasTypeError("int", str(type(face_angle)))
            if face_angle < 88:
                value -= 3
                logging.debug(" ... Hand angle corrected by -3° (face is {}°)"
                              "".format(face_angle))
            elif face_angle > 92:
                value += 2
                logging.debug(" ... Hand angle corrected by +2° (face is {}°)"
                              "".format(face_angle))

            else:
                # for smoothing.
                correctness = (face_angle - 90) // 2
                value += correctness

        return value
