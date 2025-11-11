# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.whatkeyexc.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Exceptions for the Cued Speech keys generator.

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

from sppas.core.coreutils import error

# ----------------------------------------------------------------------------


class sppasCuedRulesValueError(ValueError):
    """:ERROR 1322:.

    A Cued Speech syllable must be a sequence of C-V phonemes.
    Got '{}' instead.

    """

    def __init__(self, value):
        self._status = 1322
        self.parameter = error(self._status) + \
                         (error(self._status, "annotations")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# ----------------------------------------------------------------------------


class sppasCuedRulesMinValueError(ValueError):
    """:ERROR 1321:.

    A Cued Speech syllable should contain at least one phoneme.
    Got {} instead.

    """

    def __init__(self, value):
        self._status = 1321
        self.parameter = error(self._status) + \
                         (error(self._status, "annotations")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)

# ----------------------------------------------------------------------------


class sppasCuedRulesMaxValueError(ValueError):
    """:ERROR 1323:.

    A Cued Speech syllable should contain a maximum of two phonemes.
    Got {} instead.

    """

    def __init__(self, value):
        self._status = 1323
        self.parameter = error(self._status) + \
                         (error(self._status, "annotations")).format(value)

    def __str__(self):
        return repr(self.parameter)

    def get_status(self):
        return self._status

    status = property(get_status, None)
