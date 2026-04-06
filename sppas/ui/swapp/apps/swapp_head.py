# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.apps.swapp_response.py
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

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLHeadNode

from sppas.ui.swapp.wappsg import wapp_settings

# ---------------------------------------------------------------------------


CSS_MIME_TYPE = "text/css"
JS_MIME_TYPE = "application/javascript"

# ---------------------------------------------------------------------------


class swappHeadNode(HTMLHeadNode):
    """Node for the head of each page.

    """

    def __init__(self, parent, title: str = "SPPAS"):
        """Create the head node.

        """
        super(swappHeadNode, self).__init__(parent)
        self.reset(title)

    # -----------------------------------------------------------------------

    def reset(self, title: str):
        """Reset the head to its default values.

        :param title: The title of the page to be added into the head.

        """
        # Delete the existing list of children
        self.clear_children()

        # The default meta tags
        self.meta({"charset": "utf-8"})
        self.meta({"http-equiv": "X-UA-Compatible", "content": "IE=edge"})
        self.meta({"name": "viewport",
                   "content": "width=device-width, initial-scale=1.0, user-scalable=yes"})

        # Add the given title
        title_node = HTMLNode(self.identifier, "title", "title", value=title)
        self.append_child(title_node)

        # Add the CSS style, from Whakerexa
        self.link(rel="stylesheet", href=wapp_settings.wexa_statics + "css/wexa.css", link_type=CSS_MIME_TYPE)
        self.link(rel="stylesheet", href=wapp_settings.wexa_statics + "css/layout.css", link_type=CSS_MIME_TYPE)
        self.link(rel="stylesheet", href=wapp_settings.wexa_statics + "css/button.css", link_type=CSS_MIME_TYPE)
        self.link(rel="stylesheet", href=wapp_settings.wexa_statics + "css/menu.css", link_type=CSS_MIME_TYPE)

        # Add the javascript, from Whakerexa
        self.script(src=wapp_settings.wexa_statics + "js/wexa.js", script_type="module")
