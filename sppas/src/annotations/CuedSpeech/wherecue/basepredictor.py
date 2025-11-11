# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.basepredictor.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class for multi-models predictors (angles, positions...).

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
from sppas.core.coreutils import sppasKeyError

# ---------------------------------------------------------------------------


class BaseWhereModelPredictor:
    """Base class for any multi-models predictor.

    """

    # The default version number used to define a prediction system.
    DEFAULT_VERSION = 0

    # -----------------------------------------------------------------------

    def __init__(self, *args):
        """Create a hand transitions predictor.

        :param version_number: (int) Version of the predictor system.

        """
        # A dictionary to associate a version number and a class to instantiate.
        self._models = dict()

        self._model = None
        self._version = BaseWhereModelPredictor.DEFAULT_VERSION

    # -----------------------------------------------------------------------

    def version_numbers(self) -> list:
        """Return the whole list of supported version numbers."""
        return list(self._models.keys())

    # -----------------------------------------------------------------------

    def get_version_number(self) -> int:
        """Return the version number of the selected predictor (int)."""
        return self._version

    # -----------------------------------------------------------------------

    def set_version_number(self, version_number: int) -> None:
        """Change the predictor version number.

        :param version_number: (int) One of the supported versions.
        :raises: sppasKeyError: if invalid version number
        :raises: sppasTypeError: invalid type for given version_number

        """
        try:
            v = int(version_number)
        except ValueError:
            raise sppasTypeError("int", str(type(version_number)))

        authorized = self.version_numbers()
        try:
            if v not in authorized:
                raise sppasKeyError(str(authorized), version_number)
        except ValueError:
            logging.error("{}: Invalid predictor version {}. Expected one of: {}"
                          "".format(self.__name__, version_number, authorized))
            raise sppasKeyError(str(authorized), version_number)

        # The given version is correct.
        self._version = v
        self._model = self._models[self._version]()

    model_version = property(get_version_number, set_version_number)

    # -----------------------------------------------------------------------

    def vowel_codes(self) -> tuple:
        """Return the list of vowel codes the class can predict.

        """
        if self._model is None:
            return ()
        if hasattr(self._model, "vowel_codes") is False:
            return ()
        return self._model.vowel_codes()
