# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.wkps.__init__.py
:author:   Barthélémy Drabczuk, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  The application workspace manager.

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

*****************************************************************************
wkps: management of files into workspaces
*****************************************************************************

Description:
============

This package includes classes to manage a bunch of files organized into
workspaces. A workspace is made of data related to the file names and a
list of references to make relations between file roots.

Requires the following other packages:

* config
* structs

and globals: paths, sppasIndexError.

"""

from .filebase import FileBase
from .filebase import States
from .filestructure import FileName, FileRoot, FilePath
from .fileref import sppasCatReference, sppasRefAttribute
from .filedatafilters import sppasFileDataFilters
from .workspace import sppasWorkspace
from .sppasWkps import sppasWkps
from .wio import sppasWkpRW
from .appwkpm import sppasWkpsManager

__all__ = (
    "FileBase",
    "States",
    "sppasWorkspace",
    "FileName",
    "FileRoot",
    "FilePath",
    "sppasRefAttribute",
    "sppasCatReference",
    "sppasFileDataFilters",
    "sppasWkps",
    "sppasWkpRW",
    "sppasWkpsManager"
)
