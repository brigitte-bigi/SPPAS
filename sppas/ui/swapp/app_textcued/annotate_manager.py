"""
:filename: annotate_page.annotate_manager.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Fieldsets Management of annotate page.

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

import re
from whakerpy import HTMLNode

from ..components import BaseViewNode
from ..components import ViewManager
from ..components import ViewBarNode

from .norm_fieldset import NormalizeFieldset
from .phon_fieldset import PhonetizeFieldset
from .cuedsp_fieldset import CuedspeechFieldset
from .result_fieldset import AnnotResultFieldset

# -----------------------------------------------------------------------


def strip_string(entry):
    """Strip the string: multiple whitespace, tab and CR/LF.

     Remove multiple whitespace, tab and CR/LF inside the string.

     :return: (str)

     """
    e = re.sub("[\t]+", r" ", entry)
    e = re.sub("[\n]+", r" ", e)
    e = re.sub("[\r]+", r" ", e)
    if "\ufeff" in e:
        e = re.sub("\ufeff", r" ", e)

    e = re.sub("[\\s]+", r" ", e)
    return e

# ---------------------------------------------------------------------------


class AnnViewManager(ViewManager):
    """Manager for a series of annotation views."""

    def __init__(self, parent_id):
        """Create a view manager dedicated to some of the SPPAS annotations.

        :param parent_id: (str) Parent node identifier

        """
        all_views = (
            NormalizeFieldset(parent_id),
            PhonetizeFieldset(parent_id),
            CuedspeechFieldset(parent_id),
            AnnotResultFieldset(parent_id)
        )
        super(AnnViewManager, self).__init__(all_views)

        # A dictionary to store each annotation input/output:
        # Key is the annotation identifier. Value is a tuple with:
        #  - 0: the serialized result returned by annotate() -- used by the wizard
        #  - 1: the input text given to annotate() -- used by the annotation
        #  - 2: the result returned by annotate() "as it" but converted into a string
        self._results = dict()
        self.__reset_results()

    # ---------------------------------------------------------------------------

    def process_annotate_events(self, events: dict) -> bool:
        """Process the given events coming from the response.

        It is supposed that the events dictionary only contains events related to
        the annotation -- but not events for any other page!

        :param events: (dict) key=event_name, value=event_value
        :return: (bool) False if invalid events

        """
        # Restart to first view process
        if len(events) == 0:
            self.set_current_view_by_index(0)
            return True

        lang = "und"
        text = ""
        task = None

        # Collect information of the form
        for event_name, event_value in events.items():
            # Set annotation task
            if event_name == "task":
                task = event_value

            # Set annotation lang
            if event_name == "lang":
                lang = event_value

            # Get the text from the event for the annotation input:
            #  -> the input text, or the normalization text
            elif event_name == "input_text":
                # Format text by removing multiple whitespace, \n and \t
                text = strip_string(event_value)

            # Get the text from the event for the annotation input: cuedspeech
            #  -> the phonetization the user has chosen
            elif event_name.endswith("phon_input"):
                text += f"{event_value} "

            # Get previous results from the hidden inputs
            # A result is a list but it is collected item by item!
            elif event_name.endswith("_result"):
                information = event_name.split("_")
                view_id = information[0]
                if view_id in self.get_views_identifiers():
                    # Get result item index and store this result
                    res_idx = int(information[1])
                    self.set_result(view_id, res_idx, event_value.replace('%encoded%', ','))

        # Process the current annotation
        if task in self.get_views_identifiers():
            # Perform the task
            self.set_current_view(task)
            self.annotate(task, text, lang)
            self.next_view()
            return True
        else:
            return False

    # ---------------------------------------------------------------------------
    # Override from ViewManager
    # ---------------------------------------------------------------------------

    def set_current_view(self, view: BaseViewNode | str) -> None:
        """Override.

        :param view: (BaseView|str) View instance or node identifier
        :raises: sppasTypeError: If the index isn't an integer
        :raises: IndexRangeException: If the index is negative or out of bounds
        :return: (BaseView) The instance of the new current view or None if the view doesn't found in the manager

        """
        super().set_current_view(view)

        # Reset when restart to the first view
        if self.get_current_view_index() == 0:
            self.__reset_results()

        # Update its results
        self.get_current_view().set_ann_results(self._results)

    # ---------------------------------------------------------------------------
    # Override parent method
    # ---------------------------------------------------------------------------

    def next_view(self) -> None:
        """Override. Overrides in order to assign results to views.

        :raises: sppasTypeError: If the index isn't an integer
        :raises: IndexRangeException: If the index is negative or out of bounds

        """
        super().next_view()

        # Update its results
        self.get_current_view().set_ann_results(self._results)

    # ---------------------------------------------------------------------------
    # GETTERS & SETTERS
    # ---------------------------------------------------------------------------

    def get_results(self) -> dict:
        """Return a copy of the results."""
        return self._results.copy()

    # ---------------------------------------------------------------------------

    def set_result(self, annotation_id: str, idx: int, result: str) -> None:
        """Store the result of a previously performed annotation.

        :param annotation_id: (str) The annotation identifier
        :param idx: (int) Index of the given result (0=ann result, 1=ann input)
        :param result: (str)

        """
        if annotation_id in self._results and idx in (0, 1):
            self._results[annotation_id][idx] = result

    # ---------------------------------------------------------------------------
    # PUBLIC METHODS
    # ---------------------------------------------------------------------------

    def annotate(self, annotation_id: str, text, lang) -> None:
        """Perform the given annotation and store its serialized results.

        :param annotation_id: (str) The annotation identifier
        :param text: (str) The input text to be annotated
        :param lang: (str) The input language

        """
        view = self.get_view(annotation_id)
        if view is not None:
            # Annotate, get output result, store it
            try:
                result = view.annotate(text, lang)
                serialized_result = view.serialize_ann_result(result)
                formatted_result = view.format_ann_result(result)
            except NotImplementedError:
                # This view can't annotate! Define an empty result.
                result = ""
                serialized_result = ""
                formatted_result = ""

            # Store this result into the current dictionary of results
            self._results[annotation_id] = [serialized_result, text]

            # Store the formatted result as input of the next annotation
            idx = self.get_current_view_index()
            if self.has_next() is True:
                next_id = self[idx+1].identifier
                self._results[next_id] = ["", formatted_result]

        # Update results in views
        for view_id in self.get_views_identifiers():
            self.get_view(view_id).set_ann_results(self._results)

    # ---------------------------------------------------------------------------
    # PRIVATE METHODS
    # ---------------------------------------------------------------------------

    def __reset_results(self):
        """Reset the stored results."""
        self._results.clear()
        for view_id in self.get_views_identifiers():
            self._results[view_id] = ["", ""]

# ---------------------------------------------------------------------------


class AnnViewBar(ViewBarNode):

    # ---------------------------------------------------------------------------
    # Override from ViewBar
    # ---------------------------------------------------------------------------

    def _create_wizards(self) -> None:
        super()._create_wizards()

        for i, view_id in enumerate(self._views.get_views_identifiers()):
            node = self._items[i]
            results = self._views.get_results()[view_id]
            if len(results[0]) > 0:
                if view_id == "result":
                    p = HTMLNode(node.identifier, None, "p", value=results[0])
                    node.append_child(p)
                else:
                    p = HTMLNode(node.identifier, None, "p", value=results[1])
                    node.append_child(p)
