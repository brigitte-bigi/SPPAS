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

from sppas.ui import _
from sppas.ui.swapp.htmltags import sppasHTMLButton

# ---------------------------------------------------------------------------


MSG_HOME = _("Website")
MSG_DOC = _("Book")
MSG_TUTOS = _("Tutorials")
MSG_FAQ = "F.A.Q."
MSG_SRC = _("Source code")
MSG_AUTH = _("The author")

# ---------------------------------------------------------------------------


class LinksNode(HTMLNode):
    """The section with external links of the dashboard application.

    """

    def __init__(self, parent_id):
        super(LinksNode, self).__init__(parent_id, "dashboard_links_sec", "section")
        self.add_attribute("id", self.identifier)
        self.add_attribute("class", "links-panel")

        self.__link_button("web", "sppas_logo_v3", MSG_HOME, link="https://sppas.org/")
        self.__link_button("docu", "link_docweb", MSG_DOC, link="https://sppas.org/book.html")
        self.__link_button("tuto", "link_tutovideo", MSG_TUTOS, link="https://sppas.org/tutorial.html")
        self.__link_button("faq", "link_question", MSG_FAQ, link="https://sppas.org/faq.html")
        self.__link_button("src", "badge-sourceforge", MSG_SRC, link="https://sourceforge.net/p/sppas/code/ci/master/tree/")
        self.__link_button("author", "link_author", MSG_AUTH, link='https://sppas.org/bigi/')

    # -----------------------------------------------------------------------

    def __link_button(self, ident, icon_name, text, link):
        """A specific button on which the ident is on the span text.

        """
        attributes = dict()
        attributes["class"] = "link-button"
        # Accessibility:
        # - the role of the button is "link"
        attributes["role"] = "link"
        # - the link must works with either the mouse or the keyboard 'enter'
        event = "tabToLink(event,'" + link + "');"
        attributes["onclick"] = event
        attributes["onkeydown"] = event

        button_node = sppasHTMLButton(self.identifier, ident+"_btn", attributes)
        button_node.set_icon(icon_name, attributes={"class": "link-button-icon"})
        button_node.set_text(ident+"_text", text, attributes={"class": "link-button-text"})

        self.append_child(button_node)
