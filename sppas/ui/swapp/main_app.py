"""
:filename: sppas.ui.swapp.main_app.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The main class for any of the SPPAS Web-based Applications.

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

from whakerpy.httpd import HTTPDHandler
from whakerpy.httpd import BaseHTTPDServer
from whakerpy.httpd import HTTPDHandlerUtils

from sppas.core.config import cfg
from sppas.core.coreutils import sppasKeyError
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.ui.swapp.wappsg import wapp_settings

from .wapps import *

# ---------------------------------------------------------------------------


class sppasWebApp:
    """Create and run any of the SPPAS web-based applications.

    """

    # Set the default application when no app options are specified
    DEFAULT_APP = WEB_APPLICATIONS[0]

    # ---------------------------------------------------------------------------

    @staticmethod
    def get_web_app_by_name(name: str) -> WebApplicationInfo:
        """Retrieve a web application by its name.

        :param name: Name of the application to retrieve.
        :return: The matching WebApplicationInfo instance.
        :raises: KeyError: If no application with the given name exists.

        """
        for app in WEB_APPLICATIONS:
            if app.name == name:
                return app
        raise sppasKeyError("Web Applications list", name)

    # ---------------------------------------------------------------------------

    class wappServer(BaseHTTPDServer):
        """A custom HTTPD server for SPPAS wapp.

        """

        def create_pages(self, app_type: str = 'dashboard'):
            """Override. Add bakeries for dynamic HTML pages of this app.

            :param app_type: (str) One of the WEB_APPLICATIONS app name

            """
            # Instantiate the response of the default page for the requested application
            for web_app in WEB_APPLICATIONS:
                # This is the requested one.
                if app_type == web_app.name:
                    logging.debug(f"HTTPD server initialization for {web_app.name}...")
                    # Instantiate its response and add it to the server's pages dictionary
                    _bakery = web_app.bakery()
                    _page = _bakery.get_default_page()
                    self._pages[_page] = _bakery.bake_response(_page)
                    self._default = _page
                    break

            # If the requested page is the one of the Dashboard Application, then
            # add all other apps
            if app_type == sppasWebApp.DEFAULT_APP.name:
                # Adding all applications to the dashboard response allows their cards
                # to be displayed in the interface.
                apps = WEB_APPLICATIONS.copy()
                # Do not re-create the dashboard!
                apps.pop(0)
                # Get the instantiated dashboard response and add apps to it
                _response = self._pages[self._default]
                _response.add_apps(apps)
                # Adding applications to the server's pages allows them to be accessed
                # directly as known web apps. All apps must be created, not only the
                # ones the UI is showing.
                for web_app in apps:
                    try:
                        _bakery = web_app.bakery()
                    except sppasEnableFeatureError as e:
                        logging.info(f"Application {web_app.name} disabled: {e}.")
                        pass
                    else:
                        _page = _bakery.get_default_page()
                        self._pages[_page] = _bakery.bake_response(_page)

        # -----------------------------------------------------------------------
        # OVERRIDE
        # -----------------------------------------------------------------------

        def page_bakery(self, page_name: str, headers: dict, events: dict, has_to_return_data: bool = False) -> tuple:
            """Return the page content and response status.

            This method should be invoked after a POST request in order to
            take the events into account when baking the HTML page content.

            :param page_name: (str) Requested page name
            :param headers: (dict) The headers ot the http request
            :param events: (dict) key=event name, value=event value
            :param has_to_return_data: (bool) False by default - Boolean to know if the server return data or html page
            :return: tuple(bytes, HTTPDStatus)

            """
            # Something that is very uggly first!
            if page_name.startswith("textcueing_") is True and page_name.endswith(".html") is True:
                page_name = "textcueing.html"

            # An unknown response for yet
            if page_name not in self._pages:
                # Browse through the known bakeries to find which one is able
                # to bake the response.
                for web_app in WEB_APPLICATIONS:
                    try:
                        _bakery = web_app.bakery()
                        if _bakery.is_page(page_name) is True:
                            self._pages[page_name] = _bakery.bake_response(page_name)
                    except sppasEnableFeatureError as e:
                        logging.info(f"Application {web_app.name} disabled: {e}.")

            # Process received events and bake the given page.
            return HTTPDHandlerUtils.bakery(self._pages, page_name, headers, events, has_to_return_data)

    # -----------------------------------------------------------------------

    def __init__(self, arguments: dict | None = None):
        """HTTP Server initialization.

        Create the application for the GUI of SPPAS based on http.

        """
        self.__location = "localhost"
        self.__port = self.__port_value()
        self.__server = None
        server_address = (self.__location, self.__port)

        self.__server = sppasWebApp.wappServer(server_address, HTTPDHandler)

        if arguments is not None and len(arguments) > 0:
            _app = None
            # Check if any known application was explicitly requested.
            # The search follows the order defined in WEB_APPLICATIONS.
            _names = list()
            for web_app in WEB_APPLICATIONS:
                _names.append(web_app.name)
                # If the argument matches the application name, use it.
                if arguments.get(web_app.name, False) is True:
                    _app = web_app
                    break
            if _app is None:
                raise sppasKeyError(_names, arguments.keys())
        else:
            # Define the application to launch. Use the default one initially.
            _app = sppasWebApp.DEFAULT_APP

        # Launch the selected application.
        self.__server.create_pages(_app.name)

    # -----------------------------------------------------------------------

    def __port_value(self):
        """Return a port value for this instance."""
        pport = wapp_settings.hport + 1
        if pport > 99:
            pport = 80
        wapp_settings.hport = pport
        return pport + (pport*100)

    # -----------------------------------------------------------------------

    def client_url(self):
        """Return the client URL of this server.

        """
        return "http://{:s}:{:d}/".format(self.__location, self.__port)

    # -----------------------------------------------------------------------

    def run(self):
        """Run the application with a main loop.

        :return: (int) Exit status (0=normal)

        """
        try:
            # Start the main loop of the HTTP server
            self.__server.serve_forever()
            # Notice that the sppasHTTPDHandler can shut down the server --
            # allowed because it's a local application, not an internet service.
        except KeyboardInterrupt:
            # Stop the server
            self.__server.shutdown()

        # Save current configuration
        logging.debug("Save config files.")
        cfg.save()
        wapp_settings.save()

        # Return exit status 0 = normal.
        return 0
