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
from sppas.ui.swapp.components.swapp_view import swappBaseView
from sppas.ui.swapp.wappcore.wappsg import wapp_settings

# ---------------------------------------------------------------------------


MSG_REFRESH = _("Refresh")
MSG_SAVE = _("Save")
MSG_CLEAR = _("Clear")
MSG_MESSAGES = _("Messages")
MSG_LOGS = _("Logs")

# ---------------------------------------------------------------------------

MSG_HEADER = f"SPPAS {sg.__release__} » " + _("Infos")

BODY_SCRIPT = f"""
        import {{ TraceManager }} from '/{wapp_settings.js}sppas.js';

        const traceManager = new TraceManager();
        traceManager.handleTraceManagerOnLoad();
"""

# ---------------------------------------------------------------------------


class TraceView(swappBaseView):
    """View class responsible for populating the *trace.html* page.

    This class represents the **View** component of the "Traces" page.
    It receives an existing :class:`HTMLTree` instance and fills it with
    the content of the shared trace store: the useful trace/info messages
    of all the SPPAS components. It replaces the former wx log window.

    The Save and Clear actions are sent with a native form POST. The only
    JavaScript of the page is the heartbeat of the TraceManager: the
    server knows the single tab displaying the traces is open.

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
        # No Dashboard button here: the page opens in its own tab, the app
        # which opened it stays in the other one.
        _s = TagNode(self._htree.body_nav.identifier, None, "section")
        self.append_pin_button(_s)
        self.append_accessibility_buttons(_s)
        self._htree.body_nav.append_child(_s)

    # -----------------------------------------------------------------------

    def populate_body_script(self):
        """Override. Populate the script body section.

        """
        self._htree.body_script.add_attribute("type", "module")
        self._htree.body_script.set_value(BODY_SCRIPT)

    # -----------------------------------------------------------------------
    # Update the tree -- for baking the page
    # -----------------------------------------------------------------------

    def populate_tree_content(self, header_text: str, api_text: str,
                              ui_text: str, status_text: str = ""):
        """Populate the tree content with the given trace.

        The records are displayed in two side-by-side panels: the messages
        of the API on the left, the logs of the interfaces on the right.

        :param header_text: (str) The header of the trace store.
        :param api_text: (str) The serialized records of the API origin.
        :param ui_text: (str) The serialized records of the UI origin.
        :param status_text: (str) The status of the last action, if any.

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

        # The status of the last action -- an inline message, never a dialog.
        if len(status_text) > 0:
            _status = HTMLNode(self._htree.body_main.identifier, None, "p",
                               value=html.escape(status_text))
            _status.set_attribute("class", "status-message")
            _status.set_attribute("role", "status")
            self._htree.body_main.append_child(_status)

        # The header of the store, once, above the two panels.
        # The values are escaped: they are plain text and could contain
        # characters interpreted as HTML.
        _header = HTMLNode(self._htree.body_main.identifier, None, "pre",
                           value=html.escape(header_text))
        _header.set_attribute("id", "trace_header")
        self._htree.body_main.append_child(_header)

        # The records, in two side-by-side panels: one for each origin.
        _panels = TagNode(self._htree.body_main.identifier, None, "section")
        _panels.set_attribute("id", "trace_panels")
        _panels.set_attribute("class", "flex-panel")
        self._htree.body_main.append_child(_panels)

        _api = TagNode(_panels.identifier, None, "section")
        _api.set_attribute("class", "width_50")
        _panels.append_child(_api)
        _title = HTMLNode(_api.identifier, None, "h2", value=MSG_MESSAGES)
        _api.append_child(_title)
        _content = HTMLNode(_api.identifier, None, "pre",
                            value=html.escape(api_text))
        _content.set_attribute("id", "trace_api_content")
        _api.append_child(_content)

        _ui = TagNode(_panels.identifier, None, "section")
        _ui.set_attribute("class", "width_50")
        _panels.append_child(_ui)
        _title = HTMLNode(_ui.identifier, None, "h2", value=MSG_LOGS)
        _ui.append_child(_title)
        _content = HTMLNode(_ui.identifier, None, "pre",
                            value=html.escape(ui_text))
        _content.set_attribute("id", "trace_ui_content")
        _ui.append_child(_content)
