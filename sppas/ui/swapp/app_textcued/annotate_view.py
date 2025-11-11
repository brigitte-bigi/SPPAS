"""
:filename: annotate_view.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: The base node to perform an automatic annotation.

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

from __future__ import annotations
import random
import logging

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLButtonNode

from sppas.src.annotations import sppasParam
from sppas.core.coreutils import ISO639
from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess

from ..components import BaseViewNode

# ---------------------------------------------------------------------------


class SPPASAnnotateNode(BaseViewNode):
    """Base class representing a section to perform an automatic annotation.

    """

    MSG_LANG = _("Choose language resource: ")
    MSG_TEXT = _("Enter or verify the text to be annotated automatically: ")
    MSG_TEXT_HERE = _("Enter or paste your text here")

    # -----------------------------------------------------------------------

    def __init__(self, parent_id, annotation_id, title="", legend=""):
        """Create the section node for an annotation.

        The created node is a fieldset element with the given annotation_id identifier.

        :param parent_id: (str) Parent node identifier
        :param annotation_id: (str) Annotation identifier.
        :param title: (str) the section title

        """
        super(SPPASAnnotateNode, self).__init__(parent_id, annotation_id)
        # The stringified results of the annotations.
        self._ann_results = dict()

        # A short version of the title to print in the views bar
        self._msg = title

        # Default text for the action button
        self._btn_text = annotation_id

        # Fill-in the node with children
        self.__create(legend)

        # Annotation parameters -- should be for annotation steps only
        config_name = annotation_id + ".json"
        logging.debug(config_name)
        self._parameters = sppasParam([config_name])
        self._ann_step_idx = self._parameters.activate_annotation(annotation_id)

    # -----------------------------------------------------------------------

    def set_ann_results(self, results: dict()) -> None:
        """Store results of all annotations.

        :param results: (dict) Dict of tuple(result, input_text, input_descr)

        """
        self._ann_results = results

    # -----------------------------------------------------------------------

    def update(self) -> None:
        """Update the form content."""
        self._form.clear_children()
        self._add_task_in_form()
        # An annotation fieldset content.
        # Must be overridden to define a specific annotation content.
        self._fill_content_form()
        self._fill_button_form()

    # -----------------------------------------------------------------------
    # To be overridden by SubClasses
    # -----------------------------------------------------------------------

    @staticmethod
    def serialize_ann_result(result) -> str:
        """Convert the annotation result into a human-readable string.

        Must be overridden by subclasses that are annotating.

        :return: (str) to be defined by the subclasses

        """
        return str(result)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_ann_result(result) -> str:
        """Convert the annotation result into an input for the next annotation.

        Must be overridden by subclasses that are annotating.

        :return: (str) to be defined by the subclasses

        """
        return ""

    # -----------------------------------------------------------------------

    @staticmethod
    def annotate(text: str, lang: str = "und") -> tuple:
        """Return the result of annotation on the given text.

        Must be overridden by subclasses that are annotating.

        :param text: (str) Input text to be annotated
        :param lang: (str) Language of the text (iso639-1)
        :return: (tuple) with list of tokens, str, str

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Protected -- construct the UI
    # -----------------------------------------------------------------------

    def _add_task_in_form(self) -> None:
        """Indicate the annotation identifier in a hidden input of the form.

        Should not be overridden. Must be added to any 'form' child element.

        """
        task_name = "task"
        task = HTMLNode(self._form.identifier, None, "input",
                        attributes={"name": task_name, "type": "hidden", "value": self.identifier})
        self._form.append_child(task)

    # -----------------------------------------------------------------------
    # Can be overridden
    # -----------------------------------------------------------------------

    def _set_lang_choices(self):
        """Fill-in the dictionary with language choices."""
        _choices = dict()
        if self._ann_step_idx > -1:
            iso_codes = self._parameters.get_langlist(self._ann_step_idx)
            for code in iso_codes:
                info = ISO639.LANGUAGES.get(code, None)
                if info is not None:
                    lang_name = info.language_name
                else:
                    lang_name = "Undefined"
                _choices[code] = lang_name
            logging.debug(f"Languages for annotation {self.identifier}: {_choices}")
        else:
            logging.debug(f"No language for annotation {self.identifier}")

        return _choices

    # -----------------------------------------------------------------------

    def _fill_content_form(self) -> None:
        """Fill the form with annotation parameters and input.

        Generic inputs: the language and a textarea.

        """
        # Annotation language
        # self._lang_choices({"fra": "Français", "eng": "American English"})
        self._lang_choices(self._set_lang_choices())

        # Text to be annotated
        self._input_textarea(SPPASAnnotateNode.MSG_TEXT, SPPASAnnotateNode.MSG_TEXT_HERE)

    # -----------------------------------------------------------------------

    def _lang_choices(self, languages: dict):
        """Create both a label and a select element with the list of language resources.

        :param languages: (dict) key=iso639-3 value=name

        """
        label = HTMLNode(self._form.identifier, None, "label",
                         attributes={"for": "lang"},
                         value=SPPASAnnotateNode.MSG_LANG)
        self._form.append_child(label)
        div = HTMLNode(self._form.identifier, None, "div",
                       attributes={"class": "select width_50"})
        self._form.append_child(div)
        select = HTMLNode(div.identifier, None, "select",
                          attributes={"id": "lang", "name": "lang"})
        div.append_child(select)

        for iso in languages:
            description = iso + " - " + languages[iso]
            option = HTMLNode(select.identifier, None, "option",
                              attributes={"value": iso}, value=description)
            select.append_child(option)

    # -----------------------------------------------------------------------

    def _input_textarea(self, label_text, placeholder=""):
        """Add a textarea to the form.

        """
        label = HTMLNode(self._form.identifier, None, "label", attributes={"for": "input_text"},
                         value=label_text)
        self._form.append_child(label)
        att = dict()
        att["id"] = "input_text"
        att["name"] = "input_text"
        att["required"] = None
        att["class"] = "text-input width_full"
        att["placeholder"] = placeholder
        att["maxlength"] = "128"  # max nb of chars
        att["rows"] = "4"
        textarea = HTMLNode(self._form.identifier, None, "textarea", attributes=att)
        self._form.append_child(textarea)

        # the textarea content is the current input in result, if exists.
        if self.identifier in self._ann_results:
            r = self._ann_results[self.identifier]
            if len(r[1]) > 0:
                textarea.set_value(r[1].replace("%27", "'"))

    # -----------------------------------------------------------------------

    def _fill_button_form(self):
        """Add the annotation button and results to the form.

        """
        # Action button
        # --------------
        att = dict()
        att["type"] = "submit"
        att["class"] = "flex-panel center action-button"
        btn = HTMLButtonNode(self._form.identifier, self.identifier + "_action_btn", attributes=att)
        annot_icon = sppasImagesAccess.get_icon_filename("annotation")
        btn.set_icon(annot_icon, attributes={"class": "flex-item small-logo"})
        btn.set_text("submit_text", self._btn_text, attributes={"class": "flex-item center"})
        self._form.append_child(btn)

        # Hidden inputs used to store previous results
        # --------------------------------------------
        for a in self._ann_results:
            r = self._ann_results[a]

            node = HTMLNode(self._form.identifier, a + "_0_result", "input",
                            attributes={"name": a + "_0_result", "type":"hidden", "value":r[0]})
            self._form.append_child(node)

            node = HTMLNode(self._form.identifier, a + "_1_result", "input",
                            attributes={"name": a + "_1_result", "type":"hidden", "value":r[1]})
            self._form.append_child(node)

    # -----------------------------------------------------------------------

    def _create_form(self) -> None:
        """Create the form to be filled-in with annotation configuration.

        """
        att = dict()
        att["id"] = "annotate_form"
        att["method"] = "POST"
        page_id = random.randint(10000, 99999)
        att["action"] = "textcueing_{:d}.html".format(page_id)
        self._form = HTMLNode(self._fieldset.identifier, att["id"], "form", attributes=att)
        self._fieldset.append_child(self._form)
        self._add_task_in_form()

    # -----------------------------------------------------------------------

    def _create_extra_content(self) -> None:
        """Create any content to be added after the fieldset.

        """
        pass

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __create(self, legend):
        """Create the children nodes."""
        # A fieldset with its legend
        self._fieldset = HTMLNode(self.identifier, "annotate_fieldset", "fieldset", attributes={"class": "annotate-fieldset"})
        self.append_child(self._fieldset)

        node = HTMLNode(self._fieldset.identifier, None, "legend", value=legend)
        self._fieldset.append_child(node)

        # A form with annotation input and parameters
        self._create_form()

        # Any content to be added below the form
        self._create_extra_content()
