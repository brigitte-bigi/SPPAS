"""
:filename: sppas.ui.swapp.app_dashboard.nodes.publis_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The references dialog of the SPPAS Dashboard Application.

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

from sppas.ui.swapp import sppasImagesAccess
from sppas.ui import _

# ----------------------------------------------------------------------------

MSG_HEADER_ABOUT = _("How to cite SPPAS")
MSG_MAIN_CITE = _("For a general citation of SPPAS, use the reference below:")
MSG_OTHERS_CITE = _("please refer to the related specific publication")
MSG_CLICK_HERE = _("Click here to get all references")

MSG_CITATION = """
                Brigitte Bigi.
                <b>SPPAS - MULTI-LINGUAL APPROACHES TO THE AUTOMATIC ANNOTATION OF SPEECH.</b>
                <i>The Phonetician.</i> Journal of the International Society of Phonetic Sciences, 2015,
                Journal of ISPhS/International Society of Phonetic Sciences, 111-112 (ISSN:0741-6164), 
                pp. 54-69.
      """

# ---------------------------------------------------------------------------


class PublisDialog(HTMLNode):
    """A dialog for the user to see the About and Update information.

    """

    def __init__(self, parent_id, identifier: str = "publis_dialog"):
        """Create a dialog to show "About SPPAS".

        """
        super(PublisDialog, self).__init__(parent_id, identifier, "dialog")
        self.add_attribute("id", self.identifier)
        self.add_attribute("role", "alertdialog")
        self.add_attribute("class", "info hidden-alert about-dialog")
        self.add_attribute("aria-label", "References SPPAS dialog")

        # header
        # ------
        _header_section = TagNode(self.identifier, None, "header")
        self.append_child(_header_section)
        _p = HTMLNode(_header_section.identifier, None, "p", value=MSG_HEADER_ABOUT)
        _header_section.append_child(_p)

        # main
        # ----
        _main_section = TagNode(self.identifier, None, "main")
        self.append_child(_main_section)

        # at left: Reference image in a link
        _a = TagNode(_main_section.identifier, None, "a")
        _a.set_attribute("class", "noborder")
        _a.set_attribute("role", "button")
        _a.set_attribute("target", "_blank")
        _a.set_attribute("href", "https://hal.science/hal-01417876")
        _main_section.append_child(_a)
        _logo = EmptyNode(_a.identifier, None, "img")
        _logo.set_attribute("src", sppasImagesAccess.get_image_filename("article_reference"))
        _logo.set_attribute("alt", "Capture article")
        _a.append_child(_logo)

        # at right: information
        _content_section = TagNode(_main_section.identifier, None, "section")
        _main_section.append_child(_content_section)
        PublisDialog._append_content(_content_section)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_content(parent: TagNode):
        _article1 = TagNode(parent.identifier, None, "article")
        parent.append_child(_article1)
        _p = HTMLNode(_article1.identifier, None, "p", value=MSG_MAIN_CITE)
        _article1.append_child(_p)
        _b = HTMLNode(_article1.identifier, None, "blockquote", value=MSG_CITATION)
        _article1.append_child(_b)

        _article2 = TagNode(parent.identifier, None, "article")
        parent.append_child(_article2)
        _p = HTMLNode(_article2.identifier, None, "p", value=MSG_OTHERS_CITE)
        _article2.append_child(_p)
        PublisDialog._append_link(_article2, "https://sppas.org/book_references.html", MSG_CLICK_HERE)

    # -----------------------------------------------------------------------

    @staticmethod
    def _append_link(parent: TagNode, href: str, value: str):
        _a = HTMLNode(parent.identifier, None, "a", value=value)
        _a.set_attribute("target", "_blank")
        _a.set_attribute("class", "external-link")
        # _a.set_attribute("onclick", "this.href = window.Wexa.accessibility.setUrlWithParameters(this.href);")
        _a.set_attribute("href", href)
        parent.append_child(_a)
