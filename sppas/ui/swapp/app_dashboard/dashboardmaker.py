# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_dashboard.dashboardmaker.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: The web page of the "Dashboard" interface.

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

from whakerpy.htmlmaker import HTMLNode
from whakerkit.responses import WhakerKitResponse

from sppas.core.config import sg
from sppas.core.config import sppasExecProcess
from sppas.core.preinstall.installer import quote

from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess

from ..wappsg import wapp_settings
from ..wappinfo import WebApplicationInfo
from ..htmltags.hstatusnode import HTMLTreeError410
from ..htmltags import SwappHeader
from ..htmltags import SwappFooter

from .agree_node import AgreementNode
from .links_node import LinksNode
from .apps_node import AppsNode
from .script_node import SwappScript

# ---------------------------------------------------------------------------

BASE_HEADER_IMG = "splash-v5-transparent.png"

JS_SCRIPT = """
function start_sppas() {
    const request_manager = new RequestManager();
    request_manager.send_post_request({start_sppas: true});
}
"""

MSG_TITLE = _("SPPAS Dashboard")
MSG_LINKS = _("Learn More on the Web:")
MSG_APPS_STABLE = _("Explore Applications:")
MSG_APPS_DEVEL = _("Under-development applications:")
MSG_EXIT = _("Time to say Goodbye!")
MSG_APP_NOT_ADDED = _("The application {app} is not added to the Dashboard.")
MSG_DESCR_WX = _("Launches the classic graphical interface for speech annotation and analysis.")

# -----------------------------------------------------------------------


class DashboardAppResponseRecipe(WhakerKitResponse):
    """The sppas_dashboard.html HTTPD response bakery.

    Allows to launch a web application and the SPPAS wx app.
    Also includes useful links to get help, etc.

    """

    def __init__(self, name="Dashboard", tree=None, title=MSG_TITLE):
        """Create the ResponseRecipe for the Dashboard application.

        """
        # The list of applications in the dashboard
        self.__web_bakeries = list()

        # Whether the user agreed the license, or not
        self.__agreement = False

        super(DashboardAppResponseRecipe, self).__init__(name, tree, title)

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def add_app(self, application: WebApplicationInfo) -> bool:
        """Add an application into the dashboard.

        :param application: (WebApplicationInfo) The application to add.
        :return: (bool) True if the app was added, False otherwise.

        """
        # All the reasons not to add the app:
        # bad instance, invisible app, already defined, invalid res
        if isinstance(application, WebApplicationInfo) is False:
            return False
        if application.show is False:
            return False
        for web_app in self.__web_bakeries:
            if web_app.name == application.name:
                return False

        self.__web_bakeries.append(application)
        return True

    # -----------------------------------------------------------------------

    def add_apps(self, applications: list) -> None:
        """Add a list of applications.

        :param applications: (list) The list of applications of type WebApplicationInfo.

        """
        for web_app in applications:
            success = self.add_app(web_app)
            if success is False:
                logging.error(MSG_APP_NOT_ADDED.format(app=str(web_app)))

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM Whakerpy
    # -----------------------------------------------------------------------

    @classmethod
    def page(cls) -> str:
        """Override. Return the HTML page name."""
        return "sppas_dashboard.html"

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
        self._htree.head.link("stylesheet", wapp_settings.css + "/page_dashboard.css", link_type="text/css")
        # Added js scripts
        self._htree.head.script(wapp_settings.js + "/scriptutils.js", "application/javascript")
        script = HTMLNode(self._htree.head.identifier, None, "script",
                          value=JS_SCRIPT, attributes={'type': "application/javascript"})
        self._htree.head.append_child(script)

        # Add components
        self.enable_components(['Dialog'])

        # Header
        self._htree.body_header = SwappHeader(self._htree.identifier, title=MSG_TITLE)

        # Footer
        self._htree.body_footer = SwappFooter(self._htree.identifier)
        # Add the banner image at bottom of the page
        splash = HTMLNode(self._htree.body_footer.identifier, None, "img", attributes={
            'id': "banner-img",
            'class': "width_full fixed-bottom",
            'src': f"{wapp_settings.images}/{BASE_HEADER_IMG}",
            'alt': ""
        })
        self._htree.body_footer.append_child(splash)

        # Script
        self._htree.body_script = SwappScript(self._htree.identifier)

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        """Override.

        """
        logging.debug(f" >>>>> Page Application Dashboard -- Process events: {events} <<<<<< ")
        self._status.code = 200
        dirty = True

        if 'licence_agreement' in events.keys():
            self.__agreement = True
            logging.info("Licence agreement is satisfied.")

        if "start_sppas" in events.keys():
            command = quote(sys.executable)  # guessing this UI is launch with SPPAS py env
            command += " sppas/__main__.py"
            pyprocess = sppasExecProcess()
            try:
                pyprocess.run(command)
                out = pyprocess.out()
            except Exception as e:
                logging.error(str(e))

        return dirty

    # -----------------------------------------------------------------------

    def _bake(self) -> None:
        self._htree.body_main.add_attribute("id", "main-content")
        if self._status.code == 410:
            self._htree = HTMLTreeError410()
        else:
            # agreement dialog
            if self.__agreement is False:
                wn = AgreementNode(self._htree.body_main.identifier)
                self._htree.body_main.append_child(wn)

            # list of stable apps section
            h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_APPS_STABLE)
            self._htree.body_main.append_child(h2)
            self.__append_apps_node()

            # list of devel apps section
            # h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_APPS_DEVEL)
            # self._htree.body_main.append_child(h2)
            # ln = AppsNode(self._htree.body_main.identifier)
            # self._htree.body_main.append_child(ln)

            # list of recommended links section
            h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_LINKS)
            self._htree.body_main.append_child(h2)
            ln = LinksNode(self._htree.body_main.identifier)
            self._htree.body_main.append_child(ln)

    # -----------------------------------------------------------------------

    def __append_apps_node(self):
        """Create and append the applications into the tree."""
        # Create the section node
        apps = AppsNode(self._htree.body_main.identifier)
        self._htree.body_main.append_child(apps)
        # Add SPPAS wx app
        icon = sppasImagesAccess.get_icon_filename("sppas-logo-v5")
        #apps.create_app_card(sg.__name__, wapp_settings.icons + "Refine/sppas-logo-v5.png", MSG_DESCR_WX, "start_sppas();")
        apps.create_app_card(sg.__name__, icon, MSG_DESCR_WX, "start_sppas();")
        # Add the other apps
        for web_app in self.__web_bakeries:
            enable = True
            # LAUNCHING THE SETUP from the Dashboard App IS NOT IMPLEMENTED YET
            if 'setup' in web_app.name.lower():
                enable = False
            try:
                _bakery = web_app.bakery()
                apps.create_app_card(_bakery.name(),
                                     _bakery.icon(),
                                     _bakery.description(),
                                     _bakery.get_default_page(),
                                     enable)
            except Exception as e:
                logging.error(f"Failed to create app card for {web_app.name}: {str(e)}")
        return apps
