#!/usr/bin/env python
"""
:filename: sppas.bin.makedoc.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Create the Application Programming Interface (API) Documentation

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

# Create documentation of SPPAS with ClammingPy

import sys
import os
import logging

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas

try:
    from clamming import ClamsModules
    from clamming import ExportOptions
except ImportError:
    print("This program requires `Clamming` documentation generator.")
    print("It can be installed with: pip install ClammingPy.")
    print("See <https://pypi.org/project/Clamming/> for details.")
    sys.exit(-1)


# ---------------------------------------------------------------------------
logging.getLogger().setLevel(0)

# -------------------------------------------------
# List of modules to be documented: automatically create the documentation of
# all known classes of the following 'sppas' packages.
# -------------------------------------------------
packages = list()
packages.append(sppas.config)
packages.append(sppas.preinstall)
packages.append(sppas.src.utils)
packages.append(sppas.src.structs)
packages.append(sppas.src.anndata)
packages.append(sppas.src.imgdata)
packages.append(sppas.src.videodata)
packages.append(sppas.src.wkps)
packages.append(sppas.src.resources)
packages.append(sppas.src.analysis)
packages.append(sppas.src.annotations)

# ----------------------------
# Options for exportation
# ----------------------------
opts_export = ExportOptions()
opts_export.software = 'SPPAS ' + sppas.config.sg.__version__
opts_export.url = 'https://sppas.org/'
opts_export.copyright = sppas.config.sg.__copyright__
opts_export.title = 'SPPAS doc'
opts_export.theme = 'light'
opts_export.favicon = 'icons/sppas.ico'   # relative path to statics
opts_export.icon = 'icons/Refine/sppas_logo_v3_64x64.png'   # relative path to statics
opts_export.readme = True

# For a local use:
opts_export.wexa_statics = "/".join(("..", "..", "ui", 'swapp', 'whakerexa', 'wexa_statics'))
opts_export.statics = "/".join(("..", "..", 'ui', 'swapp', 'statics'))
# OR
# For SPPAS website:
# opts_export.wexa_statics = "/".join(("..", 'whakerexa', 'wexa_statics'))
# opts_export.statics = "/".join(("..", 'statics'))

# -------------------------------------------------
# Generate documentation
# -------------------------------------------------
clams_modules = ClamsModules(packages)

# Export documentation into HTML files.
# One .html file = one documented class.
clams_modules.html_export_packages(os.path.join(sppas.paths.sppas, "docs", "api"), opts_export, "README.md")

# Export documentation into a Markdown file.
# One .md file = one documented module.
# clamming.ClamsPack.markdown_export_packages(packages, os.path.join("docs", "api"), html_export)
