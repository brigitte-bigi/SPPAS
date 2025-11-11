"""
:filename: sppas.config.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the configuration of SPPAS.

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

*****************************************************************************
config: configuration & globals of SPPAS
*****************************************************************************

This package includes classes to fix all global parameters. It does not
requires any other package but all other packages of SPPAS are requiring it!

All classes of this package are compatible with any version of python 2.7.6+,
except sppasExecProcess class which requires python 3.5+.

"""

# ---------------------------------------------------------------------------
# Fix the global settings and SPPAS configuration
# ---------------------------------------------------------------------------

# The global settings.
# They need to be imported first: many others need them.
from .settings import sg
from .settings import paths
from .settings import symbols
from .settings import separators
from .settings import annots
from .settings import sppasExtensionsSettings

# Initialize the translation system.
from .sppaslang import set_language

# Utility class to initialize logs with logging (stream or file).
# No external requirement.
from .logsetup import sppasLogSetup

# SPPAS Application configuration.
# It requires settings for paths, globals...
from .appcfg import sppasAppConfig

# Utility class to test or execute a subprocess and get its output.
# No external requirement.
from .process import sppasExecProcess

# Requires the settings. Under construction.
from .support import sppasPostInstall

# ---------------------------------------------------------------------------
# create the global application configuration
cfg = sppasAppConfig()
# create the global log system
lgs = sppasLogSetup(cfg.log_level)
lgs.stream_handler()
# create missing directories
sppasPostInstall().sppas_directories()
# ---------------------------------------------------------------------------

__all__ = (
    "sg",
    "cfg",
    "lgs",
    "paths",
    "symbols",
    "separators",
    "annots",
    "set_language",
    "sppasExecProcess",
    "sppasLogSetup",
    "sppasAppConfig",
    "sppasPostInstall"
)
