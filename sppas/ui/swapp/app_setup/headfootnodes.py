"""
:filename: sppas.ui.swapp.app_setup.headernodes.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A node to represent the HTML body header of the setup app.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

Requirements:

- javascript functions:
    * colors_scheme_switch(checkbox);
    * contrast_scheme_switch(checkbox);
    * tabToLink(event, url);
    * notify_action(object);
- several css properties (flex-panel, flex-item, ...)

"""

from whakerpy.htmlmaker import HTMLNode

from sppas.core.config import sg
from sppas.core.coreutils import msg

from ..htmltags import sppasHTMLButton

# -----------------------------------------------------------------------


MSG_ACTION_BACK = msg('Back', "ui")
MSG_ACTION_NEXT = msg('Next', "ui")
MSG_ACTION_INSTALL = msg('Install', "ui")
MSG_ACTION_CANCEL = msg('Cancel', "ui")
MSG_ACTION_DONE = msg('Done', "ui")

# -----------------------------------------------------------------------


class SetupHeaderNode(HTMLNode):
    """Append a navigation bar which allows to see field names.

    This header CSS is inspired by this breadcrumbs style:
    https://thecodeplayer.com/walkthrough/css3-breadcrumb-navigation

    """

    def __init__(self, parent_id, fieldsets, current):
        """Create a panel for the Setup app header.

        :param parent_id: (str) Identifier
        :param fieldsets: (list of setup fieldsets)
        :param current: (SetupBaseFieldset) The currently enabled fieldset

        """
        super(SetupHeaderNode, self).__init__(
            parent_id, "headerbar", "section",
            attributes={"class": "flex-panel"})
        self.__fieldnames = [f.get_msg() for f in fieldsets]
        cur_idx = fieldsets.get_index(current)

        event_link = "tabToLink(event,'" + sg.__url__ + "');"
        blink = sppasHTMLButton(parent=self.identifier, identifier="logo_btn")
        blink.add_attribute("onclick", event_link)
        ic = blink.set_icon("sppas_logo_v3")
        ic.add_attribute("alt", "SPPAS website")

        witems = HTMLNode(self.identifier, "wizarditems", "ol", attributes={"class": "flex-item breadcrumb"})
        for i, fieldnode in enumerate(fieldsets):
            li = HTMLNode(witems.identifier, "wizarditem_%d" % i, "li", value=fieldnode.get_msg())
            if i < cur_idx:
                li.set_attribute("class", "visited")
            elif i == cur_idx:
                li.set_attribute("class", "active")
            witems.append_child(li)

        self.append_child(blink)
        self.append_child(witems)

    # -----------------------------------------------------------------------

    def update(self, cur_idx):
        """Update the header by highlighting the given n-th fieldset.

        """
        raise NotImplementedError

# -----------------------------------------------------------------------


class SetupActionsNode(HTMLNode):
    """Append an action bar which allows browsing through fieldsets.

    """

    def __init__(self, parent_id, fieldsets, current, can_install=True):
        """Create a panel for the Setup app footer.

        :param parent_id: (str) Identifier
        :param fieldsets: (list of setup fieldsets)
        :param current: (SetupBaseFieldset) The currently enabled fieldset

        """
        super(SetupActionsNode, self).__init__(
            parent_id, "actions_container", "section",
            attributes={"class": "flex-panel", "id": "actions_container"})
        self.__fieldnames = [f.get_msg() for f in fieldsets]
        cur_idx = fieldsets.get_index(current)

        # --- b1 = Prev
        b1 = sppasHTMLButton(parent=self.identifier, identifier="prev_btn")
        b1.set_icon("arrow_left")
        b1.set_text(None, MSG_ACTION_BACK)
        # b1 is disabled if first fieldset (no prev fieldset)
        if cur_idx == 0:  # or cur_idx+1 == len(fieldsets):
            b1.add_attribute("disabled", None)

        # --- b2 = Next or Install
        if cur_idx >= len(fieldsets) - 2 and can_install:
            # Create the installation button
            b2 = sppasHTMLButton(parent=self.identifier, identifier="install_btn")
            b2.set_text(None, MSG_ACTION_INSTALL)
            b2.set_icon("install")
            b2.add_attribute("class", "install-button")   # for a different color
        else:
            b2 = sppasHTMLButton(parent=self.identifier, identifier="next_btn")
            b2.set_text(None, MSG_ACTION_NEXT)
            b2.set_icon("arrow_right")
        # b2 is disabled if last fieldset (no next fieldset)
        if cur_idx+1 == len(fieldsets):
            b2.add_attribute("disabled", None)

        # --- b3 = Cancel or Done if installation was performed (i.e. if last field)
        if cur_idx+1 == len(fieldsets):
            b3 = sppasHTMLButton(parent=self.identifier, identifier="exit_btn")
            b3.set_icon("exit")
            b3.set_text(None, MSG_ACTION_DONE)
        else:
            b3 = sppasHTMLButton(parent=self.identifier, identifier="cancel_btn")
            b3.set_icon("cancel")
            b3.set_text(None, MSG_ACTION_CANCEL)

        # --- shared action button properties
        for b in (b1, b2, b3):
            event_submit = "notify_action(this);"
            b.add_attribute("class", "flex-item")
            # b.add_attribute("type", "submit")
            b.add_attribute("onclick", event_submit)
            b.add_attribute("value", str(fieldsets.get_index(current)))
            self.append_child(b)
