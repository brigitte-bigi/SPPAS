"""
:filename: sppas.ui.swapp.app_textcued.textcued.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Bakery for the web-based application "Text Cued" of SPPAS.

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
import logging

from whakerpy.httpd import BaseResponseRecipe
from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess

from ..apps.swapp_bakery import swappWebData

from .textcuedmaker import TextCuedResponseRecipe
from .app_launcher import TextCuedLauncherRecipe

# ---------------------------------------------------------------------------


MSG_DESCR = _("Automatically generates the sequence of keys to be used for cueing from a written text.")
MSG_NAME = _("Text Cueing")

# ---------------------------------------------------------------------------


class TextCuedWebData(swappWebData):
    """Parse the JSON file, store data and create the bakery system.

    """

    def __init__(self, json_filename: str | None = None) -> None:
        """Create a TextCuedWebData instance.

        """
        super(TextCuedWebData, self).__init__(json_filename)
        # Filename of the default page.
        self._default = TextCuedLauncherRecipe.page()

    # -----------------------------------------------------------------------

    @staticmethod
    def icon() -> str:
        """Return the page icon name."""
        return sppasImagesAccess.get_icon_filename("ACS_text")

    @staticmethod
    def description() -> str:
        """Return a short description of the application."""
        return MSG_DESCR

    @staticmethod
    def name() -> str:
        """Return a short name of the application."""
        return MSG_NAME

    @staticmethod
    def id() -> str:
        """Return an identifier of the application."""
        return "TextCueing"

    # -----------------------------------------------------------------------

    def is_page(self, page_name: str) -> bool:
        """Override. Return true if the given page name can be baked.

        :param page_name: The name of the page to check.
        :return: (bool) True if the given page name can be baked.

        """
        if page_name in self._pages:
            return True
        if page_name.startswith("textcueing") is True and page_name.endswith(".html") is True:
            return True
        if page_name == "textcue.html":
            return True
        return False

    # -----------------------------------------------------------------------

    def bake_response(self, page_name: str, default: str = "") -> BaseResponseRecipe | None:
        """Return the bakery system to create the requested page dynamically.

        :param page_name: (str) Name of the page to bake.
        :param default: (str) Default value for the page name if the page does not exist.
        :return: (BaseResponseRecipe|None)

        """
        logging.info(f"Requested page name: {page_name}")

        # Create a specific response to use TextCueing of SPPAS
        if page_name.startswith("textcueing") is True and page_name.endswith(".html") is True:
            return TextCuedResponseRecipe()

        if page_name == TextCuedLauncherRecipe.page():
            return TextCuedLauncherRecipe()

        # Any other page name
        return None
