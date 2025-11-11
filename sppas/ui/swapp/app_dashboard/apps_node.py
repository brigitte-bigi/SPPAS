"""
:filename: sppas.ui.swapp.app_dashboard.apps_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The apps section of the SPPAS Dashboard Application.

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

from whakerpy.htmlmaker import HTMLNode

from sppas.ui import _

# ---------------------------------------------------------------------------


MSG_LAUNCH = _("Launch")

# ---------------------------------------------------------------------------


class AppsNode(HTMLNode):
    """The section with applications of the dashboard application.

    """
    def __init__(self, parent_id):
        super(AppsNode, self).__init__(parent_id, "dashboard_apps_sec", "section")
        self.add_attribute("id", self.identifier)
        self.add_attribute("class", "apps-panel")

    # -----------------------------------------------------------------------

    def create_app_card(self, name, icon_name, text, link, enable=True):
        """A specific card to represent the card of an app to launch.

        <article class="app">
          <img
            class="app-background-img"
            src="sppas/ui/swapp/statics/icons/Refine/sppas_logo_v3.png"
            alt="SPPAS logo"
          />
          <div class="app-content | flow">
            <div class="app-container | flow">
              <h2 class="app-title">SPPAS</h2>
              <p class="app-description">
                Graphical User Interface to perform the automatic annotation and analysis of speech.
              </p>
            </div>
            <button class="app-button">Launch</button>
          </div>
        </article>

        :param name: (str) The short name of the application.
        :param icon_name: (str) Name of an image representing the application
        :param text: (str) Text description of the application
        :param link: (str) Link to the application
        :param enable: (bool) Enable or disable the node.

        """
        ident = name.lower().replace(" ", "_")
        article = HTMLNode(self.identifier, ident+"_article", "article")
        article.add_attribute("class", "app")
        self.append_child(article)

        # Define the background image
        attributes = dict()
        attributes["class"] = "app-background-img"
        attributes["src"] = icon_name
        attributes["alt"] = name + " logo"
        img = HTMLNode(article.identifier, ident+"_img", "img", attributes=attributes)
        article.append_child(img)

        # Define the content of the card: a container and a button
        content = HTMLNode(article.identifier, ident + "_content", "div")
        content.add_attribute("class", "app-content | flow")
        article.append_child(content)

        # Container for a title and a description
        container = HTMLNode(content.identifier, ident + "_container", "div")
        container.add_attribute("class", "app-container | flow")
        content.append_child(container)

        # - title
        title = HTMLNode(container.identifier, ident + "_title", "h2", value=name)
        title.add_attribute("id", ident + "_title")
        title.add_attribute("class", "app-title")
        container.append_child(title)

        # - description
        descr = HTMLNode(container.identifier, ident + "_descr", "p", value=text)
        descr.add_attribute("class", "app-description")
        container.append_child(descr)

        # Launch button
        if enable is False:
            button = HTMLNode(content.identifier, ident + "_button", "button", value=MSG_LAUNCH)
            button.add_attribute("class", "app-button")
            button.add_attribute("disabled", None)
        else:
            if link.endswith(".html"):
                button = HTMLNode(content.identifier, ident + "_button", "a", value=MSG_LAUNCH, attributes={
                    'href': link,
                    'role': "button",
                    'target': "_blank",
                    'class': "app-button",
                    "id": ident + "_button"
                })
            else:
                button = HTMLNode(content.identifier, ident + "_button", "button", value=MSG_LAUNCH)
                button.add_attribute("class", "app-button")
                button.add_attribute("onclick", link)
        content.append_child(button)
