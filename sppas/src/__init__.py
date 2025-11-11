"""
:filename: sppas.src.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SPPAS API source code.

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

    -------------------------------------------------------------------------

Import all source packages of the API. Some classes will raise an exception
if the feature is not enabled.

"""

# Global data structures and utilities
from .utils import *
from .structs import *
from .calculus import *

# Data structures to manage files to work with and data knowledge files
from .wkps import *
from .resources import *

# Data structure to represent annotated data and recordings
from .anndata import *
from .imgdata import *
from .videodata import *

# The features of SPPAS
from .annotations import *
from sppas.src.annotations.Align.models import *
from .analysis import *
from .plugins import *
