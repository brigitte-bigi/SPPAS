# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.utils.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Utilities for SPPAS.

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
utils: utility classes.
*****************************************************************************

This package includes any utility class to extend python features.
Currently, it implements a class to manage identically unicode data
with all versions of python. It also includes a comparator of data
which is very powerful for lists and dictionaries, a bidirectional
dictionary, a representation of time, etc.

Requires the following other packages:

* config

"""

from .datatype import sppasTime
from .datatype import sppasType
from .datatype import bidict
from .compare import sppasCompare
from .fileutils import sppasDirUtils
from .fileutils import sppasFileUtils

__all__ = (
    "sppasTime",
    "sppasType",
    "sppasDirUtils",
    "sppasFileUtils",
    "sppasCompare",
    "bidict"
)
