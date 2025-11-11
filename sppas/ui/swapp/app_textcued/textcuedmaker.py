"""
:filename: sppas.ui.swapp.app_textcued.textcuedmaker.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Response for the web-based application "Text Cued" of SPPAS.

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
from sppas.ui.swapp import sppasImagesAccess
from sppas.ui.swapp.htmltags import SwappHeader
from sppas.ui.swapp.htmltags import SwappFooter
from sppas.ui import _

from .annotate_manager import AnnViewManager
from .annotate_manager import AnnViewBar

# -----------------------------------------------------------------------


MSG_APP_TITLE = _("Automatic CuedSpeech from Text")
MSG_TITLE = _("Text Cueing")
MSG_DESCR = _("Allows to generate automatically the sequence of keys to be cued from a written text")
MSG_H1 = _("Cueing from a written text")

# -----------------------------------------------------------------------


class TextCuedResponseRecipe(WhakerKitResponse):
    """The textcueing.html HTTPD response baker.

    This application allows to generate automatically the sequence of keys to
    be cued from a written text in the UI. It performs the followings:

    1. Text Normalization
    2. Phonetization
    3. Basic Alignment
    4. Cued Speech (the 'what' question only)

    """

    def __init__(self, name="TextCuedMaker", tree=None, title=MSG_TITLE):
        super(TextCuedResponseRecipe, self).__init__(name, tree, title)

        # create the fieldsets manager and instantiate all fieldsets
        self.__views = AnnViewManager(self._htree.body_main.identifier)

    # -----------------------------------------------------------------------
    # STATIC METHODS
    # -----------------------------------------------------------------------

    @classmethod
    def page(cls) -> str:
        """Return a short description of the application."""
        return "textcueing.html"

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
        #self._htree.head.append_child(HTMLNode(self._htree.head.identifier, None, "script",
        #    value=ACSAnnotateResponse.JS_SCRIPT))

        self._htree.body_header = SwappHeader(self._htree.identifier, title=MSG_APP_TITLE)
        self._htree.body_footer = SwappFooter(self._htree.identifier)

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Process the given events coming from the POST of any form.

        :param events (dict): The events received by the server (key=event_name, value=event_value)
        :return: (bool) True if the whole page must be re-created

        """
        logging.debug(f" >>>>> Page Text Cued Annotation -- Process events: {events} <<<<<< ")
        success = self.__views.process_annotate_events(events)
        if success is True:
            self._status.code = 200
        else:
            self._status.code = 400
            # 400 Bad Request response status code indicates that the server
            # cannot or will not process the request due to something that is
            # perceived to be a client error.

        return True

    # -----------------------------------------------------------------------

    def _bake(self):
        """Create the dynamic page content in HTML.

        """
        sec = HTMLNode(self._htree.body_main.identifier, None, "section")
        self._htree.body_main.append_child(sec)

        node = HTMLNode(sec.identifier, None, "h1", value=MSG_H1)
        sec.append_child(node)

        # Create the HTML current view --
        # The view **must** be created before the wizard.
        view = self.__views.get_current_view()
        view.update()

        # Create the views bar and append -- before the view to display it at top
        self.__views_bar = AnnViewBar(self._htree.body_main.identifier, self.__views)
        self._htree.body_main.append_child(self.__views_bar)

        # Append view in the body_main
        self._htree.body_main.append_child(view)

        # Special for cued speech view
        if view.identifier == "cuedspeech":
            script = view.get_script(self._htree.head.identifier)
            self._htree.head.remove_child(script.identifier)
            self._htree.head.append_child(script)
