# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_videocued.videocuedmaker.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: The web page of the "Cued Speech Video Tagger" interface.

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

from whakerkit.responses import WhakerKitResponse

from sppas.ui import _

from ..components import ViewManager
from ..components import ViewBarNode
from ..wappsg import wapp_settings
from ..htmltags.hstatusnode import HTMLTreeError410
from ..htmltags import SwappHeader
from ..htmltags import SwappFooter

from .view_workspace import ViewWorkspace
from .view_hands import ViewHands
from .view_filters import ViewFilter
from .view_exec import ViewExec

# -----------------------------------------------------------------------


MSG_TITLE = _("VideoCueing")

# -----------------------------------------------------------------------


class VideoCuedResponseRecipe(WhakerKitResponse):

    def __init__(self, name="VideoCueing", tree=None, title=MSG_TITLE):
        super(VideoCuedResponseRecipe, self).__init__(name, tree, title)

        # create view manager and instantiate all views
        self.__views = ViewManager()

        self.__views.add_view(ViewWorkspace(self._htree.body_main.identifier))
        self.__views.add_view(ViewHands(self._htree.body_main.identifier))
        self.__views.add_view(ViewFilter(self._htree.body_main.identifier))
        self.__views.add_view(ViewExec(self._htree.body_main.identifier))

        # we have to create the ViewBar after all views added into the manager
        self.__view_bar = ViewBarNode(self._htree.body_main.identifier, self.__views)

    # -----------------------------------------------------------------------
    # OVERRIDE METHODS FROM Whakerpy
    # -----------------------------------------------------------------------

    @classmethod
    def page(cls) -> str:
        """Override. Return the HTML page name."""
        return "videocueing.html"

    # -----------------------------------------------------------------------

    def create(self):
        """Override. Create the fixed page content in HTML.

        The fixed content corresponds to the parts that can't be invalidated:
        head, body_header, body_footer.

        """
        super().create()

        # The default links
        self._htree.head.link(rel="logo icon", href=wapp_settings.icons + "sppas.ico")
        self._htree.head.link("stylesheet", wapp_settings.css + "/main_swapp.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "/page_textcued.css", link_type="text/css")
        self._htree.head.link("stylesheet", wapp_settings.css + "/page_autocued.css", link_type="text/css")

        # Enable css and js dependencies for components that the webapp use
        self.enable_components(["Views", "AnnotParamDialog"])

        self._htree.body_header = SwappHeader(self._htree.identifier, title="CuedSpeech Video Tagger")
        self._htree.body_footer = SwappFooter(self._htree.identifier)

    # -----------------------------------------------------------------------

    def _process_events(self, events: dict, **kwargs) -> bool:
        logging.debug(f" >>>>> Page Cued Speech Video Tagger -- Process events: {events} <<<<<< ")
        self._status.code = 200
        dirty = True

        for event_name, event_value in events.items():
            if event_name in ("next_view_event", "prev_view_event"):
                self._status.code = self.__views.process_event(event_name, event_value)

                # we successfully pass to the next view
                if self._status.code == 200:
                    self.__result_view()
                    self.__view_bar.update_wizards()
                else:
                    dirty = False

            else:
                self._status.code = self.__views.get_current_view().process_event(event_name, event_value)

                if self._status.code == 200:
                    self.__result_view_events(event_name, event_value)
                elif self._status.code == 205:
                    logging.warning(f"Unknown event received : {event_name}")
                    dirty = False

        return dirty

    # -----------------------------------------------------------------------

    def _bake(self) -> None:
        if self._status.code == 410:
            self._htree = HTMLTreeError410()
            return None

        current_view = self.__views.get_current_view()

        # set script of the current view
        script = current_view.get_script(self._htree.head.identifier)
        self._htree.head.remove_child(script.identifier)
        self._htree.head.append_child(script)

        # append the views bar
        self._htree.body_main.append_child(self.__view_bar)

        # create the html view and append it in the body_main
        current_view.update()
        self._htree.body_main.append_child(current_view)

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    def __result_view(self) -> None:
        """Manage things to do after a view 'finished' and the user pass to the next.
        Most often, get data of the last view to pass to the next (the current now).

        """
        # the user chosen a hands set, register the choice and pass it to the new view
        if isinstance(self.__views.get_current_view(), ViewFilter):
            hands_set = self.__views[self.__views.get_current_view_index() - 1].get_hands_set_chosen()
            self.__views.get_current_view().set_hands_set(hands_set)  # give hands set to the filter view

        # the user chosen a filter (or not) and configure all options to launch the annotation
        elif isinstance(self.__views.get_current_view(), ViewExec):
            # give files and options to the exec view and start the annotation
            workspace, files = self.__views[0].get_files(workspace=True)
            options = self.__views[self.__views.get_current_view_index() - 1].get_options()

            self.__views.get_current_view().set_files(workspace, files)
            self.__views.get_current_view().start_process(options)

    # -----------------------------------------------------------------------

    def __result_view_events(self, event_name: str, event_value: object) -> None:
        """Manage data to response to the client following the event and the current view.

        :param event_name: (str) the name of the current event process
        :param event_value: (object) the value of the current event process

        """
        # event when the user click on arrows to change hand pos of a hands set in the hands set view
        if event_name == "change_hand_pos" and isinstance(self.__views.get_current_view(), ViewHands):
            self._data = {'hand_pos': self.__views.get_current_view().get_hand_pos(event_value[0])}

        # event in the hands filter view to load hands image filtered
        elif event_name == "load_hand" and isinstance(self.__views.get_current_view(), ViewFilter):
            self._data = self.__views.get_current_view().get_filtered_hand(event_value)

        # event of the last view to know if the annotation has finished or not
        elif event_name == "update_process" and isinstance(self.__views.get_current_view(), ViewExec):
            self._data = {'process_running': self.__views.get_current_view().is_annot_running()}

        # event of the last view to restart the annotation once finished
        elif event_name == "restart_process_event" and isinstance(self.__views.get_current_view(), ViewExec):
            options = self.__views[self.__views.get_current_view_index() - 1].get_options()
            # give options to the exec view and start the annotation
            self.__views.get_current_view().start_process(options)
