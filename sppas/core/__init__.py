# -*- coding : UTF-8 -*-
"""
:filename: sppas.core.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the management of SPPAS core classes.

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

This is the core initialization file for the SPPAS package.
It ensures proper configuration of the translation system and the enabled
features.

"""

import logging
import sys

# ----------------------------------------------------------------------------
# config package must be imported at first.
# Handle language setting if the translation system was already initialized.
# This happens when 'config' was imported before importing 'sppas'.
# ----------------------------------------------------------------------------

# Default: no language enforced
lang = None

# Check if 'config' was previously imported
if "config" in sys.modules:
    # Access the already-imported config module (outside the sppas namespace)
    from .config.sppaslang import translator

    if translator is not None:
        # A language was explicitly set before; retrieve it
        # This ensures language consistency across imports
        lang = translator.get_default_lang()

# Now import the 'config' package properly
# from the local 'sppas' namespace.
# -----------------------------------------

from .config import *

# Restore the desired language after re-importing the config module.
# This is needed because set_language sets both the default lang
# and the public translator instance.
if lang is not None:
    from .config.sppaslang import set_language
    set_language(lang)

# ---------------------------------------------------------------------------
# Core utilities and other core packages
# ---------------------------------------------------------------------------

from .coreutils import *
from .preinstall import *

# Check if the required dependencies can be imported
# --------------------------------------------------
# Hack to avoid ImportError: DLL load failed while importing _framework_bindings.
# This error occurs specifically if mediapipe is imported AFTER wxPython.
# Since DepsFeatureChecker() checks both 'wxpython' and 'mediapipe' features,
# we explicitly import mediapipe BEFORE running DepsFeatureChecker.
# The order matters because 'wxpython' is listed before 'mediapipe' in features.ini.
try:
    import mediapipe
except Exception as e:
    pass

DepsFeatureChecker().check(do_report=True)

# Check if enabled features can really be imported -- update if not.
# ------------------------------------------------

# Use Features to check if all python dependencies are correctly assigned to 'cfg'
features = Features(req="", cmdos="")
features.check_deps(test_all=True)

# Update enabled features in config
for fid in features.get_ids("deps"):
    cfg.set_feature(fid, features.enable(fid))
    state = "OK" if features.enable(fid) else "DISABLED"
    logging.debug(f"{fid:15}: {state}")
cfg.save()
