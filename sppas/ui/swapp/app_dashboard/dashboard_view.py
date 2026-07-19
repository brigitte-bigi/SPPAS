"""
:filename: sppas.ui.swapp.app_dashboard.dashboard_view.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Dashboard View of the MVC paradigm.

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
from whakerpy.htmlmaker import HTMLTree
from whakerpy.htmlmaker import TagNode
from whakerpy.htmlmaker import HTMLNode

from sppas.core.config import sg
from sppas.ui import _
from sppas.ui.swapp import sppasImagesAccess
from sppas.ui.swapp.components.swapp_view import swappBaseView
from sppas.ui.swapp.wappcore.wappsg import wapp_settings

from .nodes.agree_node import AgreementDialog
from .nodes.trace_dialog import TraceInfoDialog
from .nodes.links_node import LinksNode
from .nodes.links_node import AboutsNode
from .nodes.apps_node import AppsNode

# ---------------------------------------------------------------------------


MSG_LINKS = _("Learn more on the Web:")
MSG_ABOUT = _("Find out more:")
MSG_APPS_STABLE = _("Explore Applications:")
MSG_APPS_DEVEL = _("Under-development applications:")
MSG_APP_NOT_ADDED = _("The application {app} is not added to the Dashboard.")
MSG_DESCR_WX = _("Launches the graphical interface for speech annotation and analysis.")
MSG_WKP = _("Workspace: ")

# ---------------------------------------------------------------------------

MSG_HEADER = f"SPPAS {sg.__release__} » Dashboard"

BODY_SCRIPT = f"""
        import {{ DashboardManager }} from '/{wapp_settings.js}sppas.js';

        const dashboardManager = new DashboardManager();
        dashboardManager.handleDashboardManagerOnLoad();

        window.Wexa.links.handleLinksWithParameters(['web_button', 'docu_button', 'res_button', 'tuto_button', 'faq_button']);
        window.Wexa.links.handleLinksWithParameters(['link-trace_button']);
        window.Wexa.links.handleLinks(['src_button', 'award_button']);
