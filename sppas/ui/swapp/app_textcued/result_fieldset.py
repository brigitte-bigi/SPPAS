"""
:filename: annotate_page.result_fieldset.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: This file contains the annotation result fieldset (last fieldset) of the annotate page.

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

import logging
import ast

from whakerpy import HTMLNode
from sppas.core.config import separators
from sppas.ui.swapp.wappsg import wapp_settings
from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess

from .annotate_view import SPPASAnnotateNode

# ---------------------------------------------------------------------------


MSG_ANN_NAME = _("Cued text")
MSG_FIELD_TITLE = _("Cued Speech keys of the text")
MSG_RESULT = _("Sequence of keys of the phonetized text: ")
MSG_PREV_INPUT = _("See the text previously phonetized")
MSG_NO_RESULT = _("The system did not generated a result.")
MSG_BACK = _("Start again")

# ---------------------------------------------------------------------------


class AnnotResultFieldset(SPPASAnnotateNode):

    def __init__(self, parent_id: str):
        super(AnnotResultFieldset, self).__init__(parent_id, "result")
        self._msg = MSG_ANN_NAME

    # ---------------------------------------------------------------------------

    def update(self) -> None:
        """Create HTML nodes of the fieldset."""
        logging.debug(f" ====== {self.identifier} node update form ===== ")
        self.clear_children()

        h1 = HTMLNode(self.identifier, None, "h1", value=MSG_FIELD_TITLE)
        self.append_child(h1)

        # In case of error(s):
        if "result" not in self._ann_results:
            result = HTMLNode(self.identifier, None, "p", value=MSG_NO_RESULT)
            self.append_child(result)
            # Re-annotate button
            self._create_restart_button()
            return

        sequence = MSG_RESULT + "<span style='font-size:120%; font-weight:bold;'>" + self._ann_results["cuedspeech"][0] + "</span>"
        p = HTMLNode(self.identifier, None, "p", value=sequence)
        self.append_child(p)
        cs_result = self._ann_results["result"][1]

        if cs_result is None or "None" in cs_result:
            result = HTMLNode(self.identifier, None, "p", value=MSG_NO_RESULT)
            self.append_child(result)
            # Re-annotate button
            self._create_restart_button()
            return

        # Everything is going well. There's a result to display!
        for result in ast.literal_eval(cs_result):

            cuedsp = result[0].replace("%27", "'").split(separators.syllables)
            phones = result[1].replace("%27", "'").split(separators.syllables)
            _with_phones = True
            if len(cuedsp) != len(phones):
                _with_phones = False

            for i, key_code in enumerate(cuedsp):

                result = HTMLNode(self.identifier, None, "h3", value=key_code)
                self.append_child(result)

                if _with_phones is True:
                    phon_code = phones[i]
                    if "nil" in phones[i]:
                        phon_code = phon_code.replace("vnil", "&empty;")
                        phon_code = phon_code.replace("cnil", "&empty;")
                    result = HTMLNode(self.identifier, None, "p", value=phon_code)
                    self.append_child(result)

                # create result image visualization
                content = key_code.split(separators.phonemes)
                if len(content) == 2:
                    shape_code, vowel_code = content
                else:
                    logging.error("Malformed key: {:s}".format(key_code))
                    continue

                # the images of the hand and the face are in a section
                sec = HTMLNode(self.identifier, None, "section", attributes={'class': "box-images"})
                self.append_child(sec)

                # create hand shape image
                hand_img = HTMLNode(sec.identifier, None, "img", attributes={
                    'src': wapp_settings.images + f"/textcued/drawcue_{shape_code}.png",
                    'alt': "Hand shape for the current hand shape",
                    'class': "hand-img"
                })
                sec.append_child(hand_img)

                # create face target image
                face_img = HTMLNode(sec.identifier, None, "img", attributes={
                    'src': wapp_settings.images + f"/textcued/pos_{vowel_code}.png",
                    'alt': "Face with pointer to indicate the current target of the hand"
                })
                sec.append_child(face_img)

        # Re-annotate button
        self._create_restart_button()
        self._ann_results["result"] = [self._ann_results["cuedspeech"][0], cs_result]

    # -----------------------------------------------------------------------

    def _create_restart_button(self):
        """Create a button to go back to the textcue.html page.

        "textcue.html" redirection page name should not be hard-coded.

        """
        node = HTMLNode(self.identifier, None, "section")
        self.append_child(node)
        node.append_child(HTMLNode(node.identifier, None, "hr"))
        a = HTMLNode(node.identifier, None, "a", value=MSG_BACK,
                     attributes={"href": "textcue.html", "role": "button", "class": "action-button flex-panel"})
        node.append_child(a)

        redo_icon = sppasImagesAccess.get_icon_filename("redo")
        img = HTMLNode(a.identifier, None, "img",
                       attributes={"src": redo_icon, "alt": "", "class": "small-logo"})
        a.append_child(img)

    # -----------------------------------------------------------------------

    def _create_form(self) -> None:
        """Override. Create the form to be filled-in with annotation configuration.

        """
        pass

    # -----------------------------------------------------------------------

    def _fill_content_form(self) -> None:
        """Override. Fill the form with annotation parameters and input.

        """
        pass

    # -----------------------------------------------------------------------

    def _fill_button_form(self) -> None:
        """Override. Fill the form with annotation parameters and input.

        """
        pass
