"""
:filename: sppas.ui.swapp.app_videocued.view_workspace.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a view node of the Cued Tag app to choose the workspace to use.

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

from sppas.src.wkps.workspace import States
from sppas.src.wkps.sppasWkps import sppasWkps

from ..components import BaseViewNode

# -----------------------------------------------------------------------

VIEW_MSG = "Workspace and files choice"

JS_SCRIPT = """
async function wkps_select_change(element) {
    const request_manager = new RequestManager();
    await request_manager.send_post_request({wkps_chosen: element.value});

    if (request_manager.status === 200) {
        window.location = window.location.href;
    }
}

function check_file(element) {
    const request_manager = new RequestManager();

    if (element.checked) {
        request_manager.send_post_request({checked_file: element.value});
    } else {
        request_manager.send_post_request({unchecked_file: element.value});
    }
}
"""

# -----------------------------------------------------------------------


class ViewWorkspace(BaseViewNode):

    def __init__(self, parent_id: str):
        super(ViewWorkspace, self).__init__(parent_id, VIEW_MSG.replace(' ', '_'))
        self._msg = VIEW_MSG
        self._script = JS_SCRIPT

        self.__workspace_chosen = ""
        self.__files = list()
        self.__wkps = sppasWkps()

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def get_files(self, workspace: bool = False) -> tuple:
        if workspace is True:
            return self.__workspace_chosen, self.__files
        else:
            return self.__files

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM BaseView
    # -----------------------------------------------------------------------

    def validate(self) -> bool:
        if len(self.__workspace_chosen) == 0:
            return False

        if len(self.__files) == 0:
            return False

        return True

    # -----------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        code = 200

        if event_name == 'wkps_chosen':
            if len(event_value) == 0 or event_value in self.__wkps:
                self.__workspace_chosen = event_value

                if len(event_value) > 0:
                    self.__files = self.__get_all_wkp_files(event_value, States().CHECKED)

            else:
                logging.warning(f"Unknown received workspace name : {event_value}")
                code = 400

        elif event_name == "checked_file":
            if event_value not in self.__files:
                self.__files.append(event_value)
            else:
                logging.warning(f"file checked received but already checked in back-end : {event_value}")
                code = 400

        elif event_name == "unchecked_file":
            if event_value in self.__files:
                self.__files.remove(event_value)
            else:
                logging.warning(
                    f"file unchecked received but doesn't found in the list of selected file : {event_value}")
                code = 400

        # unknown event received
        else:
            code = 205

        return code

    # -----------------------------------------------------------------------

    def update(self) -> None:
        self.clear_children()

        h2 = HTMLNode(self.identifier, None, "h2", value="Choose a workspace and its files to use")
        self.append_child(h2)

        self.__create_wkps_choice()

        if len(self.__workspace_chosen) > 0:
            self.append_child(HTMLNode(self.identifier, None, "hr"))
            self.__create_files_choice()

            next_button = HTMLNode(self.identifier, None, "button", value="Validate", attributes={
                'name': "next_view",
                'onclick': "notify_event(this)"
            })
            self.append_child(next_button)

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __create_wkps_choice(self) -> None:
        select = HTMLNode(self.identifier, "wkps-select", "select",
                          attributes={'id': "wkps-select", 'onchange': "wkps_select_change(this)"})
        self.append_child(select)

        default_option = HTMLNode(select.identifier, None, "option", value="",
                                  attributes={'value': ""})
        select.append_child(default_option)

        for wkp_name in self.__wkps:
            current_option = HTMLNode(select.identifier, None, "option", value=wkp_name, attributes={'value': wkp_name})
            if wkp_name == self.__workspace_chosen:
                current_option.set_attribute("selected", "selected")

            select.append_child(current_option)

    # -----------------------------------------------------------------------

    def __create_files_choice(self):
        files_section = HTMLNode(self.identifier, "files-section", "section")
        self.append_child(files_section)

        files = self.__get_all_wkp_files(self.__workspace_chosen, States().CHECKED)

        for current_file in files:
            filename = os.path.basename(current_file)

            checkbox = HTMLNode(files_section.identifier, None, "input", attributes={
                'type': "checkbox",
                'name': filename,
                'value': current_file,
                'onchange': "check_file(this)"
            })
            if current_file in self.__files:
                checkbox.set_attribute("checked", "checked")
            files_section.append_child(checkbox)

            checkbox_label = HTMLNode(files_section.identifier, None, "label", value=filename, attributes={'for': filename})
            files_section.append_child(checkbox_label)

    # -----------------------------------------------------------------------

    def __get_all_wkp_files(self, workspace_name: str, states: int) -> list:
        wkp_index = self.__wkps.index(workspace_name)
        workspace = self.__wkps.load_data(wkp_index)
        files = workspace.get_filename_from_state(states)

        files_path = list()
        for current in files:
            files_path.append(str(current))

        return files_path
