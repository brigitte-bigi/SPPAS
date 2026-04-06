# -*- coding: UTF-8 -*-
"""
:filename: spas.ui.swapp.components.view.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Classes to create and manage views based on fieldset element.

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
from whakerpy.htmlmaker import HTMLNode

from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import IndexRangeException

# -----------------------------------------------------------------------


class BaseViewNode(HTMLNode):

    REQUIRED = ["views.css"]


    def __init__(self, parent_id: str, identifier: str | None = None, **kwargs):
        """Create the section node for any dynamic fieldset.

        The created node is a 'section' element with the given identifier.
        The subclass has to create the embedded fieldset.

        :param parent_id: (str) Parent node identifier
        :param identifier: (str) Node identifier.

        """
        super(BaseViewNode, self).__init__(parent_id, identifier, "section")

        # A short version of the view title to print in the views bar
        self._msg = ""
        self._script = None

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def get_msg(self) -> str:
        """Return the title message of the view (str)."""
        return self._msg

    # -----------------------------------------------------------------------

    def get_script(self, parent_id: str) -> HTMLNode | None:
        """Return the script of the view to add on the page."""
        if isinstance(parent_id, str) is False:
            raise sppasTypeError(parent_id, "str")

        if self._script is None:
            return None
        else:
            return HTMLNode(parent_id, "current_view_script", "script", value=self._script,
                            attributes={'type':  "application/javascript"})

    # -----------------------------------------------------------------------

    def validate(self) -> bool:
        """Return a boolean to know if the view is fulfilled.

        :return: (bool) True if the view is validated or False else

        """
        return True

    # -----------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        """Process a received event trigger by this view.

        :param event_name: (str) Identifier name of the posted data
        :param event_value: (any) Value of the corresponding posted data
        :return: (int) Status value (default: 205)

        """
        return 205

    # -----------------------------------------------------------------------

    def update(self) -> None:
        """Clear and recreate all html nodes of the view."""
        pass


# -----------------------------------------------------------------------


class ViewManager:

    def __init__(self, views: list[BaseViewNode] = None, view_index: int = 0,
                 prev_event_name: str = "prev_view_event", next_event_name: str = "next_view_event"):
        """Create a ViewManager instance.

        :param views: (list[BaseView]) A list of views
        :param view_index: (int) The index of the view to used
        :param next_event_name: (str) The name of the event to process to pass to the next view, 'next_view_event' by default
        :param prev_event_name: (str) The name of the event to process to pass to the previous view, 'prev_view_event' by default
        :raises sppasTypeError: If the given index isn't an integer or the list doesn't contain only view
        :raises IndexRangeException: If the given index is negative or out of bounds

        """
        self.__prev_event = prev_event_name
        self.__next_event = next_event_name

        if views is None:
            views = list()
        else:
            for current in views:
                if hasattr(current, "update") is False:
                    raise sppasTypeError(current, "BaseView")

        self.__views = views
        self.__current_index = None

        if len(self.__views) > 0:
            self.set_current_view_by_index(view_index)

    # ---------------------------------------------------------------------------
    # GETTERS & SETTERS
    # ---------------------------------------------------------------------------

    def get_current_view(self) -> BaseViewNode:
        """Return the current view used.

        :return: (BaseFieldset) The current fieldset

        """
        return self.__views[self.__current_index]

    # ---------------------------------------------------------------------------

    def get_current_view_index(self) -> int:
        """Return the current index of the view used.

        :return: (int) The index of the current view

        """
        return self.__current_index

    # ---------------------------------------------------------------------------

    def get_view(self, view: str) -> BaseViewNode | None:
        """Return the view with given name or None.

        :param view: (BaseView) View node identifier
        :return: (Node | None)

        """
        for current in self.__views:
            if current.identifier == view:
                return current

        return None

    # -----------------------------------------------------------------------

    def get_view_index(self, view: BaseViewNode | str) -> int:
        """Get the index of the given view.

        :param view: (BaseView) View instance or node identifier
        :raises ValueError: Raises when the given view isn't found
        :return: (int) The index of the view

        """
        for index, current in enumerate(self.__views):
            # parameter identifier given
            if isinstance(view, str) is True:
                if current.identifier == view:
                    return index

            # parameter view given
            elif hasattr(view, "identifier") is True and current.identifier == view.identifier:
                return index

        raise ValueError(f"View index not found : {view.identifier}")

    # ---------------------------------------------------------------------------

    def get_views_identifiers(self) -> list[str]:
        """Returns all identifiers of the views.

        :return: (list[str]) All views node identifiers

        """
        return [view.identifier for view in self.__views]

    # ---------------------------------------------------------------------------

    def set_current_view(self, view: BaseViewNode | str) -> BaseViewNode | None:
        """Set the current view by this instance or node identifier.

        :param view: (BaseView|str) View instance or node identifier
        :return: (BaseView) The instance of the new current view or None if the view doesn't found in the manager

        """
        if self.has_view(view):
            self.__current_index = self.get_view_index(view)
            return self.get_current_view()
        else:
            return None

    # ---------------------------------------------------------------------------

    def set_current_view_by_index(self, index: int) -> BaseViewNode:
        """Set the current view by this index.

        :param index: (int) The index of the current view
        :raises sppasTypeError: If the index isn't an integer
        :raises IndexRangeException: If the index is negative or out of bounds
        :return: (int) The instance of the new current view

        """
        if isinstance(index, int) is False:
            raise sppasTypeError(index, "int")

        if index < 0 or index >= len(self.__views):
            raise IndexRangeException(index, 0, len(self.__views))

        self.__current_index = index
        return self.get_current_view()

    # ---------------------------------------------------------------------------

    def add_view(self, view: BaseViewNode, insert_index: int = None) -> None:
        """Append a given view to the list of views.
        If you give an optional index the view will be inserted at this index,  also the current view
        will not be changed even if it's at this index.

        :param view: (BaseView) The view to add in the manager
        :param insert_index: (int) The index where to insert the new view in the manager
        :raises sppasTypeError: If the parameter isn't an instance of BaseView

        """
        if hasattr(view, "update") is False:
            raise sppasTypeError(view, "BaseView")

        if insert_index is None:
            self.__views.append(view)
        else:
            if insert_index < 0 or insert_index >= len(self.__views):
                self.__views.insert(insert_index, view)

        if len(self.__views) == 1:
            self.__current_index = 0

    # ---------------------------------------------------------------------------
    # PUBLIC METHODS
    # ---------------------------------------------------------------------------

    def has_view(self, view: BaseViewNode | str) -> bool:
        try:
            index = self.get_view_index(view)
            return True
        except ValueError:
            return False

    # ---------------------------------------------------------------------------

    def has_next(self) -> bool:
        """Check if we have a view after the current view.

        :return: (bool) True if the current view has a view after him, False else

        """
        return self.__current_index < len(self.__views) - 1

    # ---------------------------------------------------------------------------

    def has_previous(self) -> bool:
        """Check if we have a view before the current view.

        :return: (bool) True if the current view has a fieldset before him, False else

        """
        return self.__current_index > 0

    # ---------------------------------------------------------------------------

    def next_view(self) -> BaseViewNode | None:
        """Switch to the next view and return them.
        If the current fieldset is the last, we stay with the current fieldset and returns None.

        :return: (BaseView or None) The next view or None if the view is the last

        """
        if self.__current_index >= len(self.__views) - 1:
            self.__current_index = len(self.__views) - 1
            return None

        self.__current_index += 1
        return self.get_current_view()

    # ---------------------------------------------------------------------------

    def previous_view(self) -> BaseViewNode | None:
        """Switch to the previous view and return them.
        If the current view is the first, we stay with the current view and returns None.

        :return: (BaseView or None) The previous view or None if the current is the first

        """
        if self.__current_index == 0:
            self.__current_index = 0
            return None

        self.__current_index -= 1
        return self.get_current_view()

    # ---------------------------------------------------------------------------

    def process_event(self, event_name: str, event_value: object) -> int:
        """Default process of the event to pass to the next or previous view.

        :event_name (str): The name of the event
        :event_value (object): The value of the event
        :return: (int) The response code of process event (205 if unknown given event)

        """
        code = 205

        # process next view event
        if event_name == self.__next_event:
            if self.get_current_view().validate():
                if self.has_next():
                    self.next_view()
                    code = 200
                else:
                    logging.warning(f"{self.__next_event} received but we are already in the last fieldset !")
                    code = 403
            else:
                logging.warning("the client doesn't validate the current view !")
                code = 403

        # process previous view event
        elif event_name == self.__prev_event:
            if self.has_previous():
                self.previous_view()
                code = 200
            else:
                logging.warning(f"{self.__prev_event} received but we are already in the first view !")
                code = 403

        return code

    # -----------------------------------------------------------------------
    # OVERLOADS METHODS FROM Object class
    # -----------------------------------------------------------------------

    def __contains__(self, view: BaseViewNode | str) -> bool:
        """Check if the given view is in the list.

        :param view: (BaseView|str) The view to check if we contain it or its identifier
        :return: (bool) True if the list contains the given view, False else

        """
        if view in self.__views:
            return True
        else:
            for current in self.__views:
                if current.identifier == view:
                    return True

        return False

    # -----------------------------------------------------------------------

    def __iter__(self) -> BaseViewNode:
        """Iterate the current view in a for each loop.

        :return: (BaseView) The current view

        """
        for current in self.__views:
            yield current

    # -----------------------------------------------------------------------

    def __getitem__(self, i: int) -> BaseViewNode:
        """Get the view by the index.

        :param i: (int) The index of the view
        :return: (BaseView) The view corresponding with the given index

        """
        return self.__views[i]

    # -----------------------------------------------------------------------

    def __len__(self) -> int:
        """Get the number of views.

        :return: (int) The number of views

        """
        return len(self.__views)


# -----------------------------------------------------------------------


class ViewBarNode(HTMLNode):
    """Append a navigation bar which allows to see views name.

    This header CSS is inspired by this breadcrumbs style:
    https://thecodeplayer.com/walkthrough/css3-breadcrumb-navigation

    """

    def __init__(self, parent_id: str, view_manager: ViewManager):
        """Create a panel for the view header.

        :param parent_id: (str) Identifier of the html node parent
        :param view_manager: (ViewManager) The view manager

        """
        super(ViewBarNode, self).__init__(parent_id, "views-bar", "section", attributes={"class": "flex-panel"})

        self._views = view_manager
        self._items = list()
        self._create_wizards()

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def update_wizards(self) -> None:
        """Update the wizards in the header.

        Method to use when the user change the page.

        """
        self.clear_children()
        self._items.clear()

        self._create_wizards()

    # -----------------------------------------------------------------------
    # PROTECTED METHODS
    # -----------------------------------------------------------------------

    def _create_wizards(self) -> None:
        """Create the wizards items in the views header."""
        # create wizard_items
        wizard_items = HTMLNode(self.identifier, "wizard-items", "ul", attributes={"class": "tilesWrap"})
        self.append_child(wizard_items)

        for index, view in enumerate(self._views):
            li = HTMLNode(wizard_items.identifier, f"wizard-item-{index}", "li")
            self._items.append(li)
            wizard_items.append_child(li)

            if index < self._views.get_current_view_index():
                li.set_attribute("class", "visited")
            elif index == self._views.get_current_view_index():
                li.set_attribute("class", "active")

            h2 = HTMLNode(li.identifier, None, "h2", value=f"{index + 1}")
            li.append_child(h2)
            h3 = HTMLNode(li.identifier, None, "h3", value=view.get_msg())
            li.append_child(h3)
