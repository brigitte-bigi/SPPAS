"""
:filename: sppas.ui.swapp.app_dashboard.links_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The links section of the SPPAS Dashboard Application.

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
from whakerpy.htmlmaker import HTMLNode

from sppas.ui.swapp.nodes import sppasHTMLButton
from sppas.ui.swapp.nodes import sppasHTMLLink

# ---------------------------------------------------------------------------


class BaseLinksNode(HTMLNode):

    def __init__(self, parent_id, identifier: str):
        super(BaseLinksNode, self).__init__(parent_id, identifier, "section")
        self.add_attribute("id", self.identifier)
        self.add_attribute("class", "cards-panel")
        self.add_attribute("class", "links-panel")

    # ----------------------------------------------------------------------

    def link_button(self, ident, icon_name, text, link):
        """A card leading to a page: a link, on which the ident is on the span text.

        :return: (sppasHTMLLink)

        """
        link_node = sppasHTMLLink(self.identifier, identifier=ident+"_button")

        # - design
        link_node.remove_attribute("class")  # just in case...
        link_node.add_attribute("class", "card")
        link_node.add_attribute("class", "link-button")
        # - link, followed by the browser and by goToLink() of Whakerexa,
        #   which carries the accessibility parameters over to the page.
        #   A page of the internet is opened in a tab of its own: this page
        #   stays where it is, and one comes back to it by closing that tab.
        link_node.add_attribute("href", link)
        link_node.add_attribute("title", link)
        if link.startswith("http://") is True or link.startswith("https://") is True:
            link_node.add_attribute("target", "_blank")
            link_node.add_attribute("rel", "noopener")
        # - content. The drawing is asked for by its name: the icon manager
        #   of Whakerexa writes it first, before the label. A name the set
        #   of SPPAS does not carry falls back on the one of the framework,
        #   instead of a broken image.
        link_node.add_attribute("data-icon", icon_name)
        link_node.set_text(ident+"_text", text, attributes={"class": "link-button-text"})

        self.append_child(link_node)
        return link_node

    # ----------------------------------------------------------------------

    def page_button(self, ident, icon_name, text, link):
        """A card leading to an internal page of SPPAS.

        The link is followed by goToLink() of Whakerexa, which preserves
        the accessibility parameters when navigating to the page.

        :return: (sppasHTMLLink)

        """
        button_node = self.link_button(ident, icon_name, text, link)
        button_node.add_attribute("class", "page-button")
        return button_node

    # ----------------------------------------------------------------------

    def dialog_button(self, ident, icon_name, text, dialog_name):
        """A specific button which is used to open a modal dialog.

		<button name="about-button" onclick="Wexa.dialog.open('about_dialog', true)">Open About</button>

        :return: (sppasHTMLButton)

        """
        button_node = sppasHTMLButton(self.identifier, identifier=ident+"_button")
        button_node.add_attribute("onclick", f"Wexa.dialog.open('{dialog_name}', true)")

        # - design
        button_node.remove_attribute("class")  # just in case...
        button_node.add_attribute("class", "card")
        button_node.add_attribute("class", "link-button")

        # content
        button_node.add_attribute("data-icon", icon_name)
        button_node.set_text(ident+"_text", text, attributes={"class": "link-button-text"})

        self.append_child(button_node)
        return button_node
