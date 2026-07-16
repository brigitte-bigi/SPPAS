"""
:filename: sppas.ui.swapp.pages.swapp_pages.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The provider of all the generic pages of swapp.

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

from __future__ import annotations
import logging

from whakerpy.httpd import BaseResponseRecipe

from ..apps.swapp_bakery import swappWebData

from .citemaker import CiteResponseRecipe

# ---------------------------------------------------------------------------


class swappPagesData(swappWebData):
    """Serve all the generic pages of swapp.

    A page is a document with its own URL and without business logic: see
    the taxonomy in the README of swapp. All the pages are served by this
    single provider, registered in the WEB_PAGES registry -- not in the
    WEB_APPLICATIONS one, so no card is created in the Dashboard.

    """

    # The ResponseRecipe classes of all the known generic pages.
    PAGE_RECIPES = (CiteResponseRecipe, )

    def __init__(self, json_filename: str | None = None) -> None:
        """Create a swappPagesData instance.

        """
        super(swappPagesData, self).__init__(json_filename)
        self._default = CiteResponseRecipe.page()

    # -----------------------------------------------------------------------

    def is_page(self, page_name: str) -> bool:
        """Override. Return true if the given page name can be baked.

        :param page_name: The name of the page to check.
        :return: (bool) True if the given page name can be baked.

        """
        for recipe in swappPagesData.PAGE_RECIPES:
            if page_name == recipe.page():
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

        for recipe in swappPagesData.PAGE_RECIPES:
            if page_name == recipe.page():
                return recipe()

        # Any other page name
        return None
