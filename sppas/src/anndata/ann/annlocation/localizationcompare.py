# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.annlocation.localizationcompare.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Comparison methods of 2 localizations, used by the filter system.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

from sppas.src.utils.datatype import sppasType
from sppas.src.structs.basecompare import sppasBaseCompare

from ...anndataexc import AnnDataTypeError

from .point import sppasPoint
from .interval import sppasInterval
from .disjoint import sppasDisjoint

# ---------------------------------------------------------------------------


class sppasLocalizationCompare(sppasBaseCompare):
    """Comparison methods for sppasBaseLocalization.

    """

    def __init__(self):
        """Create a sppasLocalizationCompare instance."""
        super(sppasLocalizationCompare, self).__init__()

        self.methods['rangefrom'] = sppasLocalizationCompare.rangefrom
        self.methods['rangeto'] = sppasLocalizationCompare.rangeto

    # -----------------------------------------------------------------------

    @staticmethod
    def rangefrom(localization, x):
        """Return True if localization is starting at x or after.

        :param localization: (sppasBaseLocalization)
        :param x: (int, float, sppasPoint)
        :returns: (bool)

        """
        if (sppasType().is_number(x) or isinstance(x, sppasPoint)) is False:
            raise AnnDataTypeError(x, "int/float/sppasBaseLocalization")

        return sppasLocalizationCompare.__get_begin(localization) >= x

    # -----------------------------------------------------------------------

    @staticmethod
    def rangeto(localization, x):
        """Return True if localization is ending at x or before.

        :param localization: (sppasBaseLocalization)
        :param x: (int, float, sppasPoint)
        :returns: (bool)

        """
        if (sppasType().is_number(x) or isinstance(x, sppasPoint)) is False:
            raise AnnDataTypeError(x, "int/float/sppasBaseLocalization")

        return sppasLocalizationCompare.__get_end(localization) <= x

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __get_begin(localization):
        """Return the begin point of a localization."""
        if isinstance(localization, sppasPoint):
            return localization
        elif isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_begin()

        raise AnnDataTypeError(localization, "sppasBaseLocalization")

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_end(localization):
        """Return the end point of a localization."""
        if isinstance(localization, sppasPoint):
            return localization
        elif isinstance(localization, (sppasInterval, sppasDisjoint)):
            return localization.get_end()

        raise AnnDataTypeError(localization, "sppasBaseLocalization")
