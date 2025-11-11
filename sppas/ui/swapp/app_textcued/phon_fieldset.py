"""
:filename: annotate_page.phon_fieldset.py
:author: Florian Lopitaux, Brigitte Bigi
:contact: contact@sppas.org
:summary: Phonetize fieldset of the annotate page.

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

from sppas.ui import _
from .text2cue import TextToCues
from .annotate_view import SPPASAnnotateNode

# ---------------------------------------------------------------------------

MSG_FIELD_LEGEND = _("Sequence of words to be phonetized")
MSG_BREADCRUMB = _("Normalized text")
MSG_PREV_INPUT = _("See the text previously entered")
MSG_ANN_NAME = _("Phonetize text")

MSG_REF = _("Bibliographical reference")

# ---------------------------------------------------------------------------


HTML_REFERENCE = """
      <h2>{:s}</h2>

      <blockquote><p>
            Brigitte Bigi (2016).
            <a class="external-link" href="http://link.springer.com/chapter/10.1007%2F978-3-319-43808-5_30">
                  A phonetization approach for the forced-alignment task in SPPAS.
            </a>
            Human Language Technology. Challenges for Computer Science and Linguistics, LNAI 9561, pp. 515–526.
      </p>
      </blockquote>
""".format(MSG_REF)

# ---------------------------------------------------------------------------


class PhonetizeFieldset(SPPASAnnotateNode):
    """Phonetization automatic annotation.

    Requires a normalized text.
    Produces phonetized tokens.

    """

    def __init__(self, parent_id: str):
        super(PhonetizeFieldset, self).__init__(parent_id, "phonetize", MSG_BREADCRUMB, MSG_FIELD_LEGEND)
        self.set_attribute("id", "phonetize")
        self._btn_text = MSG_ANN_NAME

    # ---------------------------------------------------------------------------
    # PUBLIC METHODS
    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_ann_result(result) -> str:
        """Override. Convert the phonetized result into a string.

        The Phonetization result is a list of tuple(token, phones, status).

        :return: (str) Sequence of phonemes

        """
        return TextToCues.serialize_phonetized(result)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_ann_result(result) -> str:
        """Override. Convert the annotation result into an input for the cuedspeech.

        :return: (str) Sequence of tokens

        """
        return TextToCues.format_phonetized(result)

    # ---------------------------------------------------------------------------

    def annotate(self, text: str, lang: str = "und") -> list:
        """Override. Return the result of "Phonetization" on the given text.

        :param text: (str) Input text to be annotated
        :param lang: (str) Language of the text (iso639-1)
        :return: (list) list of phonetized tokens

        """
        annotator = TextToCues(lang)
        return annotator.phonetizer(text)

    # -----------------------------------------------------------------------
    # Override.
    # -----------------------------------------------------------------------

    def _create_extra_content(self) -> None:
        """Override. Create any content to be added below the form.

        """
        section = HTMLNode(self.identifier, "references", "section", value=HTML_REFERENCE)
        self.append_child(section)
