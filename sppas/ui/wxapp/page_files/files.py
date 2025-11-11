# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_files.files.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Main panel of the page 'files'.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

It manages:

    - the set of workspaces,
    - the list of files of a workspace,
    - the list of references of a workspace, and
    - the actions to perform on both of them.

"""
import logging

import wx

from sppas.core.coreutils import sppasTypeError
from sppas.src.wkps import sppasWorkspace

from ..events import sb   # the global SppasEventBinder instance
from ..events import sppasDataChangedEvent
from ..windows import sppasPanel
from ..windows import sppasStaticLine

from .workspaces import WorkspacesPanel
from .pathstree import PathsTreePanel
from .refstree import ReferencesTreePanel
from .associate import AssociatePanel

# ---------------------------------------------------------------------------


class sppasFilesPanel(sppasPanel):
    """Main panel to browse and select workspaces and their content.

    This panel is managing 4 areas:

        1. the workspaces;
        2. the tree-view of files;
        3. an association toolbar to link files and references;
        4. the references.

    """

    def __init__(self, parent):
        super(sppasFilesPanel, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
            name="page_files"
        )

        # Construct the GUI
        self._create_content()
        self._setup_events()

        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        # Organize items and fix a size for each of them
        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (sppasWorkspace) data of the files-viewer model.

        """
        return self.FindWindow("files_panel").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to display to this page.

        :param data: (sppasWorkspace)

        """
        if isinstance(data, sppasWorkspace) is False:
            raise sppasTypeError("sppasWorkspace", type(data))

        # Set to all children.
        self.__send_data(self.GetParent(), data)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """Create the main content."""
        # Create all the panels
        wp = WorkspacesPanel(self, name='wkps_panel')
        fm = PathsTreePanel(self, name="files_panel")
        ap = AssociatePanel(self, name="assoc_panel")
        cm = ReferencesTreePanel(self, name="refs_panel")

        # Organize all the panels vertically, separated by 2px grey lines.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wp, 1, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(fm, 5, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(ap, 0, wx.EXPAND, 0)
        sizer.Add(self.__create_vline(), 0, wx.EXPAND, 0)
        sizer.Add(cm, 3, wx.EXPAND, 0)

        self.SetSizer(sizer)

    # ------------------------------------------------------------------------

    def __create_vline(self):
        """Create a vertical line, used to separate the panels."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL, name="static_line")
        line.SetMinSize(wx.Size(2, -1))
        line.SetSize(wx.Size(2, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(2)
        # line.SetForegroundColour(wx.Colour(128, 128, 128, 128))
        return line

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Capture keys
        self.Bind(wx.EVT_CHAR_HOOK, self._process_key_event)

        # The data have changed.
        # This event is sent by any of the children or by the parent
        self.Bind(sb.EVT_DATA_CHANGED, self._process_data_changed)

        # An action is requested.
        self.Bind(sb.EVT_ACTION, self._process_action)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 65:    # alt+a Add files
                self.FindWindow("files_panel").add()

            elif key_code == 69:  # alt+e Export workspace
                self.FindWindow("wkps_panel").export_wkp()

            elif key_code == 70:  # alt+f Check files
                self.FindWindow("assoc_panel").check_filter()

            elif key_code == 71:  # alt+g Check all files
                self.FindWindow("assoc_panel").check_all()

            elif key_code == 73:  # alt+i Import workspace
                self.FindWindow("wkps_panel").import_wkp()

            elif key_code == 75:  # alt+l Link files/refs
                self.FindWindow("assoc_panel").add_links()

            elif key_code == 77:  # alt+n Rename the workspace
                self.FindWindow("wkps_panel").rename_wkp()

            elif key_code == 82:  # alt+r Create a reference
                self.FindWindow("refs_panel").create_ref()

            elif key_code == 83:  # alt+s Pin&Save the workspace
                self.FindWindow("wkps_panel").pin_save_wkp()

            elif key_code == 87:  # alt+w Remove checked
                self.FindWindow("files_panel").remove()

            else:
                event.Skip()

        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            data = event.GetWorkspace()
        except AttributeError:
            wx.LogError('Page Files: Data were not sent in the event emitted by {:s}'
                        '.'.format(emitted.GetName()))
            return

        self.__send_data(emitted, data)

    # -----------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        action = event.GetAction()
        logging.debug("Process action: {:s}".format(action))

        if action == "delete":
            files_win = self.FindWindow("files_panel")
            if emitted != files_win:
                files_win.delete()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __send_data(self, emitted, data):
        """Set a change of data to the children, send to the parent.

        :param emitted: (wx.Window) The panel the data are coming from
        :param data: (sppasWorkspace)

        """
        # Set the data to appropriate children panels
        for panel in self.GetChildren():
            if panel is not emitted and panel.GetName() in ("wkps_panel", "files_panel", "assoc_panel", "refs_panel"):
                panel.set_data(data)

        # Send the data to the parent
        pm = self.GetParent()
        if pm is not None and emitted is not pm:
            evt = sppasDataChangedEvent(self.GetId())
            evt.SetEventObject(self)
            evt.SetWorkspace(data)
            wx.PostEvent(self.GetParent(), evt)

# ----------------------------------------------------------------------------


class TestPanelFiles(sppasFilesPanel):
    def __init__(self, parent):
        super(TestPanelFiles, self).__init__(parent)
