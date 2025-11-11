# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.whenhandexc.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Exceptions for the Cued Speech keys generator.

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

from sppas.core.coreutils import error

# ----------------------------------------------------------------------------


class sppasCuedPredictorError(ValueError):
    """:ERROR 1325:.

    No predictor system is defined.

    """

    def __init__(self):
        self._status = 1325
        self.parameter = error(self._status) + \
                         (error(self._status, "annotations"))

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)
