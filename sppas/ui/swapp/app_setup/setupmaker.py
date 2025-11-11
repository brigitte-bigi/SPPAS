"""
:filename: sppas.ui.swapp.app_setup.setupmaker.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The web-based application "Setup" of SPPAS.

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

import sys
import logging
import traceback
from threading import Thread

from whakerpy.htmlmaker import HTMLNode
from whakerkit.responses import WhakerKitResponse

from sppas.core.config import lgs
from sppas.core.coreutils import sppasLogFile
from sppas.core.preinstall import sppasInstallerDeps
from sppas.ui import _

from ..wappsg import wapp_settings
from ..wexc import sppasHTMLIncompleteFieldset
from ..htmltags.hstatusnode import HTMLTreeError410
from ..htmltags import SwappHeader
from ..htmltags import SwappFooter

from .fieldsets import SetupFieldsets
from .headfootnodes import SetupHeaderNode
from .headfootnodes import SetupActionsNode

# -----------------------------------------------------------------------


MSG_TITLE = _("SPPAS Setup")

# -----------------------------------------------------------------------


class SetupResponseRecipe(WhakerKitResponse):
    """The setup.html HTTPD response bakery.

    This application setup allows to install several external programs
    SPPAS is requiring in order to enable some of its features.

    For a good UX when installing:
        1. Queue up the long-running requested installation task
        2. Respond immediately so user can get back to his/her busy life
        3. Handle the long-running task out of process
        4. Allow the user to check the status of the long-running task
        5. Notify the user when the task status is changed or is completed

    """

    def __init__(self, name="Setup", tree=None, title=MSG_TITLE):
        # Fix logging
        log_report = sppasLogFile(pattern="install_ui")
        lgs.file_handler(log_report.get_filename(), with_stream=True)

        # Create the SPPAS installer system for dependencies
        try:
            self.__installer = sppasInstallerDeps()
        except Exception as e:
            logging.error("No installation will be performed. The installer "
                          "wasn't created due to the following error: {}"
                          "".format(str(e)))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            self.__installer = None
        self.__th = Thread(target=self.__install_features)
        self.__errors = ""

        # The wizard pages are fieldset tags
        self.__fieldsets = SetupFieldsets(self.__installer)
        self.__current = self.__fieldsets[0]

        # OK, now it's possible to create the page content
        super(SetupResponseRecipe, self).__init__(name, tree, title)

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM Whakerpy
    # -----------------------------------------------------------------------

    @classmethod
    def page(cls) -> str:
        """Override. Return the HTML page name."""
        return "setup.html"

    # -----------------------------------------------------------------------

    def create(self) -> None:
        """Override. Create the fixed page content in HTML.

        The fixed content corresponds to the parts that can't be invalidated:
        head, body_header, body_footer.

        """
        super().create()
        self._htree.head.link(rel="logo icon", href=wapp_settings.icons + "sppas.ico")

        # The default links
        self._htree.head.link("stylesheet", wapp_settings.css + "/main_swapp.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "/page_setup.css", link_type="text/css")
        # Added js scripts
        self._htree.head.script(wapp_settings.js + "/scriptutils.js", "application/javascript")

        # Add components
        self.enable_components(['ProgressBar'])

        # Header
        self._htree.body_header = SwappHeader(self._htree.identifier, title=MSG_TITLE)

        # Footer
        self._htree.body_footer = SwappFooter(self._htree.identifier)

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Process the given events coming from the POST of any form.

        :param events (dict): key=event_name, value=event_value
        :return: (bool) True if the whole page must be re-created.

        """
        self._status.code = 200

        # Priority is given to "install" events.
        for event in events:
            if "install" in event:
                return self.__process_install_event(event)

        # Other possible events -- only if no "install" event in the list.
        refresh = True
        for event_name in events:
            event_value = events[event_name]

            # --- Action events to browse fields ---

            if event_name in ("cancel_btn_action", "exit_btn_action"):
                self._status.code = 410

            elif event_name == "prev_btn_action":
                # does the client re-ask the same page and is sending the data
                # of the previously posted request???
                if str(self.__fieldsets.get_index(self.__current)) == event_value:
                    self.__current = self.__fieldsets.prev_field(self.__current)
                else:
                    logging.debug("... hum, the client re-asked the same page twice!")

            elif event_name == "next_btn_action":
                # does the client re-ask the same page and is sending the data
                # of the previously posted request???
                if str(self.__fieldsets.get_index(self.__current)) == event_value:
                    try:
                        self.__current.validate()
                        self.__current = self.__fieldsets.next_field(self.__current)
                    except sppasHTMLIncompleteFieldset as e:
                        # validate failed.
                        # self.__current does not change!
                        # [ we should open a modal panel with the error ...
                        # we re-send the same page instead ]
                        logging.error(e)
                else:
                    logging.debug("... hum, the client re-asked the same page twice!")

            # --- Feature events to choose what to install ---

            elif event_name.startswith("feature_") and event_name.endswith("_posted") is True:
                # it is asked to enable/disable a feature
                do_enable = not self.__installer.enable(event_value)
                self.__installer.enable(event_value, do_enable)
                logging.debug(" - feature {} enable is: {}".format(event_value, do_enable))

                self._status.code, checkbox_child = self.__current.process_event(event_name, event_value)
                self._data = checkbox_child  # set data to send to the client
                refresh = False

            elif event_name.endswith("_posted") is True:
                self._status.code = self.__current.process_event(event_name, event_value)

            else:
                logging.error("Unknown event name {:s}".format(event_name))
                self._status.code = 205
                refresh = False

        return refresh

    # -----------------------------------------------------------------------

    def __process_install_event(self, event):
        """Process an installation event: start, update or complete.

        """
        # If the installation button was clicked
        if event == "install_btn_action":
            if self._status.code == 202:
                return False
            else:
                self.__process_install()
                self._status.code = 202
                # 202 Accepted
                # The request has been accepted for processing,
                # but the processing has not been completed.
                return True

        # JS of the page informed the process started and the
        # page will be updated regularly
        elif event == "update_js_install":
            # JS of the page informed the installation is completed
            # or JS of the page informed the installation is running but
            # it's not.
            if self.__th.is_alive() is False:
                self._status.code = 200
                if hasattr(self.__current, "completed") and callable(getattr(self.__current, "completed")):
                    self.__current.completed(self.__errors, self.__installer)
                return True

            # JS of the page informed the installation is running
            # and the progress has to be updated.
            else:
                self._status.code = 202
                # If JS sent this event, it means the process should be still
                # running. The page needs refresh to show the update.
                return True

        return False

    # -----------------------------------------------------------------------

    def _bake(self):
        """Create the dynamic page content in HTML."""
        # Define this page content: a form with a header, fieldsets and actions.
        self.comment("Body content")

        if self._status in (100, 200, 202):
            # Create a header. It displays the current page, and have actions.
            # not displayed if installing
            if self._status != 202:
                setup_header = SetupHeaderNode(self._htree.body_main.identifier, self.__fieldsets, self.__current)
                self._htree.body_main.append_child(setup_header)

            # attach the current fieldset node to the body main of the tree
            self.__current.set_parent(self._htree.body_main.identifier)
            self._htree.body_main.append_child(self.__current)

            # create an actions navbar
            # not displayed if installing
            if self._status.code != 202:
                action_nav = SetupActionsNode(self._htree.body_main.identifier, self.__fieldsets, self.__current, self.__installer is not None)
                self._htree.body_main.append_child(action_nav)

            if self._status == 202:
                # Fill-in the data for json send
                self._data = dict()
                p = self.__current.get_progress()
                self._data["percent"] = p.get_percent()
                self._data["text"] = p.get_text()
                self._data["header"] = p.get_header()

        elif self._status == 410:
            # The 410 is "Gone" response sent when the requested content has been
            # permanently deleted from server, with no forwarding address.
            self._htree = HTMLTreeError410()

            # The 444 is "No Response" but it's a non-official code. It is
            # used internally to instruct the server to return no information
            # to the client and close the connection immediately.

        else:
            # This should not happen.
            status = HTMLNode(self._htree.body_main.identifier, None, "h1",
                              value="HTTP response {:d}".format(self._status.code))
            self._htree.body_main.append_child(status)

    # -----------------------------------------------------------------------
    # Installation process is here and private!
    # -----------------------------------------------------------------------

    def __process_install(self):
        """Start the installation in a thread."""
        if self.__th.is_alive() is True:
            return
        logging.info("--- Selected features for installation ---")
        for ftype in ("deps", "lang", "annot", "spin"):
            ids = self.__installer.features_ids(ftype)
            enabled = [fid for fid in ids if self.__installer.enable(fid)]
            logging.info(f"{ftype}: {len(enabled)} is {enabled}")

        # The current page is the list of features.
        # Switch to the installation page.
        self.__current = self.__fieldsets[self.__fieldsets.get_index_from_name("install_field")]

        # Create a progress system
        progress = self.__current.install_progress(self._htree)
        self.__installer.set_progress(progress)
        # ... but the installer does not indicate a percentage
        # p = progress.get_node().get_child("percent")
        # p.add_attribute("class", "progress-infinite")

        # Start the installation process .
        # It is not allowed to be stopped, only killed with the app!
        self.__errors = ""
        self.__th = Thread(target=self.__install_features)
        self.__th.daemon = True  # If the main thread is killed, this thread will be killed as well.
        self.__th.start()

    # -----------------------------------------------------------------------

    def __install_features(self):
        """Install all the enabled features, of any type."""
        self.__errors = self.__installer.install()
