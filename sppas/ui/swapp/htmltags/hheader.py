# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.htmltags.hheader.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Default header node for any SPPAS Web APPlication.

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

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLHeaderNode
from whakerkit.nodes.accessibility import WhakerKitAccessibilityNavNode

from sppas.ui import _

# -----------------------------------------------------------------------


MSG_SKIP = _("Skip to content")

# -----------------------------------------------------------------------


class SwappHeader(HTMLHeaderNode):
    """Create the default header node for any SPPAS Web APPlication.

    """

    def __init__(self, parent_id: str, title: str = "SPPAS Application"):
        super(SwappHeader, self).__init__(parent_id)
        self.set_attribute("id", "header-content")
        self.__title = title
        self.__nav = None
        self.__create_content()

    # -----------------------------------------------------------------------
    # SETTERS
    # -----------------------------------------------------------------------

    def set_title(self, title: str) -> None:
        """Set the title of the application for the header node.

        :param title: (str) The title of the application for the header node.

        """
        self.__title = str(title)

        # Update this node with the new title
        self.clear_children()
        self.__create_content()

    # -----------------------------------------------------------------------

    def get_header_nav(self):
        """Return the 'nav' element already containing Accessibility buttons."""
        return self.__nav

    # -----------------------------------------------------------------------

    def __create_content(self) -> None:
        """Create the node content.

        """
        # Skip button, for accessibility compliance
        a = HTMLNode(self.identifier, None, "a", value=MSG_SKIP)
        a.set_attribute("role", "button")
        a.set_attribute("class", "skip")
        a.set_attribute("href", "#main-content")
        a.set_attribute("aria-label", "skip-to-content")
        self.append_child(a)

        # Contrast & theme buttons, for accessibility compliance
        if self.__nav is None:
            self.__nav = WhakerKitAccessibilityNavNode(self.identifier)
        self.append_child(self.__nav)

        # Application title
        h1 = HTMLNode(self.identifier, None, "h1", value=self.__title,
                      attributes={"class": "fixed-almost-top"})
        self.append_child(h1)
