# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.structs.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the data structures of SPPAS.

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

*****************************************************************************
structs: access and manage data structures.
*****************************************************************************

This package includes classes to manage data like un-typed options, a
language, a dag...

Requires the following other packages:

* config
* utils

"""

from .basecompare import sppasBaseCompare
from .basecompare import sppasListCompare
from .basefilters import sppasBaseFilters
from .basefset import sppasBaseSet
from .baseoption import sppasBaseOption
from .baseoption import sppasOption
from .lang import sppasLangResource
from .metainfo import sppasMetaInfo
from .tips import sppasTips

__all__ = (
    "sppasBaseCompare",
    "sppasListCompare",
    "sppasBaseFilters",
    "sppasBaseSet",
    "sppasBaseOption",
    "sppasOption",
    "sppasLangResource",
    "sppasMetaInfo",
    "sppasTips"
)
