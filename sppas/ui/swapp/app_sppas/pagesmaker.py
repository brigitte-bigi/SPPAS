"""
:filename: sppas.ui.swapp.app_setup.setupmaker.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The web-based application of SPPAS.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

This application allows to use SPPAS with a web-based font-end:
annotations, analysis, edit, file conversion, plugins.

"""

from .pagemenu import sppasMainAppMenuNode
from .page_files.filesmaker import FilesResponseRecipe
from .page_edit.editmaker import EditResponseRecipe

# ---------------------------------------------------------------------------


class sppasMainPagesMaker(object):
    """Create a ResponseMaker instance from an HTML page name.

    """

    # A dictionary to associate a page name and a class to instantiate.
    PAGES = dict()
    PAGES[FilesResponseRecipe.page()] = FilesResponseRecipe
    PAGES[EditResponseRecipe.page()] = EditResponseRecipe

    # -----------------------------------------------------------------------

    @staticmethod
    def pages():
        """Return the whole list of supported page names (case-sensitive)."""
        return list(sppasMainPagesMaker.PAGES.keys())

    # -----------------------------------------------------------------------

    def __init__(self, page_name=None):
        """Create a new instance.

        :param page_name: (str) Set a page name or let's use the default one.

        """
        self.__default = FilesResponseRecipe().page
        self.__pagename = ""
        if page_name in sppasMainPagesMaker.PAGES:
            self.__pagename = page_name

    # -----------------------------------------------------------------------

    @property
    def default(self) -> str:
        """Return the default page name."""
        return self.__default

    # -----------------------------------------------------------------------

    def create(self):
        """Return the ResponseRecipe corresponding to the page name.

        :returns: (ResponseRecipe)

        """
        # Create the Menubar node with no parent: a 'nav' tag
        menu = sppasMainAppMenuNode(None)
        for page_name in sppasMainPagesMaker.PAGES.keys():
            page_inst_name = sppasMainPagesMaker.PAGES[page_name]
            menu.add_menu_entry(
                page_inst_name.ident(),
                page_name,
                page_inst_name.icon(),
                page_inst_name.title()
            )

        # Create the requested page
        page = None
        for page_ident in sppasMainPagesMaker.PAGES.keys():
            if page_ident.lower() == self.__pagename.lower():
                page = sppasMainPagesMaker.PAGES[page_ident]()

        if page is None:
            page = sppasMainPagesMaker.PAGES[self.__default]()

        # Set this page the current one in the menubar
        # page.add_nav(menu)
        menu.set_parent(page._htree.body_header.identifier)
        page._htree.body_header.append_child(menu)

        menu.set_current(page.ident())

        return page
