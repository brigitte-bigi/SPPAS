"""
:filename: sppas.ui.swapp.pages.about_view.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: View of the "About" page.

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
from whakerpy.htmlmaker import HTMLTree
from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import TagNode
from whakerpy.htmlmaker import EmptyNode

from sppas.core.config import sg
from sppas.core.config import cfg
from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess
from sppas.ui.swapp.apps.swapp_view import swappBaseView

# ---------------------------------------------------------------------------


# Le code source « sppas » est à jour.
MSG_UP_TO_DATE = _("The « sppas » source code is up to date.")
# Une mise à jour du code source « sppas » est disponible. Lancez Setup pour l’installer.
MSG_UPDATE = _("An update of the « sppas » source code is available. Run Setup to install it.")
# Version
MSG_VERSION = _("Version")
# Notes de version
MSG_RELEASES_NOTES = _("Release notes")
# SPPAS est développé par
MSG_DEVEL_BY = _("SPPAS is developed by ")
# en collaboration avec des phonéticiens et des utilisateurs, dans le but de proposer des outils utiles, fiables et adaptés aux besoins réels.
MSG_IN_COLLAB = _(" in close collaboration with phoneticians and users, with the aim of providing useful, reliable tools adapted to real research needs.")
# Vous souhaitez aider ? Vous pouvez participer en
MSG_WOULD_YOU_LIKE = _("Would you like to help? You can contribute by ")
# créant des ressources.
MSG_CREATING_RESOURCES = _("creating resources.")

# Information de licence
# Liste des langues
# Ecrire des scripts
MSG_LINK_LICENSE = _("License information")
MSG_LINK_LANG = _("List of languages")
MSG_LINK_SCRIPT = _("Write scripts")

# ---------------------------------------------------------------------------

MSG_HEADER = f"SPPAS {sg.__release__} » " + _("About")

BODY_SCRIPT = """
        window.Wexa.links.handleLinksWithParameters(['link-dashboard_button']);
        window.Wexa.links.handleLinks(['link-sppas_button']);
