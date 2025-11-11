"""
:filename: sppas.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Import all source packages.

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

Import all packages of the SPPAS API, located in the "src" package.
Do not import python programs of bin and scripts nor the user interfaces.

"""

# ----------------------------------------------------------------------------
# Import SPPAS core. It doesn't require any external library.
# ----------------------------------------------------------------------------
from .core import *

# ----------------------------------------------------------------------------
# Try importing all API packages from 'src'.
# This includes tools and modules relying on external dependencies.
# If these dependencies are missing, the base feature cannot be enabled,
# and the import will fail gracefully.
# ----------------------------------------------------------------------------
from .src import *

# ---------------------------------------------------------------------------

# sg is an instance of sppasGlobalSettings() defined in config package.
# Some information are loaded from the codemeta.json external config file.
__version__ = sg.__version__
__name__ = sg.__name__
__author__ = sg.__author__
__docformat__ = sg.__docformat__
__copyright__ = sg.__copyright__
