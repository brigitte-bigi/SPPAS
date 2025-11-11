"""
:filename: sppas.ui.swapp.app_videocued.view_filters.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a view node of the Cued Tag app to choose the hands set to use.

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

from __future__ import annotations
import os
import logging
import cv2

from whakerpy.htmlmaker import HTMLNode

from sppas.core.coreutils import sppasError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageSightsReader
from sppas.src.annotations.CuedSpeech import sppasCuedSpeech
from sppas.src.annotations.CuedSpeech.whowtag.handproperties import sppasHandProperties
from sppas.src.annotations.CuedSpeech.whowtag import sppasHandFilters
from sppas.ui import _

from ..components import BaseViewNode
from ..components import AnnotParamDialog

# -----------------------------------------------------------------------


MSG_VIEW_TITLE = _("Hands filter")
MSG_APPLY_FILTER = _("A filter can optionally be applied on the hands")
MSG_PREVIOUS = _("Previous")
MSG_NEXT = _("Next")
MSG_CONFIGURE = _("Configure")
MSG_ANNOTATE = _("Annotate")

# -----------------------------------------------------------------------


JS_SCRIPT = """
function filter_chosen(radio_button) {
    const request_manager = new RequestManager();
    request_manager.send_post_request({'filter_chosen': radio_button.value});

    // reset old hands panel chosen
    let old_hands_panel = document.getElementById("selected");
    if (old_hands_panel != null) {
        old_hands_panel.id = "";
    }

    // set new hands panel chosen
    radio_button.parentNode.id = "selected";
}

async function load_hand_filtered(filter) {
    const request_manager = new RequestManager();
    const imageBlob = await request_manager.send_post_request({'load_hand': filter}, "image/png");

    // load hand image received from request
    let url = URL.createObjectURL(imageBlob);
    const loadImagePromise = new Promise(resolve => {
        let hand_img = document.getElementById("hand-" + filter);
        
        hand_img.onload = () => {
            URL.revokeObjectURL(url);
            resolve();
        };
        hand_img.src = url;
    });

    await loadImagePromise;
}

