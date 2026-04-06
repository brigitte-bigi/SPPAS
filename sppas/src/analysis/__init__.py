# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.config.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the automatic data analysis of SPPAS.

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
analysis: automatic data analysis
*****************************************************************************

This package includes all the automatic analysis of annotated data.
It requires the following other packages:

* config
* structs
* anndata
* calculus

"""

from .tierstats import sppasTierStats
from .tierfilters import sppasTierFilters
from .tierfilters import SingleFilterTier
from .tierfilters import RelationFilterTier

__all__ = (
    "sppasTierStats",
    "sppasTierFilters",
    "SingleFilterTier",
    "RelationFilterTier"
)