"""

# ---------------------------------------------------------------------------


class AboutView(swappBaseView):
    """View class responsible for populating the *about.html* page.

    This class represents the **View** component of the "About" page.
    It receives an existing :class:`HTMLTree` instance and fills it with the
    information about SPPAS and its update state. As a page, it has no
    business logic: its content is pure information, reachable from the nav
    of any app.

    """

    def __init__(self, tree: HTMLTree):
        """Initialize and populate the "About" view structure.

        :param tree: (HTMLTree) An existing HTML tree to populate with
                     the page-specific content.
        :raises: TypeError: tree is not an instance of HTMLTree

        """
        if isinstance(tree, HTMLTree) is False:
            raise TypeError("AboutView: tree must be an instance of HTMLTree. Got {}".format(type(tree)))
        super().__init__(tree, MSG_HEADER)

        # The SPPAS way of organizing an illustration with its content.
        self._htree.body_main.add_attribute("class", "illustrated-content")

    # -----------------------------------------------------------------------
    # Populate the tree
    # -----------------------------------------------------------------------

    def _populate_head_css(self):
        """Override. Populate the `<head>` section of the HTML tree for CSS links.

        No page-specific stylesheet: the page relies on the shared one only.

        """
        pass

    # -----------------------------------------------------------------------

    def _populate_body_header(self):
        """Override. Populate the header area of the page.

        """
        self.append_responsive_menu_button(self._htree.body_header)

    # -----------------------------------------------------------------------

    def _populate_body_nav(self):
        """Override. Populate the nav area of the page.

        """
        _s = TagNode(self._htree.body_nav.identifier, None, "section")
        self.append_pin_button(_s)
        self.append_accessibility_buttons(_s)
        self._htree.body_nav.append_child(_s)

        self.append_dashboard_link_button(self._htree.body_nav)
        self.append_sppas_link_button(self._htree.body_nav)

    # -----------------------------------------------------------------------

    def populate_body_script(self):
        """Override. Populate the script body section.

        """
        self._htree.body_script.add_attribute("type", "module")
        self._htree.body_script.set_value(BODY_SCRIPT)

    # -----------------------------------------------------------------------
    # Update the tree -- for baking the page
    # -----------------------------------------------------------------------

    def populate_tree_content(self):
        """Populate the tree content with the information about SPPAS.

        """
        # At left: the SPPAS logo, in a link
        _a = TagNode(self._htree.body_main.identifier, None, "a")
        _a.set_attribute("class", "noborder")
        _a.set_attribute("role", "button")
        _a.set_attribute("target", "_blank")
        _a.set_attribute("href", "https://sppas.org/")
        self._htree.body_main.append_child(_a)
        _logo = EmptyNode(_a.identifier, None, "img")
        _logo.set_attribute("src", sppasImagesAccess.get_image_filename("sppas-logo-v5"))
        _logo.set_attribute("alt", "logo SPPAS")
        _a.append_child(_logo)

        # At right: the information
        _content_section = TagNode(self._htree.body_main.identifier, None, "section")
        self._htree.body_main.append_child(_content_section)
        AboutView._append_content(_content_section)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_content(parent: TagNode):
        # Title: Program name + release. The h1 of the page is its header.
        _node = HTMLNode(parent.identifier, None, "h2", value=" ".join([sg.__name__, sg.__release__]))
        _node.set_attribute("id", "program_name")
        parent.append_child(_node)

        # Version block
        # -------------
        _article1 = TagNode(parent.identifier, None, "article", attributes={"class": "version-block"})
        parent.append_child(_article1)
        _p = TagNode(_article1.identifier, None, "p")
        _article1.append_child(_p)
        if cfg.update_info.get('update'):
            _span1 = HTMLNode(_p.identifier, None, "span", value="↻")
            _span1.set_attribute("class", "red")
            _span2 = HTMLNode(_p.identifier, None, "span", value=MSG_UPDATE)
        else:
            _span1 = HTMLNode(_p.identifier, None, "span", value="✔")
            _span1.set_attribute("class", "green")
            _span2 = HTMLNode(_p.identifier, None, "span", value=MSG_UP_TO_DATE)
        _span1.set_attribute("aria-hidden", "true")
        _p.append_child(_span1)
        _p.append_child(_span2)
        _p = HTMLNode(_article1.identifier, None, "p", value=" ".join([MSG_VERSION, sg.__version__]))
        _p.add_attribute("class", "details")
        _article1.append_child(_p)
        _a = HTMLNode(_p.identifier, None, "a", value=MSG_RELEASES_NOTES)
        _a.set_attribute("href", "https://sppas.org/book_changes.html#latest")
        _a.set_attribute("target", "_blank")
        _a.set_attribute("class", "external-link")
        _p.append_child(_a)

        # Contribute block
        # ----------------
        _article2 = TagNode(parent.identifier, None, "article")
        parent.append_child(_article2)
        _link = ' <a target="_blank" class="external-link" href="https://sppas.org/bigi/">Brigitte Bigi</a> '
        _p = HTMLNode(_article2.identifier, None, "p", value=" ".join([MSG_DEVEL_BY, _link, MSG_IN_COLLAB]))
        _article2.append_child(_p)
        _p = HTMLNode(_article2.identifier, None, "p", value=MSG_WOULD_YOU_LIKE)
        _article2.append_child(_p)
        AboutView._append_link(_p, "https://sppas.org/resources.html#contribute", MSG_CREATING_RESOURCES)

        # More links block -- was the footer of the dialog
        # ----------------
        _article3 = TagNode(parent.identifier, None, "article")
        parent.append_child(_article3)
        _p_links = TagNode(_article3.identifier, None, "p")
        AboutView._append_link(_p_links, "https://sppas.org/book_introduction.html#license", MSG_LINK_LICENSE)
        AboutView._append_link(_p_links, "https://sppas.org/resources.html", MSG_LINK_LANG)
        AboutView._append_link(_p_links, "https://sppas.org/scripting.html", MSG_LINK_SCRIPT)
        _article3.append_child(_p_links)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_link(parent: TagNode, href: str, value: str):
        _a = HTMLNode(parent.identifier, None, "a", value=value)
        _a.set_attribute("target", "_blank")
        _a.set_attribute("class", "external-link")
        _a.set_attribute("href", href)
        parent.append_child(_a)
