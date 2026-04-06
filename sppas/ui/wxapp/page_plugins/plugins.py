# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_plugins.plugins.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Main panel of the page for the plugins of SPPAS.

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

"""

import wx

from sppas.src.wkps import States
from sppas.ui import _

from ..events import sb
from ..events import sppasDataChangedEvent
from ..windows import sppasPanel
from ..windows import sppasToolbar
from ..windows import Error, Information
from ..windows import sppasChoiceDialog
from ..windows import sppasFileDialog
from ..windows import sppasStaticLine

from .plugslist import sppasPluginsList


# ---------------------------------------------------------------------------
# List of displayed messages:


PGS_TITLE = _("Plugins: ")
PGS_ACT_ADD = _("Install")
PGS_ACT_DEL = _("Delete")
PGS_ACT_ADD_ERROR = _("Plugin '{:s}' can't be installed due to the following"\
                      " error:\n{!s:s}")
PGS_ACT_DEL_ERROR = _("Plugin '{:s}' can't be deleted due to the following"\
                      " error:\n{!s:s}")
FLS_MSG_CONFIRM_DEL = _("Are you sure you want to delete the plugin {:s}?")

PGS_NO_PLUGINS = _("No plugin installed.")
PGS_TO_DELETE = _("Select the plugin to delete:")
PGS_DELETED = _("Plugin {:s} was successfully deleted.")
PGS_INSTALLED = _("Plugin successfully installed in folder {:s}.")
PGS_ERR_ADD = _("Install error")
PGS_ERR_DEL = _("Delete error")

# ----------------------------------------------------------------------------


class sppasPluginsPanel(sppasPanel):
    """Create a panel to manage plugins and use them on the selected files.

    """

    PLUGINS_COLOUR = wx.Colour(196, 128, 196, 196)

    def __init__(self, parent):
        super(sppasPluginsPanel, self).__init__(
            parent=parent,
            name="page_plugins",
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE,
        )

        # Construct the GUI
        self._create_content()
        self._setup_events()

        # Look&feel
        try:
            self.SetBackgroundColour(wx.GetApp().settings.bg_color)
            self.SetForegroundColour(wx.GetApp().settings.fg_color)
            self.SetFont(wx.GetApp().settings.text_font)
        except AttributeError:
            self.InheritAttributes()

        self.Layout()

    # ------------------------------------------------------------------------
    # Public methods to access the data
    # ------------------------------------------------------------------------

    def get_data(self):
        """Return the data currently displayed in the list of files.

        :returns: (sppasWorkspace) data of the files-viewer model.

        """
        return self.FindWindow("pluginslist").get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        self._pluginslist.set_data(data)

    # -----------------------------------------------------------------------
    # Colours & Fonts
    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. """
        wx.Panel.SetForegroundColour(self, colour)
        for c in self.GetChildren():
            if c.GetName() != "hline":
                c.SetForegroundColour(colour)

    # ------------------------------------------------------------------------
    # Private methods to construct the panel.
    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        tb = self.__create_toolbar()
        fv = sppasPluginsList(self, name="pluginslist")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND, border=0)
        sizer.Add(self._create_hline(), 0, wx.EXPAND)
        sizer.Add(fv, 1, wx.EXPAND, border=0)
        self.SetSizer(sizer)

        self.SetMinSize(wx.Size(sppasPanel.fix_size(320), sppasPanel.fix_size(200)))
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def _create_hline(self):
        """Create an horizontal line, used to separate the toolbar."""
        line = sppasStaticLine(self, orient=wx.LI_HORIZONTAL, name="hline")
        line.SetMinSize(wx.Size(-1, 20))
        line.SetPenStyle(wx.PENSTYLE_SHORT_DASH)
        line.SetDepth(1)
        line.SetForegroundColour(self.PLUGINS_COLOUR)
        return line

    # -----------------------------------------------------------------------

    @property
    def _pluginslist(self):
        return self.FindWindow("pluginslist")

    # -----------------------------------------------------------------------

    def __create_toolbar(self):
        """Create the toolbar."""
        tb = sppasToolbar(self)
        tb.set_focus_color(sppasPluginsPanel.PLUGINS_COLOUR)
        tb.AddTitleText(PGS_TITLE, sppasPluginsPanel.PLUGINS_COLOUR)
        tb.AddButton("plugin-import", PGS_ACT_ADD)
        tb.AddButton("plugin-delete", PGS_ACT_DEL)
        return tb

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

        # The user clicked (LeftDown - LeftUp) an action button of the toolbar
        self.Bind(wx.EVT_BUTTON, self._process_action)

        # The data have changed.
        # This event is sent by any of the children or by the parent
        self.Bind(sb.EVT_DATA_CHANGED, self._process_data_changed)

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        cmd_down = event.CmdDown()
        shift_down = event.ShiftDown()

        event.Skip()

    # ------------------------------------------------------------------------

    def _process_action(self, event):
        """Process an action of a button.

        :param event: (wx.Event)

        """
        name = event.GetEventObject().GetName()

        if name == "plugin-import":
            self._install()

        elif name == "plugin-delete":
            self._delete()

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        try:
            # wkp = event.data
            wkp = event.GetWorkspace()
        except AttributeError:
            wx.LogError("Page Plugins: "
                        "Data were not sent in the event emitted by {:s}."
                        "".format(emitted.GetName()))
            return

        if emitted != self._pluginslist:
            try:
                self._pluginslist.set_data(wkp)
            except:
                pass

        # Send the data to the parent
        pm = self.GetParent()
        if pm is not None and emitted != pm:
            wkp.set_state(States().CHECKED)
            evt = sppasDataChangedEvent(pm.GetId())
            evt.SetEventObject(self)
            evt.SetWorkspace(wkp)
            wx.PostEvent(self.GetParent(), evt)

    # ------------------------------------------------------------------------

    def _delete(self):
        """Delete a plugin."""
        wx.LogMessage('User asked to delete a plugin')

        keys = self._pluginslist.get_plugins()
        wx.LogMessage('List of plugins: {:s}'.format(str(keys)))
        if len(keys) == 0:
            Information(PGS_NO_PLUGINS)
            return None

        dlg = sppasChoiceDialog(PGS_TO_DELETE, choices=keys)
        if dlg.ShowModal() == wx.ID_OK:
            plugin_id = dlg.GetStringSelection()
            try:
                self._pluginslist.delete(plugin_id)
                Information(PGS_DELETED.format(plugin_id))
            except Exception as e:
                message = PGS_ACT_DEL_ERROR.format(plugin_id, str(e))
                Error(message)

        dlg.Destroy()

    # ------------------------------------------------------------------------

    def _install(self):
        """Import a plugin from a zip file."""
        wx.LogMessage("User asked to install a plugin")

        # Get the name of the file to be imported
        dlg = sppasFileDialog(self, title=PGS_ACT_ADD,
                              style=wx.FC_OPEN | wx.FC_NOSHOWHIDDEN)
        dlg.SetWildcard("ZIP files|*.zip")  #  |*.[zZ][iI][pP]")
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            try:
                folder = self._pluginslist.install(filename)
                Information(PGS_INSTALLED.format(folder))

            except Exception as e:
                message = PGS_ACT_ADD_ERROR.format(filename, str(e))
                Error(message)

        dlg.Destroy()
