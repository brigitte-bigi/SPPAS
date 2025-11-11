"""
:filename: sppas.ui.swapp.app_videocued.view_exec.py
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a "Run" view node of the Cued Tag app.

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
from threading import Thread
from whakerpy import HTMLNode

from sppas.core.coreutils import sppasError
from sppas.src.wkps import sppasWorkspace
from sppas.src.wkps import sppasWkpRW
from sppas.src.anndata import sppasTrsRW
from sppas.src.videodata import video_extensions
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag import CuedSpeechVideoTagger

from ..components import BaseViewNode

# -----------------------------------------------------------------------

VIEW_MSG = "Annotation Running"

JS_SCRIPT = """
let loop_id;

function updateAnnotationProcess() {
    const request_manager = new RequestManager();

    // send request to the server
    request_manager.send_post_request({"update_process": true})
        .then(response => {
            if (response["process_running"] === false) {
                // Process finished, we don't need to re-ask the progression every 3s
                clearInterval(loop_id);
                
                window.location = window.location.href;
            }
        });
}

// start a loop each 3 seconds to ask the progression
OnLoadManager.addLoadFunction(() => {
    let title = document.getElementById("title");
    if (title.innerText !== "Process finish") {
        loop_id = setInterval(updateAnnotationProcess, 3000);   
    }
});
"""

# -----------------------------------------------------------------------


class ViewExec(BaseViewNode):

    def __init__(self, parent_id: str):
        super(ViewExec, self).__init__(parent_id, VIEW_MSG.replace(' ', '_'))
        self._msg = VIEW_MSG
        self._script = JS_SCRIPT

        self.__ann_process = None

        self.__output = None
        self.__workspace = None
        self.__selected_files = list()

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def is_annot_running(self) -> bool:
        if self.__ann_process is None:
            return False

        return self.__ann_process.is_alive()

    # -----------------------------------------------------------------------
    # SETTERS
    # -----------------------------------------------------------------------

    def set_files(self, workspace: sppasWorkspace, files: list):
        if isinstance(workspace, str):
            if os.path.isfile(workspace) is False:
                workspace = os.path.join("workspaces", workspace + ".wjson")

            wp = sppasWkpRW(workspace)
            self.__workspace = wp.read()
        else:
            self.__workspace = workspace

        self.__selected_files = files

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM BaseView
    # -----------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        code = 205

        if event_name == "update_process":
            code = 200

        elif event_name == "restart_process_event":
            code = 200

        elif event_name == "exit_program_event":
            code = 410

        return code

    # -----------------------------------------------------------------------

    def update(self) -> None:
        self.clear_children()
        if self.__ann_process is None:
            raise sppasError("Annotation process doesn't started")

        if self.__ann_process.is_alive():
            h1 = HTMLNode(self.identifier, None, "h1", value="Cued speech annotation running", attributes={'id': "title"})
            self.append_child(h1)

            spinner = HTMLNode(self.identifier, "spinner", "div", attributes={"id": "spinner", "class": "spinner"})
            self.append_child(spinner)

        else:
            h2 = HTMLNode(self.identifier, None, "h1", value="Process finish", attributes={'id': "title"})
            self.append_child(h2)

            p = HTMLNode(self.identifier, None, "p", value=f"Annotated video created in '{self.__output}'")
            self.append_child(p)

            btn_section = HTMLNode(self.identifier, "btn-container", "div", attributes={'class': "flex-panel"})
            self.append_child(btn_section)

            prev_button = HTMLNode(btn_section.identifier, None, "button", value="Back", attributes={
                'name': "prev_view",
                'onclick': "notify_event(this)"
            })
            btn_section.append_child(prev_button)

            restart_button = HTMLNode(btn_section.identifier, None, "button", value="Restart", attributes={
                'name': "restart_process",
                'onclick': "notify_event(this)"
            })
            btn_section.append_child(restart_button)

            quit_button = HTMLNode(btn_section.identifier, None, "button", value="Quit", attributes={
                'name': "exit_program",
                'onclick': "notify_event(this)"
            })
            btn_section.append_child(quit_button)

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def start_process(self, ann_options: list, lang: str = "fra") -> None:
        if self.__workspace is None or len(self.__selected_files) == 0:
            raise sppasError(f"Can't start processing annotation because workspace and files doesn't given")

        video_file, coords_file = self.__find_specific_files(self.__selected_files)

        params = sppasParam(["cuedspeech.json"])
        step_index = params.activate_annotation("cuedspeech")
        params.set_lang(lang, step=step_index)

        output = os.path.splitext(video_file)[0]
        for opt in ann_options:
            params.set_option_value(step_index, opt.get_key(), opt.get_value())
            if opt.get_key() == "outputpattern":
                output += opt.get_value()

        # variable for interface when the process will be finish
        self.__output = f"{output}.mp4"

        # launch with tagger because xra coords file already exists
        if coords_file is not None and os.path.exists(coords_file):
            if video_file is None or os.path.exists(video_file) is False:
                raise sppasError(f"Video file not found {video_file}")

            parser = sppasTrsRW(coords_file)
            transcription = parser.read()

            annotation = CuedSpeechVideoTagger()
            annotation.set_cue_rules(CuedSpeechKeys(params.get_langresource(step_index)[0]))
            annotation.load(video_file)

            for current_option in ann_options:
                if current_option.get_key() in ("handsset", "handsfilter", "infotext", "vowelspos"):
                    annotation.set_option(current_option.get_key(), current_option.get_value())

            self.__ann_process = Thread(target=annotation.tag_with_keys, daemon=True, args=(transcription, output))

        # launch with the annotation if the coords file doesn't exist
        else:
            params.set_workspace(self.__workspace)
            params.set_output_extension(".xra", "ANNOT")

            process = sppasAnnotationsManager()
            self.__ann_process = Thread(target=process.annotate, daemon=True, args=(params,))

        # we run the annotation in a different thread
        self.__ann_process.start()
        logging.info("Starting process daemon thread")

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __find_specific_files(self, files: list, coords_pattern: str = "-coords") -> tuple:
        video = None
        coords = None

        for current in files:
            _, file_extension = os.path.splitext(current)

            if file_extension in video_extensions:
                video = current
            elif file_extension == ".xra" and coords_pattern in current:
                coords = current

        return video, coords
