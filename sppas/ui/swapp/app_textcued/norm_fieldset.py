"""
:filename: annotate_page.norm_fieldset.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: This file contains the normalize fieldset (first fieldset) of the annotate page.

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

from .text2cue import TextToCues
from .annotate_view import SPPASAnnotateNode

# ---------------------------------------------------------------------------

# Title of the fieldset -- H2 element
MSG_FIELD_LEGEND = _("Hit text to be normalized")
# Text for the breadcrumb
MSG_BREADCRUMB = _("Input text")
# Text for the action button
MSG_ANN_NAME = _("Normalize text")

MSG_REF = _("Bibliographical reference")

# ---------------------------------------------------------------------------


HTML_REFERENCE = """
      <h2>{:s}</h2>

      <blockquote><p>
            Brigitte Bigi (2014).
            <a class="external-link" href="http://link.springer.com/chapter/10.1007/978-3-319-08958-4_42">
                  A Multilingual Text Normalization Approach.
            </a>
            Human Language Technology Challenges for Computer Science and Linguistics,
            LNAI 8387, pp. 515–526.
      </p>
      </blockquote>
""".format(MSG_REF)

# ---------------------------------------------------------------------------


class NormalizeFieldset(SPPASAnnotateNode):
    """Text Normalization automatic annotation.

    Requires an input text.
    The result of Text Normalization is a list of tokens.

    """

    def __init__(self, parent_id: str):
        super(NormalizeFieldset, self).__init__(parent_id, "textnorm", MSG_BREADCRUMB, MSG_FIELD_LEGEND)
        self.add_attribute("id", "textnorm")
        self._btn_text = MSG_ANN_NAME

    # ---------------------------------------------------------------------------
    # Override from AnnBaseView
    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_ann_result(result) -> str:
        """Override. Convert the normalized result into a human-readable string.

        :return: (str) Sequence of tokens

        """
        return TextToCues.serialize_normalized(result)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_ann_result(result) -> str:
        """Override. Convert the annotation result into an input for the phonetization.

        :return: (str) Sequence of tokens

        """
        return TextToCues.format_normalized(result)

    # ---------------------------------------------------------------------------

    def annotate(self, text: str, lang: str = "und") -> list:
        """Override. Return the result of "Text Normalization" on the given text.

        :param text: (str) Input text to be annotated
        :param lang: (str) Language of the text (iso639-1)
        :return: (list) list of tokens

        """
        annotator = TextToCues(lang)
        return annotator.normalizer(text)

    # -----------------------------------------------------------------------

    def _create_extra_content(self) -> None:
        """Override. Create any content to be added below the form.

        """
        section = HTMLNode(self.identifier, "references", "section", value=HTML_REFERENCE)
        self.append_child(section)
