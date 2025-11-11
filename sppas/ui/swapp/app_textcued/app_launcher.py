"""
:filename: sppas.ui.swapp.app_textcued.app_launcher.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Launcher for the web-based application "Text Cued" of SPPAS.

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
from whakerkit.responses import WhakerKitResponse

from sppas.ui.swapp.wappsg import wapp_settings
from sppas.ui.swapp.htmltags import SwappHeader
from sppas.ui.swapp.htmltags import SwappFooter
from sppas.ui import _

from .textcuedmaker import TextCuedResponseRecipe

# -----------------------------------------------------------------------


MSG_APP_TITLE = _("Automatic CuedSpeech from Text")
MSG_TITLE = _("Text Cueing")
MSG_H1 = _("Cueing from a written text")
MSG_LAUNCH = _("Launch")

# -----------------------------------------------------------------------


class TextCuedLauncherRecipe(WhakerKitResponse):
    """The textcue.html HTTPD response baker.

    This application allows to launch the page of the TextCue app.

    """

    def __init__(self, name="TextCueLauncher", tree=None, title=MSG_TITLE):
        super(TextCuedLauncherRecipe, self).__init__(name, tree, title)

    # -----------------------------------------------------------------------
    # STATIC METHODS
    # -----------------------------------------------------------------------

    @classmethod
    def page(cls) -> str:
        """Return a short description of the application."""
        return "textcue.html"

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def create(self) -> None:
        """Override. Create the fixed page content in HTML.

        The fixed content corresponds to the parts that can't be invalidated:
        head, body_header, body_footer.

        """
        super().create()
        self._htree.head.link(rel="logo icon", href=wapp_settings.icons + "ACS_text.png")

        # Add custom statics
        self._htree.head.link("stylesheet", wapp_settings.css + "/main_swapp.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "/page_textcued.css", link_type="text/css")

        self._htree.body_header = SwappHeader(self._htree.identifier, title=MSG_APP_TITLE)
        self._htree.body_footer = SwappFooter(self._htree.identifier)

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Process the given events coming from the POST of any form.

        :param events (dict): The events received by the server (key=event_name, value=event_value)
        :return: (bool) True if the whole page must be re-created

        """
        logging.debug(f" >>>>> Page Text Cued Annotation -- Process events: {events} <<<<<< ")
        self._status.code = 200
        return True

    # -----------------------------------------------------------------------

    def _bake(self):
        """Create the dynamic page content in HTML.

        """
        sec = HTMLNode(self._htree.body_main.identifier, None, "section")
        self._htree.body_main.append_child(sec)

        node = HTMLNode(sec.identifier, None, "h1", value=MSG_H1)
        sec.append_child(node)

        button = HTMLNode(sec.identifier, "textcued_button", "a", value=MSG_LAUNCH, attributes={
            'href': TextCuedResponseRecipe.page(),
            'role': "button",
            'target': "_blank",
            'class': "app-button",
            "id": "textcued_button"
        })
        sec.append_child(button)