OnLoadManager.addLoadFunction(async () => {
    const filters = [%filters%];
    
    for (let i = 0; i < filters.length; i++) {
        await load_hand_filtered(filters[i]);
    }
})
"""


# -----------------------------------------------------------------------


class ViewFilter(BaseViewNode):

    def __init__(self, parent_id: str):
        super(ViewFilter, self).__init__(parent_id, MSG_VIEW_TITLE.replace(' ', '_'))
        self._msg = MSG_VIEW_TITLE

        self.__hands_filtered = dict()
        self.__ann_options = AnnotParamDialog("cuedspeech", self.identifier)
        self.__ann_options.set_option("createvideo", True)

        # hidden in the dialog useless options already configure by the interface
        self.__ann_options.hide_option_element("createvideo")
        self.__ann_options.hide_option_element("handsset")
        self.__ann_options.hide_option_element("handsfilter")

        self.__set_script()

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def get_options(self) -> list:
        return self.__ann_options.get_options()

    # -----------------------------------------------------------------------

    def get_filtered_hand(self, filter_name: str) -> bytes:
        return cv2.imencode('.png', self.__hands_filtered[filter_name])[1].tostring()

    # -----------------------------------------------------------------------
    # SETTERS
    # -----------------------------------------------------------------------

    def set_hands_set(self, hands_set: str) -> None:
        if hands_set == self.__ann_options.get_option_value("handsset"):
            return None

        if hands_set in sppasCuedSpeech.get_hands_sets():
            self.__ann_options.set_option("handsset", hands_set)
            self.__ann_options.set_option("handsfilter", "")
        else:
            logging.warning(f"Incorrect given hands set: {hands_set}")

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM BaseView
    # -----------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        # event when the user choose a filter (click on a radio button)
        if event_name == "filter_chosen":
            if event_value in sppasCuedSpeech.get_hands_filters():
                self.__ann_options.set_option("handsfilter", event_value)
                code = 200
            else:
                logging.warning(f"Unknown filter name: {event_value}")
                code = 422

        # event during the page loading to get filtered hand
        elif event_name == "load_hand":
            if event_value in self.__hands_filtered.keys():
                code = 200
            else:
                logging.warning(f"Unknown filter name: {event_value}")
                code = 422

        # unknown event
        else:
            # check if it's an event for the annotation option (config button which open the dialog)
            # if it's not the method return 205 code
            code = self.__ann_options.process_event(event_name, event_value)

        return code

    # -----------------------------------------------------------------------

    def update(self) -> None:
        self.clear_children()

        if self.__ann_options.get_option_value("handsset") is None:
            raise sppasError("Missing hands set to display this view!")

        # add options configuration
        self.__ann_options.bake()
        self.append_child(self.__ann_options)

        # add title message
        h2_desc = HTMLNode(self.identifier, None, "h2", value=MSG_APPLY_FILTER)
        filters_container = self.__create_filter_options()

        # create buttons nav
        buttons_container = HTMLNode(self.identifier, "buttons-container", "section",
                                     attributes={'class': "flex-panel"})

        prev_button = HTMLNode(buttons_container.identifier, None, "button", 
                               value=MSG_PREVIOUS, 
                               attributes={'name': "prev_view",'onclick': "notify_event(this)"})

        configure_button = HTMLNode(buttons_container.identifier, None, "button", 
                                    value=MSG_CONFIGURE,
                                    # open_dialog() is a function from dialog.js
                                    attributes={'onclick': "open_dialog('cuedspeech-options', true);"})  
                                                
        validate_button = HTMLNode(buttons_container.identifier, None, "button", 
                                   value=MSG_ANNOTATE,
                                   attributes={'name': "next_view", 'onclick': "notify_event(this)"})

        buttons_container.append_child(prev_button)
        buttons_container.append_child(configure_button)
        buttons_container.append_child(validate_button)

        # append children to the view
        self.append_child(h2_desc)
        self.append_child(filters_container)
        self.append_child(buttons_container)

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __set_script(self) -> None:
        # prepare the JS script
        filters_str = ""
        for filter_name in sppasCuedSpeech.get_hands_filters():
            filters_str += f"'{filter_name}', "
        filters_str = filters_str[:-2]

        script = JS_SCRIPT.replace("%filters%", filters_str)
        script += "\n" + self.__ann_options.get_script()  # add the annotation options dialog script

        self._script = script

    # -----------------------------------------------------------------------

    def __create_filter_options(self) -> HTMLNode:
        filters_container = HTMLNode(self.identifier, "filters-box", "section",
                                     attributes={'class': "hands-box"})

        for filter_name in sppasHandFilters.get_filter_names():
            panel = HTMLNode(filters_container.identifier, f"{filter_name}-panel", "div",
                             attributes={'class': "hands-panel"})
            h3_name = HTMLNode(panel.identifier, None, "h3", value=filter_name)

            # create radio button
            button_choose = HTMLNode(
                panel.identifier, None, "input",
                attributes={
                    'type': "radio",
                    'name': "filter_choose",
                    'value': filter_name,
                    'onclick': f"filter_chosen(this)"
                })

            # Create hand images
            self.__hands_filtered[filter_name] = self.__apply_filter(
                filter_name, 
                shape_code="3" if filter_name == "sticks" else "5")
            
            hand_img = HTMLNode(
                panel.identifier, None, "img",
                attributes={
                    'id': f"hand-{filter_name}",
                    'alt': f"Hand image with {filter_name} filter applied."
                })

            # Custom properties if the hands set is the selected
            if filter_name == self.__ann_options.get_option_value("handsfilter"):
                panel.set_attribute("id", "selected")
                button_choose.set_attribute("checked", "checked")

            # Append children
            panel.append_child(h3_name)
            panel.append_child(hand_img)
            panel.append_child(button_choose)

            filters_container.append_child(panel)

        return filters_container

    # -----------------------------------------------------------------------

    def __apply_filter(self, filter_name: str, shape_code: str = "5") -> sppasImage:
        hand_img = sppasImage(
            filename=os.path.join(os.path.join("resources", "cuedspeech",
                                  f"{self.__ann_options.get_option_value('handsset')}_{shape_code}.png")))
        hand_sights = sppasImageSightsReader(
            os.path.join("resources", "cuedspeech", f"{self.__ann_options.get_option_value('handsset')}_{shape_code}-hands.xra"))

        # Search target index value depending on the current consonant code
        target_index = 12
        if shape_code == "0":
            target_index = 9
        elif shape_code in ("1", "6", "8"):
            target_index = 8

        # Apply the filter
        try:
            hand_properties = sppasHandProperties(hand_img, hand_sights.sights[0], target_index)
            hands_filter = sppasHandFilters()
            return getattr(hands_filter, filter_name)(hand_properties, str(shape_code))
        except AttributeError:
            logging.error(f"Unknown hands filter {filter_name}")
            return None
