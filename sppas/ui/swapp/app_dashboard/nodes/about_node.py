"""
:filename: sppas.ui.swapp.app_dashboard.about_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The about dialog of the SPPAS Dashboard Application.

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

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import TagNode
from whakerpy.htmlmaker import EmptyNode

from sppas.core import sg
from sppas.core import cfg
from sppas.ui.swapp import sppasImagesAccess
from sppas.ui import _

# ----------------------------------------------------------------------------

MSG_HEADER_ABOUT = _("About SPPAS")

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


class AboutDialog(HTMLNode):
    """A dialog for the user to see the About and Update information.

    """

    def __init__(self, parent_id, identifier: str = "about_dialog"):
        """Create a dialog to show "About SPPAS".

        <dialog id="about_dialog" role="alertdialog" class="info hidden-alert" aria-label="About dialog">

        """
        super(AboutDialog, self).__init__(parent_id, identifier, "dialog")
        self.add_attribute("id", self.identifier)
        self.add_attribute("role", "alertdialog")
        self.add_attribute("class", "info hidden-alert about-dialog")
        self.add_attribute("aria-label", "About SPPAS dialog")

        # header
        # ------
        _header_section = TagNode(self.identifier, None, "header")
        self.append_child(_header_section)
        _p = HTMLNode(_header_section.identifier, None, "p", value=MSG_HEADER_ABOUT)
        _header_section.append_child(_p)

        # main
        # ----
        _main_section = TagNode(self.identifier, None, "main")
        _main_section.set_attribute("class", "illustrated-content")
        self.append_child(_main_section)

        # main at left: SPPAS logo
        _a = TagNode(_main_section.identifier, None, "a")
        _a.set_attribute("class", "noborder")
        _a.set_attribute("role", "button")
        _a.set_attribute("target", "_blank")
        _a.set_attribute("href", "https://sppas.org/")
        _main_section.append_child(_a)
        _logo = EmptyNode(_a.identifier, None, "img")
        _logo.set_attribute("src", sppasImagesAccess.get_image_filename("sppas-logo-v5"))
        _logo.set_attribute("alt", "logo SPPAS")
        _a.append_child(_logo)

        # main at right: information
        _content_section = TagNode(_main_section.identifier, None, "section")
        _main_section.append_child(_content_section)
        AboutDialog._append_content(_content_section)

        # footer
        # ------
        _footer_section = TagNode(self.identifier, None, "footer")
        self.append_child(_footer_section)
        _p_links = TagNode(_footer_section.identifier, None, "p")
        AboutDialog._append_link(_p_links, "https://sppas.org/book_introduction.html#license", MSG_LINK_LICENSE)
        AboutDialog._append_link(_p_links, "https://sppas.org/resources.html", MSG_LINK_LANG)
        AboutDialog._append_link(_p_links, "https://sppas.org/scripting.html", MSG_LINK_SCRIPT)
        _footer_section.append_child(_p_links)

        _p_copy = HTMLNode(_footer_section.identifier, None, "p", value=sg.__copyright__)
        _p_copy.set_attribute("class", "copyright")
        _footer_section.append_child(_p_copy)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_content(parent: TagNode):
        # Title: Program name + release
        # -----------------------------
        _node = HTMLNode(parent.identifier, None, "h1", value=" ".join([sg.__name__, sg.__release__]))
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
        AboutDialog._append_link(_p, "https://sppas.org/resources.html#contribute", MSG_CREATING_RESOURCES)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_link(parent: TagNode, href: str, value: str):
        _a = HTMLNode(parent.identifier, None, "a", value=value)
        _a.set_attribute("target", "_blank")
        _a.set_attribute("class", "external-link")
        _a.set_attribute("href", href)
        parent.append_child(_a)