"""

# ---------------------------------------------------------------------------


class DashboardView(swappBaseView):
    """View class responsible for populating the *index.html* page.

    This class represents the **View** component of the MVC pattern for the
    SPPAS Dashboard web application. It receives an existing :class:`HTMLTree`
    instance and fills it with all static and semi-static visual content.

    The :class:`DashboardView` does not manage user events nor business logic;
    it focuses solely on defining the HTML structure and resources required
    for rendering the Dashboard interface.

    The generated content includes:
        - Head section with meta, stylesheets, and JS imports.
        - Header (title, navigation buttons, accessibility controls).
        - Main content area .
        - Footer with copyright information.
        - Script element

    """

    def __init__(self, tree: HTMLTree):
        """Initialize and populate the Dashboard view structure.

        :param tree: (HTMLTree) An existing HTML tree to populate with
                     the setup-specific content.
        :raises: TypeError: tree is not an instance of HTMLTree

        """
        if isinstance(tree, HTMLTree) is False:
            raise TypeError("DashboardView: tree must be an instance of HTMLTree. Got {}".format(type(tree)))
        super().__init__(tree, MSG_HEADER)

    # -----------------------------------------------------------------------
    # Getters/Setters
    # -----------------------------------------------------------------------

    def append_app_card(self, name: str, icon_name: str, text: str, link: str, enable: bool = True):
        """Append an application card to its section.

        :param name: (str) The short name of the application.
        :param icon_name: (str) Name of an image representing the application
        :param text: (str) Text description of the application
        :param link: (str) Link to the application
        :param enable: (bool) Enable or disable the card.

        """
        apps_node = self._htree.body_main.get_child(AppsNode.ID)
        apps_node.create_app_card(name, icon_name, text, link, enable)

    # -----------------------------------------------------------------------

    def append_page_link(self, name: str, icon_name: str, link: str):
        """Append a page link button to the about section.

        :param name: (str) The short name of the page.
        :param icon_name: (str) Name of an image representing the page
        :param link: (str) Link to the page

        """
        about_node = self._htree.body_main.get_child(AboutsNode.ID)
        ident = link.split(".")[0]
        about_node.page_button(ident, icon_name, name, link)

    # -----------------------------------------------------------------------
    # Populate the tree
    # -----------------------------------------------------------------------

    def _populate_head_css(self):
        """Override. Populate the `<head>` section of the HTML tree for CSS links.

        """
        self._htree.head.link("stylesheet", wapp_settings.wexa_statics + "css/dialog.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "app_dashboard.css", link_type="text/css")

    # -----------------------------------------------------------------------

    def _populate_body_header(self):
        """Override. Populate the header area of the Dashboard page.

        """
        self.append_responsive_menu_button(self._htree.body_header)

    # -----------------------------------------------------------------------

    def _populate_body_nav(self):
        """Override. Populate the nav area of the Dashboard page.

        """
        _s = TagNode(self._htree.body_nav.identifier, None, "section")
        self.append_pin_button(_s)
        self.append_accessibility_buttons(_s)
        self._htree.body_nav.append_child(_s)

        self.append_trace_link_button(self._htree.body_nav)
        self.append_exit_button(self._htree.body_nav)

    # -----------------------------------------------------------------------

    def _populate_body_footer(self, *args, **kwargs):
        """Override. Populaire the footer area of the Dashboard page.

        """
        self._htree.body_footer.append_sppas_splash()
        self._htree.body_footer.append_scroll_top()

    # -----------------------------------------------------------------------

    def populate_body_script(self):
        """Override. Populate the script body section.

        """
        self._htree.body_script.add_attribute("type", "module")
        self._htree.body_script.set_value(BODY_SCRIPT)

    # -----------------------------------------------------------------------
    # Update the tree -- for baking the page
    # -----------------------------------------------------------------------

    def populate_tree_content(self, agreement: bool = False, wx_enabled: bool = True,
                              trace_alive: bool = True,
                              wkp_name: str = "", wkp_path: str = ""):
        """Populate the tree content.

        :param agreement: (bool) The license agreement is already accepted.
        :param wx_enabled: (bool) Enable the card launching the wx interface.
        :param trace_alive: (bool) The Journal tab gave a recent sign of life.
        :param wkp_name: (str) Name of the current workspace.
        :param wkp_path: (str) Path of its file, or an empty string.

        """
        # Create the new ones
        if agreement is False:
            wn = AgreementDialog(self._htree.body_main.identifier)
            self._htree.body_main.append_child(wn)
        elif trace_alive is False:
            # The Journal tab is not open: invite the user to open it. The
            # license dialog passes first, one dialog at a time.
            wn = TraceInfoDialog(self._htree.body_main.identifier)
            self._htree.body_main.append_child(wn)

        # Add dialogs for messages
        self.append_alert_dialogs(self._htree.body_main)

        # The current workspace: a label, the name, and the path on hover.
        # It will become the button opening the "Files" app.
        if len(wkp_name) > 0:
            _wkp = TagNode(self._htree.body_main.identifier, None, "p")
            _wkp.set_attribute("id", "workspace_info")
            self._htree.body_main.append_child(_wkp)
            _s = HTMLNode(_wkp.identifier, None, "strong", value=MSG_WKP)
            _wkp.append_child(_s)
            _s = HTMLNode(_wkp.identifier, None, "span", value=wkp_name)
            _s.set_attribute("id", "workspace_name")
            if len(wkp_path) > 0:
                _s.set_attribute("title", wkp_path)
            _wkp.append_child(_s)

        # The applications section
        h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_APPS_STABLE)
        self._htree.body_main.append_child(h2)
        apps = AppsNode(self._htree.body_main.identifier)
        self._htree.body_main.append_child(apps)

        # Add SPPAS wx app, at first then other APPS
        # ------------------------------------------
        icon = sppasImagesAccess.get_image_filename("sppas_logo_v3")
        apps.create_app_card(
            sg.__name__,
            icon,
            text=MSG_DESCR_WX,
            enable=wx_enabled
        )

        # Other sections
        # --------------

        # Other links and infos
        h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_ABOUT)
        self._htree.body_main.append_child(h2)
        ln = AboutsNode(self._htree.body_main.identifier)
        self._htree.body_main.append_child(ln)

        # List of recommended links section
        h2 = HTMLNode(self._htree.body_main.identifier, None, "h2", value=MSG_LINKS)
        self._htree.body_main.append_child(h2)
        ln = LinksNode(self._htree.body_main.identifier)
        self._htree.body_main.append_child(ln)

