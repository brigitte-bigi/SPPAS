# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.components.swapp_response.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SPPAS Web-Based application ResponseRecipe.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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
from whakerpy.htmlmaker import HTMLNode
from whakerpy.httpd import BaseResponseRecipe

from .swapp_head import swappHeadNode

# ---------------------------------------------------------------------------


class swappBaseResponse(BaseResponseRecipe):
    """Create a Response system for dynamic pages.

    The page can or cannot have a static body->main content.

    """
    _name = ""

    def __init__(self,
                 name: str | None = None,
                 tree: HTMLNode | None = None,
                 title: str = "SPPAS"):
        """Create a HTTPD Response instance with a default response.

        :param name: (str) Filename of the body main content.

        """
        self._name = name
        if name is not None:
            self._page_name = os.path.basename(name)
        else:
            name = "undefined"
            self._page_name = ""

        # Inheritance with a given dynamic HTMLTree.
        super(swappBaseResponse, self).__init__(name=name, tree=tree, title=title)

    # ---------------------------------------------------------------------------
    # PUBLIC STATIC METHODS
    # ---------------------------------------------------------------------------

    @classmethod
    def page(cls):
        """Return the current HTML body->main filename or an empty string."""
        return cls._name

    # -----------------------------------------------------------------------

    def get_pagename(self) -> str:
        """Return the name of the HTML page as seen in the URL."""
        return self._page_name

    # -----------------------------------------------------------------------

    def set_pagename(self, page_name: str):
        """Set the name of this page as seen in the url.

        :param page_name: (str) Name of the HTML page.

        """
        self._page_name = page_name
        # Update current nav page
        self._htree.body_nav.set_nav_current(page_name)

    # -----------------------------------------------------------------------

    def bake(self, events: dict, headers: dict = None) -> str:
        """Override. Translate the ambient state before processing the events.

        The Whakerexa client attaches its own parameters (`wexa_*`) to every
        navigation URL, and WhakerPy turns the query string of a GET into
        events. These parameters are not application events: the color and
        contrast schemes are translated into the accessibility events every
        recipe processes, and any other `wexa_*` parameter -- purely a
        client-side matter -- is removed.

        :param events: (dict) The requested events to be processed
        :param headers: (dict) The headers of the http request received

        """
        if "wexa_color" in events:
            events["accessibility_color"] = events.pop("wexa_color")
        if "wexa_contrast" in events:
            events["accessibility_contrast"] = events.pop("wexa_contrast")
        for event_name in list(events.keys()):
            if event_name.startswith("wexa_") is True:
                events.pop(event_name)

        return super(swappBaseResponse, self).bake(events, headers)

    # -----------------------------------------------------------------------
    # Construct the tree
    # -----------------------------------------------------------------------

    def create(self):
        """To be overridden. Create the page tree.

        Create the head of the dynamic tree.

        """
        self._htree.head = swappHeadNode(self._htree.identifier, title=self._title)
        self._htree.body_main.set_attribute("id", "main-content")

    # -----------------------------------------------------------------------
    # Override WhakerPy private methods
    # -----------------------------------------------------------------------

    def _invalidate(self):
        """Override. Remove children nodes of the body->main."""
        self._htree.body_main.clear_children()
