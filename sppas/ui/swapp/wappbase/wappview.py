"""
:filename: sppas.ui.swapp.wappbase.wappview.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SPPAS Web-Based application Base View of the MVC paradigm.

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
from whakerpy.htmlmaker import HTMLNode

from sppas.core.config import sg
from sppas.core.config import cfg
from sppas.core.config import get_language

from sppas.ui import _

from ..wappcore.wapputils import sppasImagesAccess
from ..nodes.buttons.hbutton import sppasHTMLButton
from ..wappcore.wappsg import wapp_settings
from ..nodes.layout.hheader import SwappHeader
from ..nodes.layout.hfooter import SwappFooter

# ---------------------------------------------------------------------------


MSG_WEB = _("SPPAS website")
MSG_CONTRAST = _("Contrast")
MSG_COLOR = _("Color")
MSG_THEME = _("Theme")
MSG_PIN = _("Pin menu")
MSG_EXIT = _("Exit")
MSG_DASHBOARD = _("Dashboard")
MSG_HELP = _("Help")
MSG_JOURNAL = _("Journal")
MSG_FEEDBACK = _("Feedback")
MSG_ERROR = _("Error")
MSG_INFORMATION = _("Information")

# Must be appended to the HTMLTree before sppas.js
JS_INIT = (
    f"window.WEXA_JS_PATH = '/{wapp_settings.wexa_statics}js';"
    f"window.WEXA_LOG_LEVEL = {cfg.log_level};"
)

JS_WEXA_ONLOAD = """
        window.Wexa.onload.addLoadFunction(() => {
            const {MenuManager} = window.Wexa;
            window.menu = new MenuManager();
            window.menu.initSideMenu();
            window.menu.initMobileToggle();
        });
