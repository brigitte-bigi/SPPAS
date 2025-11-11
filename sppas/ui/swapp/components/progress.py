# -*- coding: UTF-8 -*-
"""
:filename: spas.ui.swapp.components.card.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Class to create a custom progress bar.

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
from whakerpy.htmlmaker import HTMLNode

from sppas.core.coreutils import sppasBaseProgress

# ---------------------------------------------------------------------------

JS_SCRIPT = """
let interval = null;

OnLoadManager.addLoadFunction(() => {
    // the time (in milliseconds) for each call to the function
    const loop_time = 1500;

    interval = setInterval(async () => {
        const request_manager = new RequestManager();
        const json_data = await request_manager.send_post_request({update_js_install: true});
        
        if (request_manager.status === 200) {
            clearInterval(interval);
    
            // we finish to install, check if we have to refresh to remove the progressbar and display install resume
            if (document.getElementById("percent") != null) {
                window.location.href = request_manager.request_url;
            }
        }

        update_bar(json_data["percent"], json_data["text"], json_data["header"]);
    }, loop_time);
});

"""

# ---------------------------------------------------------------------------


class ProgressBar(sppasBaseProgress):

    REQUIRED = ["progress.js"]


    def __init__(self, parent_identifier):
        super(ProgressBar, self).__init__()
        self.__node = HTMLNode(parent_identifier, "progress_install", "section")

        p = HTMLNode(self.__node.identifier, "percent", "progress",
                     attributes={"id": "percent", "max": "100", "value": "0"})

        self.__node.append_child(p)

    # ------------------------------------------------------------------
    # GETTERS
    # ------------------------------------------------------------------

    def get_percent(self) -> float:
        """Getter of the current progress bar percent.

        :return: (int) the percent

        """
        return self._percent

    # ------------------------------------------------------------------

    def get_text(self) -> str:
        """Getter of the text bar.

        :return: (str) the text

        """
        return self._text

    # ------------------------------------------------------------------

    def get_header(self) -> str:
        """

        :return: (str)

        """
        return self._header

    # ------------------------------------------------------------------

    def get_node(self) -> HTMLNode:
        """Return the HTMLNode of the progress.

        :return: (HTMLNode) the progress section.

        """
        return self.__node

    # ------------------------------------------------------------------

    def get_script(self) -> str:
        """Return the js script to add in the head page for the progress bar.

        :return: (str) the js script

        """
        return JS_SCRIPT

    # ------------------------------------------------------------------
    # SETTERS
    # ------------------------------------------------------------------

    def set_header(self, header):
        """Set a new progress header text.

        :param header: (str) new progress header text.

        """
        if len(header) > 0:
            self._header = str(header)
            self.__node_header()
        else:
            self._header = ""
        logging.info(self._header)

    # ------------------------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Update the progress.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text  (default: None)

        """
        if percent is not None:
            self._percent = percent
            self.__node_percent()

        if message is not None:
            logging.info('  => ' + message)
            self._text = str(message)
            self.__node_text()

    # ------------------------------------------------------------------

    def close(self):
        c = self.__node.get_child("header")
        if c is not None:
            self.__node.remove_child(c)
        c = self.__node.get_child("text")
        if c is not None:
            self.__node.remove_child(c)

    # ------------------------------------------------------------------
    # PRIVATE METHODS
    # ------------------------------------------------------------------

    def __node_header(self):
        c = self.__node.get_child("header")
        if c is not None:
            c.set_value(self._header)
        else:
            msg_node = HTMLNode(self.__node.identifier, "header", "h3", attributes={"id": "progress_header"},
                                value=self._header)
            self.__node.insert_child(0, msg_node)

    # ------------------------------------------------------------------

    def __node_text(self):
        c = self.__node.get_child("text")
        if c is not None:
            c.set_value(self._text)
        else:
            msg_node = HTMLNode(self.__node.identifier, "text", "p", attributes={"id": "progress_text"},
                                value=self._text)
            self.__node.append_child(msg_node)

    # ------------------------------------------------------------------

    def __node_percent(self):
        p = self.__node.get_child("percent")
        p.set_attribute("value", str(self._percent))
