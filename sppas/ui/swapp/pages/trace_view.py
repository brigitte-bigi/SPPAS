"""
:filename: sppas.ui.swapp.pages.trace_view.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: View of the "Traces" page.

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
import html

from whakerpy.htmlmaker import HTMLTree
from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import TagNode

from sppas.core.config import sg
from sppas.ui import _
from sppas.ui.swapp.apps.swapp_view import swappBaseView

# ---------------------------------------------------------------------------


MSG_REFRESH = _("Refresh")
MSG_SAVE = _("Save")
MSG_CLEAR = _("Clear")

# ---------------------------------------------------------------------------

MSG_HEADER = f"SPPAS {sg.__release__} » " + _("Traces")

BODY_SCRIPT = """
        window.Wexa.links.handleLinksWithParameters(['link-dashboard_button']);
"""

# ---------------------------------------------------------------------------


class TraceView(swappBaseView):
    """View class responsible for populating the *trace.html* page.

    This class represents the **View** component of the "Traces" page.
    It receives an existing :class:`HTMLTree` instance and fills it with
    the content of the shared trace store: the useful trace/info messages
    of all the SPPAS components. It replaces the former wx log window.

    The Save and Clear actions are sent with a native form POST: the page
    needs no JavaScript to offer its service.

    """

    def __init__(self, tree: HTMLTree):
        """Initialize and populate the "Traces" view structure.

        :param tree: (HTMLTree) An existing HTML tree to populate with
                     the page-specific content.
        :raises: TypeError: tree is not an instance of HTMLTree

        """
        if isinstance(tree, HTMLTree) is False:
            raise TypeError("TraceView: tree must be an instance of HTMLTree. Got {}".format(type(tree)))
        super().__init__(tree, MSG_HEADER)

    # -----------------------------------------------------------------------
    # Populate the tree
    # -----------------------------------------------------------------------

    def _populate_head_css(self):
        """Override. Populate the `<head>` section of the HTML tree for CSS links.

        No page-specific stylesheet: the page relies on the shared one only.

        """
        pass

    # -----------------------------------------------------------------------

    def _populate_body_header(self):
        """Override. Populate the header area of the page.

        """
        self.append_responsive_menu_button(self._htree.body_header)

    # -----------------------------------------------------------------------

    def _populate_body_nav(self):
        """Override. Populate the nav area of the page.

        """
        _s = TagNode(self._htree.body_nav.identifier, None, "section")
        self.append_pin_button(_s)
        self.append_accessibility_buttons(_s)
        self._htree.body_nav.append_child(_s)

        self.append_dashboard_link_button(self._htree.body_nav)

    # -----------------------------------------------------------------------

    def populate_body_script(self):
        """Override. Populate the script body section.

        """
        self._htree.body_script.add_attribute("type", "module")
        self._htree.body_script.set_value(BODY_SCRIPT)

    # -----------------------------------------------------------------------
    # Update the tree -- for baking the page
    # -----------------------------------------------------------------------

    def populate_tree_content(self, trace_text: str):
        """Populate the tree content with the given trace.

        :param trace_text: (str) The serialized content of the trace store.

        """
        # The actions, sent to the server with a native form POST
        _form = TagNode(self._htree.body_main.identifier, None, "form")
        _form.set_attribute("id", "trace_actions")
        _form.set_attribute("method", "post")
        _form.set_attribute("action", "trace.html")
        self._htree.body_main.append_child(_form)

        # Refresh sends no event: the page is simply baked again.
        _refresh = HTMLNode(_form.identifier, None, "button", value=MSG_REFRESH)
        _refresh.set_attribute("type", "submit")
        _form.append_child(_refresh)

        _save = HTMLNode(_form.identifier, None, "button", value=MSG_SAVE)
        _save.set_attribute("type", "submit")
        _save.set_attribute("name", "event_bake")
        _save.set_attribute("value", "handle_trace_save")
        _form.append_child(_save)

        _clear = HTMLNode(_form.identifier, None, "button", value=MSG_CLEAR)
        _clear.set_attribute("type", "submit")
        _clear.set_attribute("name", "event_bake")
        _clear.set_attribute("value", "handle_trace_clear")
        _form.append_child(_clear)

        # The trace content. The messages are escaped: they are plain text
        # and could contain characters interpreted as HTML.
        _content = HTMLNode(self._htree.body_main.identifier, None, "pre",
                            value=html.escape(trace_text))
        _content.set_attribute("id", "trace_content")
        self._htree.body_main.append_child(_content)
