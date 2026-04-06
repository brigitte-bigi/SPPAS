# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_dashboard.dashboard_model.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The set of application descriptors.

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

from ..wappinfo import WebApplicationInfo

# ---------------------------------------------------------------------------


class DashboardModel:
    """Manage the list of web applications displayed in the Dashboard.

    This class represents the *Model* component of the MVC architecture.
    It maintains a collection of :class:`WebApplicationInfo` instances and
    provides controlled access to them through explicit methods.

    :example:
        >>> model = DashboardModel()
        >>> model.append(WebApplicationInfo('Setup', SetupBakery, True))
        True

    """

    def __init__(self):
        """Initialize the model with an empty list of web applications."""
        self.__bakeries = list()

    # -----------------------------------------------------------------------

    def get_bakery_by_name(self, name: str) -> WebApplicationInfo | None:
        """Return the application matching the given name."""
        for app in self.__bakeries:
            if app.name == name:
                return app
        return None

    # -----------------------------------------------------------------------

    def get_names(self, visible_only: bool = False) -> list[str]:
        """Return the list of application names.

        :param visible_only: (bool) If True, return only visible applications.
        :return: (list) List of application names.

        """
        if visible_only is True:
            return [app.name for app in self.__bakeries if app.show is True]
        return [app.name for app in self.__bakeries]

    # -----------------------------------------------------------------------

    def append(self, application: WebApplicationInfo) -> bool:
        """Add a web application to the model.

        The method ensures the given application is valid, visible,
        and not already registered before adding it.

        :param application: (WebApplicationInfo) Application descriptor.
        :return: (bool) True if the application was successfully added,
                 False otherwise.

        """
        # All the reasons not to add the app:
        # bad instance, invisible app, already defined
        if isinstance(application, WebApplicationInfo) is False:
            return False
        if application.show is False:
            return False
        for web_app in self.__bakeries:
            if web_app.name == application.name:
                return False

        self.__bakeries.append(application)
        return True

    # -----------------------------------------------------------------------

    def append_all(self, applications: list) -> None:
        """Append a list of applications to the model.

        :param applications: (list) List of WebApplicationInfo objects.

        """
        for web_app in applications:
            success = self.append(web_app)
            if success is False:
                logging.error("The application {app} is not added to the "
                              "Dashboard".format(app=str(web_app)))
