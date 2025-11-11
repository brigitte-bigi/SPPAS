"""
:filename: sppas.ui.swapp.app_videocued.view_hands.py
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
import os
import logging
from whakerpy import HTMLNode

from sppas.src.annotations.CuedSpeech import sppasCuedSpeech

from ..components import BaseViewNode

# -----------------------------------------------------------------------

VIEW_MSG = "Hands choices"

JS_SCRIPT = """
function hands_chosen(radio_button) {
    const request_manager = new RequestManager();
    request_manager.send_post_request({'hands_chosen': radio_button.value});

    // reset old hands panel chosen
    let old_hands_panel = document.getElementById("selected");
    if (old_hands_panel != null) {
        old_hands_panel.id = "";
    }

    // set new hands panel chosen
    radio_button.parentNode.id = "selected";
}

async function change_hand_pos(button, value) {
    const request_manager = new RequestManager();
    const response = await request_manager.send_post_request({'change_hand_pos': [button.name, value]});

    // change hand image with new hand pos of the response
    let hand_img = document.getElementById("hand-img-" + button.name);
    hand_img.src = "resources/cuedspeech/" + button.name + "_" + response['hand_pos'] + ".png";
}
"""

# -----------------------------------------------------------------------


class ViewHands(BaseViewNode):

    def __init__(self, parent_id: str):
        super(ViewHands, self).__init__(parent_id, VIEW_MSG.replace(' ', '_'))
        self._msg = VIEW_MSG
        self._script = JS_SCRIPT

        # set attributes of hands sets
        self.__hands = dict()
        self.__hands_chosen = ""
        for hands_set_name in sppasCuedSpeech.get_hands_sets():
            self.__hands[hands_set_name] = 5

        if len(self.__hands) > 0:
            self.__hands_chosen = sppasCuedSpeech.get_hands_sets()[0]

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def get_hands_set_chosen(self) -> str:
        return self.__hands_chosen

    # -----------------------------------------------------------------------

    def get_hand_pos(self, hands_set: str) -> int:
        return self.__hands.get(hands_set)

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM BaseView
    # -----------------------------------------------------------------------

    def validate(self) -> bool:
        return self.__hands_chosen is not None

    # -----------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        code = 205

        if event_name == "hands_chosen":
            if event_value in sppasCuedSpeech.get_hands_sets():
                self.__hands_chosen = event_value
                code = 200
            else:
                logging.warning(f"Unknown hands set value : {event_value}")
                code = 422

        elif event_name == "change_hand_pos":
            hands_set, index_value = event_value

            if hands_set in self.__hands.keys():
                self.__hands[hands_set] = self.__hands[hands_set] + index_value

                if self.__hands[hands_set] < 0:
                    self.__hands[hands_set] = 8
                elif self.__hands[hands_set] > 8:
                    self.__hands[hands_set] = 0

                code = 200

            else:
                logging.warning(f"Unknown hands set value : {event_value}")
                code = 422

        return code

    # -----------------------------------------------------------------------

    def update(self) -> None:
        self.clear_children()

        h2_desc = HTMLNode(self.identifier, None, "h2", value="Choose a hands set to tag the video")

        # creates all hands panels
        hands_container = HTMLNode(self.identifier, "hands-box", "section", attributes={'class': "hands-box"})
        for hands_set_name in self.__hands:
            hands_container.append_child(self.__create_hands_panel(hands_container.identifier, hands_set_name))

        # create previous and validate button to navigate with the view
        btn_panel = HTMLNode(self.identifier, None, "section", attributes={'class': "flex-panel"})

        prev_button = HTMLNode(btn_panel.identifier, None, "button", value="Back", attributes={
            'name': "prev_view",
            'onclick': "notify_event(this)"
        })
        btn_panel.append_child(prev_button)

        validate_button = HTMLNode(btn_panel.identifier, None, "button", value="Validate", attributes={
            'name': "next_view",
            'onclick': "notify_event(this)"
        })
        btn_panel.append_child(validate_button)

        # append elements
        self.append_child(h2_desc)
        self.append_child(hands_container)
        self.append_child(btn_panel)

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __create_hands_panel(self, parent_id: str, hands_set_name: str) -> HTMLNode:
        # create panel
        panel = HTMLNode(parent_id, hands_set_name, "div", attributes={'class': "hands-panel"})

        # create name of the hands set
        name = HTMLNode(panel.identifier, None, "h3", value=hands_set_name)

        # create buttons to change the hand cued position
        prev_button = HTMLNode(panel.identifier, None, "button", value="&#8656;", attributes={
            'name': hands_set_name,
            'class': "arrow-btn prev",
            'onclick': "change_hand_pos(this, -1)"
        })

        next_button = HTMLNode(panel.identifier, None, "button", value="&#8658;", attributes={
            'name': hands_set_name,
            'class': "arrow-btn next",
            'onclick': "change_hand_pos(this, 1)"
        })

        # create hand image
        hand = HTMLNode(panel.identifier, None, "img", attributes={
            'src': os.path.join("resources", "cuedspeech", f"{hands_set_name}_{self.__hands[hands_set_name]}.png"),
            'alt': f"Current Hand image of the {hands_set_name} set of hands",
            'id': f"hand-img-{hands_set_name}",
            'class': "hand-img"
        })

        # create button to choose the hands set
        button_choose = HTMLNode(panel.identifier, None, "input", attributes={
            'type': "radio",
            'name': "hands_set_choose",
            'value': hands_set_name,
            'onclick': f"hands_chosen(this)"
        })

        # custom properties if the hands set is the selected
        if hands_set_name == self.__hands_chosen:
            panel.set_attribute("id", "selected")
            button_choose.set_attribute("checked", "checked")

        # add elements to the container
        panel.append_child(prev_button)
        panel.append_child(name)
        panel.append_child(next_button)
        panel.append_child(hand)
        panel.append_child(button_choose)

        return panel
