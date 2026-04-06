# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.annlocation.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: the anchor in time of an annotation.

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

from .localization import sppasBaseLocalization
from .point import sppasPoint
from .interval import sppasInterval
from .disjoint import sppasDisjoint
from .duration import sppasDuration
from .location import sppasLocation
from .duration import sppasDuration
from .durationcompare import sppasDurationCompare
from .localizationcompare import sppasLocalizationCompare
from .intervalcompare import sppasIntervalCompare

__all__ = [
    'sppasBaseLocalization',
    'sppasPoint',
    'sppasInterval',
    'sppasDisjoint',
    'sppasDuration',
    'sppasLocation',
    'sppasDuration',
    'sppasDurationCompare',
    'sppasLocalizationCompare',
    'sppasIntervalCompare'
]