"""

# The ThemeManager is an extra: it is imported by the pages needing it. The
# theme of SPPAS is registered like any other, and declared as the default.
JS_WEXA_THEMES = (
    f"const ThemeManager = (await import(window.WEXA_JS_PATH + '/extras/theme_manager.js')).ThemeManager;"
    f"window.themes = new ThemeManager();"
    f"window.themes.register('swapp', '{wapp_settings.css}main_swapp_theme.css');"
    f"window.themes.register('wexa_theme', '{wapp_settings.wexa_statics}css/themes/wexa_theme.css');"
    f"window.themes.register('aurora', '{wapp_settings.wexa_statics}css/themes/wexa_theme_aurora.css');"
    f"window.themes.register('highcontrast', '{wapp_settings.wexa_statics}css/themes/wexa_theme_highcontrast.css');"
    f"window.themes.setDefault('swapp');"
)

# ---------------------------------------------------------------------------


class swappBaseView:
    """Base View class for populating any SPPAS web application page.

    This class implements the **View** component in the MVC architecture used
    across SPPAS web applications. It receives an existing :class:`HTMLTree`
    instance and fills it with all static and semi-static HTML elements.

    The :class:`swappBaseView` focuses exclusively on building the structure and
    presentation of the interface; it does not handle user interactions or
    business logic.

    It typically defines:
        - The `<head>` section with meta tags, CSS, and JS imports.
        - The `<header>` area for branding or navigation controls.
        - The `<footer>` section for informational elements.
        - The `<script>` section for inline initialization.
    """

    def __init__(self, tree: HTMLTree, title: str, *args, **kwargs):
        """Initialize and populate the main HTML sections.

        :param tree: (HTMLTree) An existing HTML tree to populate.
        :raises: TypeError: If *tree* is not an instance of :class:`HTMLTree`.

        The constructor immediately fills all default sections of the page by
        invoking the `populate_*()` methods. Child classes can override the
        protected `_populate_*()` methods to extend or modify their content.

        """
        # The tree to populate
        if isinstance(tree, HTMLTree) is False:
            raise TypeError("swappBaseView expected a HTML tree instance. "
                            "Got {}".format(type(tree)))
        self._htree = tree
        self._htree.add_html_attribute("lang", get_language().split('_')[0])

        # Accessibility default values
        self._accessibility = {
            "color": wapp_settings.accessibility_color_scheme,  # str: (light,dark)
            "contrast": wapp_settings.accessibility_contrast    # bool
        }

        # Populate, to fill the given tree with content
        self.populate_head()
        self.populate_body_header(title)
        self.populate_body_nav()
        self.populate_body_footer()
        self.populate_body_script()

    # -----------------------------------------------------------------------
    # Public
    # -----------------------------------------------------------------------

    def set_accessibility(self,
                          color: str | None = None,
                          contrast: str | None = None) -> None:
        """Update the current accessibility parameters.

        This method sets the active color and/or contrast schemes used by the
        web interface. When a value is given, it replaces the previously stored
        one in the internal accessibility dictionary.

        :param color: (str | None) Name of the color scheme to apply
                      (e.g. 'dark', 'light'). If None, no change is made.
        :param contrast: (str | None) Name or flag of the contrast mode to apply.
                         An empty value disables contrast mode.

        """
        if color is not None:
            self._accessibility['color'] = color
        if contrast is not None:
            self._accessibility['contrast'] = len(contrast.strip()) > 0

    # -----------------------------------------------------------------------

    def populate_head(self):
        """Populate the `<head>` section of the HTML document.

        Adds favicon, CSS stylesheets, and JavaScript imports required for
        rendering the base web interface, including both Whakerexa and
        application-specific resources.

        """
        # The favicon: the same for all the pages and apps, on purpose. The
        # SPPAS tab of the browser keeps one constant identity.
        self._htree.head.link(rel="logo icon", href=wapp_settings.icons + "sppas5.ico")

        # CSS SWAPP links. The theme carries the id the ThemeManager swaps the
        # href of: without it, a second link is created and themes accumulate.
        self._htree.head.link("stylesheet", wapp_settings.css + "main_swapp.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "main_swapp_identity.css", link_type="text/css")
        theme_css = HTMLNode(self._htree.head.identifier, None, "link")
        theme_css.add_attribute("id", "wexa-theme")
        theme_css.add_attribute("rel", "stylesheet")
        theme_css.add_attribute("href", wapp_settings.css + "main_swapp_theme.css")
        theme_css.add_attribute("type", "text/css")
        self._htree.head.append_child(theme_css)
        # Application CSS
        self._populate_head_css()

        # JS SWAPP module
        script = HTMLNode(self._htree.head.identifier, None, "script", value=JS_INIT)
        self._htree.head.append_child(script)
        script = HTMLNode(self._htree.head.identifier, None, "script")
        script.add_attribute("src", wapp_settings.js + "sppas.js")
        script.add_attribute("type", "module")
        self._htree.head.append_child(script)

        # JS local script for the Menu -- same for all apps sharing this head.
        script = HTMLNode(self._htree.head.identifier, None, "script",
                          value=JS_WEXA_ONLOAD, attributes={'type': "module"})
        self._htree.head.append_child(script)

        # JS local script for the CSS themes -- same for all apps.
        script = HTMLNode(self._htree.head.identifier, None, "script",
                          value=JS_WEXA_THEMES, attributes={'type': "module"})
        self._htree.head.append_child(script)

        # Application JS
        self._populate_head_js()

    # -----------------------------------------------------------------------

    def populate_body_header(self, title, *args, **kwargs):
        """Populate the `<header>` section of the page.

        Replaces the current header with a :class:`SwappHeader` instance and
        delegates additional customization to `_populate_body_header()`.

        """
        self._htree.body_header = SwappHeader(self._htree.identifier, title)
        self._populate_body_header(*args, **kwargs)

    # -----------------------------------------------------------------------

    def _home_target(self) -> str:
        """Return the window name the Dashboard button of the menu switches to.

        Empty by default: the button replaces the content of the current
        tab. Override in a page living in its own persistent tab, so that
        going to the Dashboard switches to that named tab instead of
        turning its own tab into it -- see the Journal page.

        """
        return ""

    # -----------------------------------------------------------------------

    def populate_body_nav(self, *args, **kwargs):
        """Populate the `<nav>` section with navigation and accessibility tools.

        Adds base menu styling, contrast/theme accessibility buttons, and calls
        `_populate_body_nav()` for app-specific navigation items.

        """
        self._htree.body_nav.add_attribute("id", "nav-content")
        self._htree.body_nav.add_attribute("name", "nav-content")
        self._htree.body_nav.add_attribute("class", "nav-wexa")
        self._htree.body_nav.add_attribute("class", "side")
        self._htree.body_nav.add_attribute("class", "collapsible")

        self._populate_body_nav(*args, **kwargs)

    # -----------------------------------------------------------------------

    def populate_body_footer(self, *args, **kwargs):
        """Populate the `<footer>` section of the page.

        Replaces the footer with a :class:`SwappFooter` instance and invokes
        `_populate_body_footer()` for further customization.

        """
        self._htree.body_footer = SwappFooter(self._htree.identifier)
        self._populate_body_footer(*args, **kwargs)

    # -----------------------------------------------------------------------

    def populate_body_script(self):
        """Populate the `<script>` section of the page.

        To be overridden by child views when inline initialization scripts are
        required.

        """
        pass

    # -----------------------------------------------------------------------

    def update_accessibility(self):
        """Remove the color and contrast classes from the body.

        The accessibility state is carried by the classes of the root
        element: it is restored from the URL parameters by the
        AccessibilityManager of Whakerexa. Classes on the body would
        conflict with it.

        """
        body_classes = self._htree.get_body_attribute_value("class")
        if body_classes is None:
            return

        tab_classes = body_classes.split(" ")
        for class_name in ("contrast", "light", "dark"):
            if class_name in tab_classes:
                tab_classes.remove(class_name)

        self._htree.set_body_attribute("class", " ".join(tab_classes))

    # -----------------------------------------------------------------------
    # Static methods
    # -----------------------------------------------------------------------

    @staticmethod
    def append_responsive_menu_button(parent: HTMLNode) -> None:
        """Create and append the menu button, displayed by mobile screens.

        :param parent: (HTMLNode) the parent HTML node to append the button in

        """
        # The 'menu' button for a responsive #nav-content must be outside 'nav'.
        # It carries the inline "menu" SVG icon, styled by menu.css
        # (#menu-button > svg); without it the button would render empty.
        svg_menu = sppasImagesAccess.get_wexa_svg_icon("menu")
        menu_button = HTMLNode(parent.identifier, None, "button", value=svg_menu)
        menu_button.add_attribute("id", "menu-button")
        menu_button.add_attribute("name", "menu-button")
        menu_button.add_attribute("aria-label", "Menu")
        menu_button.add_attribute("aria-expanded", "false")
        menu_button.add_attribute("aria-controls", "nav-content")
        parent.append_child(menu_button)

        # Hidden checkbox required by MenuManager.initMobileToggle() to
        # track the mobile menu open/closed state.
        mobile_checkbox = HTMLNode(parent.identifier, None, "input")
        mobile_checkbox.add_attribute("type", "checkbox")
        mobile_checkbox.add_attribute("id", "mobile")
        mobile_checkbox.add_attribute("role", "button")
        mobile_checkbox.add_attribute("aria-label", "Menu")
        mobile_checkbox.add_attribute("aria-haspopup", "true")
        mobile_checkbox.add_attribute("aria-expanded", "false")
        parent.append_child(mobile_checkbox)

    # -----------------------------------------------------------------------

    @staticmethod
    def append_accessibility_buttons(parent: HTMLNode) -> None:
        """Create and append custom contrast and theme buttons.

        :param parent: (HTMLNode) the parent HTML node to append the buttons in

        """
        # CSS theme. The ThemeManager injects the icon before the label: the
        # side menu of SPPAS shows the name of an item, the top nav of the
        # documentation does not.
        css_theme_button = HTMLNode(parent.identifier, None, "button",
                                    value="<span>" + MSG_THEME + "</span>")
        css_theme_button.add_attribute("id", "btn-css-theme")
        css_theme_button.add_attribute("class", "menuitem")
        css_theme_button.add_attribute("aria-label", MSG_THEME)
        css_theme_button.add_attribute("title", MSG_THEME)
        css_theme_button.add_attribute("onclick", "window.themes && window.themes.next()")
        parent.append_child(css_theme_button)

        # contrast
        svg_contrast = sppasImagesAccess.get_wexa_svg_icon("contrast")
        contrast_image = svg_contrast + "<span>" + MSG_CONTRAST + "</span>"
        contrast_button = HTMLNode(parent.identifier, None, "button",
                                   value=contrast_image)
        contrast_button.add_attribute("id", "btn-contrast")
        contrast_button.add_attribute("class", "menuitem accessibility")
        contrast_button.add_attribute("aria-label", "contrast")
        contrast_button.add_attribute("aria-pressed", "false")
        contrast_button.add_attribute("onclick", "window.Wexa.accessibility.switchContrastScheme();")
        parent.append_child(contrast_button)

        # color scheme
        svg_theme = sppasImagesAccess.get_wexa_svg_icon("color")
        theme_image = svg_theme + "<span>" + MSG_COLOR + "</span>"
        theme_button = HTMLNode(parent.identifier, None, "button",
                                value=theme_image)
        theme_button.add_attribute("id", "btn-color")
        theme_button.add_attribute("class", "menuitem accessibility")
        theme_button.add_attribute("aria-label", "color")
        theme_button.add_attribute("aria-pressed", "false")
        theme_button.add_attribute("onclick", "window.Wexa.accessibility.switchColorScheme();")
        parent.append_child(theme_button)

    # -----------------------------------------------------------------------

    @staticmethod
    def append_sppas_link_button(parent: HTMLNode) -> sppasHTMLButton:
        """Create and append the sppas link button.

        :param parent: (HTMLNode) the parent HTML node to append the buttons in
        :return: (sppasHTMLButton) the sppas link button node

        """
        _button = sppasHTMLButton(parent.identifier, identifier="link-sppas_button")
        _button.add_attribute("data-href", sg.__url__)
        _button.add_attribute("class", "menuitem menu-png-button")
        ic = _button.set_icon("sppas-logo-v5")
        ic.add_attribute("alt", "")
        _button.set_text(None, MSG_WEB)
        parent.append_child(_button)
        return _button

    # -----------------------------------------------------------------------

    @staticmethod
    def append_home_link_button(parent: HTMLNode, home_target: str = "") -> HTMLNode:
        """Create and append the button leading to the Dashboard.

        An 'a' element, because the named target is read by the
        AccessibilityManager of Whakerexa on links only. The icon is the
        inline mono SVG of the other items: it follows --nav-fg-color,
        whatever the theme, which a PNG cannot do.

        :param parent: (HTMLNode) the parent HTML node to append the button in
        :param home_target: (str) Window name to switch to, empty to replace
        the content of the current tab
        :return: (HTMLNode) the home link button node

        """
        svg_home = sppasImagesAccess.get_wexa_svg_icon("dashboard")
        home_image = svg_home + "<span>" + MSG_DASHBOARD + "</span>"
        _button = HTMLNode(parent.identifier, "link-home_button", "a", value=home_image)
        _button.add_attribute("href", "index.html")
        _button.add_attribute("role", "button")
        _button.add_attribute("aria-label", MSG_DASHBOARD)
        _button.add_attribute("class", "menuitem menu-svg-button")
        if len(home_target) > 0:
            _button.add_attribute("data-named-target", home_target)

        parent.append_child(_button)
        return _button

    # -----------------------------------------------------------------------

    @staticmethod
    def append_help_link_button(parent: HTMLNode, page: str = "") -> HTMLNode:
        """Create and append the button opening the document of the app.

        One document per app holds both its user manual and its conceptual
        folder.

        An app whose document is not written yet gets the button disabled:
        the place of the help is the same everywhere, whether or not there
        is something to read.

        :param parent: (HTMLNode) the parent HTML node to append the button in
        :param page: (str) Path of the document, empty while it is unwritten
        :return: (HTMLNode) the help link button node

        """
        svg_help = sppasImagesAccess.get_wexa_svg_icon("help")
        help_image = svg_help + "<span>" + MSG_HELP + "</span>"
        _button = HTMLNode(parent.identifier, "link-help_button", "a", value=help_image)
        _button.add_attribute("role", "button")
        _button.add_attribute("aria-label", MSG_HELP)
        _button.add_attribute("class", "menuitem menu-svg-button")
        if len(page) > 0:
            _button.add_attribute("href", page)
        else:
            _button.add_attribute("aria-disabled", "true")

        parent.append_child(_button)
        return _button

    # -----------------------------------------------------------------------

    @staticmethod
    def append_trace_link_button(parent: HTMLNode) -> HTMLNode:
        """Create and append the button opening the Traces page.

        The page opens in its named tab: whatever the app the button is
        clicked from, the single "sppas_infos" tab is reused and reloaded.
        The button must be registered with handleLinksWithParameters() in
        the body script of the page.

        :param parent: (HTMLNode) the parent HTML node to append the button in
        :return: (HTMLNode) the trace link button node

        """
        svg_trace = sppasImagesAccess.get_wexa_svg_icon("info-square")
        trace_image = svg_trace + "<span>" + MSG_JOURNAL + "</span>"
        _button = HTMLNode(parent.identifier, None, "button", value=trace_image)
        _button.add_attribute("id", "link-trace_button")
        _button.add_attribute("aria-label", "Journal")
        _button.add_attribute("type", "button")
        _button.add_attribute("data-href", "journal.html")
        _button.add_attribute("data-target", "sppas_infos")
        _button.add_attribute("class", "menuitem menu-svg-button")
        parent.append_child(_button)
        return _button

    # -----------------------------------------------------------------------

    @staticmethod
    def append_feedback_link_button(parent: HTMLNode) -> HTMLNode:
        """Create and append the button opening the Feedback page.

        The page opens in a new tab: the user sends a feedback without
        leaving the current app. The button must be registered with
        handleLinksWithParameters() in the body script of the page.

        :param parent: (HTMLNode) the parent HTML node to append the button in
        :return: (HTMLNode) the feedback link button node

        """
        svg_feedback = sppasImagesAccess.get_wexa_svg_icon("feedback")
        feedback_image = svg_feedback + "<span>" + MSG_FEEDBACK + "</span>"
        _button = HTMLNode(parent.identifier, None, "button", value=feedback_image)
        _button.add_attribute("id", "link-feedback_button")
        _button.add_attribute("aria-label", "Feedback")
        _button.add_attribute("type", "button")
        _button.add_attribute("data-href", "feedback.html")
        _button.add_attribute("class", "menuitem menu-svg-button")
        parent.append_child(_button)
        return _button

    # -----------------------------------------------------------------------

    @staticmethod
    def append_pin_button(parent: HTMLNode) -> None:
        """Create and append the pin button of a collapsible menu.

        :param parent: (HTMLNode) the parent HTML node to append the buttons in

        """
        svg_pin = sppasImagesAccess.get_wexa_svg_icon("pin")
        pin_image = svg_pin + "<span>" + MSG_PIN + "</span>"
        _button = HTMLNode(parent.identifier, None, "button", value=pin_image)
        _button.add_attribute("id", "pin-menu")
        _button.add_attribute("aria-label", "Pin Menu")
        _button.add_attribute("type", "button")
        _button.add_attribute("aria-pressed", "false")
        _button.add_attribute("class", "menuitem menu-svg-button")
        parent.append_child(_button)
        # WAI-ARIA Authoring Practices 1.2: Use aria-controls only when the controlled
        # element is not adjacent or the relationship is not otherwise apparent to the user.
        # Notice that _button.add_attribute("aria-controls", "nav-content") is
        # ** not compatible with WhakerPy **.

    # -----------------------------------------------------------------------

    @staticmethod
    def append_exit_button(parent: HTMLNode) -> None:
        """Create and append the pin button of a collapsible menu.

        :param parent: (HTMLNode) the parent HTML node to append the buttons in

        """
        svg_exit = sppasImagesAccess.get_wexa_svg_icon("logout")
        exit_value = svg_exit + "<span>" + MSG_EXIT + "</span>"
        exit_button = HTMLNode(parent.identifier, None, "button", value=exit_value)
        exit_button.add_attribute("id", "exit-menu")
        exit_button.add_attribute("aria-label", "Exit")
        exit_button.add_attribute("type", "button")
        exit_button.add_attribute("aria-pressed", "false")
        exit_button.add_attribute("class", "menuitem menu-exit")
        parent.append_child(exit_button)

    # -----------------------------------------------------------------------

    @staticmethod
    def append_alert_dialogs(parent: HTMLNode):
        """Append the nodes of hidden dialog elements, used for messages.

        :param parent: (HTMLNode) The parent HTML node.

        """
        # A dialog to display any error message after a posted event
        dlg = HTMLNode(parent.identifier, "error_dialog", "dialog",)
        dlg.add_attribute("id", "error_dialog")
        dlg.add_attribute("role", "alertdialog")
        # Its content is written by the JS: the name has to be given here.
        dlg.add_attribute("aria-label", MSG_ERROR)
        dlg.add_attribute("class", "error hidden-alert")
        parent.append_child(dlg)

        # A dialog to display any information message after a posted event
        dlg = HTMLNode(parent.identifier, "info_dialog", "dialog",)
        dlg.add_attribute("id", "info_dialog")
        dlg.add_attribute("role", "alertdialog")
        dlg.add_attribute("aria-label", MSG_INFORMATION)
        dlg.add_attribute("class", "info hidden-alert")
        parent.append_child(dlg)

    # -----------------------------------------------------------------------
    # Protected
    # -----------------------------------------------------------------------

    def _populate_head_css(self, *args, **kwargs):
        """To be overridden by children.

        """
        self._htree.head.link("stylesheet", wapp_settings.css + "app_setup.css", link_type="text/css")

    # -----------------------------------------------------------------------

    def _populate_head_js(self, *args, **kwargs):
        """To be overridden by children.

        """
        pass

    # -----------------------------------------------------------------------

    def _populate_body_header(self, *args, **kwargs):
        """To be overridden by children.

        """
        pass

    # -----------------------------------------------------------------------

    def _populate_body_nav(self, *args, **kwargs):
        """To be overridden by children.

        """
        pass

    # -----------------------------------------------------------------------

    def _populate_body_footer(self, *args, **kwargs):
        """Can be overridden by children.

        """
        self._htree.body_footer.append_sppas_splash()
        self._htree.body_footer.append_copyright()
        self._htree.body_footer.append_scroll_top()
