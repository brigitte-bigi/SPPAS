"""
:filename: sppas.ui.swapp.wapps.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Import the available SPPAS Web-based Applications.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

import logging

from .wappinfo import WebApplicationInfo

# Import all locally developed applications
from .app_setup import SetupWebData
from .app_dashboard import DashboardWebData
from .app_sppas import MainWebData
from .app_test.app_test import TestsWebData
# Install all installed application -- the spin-offs ones
from .spinoff import *
# Import the provider of the generic pages
from .pages import swappPagesData

# Determine if we're running in debug mode (log level lower than DEBUG)
DEBUG_MODE = logging.getLogger().getEffectiveLevel() < 10

# List of all known web applications (stable and in development).
# The 'Dashboard' one is the default in the main_app.
WEB_APPLICATIONS = [
    WebApplicationInfo('Dashboard', DashboardWebData, True),
    WebApplicationInfo('Setup', SetupWebData, True),
    WebApplicationInfo('Test', TestsWebData, DEBUG_MODE),
    # WebApplicationInfo('Main', MainWebData, DEBUG_MODE),
]

# Add all discovered spin-off applications
for cls in SPINOFF_SWAPPS:
    try:
        inst = cls()        # if instantiation fails, skip the app
        app_id = inst.id()
        WEB_APPLICATIONS.append(WebApplicationInfo(app_id, cls, True))
    except Exception as e:
        logging.debug(f"SWAPP: skip {cls} (instantiation failed): {e}")

# List of the providers of the generic pages (fixed and discovered ones).
# A page is not an app: it is dispatched after the apps and it never gets
# a card in the Dashboard.
WEB_PAGES = [
    swappPagesData,
]

# Add all discovered spin-off page providers
for cls in SPINOFF_PAGES:
    try:
        inst = cls()        # if instantiation fails, skip the pages
        WEB_PAGES.append(cls)
    except Exception as e:
        logging.debug(f"SWAPP: skip pages of {cls} (instantiation failed): {e}")
