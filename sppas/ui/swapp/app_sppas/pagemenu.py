"""
:filename: sppas.ui.swapp.app_sppas.pagemenu.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: A node to generate the HTML elements of the menubar.

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

    Copyright (C) 2011-2023 Brigitte Bigi
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

from sppas.ui.swapp.htmltags import sppasHTMLButton

# ---------------------------------------------------------------------------


class sppasMainAppMenuNode(HTMLNode):
    """The menu of the application, using the nav tag.

    Does the job but should be re-written in a cleaner way!

    """

    def __init__(self, parent):
        """The nav bar of the SPPAS Main Web App pages.

        :param parent: (str) Parent identifier.

        """
        super(sppasMainAppMenuNode, self).__init__(parent, "menubar", "nav",
                                                   attributes={"class": "topbar"})

    # -----------------------------------------------------------------------

    def add_menu_entry(self, ident, page, icon, text):
        """Add a button to the menubar.

        :param ident: (str) The page identifier
        :param page: (str) Name of the HTML page linked to the button
        :param icon: (str) Icon name
        :param text: (str) Text to show
        :return: (HTMLNode)

        """
        btn = sppasHTMLButton(parent=self.identifier, identifier=ident + "_nav_btn")
        btn.add_attribute("class", "topbar_button")
        btn.add_attribute("onclick", "location='" + page + "'")
        btn.set_icon(icon, attributes={"class": "topbar_button_icon"})
        btn.set_text(None, text, attributes={"class": "topbar_button_text"})
        self.append_child(btn)
        return btn

    # -----------------------------------------------------------------------

    def set_current(self, ident):
        """Fix the current activated button.

        :param ident: (str) The page identifier
        :raise: KeyError

        """
        ident = ident + "_nav_btn"
        # Does the menu has such ident?
        btn = None
        for child in self._children:
            if child.identifier == ident:
                btn = child
                break
        if btn is None:
            raise KeyError("Menubar has no child with ident '{:s}'".format(ident))
        # Remove current page and set it to the identified btn
        for child in self._children:
            child.remove_attribute_value("class", "current_page")
        btn.add_attribute("class", "current_page")
