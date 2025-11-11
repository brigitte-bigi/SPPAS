# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.positions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Predict vowel positions from given sights with a model number.

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

from sppas.src.imgdata import sppasSights

from .basepredictor import BaseWhereModelPredictor
from .position import BaseWherePositionPredictor
from .position import WherePositionPredictorCustoms
from .position import WherePositionPredictorUnified
from .position import WherePositionPredictorObserved
from .wherecueexc import sppasCuedPredictorError

# ---------------------------------------------------------------------------


class WhereVowelPositionsPredictor(BaseWhereModelPredictor):
    """Predict the coordinates of vowels from 2D sights of a face.

    """

    # The default version number used to define a prediction system.
    DEFAULT_VERSION = 3

    # -----------------------------------------------------------------------

    def __init__(self, version_number: int = DEFAULT_VERSION):
        """Create a hand transitions predictor.

        :param version_number: (int) Version of the predictor system ranging (0-3).

        """
        super(WhereVowelPositionsPredictor, self).__init__()

        # A dictionary to associate a version number and a class to instantiate.
        self._models[0] = BaseWherePositionPredictor
        self._models[1] = WherePositionPredictorCustoms
        self._models[2] = WherePositionPredictorObserved
        self._models[3] = WherePositionPredictorUnified

        self.set_version_number(version_number)

    # -----------------------------------------------------------------------

    def get_sights_dim(self):
        """Return the number of sights this predictor was trained for."""
        return self._model.get_sights_dim()

    # -----------------------------------------------------------------------

    def set_sights_and_predict_coords(self, sights: sppasSights = None, vowels: tuple = None):
        """Set the sights of a face and predict all vowel positions.

        If no sights are provided, it uses default sights. It validates the
        input type and the number of sights before setting them and predicting
        vowel coordinates.

        :param sights: (sppasSights | None)
        :param vowels: (tuple | None) List of vowel position names. Default is all known ones.
        :raises: sppasTypeError: given parameter is not a sppasSights type.
        :raises: NotImplementedError: not the expected number of sights

        """
        if self._model is None:
            raise sppasCuedPredictorError
        self._model.set_sights_and_predict_coords(sights, vowels)

    # -----------------------------------------------------------------------

    def predict_vowels_coords(self, vowels=('n', )) -> None:
        """Estimate the absolute position of all the vowels.

        Estimate the absolute positions of specified vowels relative to the
        sights of a face. It uses predefined coordinates and calculations
        to determine these positions and stores them in a dictionary.
        Sights must be set before using this method.

        :param vowels: (tuple) List of vowel position names. If unknown, 'n' is used instead.
        :raises: sppasKeyError: Invalid given vowel code.

        """
        self._model.predict_vowels_coords(vowels)

    # -----------------------------------------------------------------------

    def get_vowel_coords(self, vowel: str = 'n') -> tuple:
        """Return the absolute position of the given vowel.

        Estimated relatively to the sights of a face. Sights must be set
        before using this method.

        :param vowel: (char) Vowel position name. If unknown, 'n' is used instead.
        :return: tuple(x, y, r) with point coordinates and radius
        :raises: sppasKeyError: Invalid given vowel code.

        """
        return self._model.get_vowel_coords(vowel)
