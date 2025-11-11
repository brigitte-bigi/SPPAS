"""
:filename: sppas.ui.swapp.apps.swapp_bakery.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Bakery for any SPPAS web-based application.

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

"""

from __future__ import annotations

from whakerpy.webapp import WebSiteData
from sppas.ui.swapp import sppasImagesAccess

# ---------------------------------------------------------------------------


class swappWebData(WebSiteData):
    """Parse the JSON file, store data and create the bakery system.

    """

    def __init__(self, json_filename: str | None = None):
        """Create a swappWebData instance.

        """
        super(swappWebData, self).__init__(json_filename)

    # -----------------------------------------------------------------------

    @staticmethod
    def icon() -> str:
        """Return the page icon name."""
        return sppasImagesAccess.get_icon_filename("sppas_64")

    @staticmethod
    def description() -> str:
        """Return a short description of the application."""
        return "No description available."

    @staticmethod
    def name() -> str:
        """Return a short name of the application."""
        return "Undefined"

    @staticmethod
    def id() -> str:
        """Return an identifier of the application."""
        return "Undefined"
