# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_sppas.page_edit.editmaker.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The page "Edit" of the SPPAS Web UI.

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

from whakerpy.htmlmaker import HTMLNode
from whakerkit.responses import WhakerKitResponse

from sppas.ui.swapp.wappsg import wapp_settings

# ---------------------------------------------------------------------------


class EditResponseRecipe(WhakerKitResponse):
    """The Recipe to create the Edit page of SPPAS Main Web UI.

    """

    @classmethod
    def page(cls) -> str:
        """Override. Return the HTML page name."""
        return "edit.html"

    @staticmethod
    def ident() -> str:
        """Return the page identifier."""
        return "edit"

    @staticmethod
    def icon() -> str:
        """Return the page icon name."""
        return "page_editor"

    # -----------------------------------------------------------------------

    def __init__(self, name="Edit", tree=None, title="Editor"):
        super(EditResponseRecipe, self).__init__(name, tree, title)

    # -----------------------------------------------------------------------

    def create(self) -> None:
        """Override. Create the fixed page content in HTML.

        The fixed content corresponds to the parts that can't be invalidated:
        head, body_header, body_footer.

        """
        super().create()

        self._htree.head.link(rel="stylesheet", link_type="text/css",
                              href=wapp_settings.statics + "css/main_swapp.css")
        # Add this page style
        # self._htree.add_css_link(os.path.join(wapp_settings.css, "page_home.css"))
        self._htree.head.link(rel="stylesheet", link_type="text/css",
                              href=wapp_settings.statics + "css/page_EDIT.css")
        # Add the menubar page style
        # self._htree.add_css_link(os.path.join(wapp_settings.css, "menubar.css"))
        self._htree.head.link(rel="stylesheet", link_type="text/css",
                              href=wapp_settings.statics + "css/menubar.css")

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Process the given events coming from the POST of any form.

        :param events (dict): key=event_name, value=event_value
        :return: (bool) True if the whole page must be re-created.

        """
        self._status.code = 200
        return False

    # -----------------------------------------------------------------------

    def _bake(self):
        """Create the Home page content in HTML."""
        # Define this page content
        self.comment("Body content")
        node = HTMLNode(self._htree.body_main.identifier, None, "p", value="Incoming...")
        self._htree.body_main.append_child(node)
