# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_dashboard.dashboard_controller.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Manages the application logic.

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
import logging
import sys
import os

from sppas.core.config import sppasExecProcess
from sppas.core.config import cfg
from sppas.core.config import paths
from sppas.core.preinstall.installer import quote
from sppas.ui.swapp.wappsg import wapp_settings

# ---------------------------------------------------------------------------


class DashboardController:
    """Controller for the SPPAS Dashboard application.

    This class represents the *Controller* component in the MVC pattern.
    It coordinates interactions between the model (list of applications)
    and the view (HTML representation). It also maintains internal state,
    such as whether the user has accepted the licence agreement.

    """

    def __init__(self, model, view):
        """Initialize the controller with a model and a view.

        :param model: (DashboardModel) The model managing the applications.
        :param view: (DashboardView) The view managing the HTML structure.

        """
        self.__model = model
        self.__view = view

    # -----------------------------------------------------------------------

    def has_agreed(self) -> bool:
        """Return the licence agreement state.

        :return: (bool) True if the licence agreement is accepted, False otherwise.

        """
        return wapp_settings.license_agreement

    # -----------------------------------------------------------------------

    def append_app(self, app) -> None:
        """Append a single web application to the model.

        :param app: (WebApplicationInfo) The application descriptor to append.

        """
        self.__model.append(app)

    # -----------------------------------------------------------------------

    def append_apps(self, apps: list) -> None:
        """Append a list of web applications to the model.

        :param apps: (list) List of WebApplicationInfo objects to append.

        """
        self.__model.append_all(apps)

    # -----------------------------------------------------------------------

    def append_pages(self, providers: list) -> None:
        """Append the pages of a list of page providers to the model.

        :param providers: (list) List of page provider classes, of type WebSiteData.

        """
        self.__model.append_pages(providers)

    # -----------------------------------------------------------------------

    def handle_licence_agreement(self) -> bool:
        """Process the licence agreement acceptance.

        This method updates the internal agreement state and logs the event.
        :return: (bool) True if the page has to be refreshed.

        """
        wapp_settings.license_agreement = True
        logging.info("Licence agreement is satisfied.")
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def handle_start_sppas() -> str:
        """Launch the classic SPPAS wx interface.

        This method executes the main entry point of the wx application
        as a subprocess. It uses the same Python interpreter as the server.

        :return: (str) Error message if any.

        """
        program = paths.ui + os.sep + os.path.join("wxapp", "__main__.py")
        command = quote(sys.executable) + " " + quote(program)
        pyprocess = sppasExecProcess()
        try:
            # IMPORTANT: timeout=None means NO timeout.
            pyprocess.run(command, timeout=None)
            pyprocess.out()
        except Exception as e:
            logging.error(str(e))
            return str(e)

        return ""

    # -----------------------------------------------------------------------

    def populate_view(self) -> None:
        """Populate the dashboard view with data from the model.

        The method instructs the view to create the page content according
        to the model data and the current agreement state.

        """
        self.__view.populate_tree_content(wapp_settings.license_agreement)

        for app_name in self.__model.get_names(visible_only=True):
            app_info = self.__model.get_bakery_by_name(app_name)
            if app_info is None:
                continue
            try:
                bakery = app_info.bakery()
                enabled = True
                if hasattr(bakery, 'get_fids') is True:
                    fids = bakery.get_fids() or []
                    # All requested features must be enabled
                    enabled = all(cfg.feature_installed(item) for item in fids)
                self.__view.append_app_card(
                    bakery.name(),
                    bakery.icon(),
                    bakery.description(),
                    bakery.get_default_page(),
                    enabled
                )
            except Exception as e:
                logging.error(f"Failed to create app card for {app_name}: {str(e)}")

            # list of devel apps section:
            # h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_APPS_DEVEL)
            # self._htree.body_main.append_child(h2)
            # ln = AppsNode(self._htree.body_main.identifier)
            # self._htree.body_main.append_child(ln)

        for recipe in self.__model.get_page_recipes():
            try:
                self.__view.append_page_link(recipe.name(), recipe.icon(), recipe.page())
            except Exception as e:
                logging.error(f"Failed to create page link for {recipe}: {str(e)}")
