# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.dialogs.file.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A custom dialog to choose files.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

import os
import wx

from sppas.core.config import paths
from .dialog import sppasDialog

# ----------------------------------------------------------------------------


class sppasFileDialog(sppasDialog):
    """Dialog class to select files.

    """

    def __init__(self, parent,
                 title="Files and directories selection",
                 style=wx.FC_OPEN | wx.FD_FILE_MUST_EXIST | wx.FC_MULTIPLE | wx.FC_NOSHOWHIDDEN):
        """Create a dialog with a file chooser.

        :param parent: (wx.Window)
        :param style: (int)

        This class supports the following styles:

            - wx.FC_DEFAULT_STYLE: The default style: wx.FC_OPEN
            - wx.FC_OPEN: Creates a file control suitable for opening files. Cannot be combined with wx.FC_SAVE.
            - wx.FC_SAVE: Creates a file control suitable for saving files. Cannot be combined with wx.FC_OPEN.
            - wx.FC_MULTIPLE: For open control only, Allows selecting multiple files. Cannot be combined with wx.FC_SAVE
            - wx.FC_NOSHOWHIDDEN: Hides the "Show Hidden Files" checkbox (Generic only)

        """
        super(sppasFileDialog, self).__init__(
            parent=parent,
            title=title,
            style=wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.STAY_ON_TOP)

        self._create_content(style)
        self._create_buttons()

        # Fix frame properties
        self.SetMinSize(wx.Size(sppasDialog.fix_size(320),
                                sppasDialog.fix_size(200)))
        self.LayoutComponents()
        self.CenterOnParent()
        self.GetSizer().Fit(self)
        self.FadeIn()

    # -----------------------------------------------------------------------
    # Public methods to manage filenames
    # -----------------------------------------------------------------------

    def GetFilename(self):
        """Return the currently selected filename."""
        return self.FindWindow("content").GetFilename()

    # -----------------------------------------------------------------------

    def GetFilenames(self):
        """Return a list of filenames selected in the control."""
        return self.FindWindow("content").GetFilenames()

    # -----------------------------------------------------------------------

    def GetPaths(self):
        """Return a list of the full paths (directory and filename) of the files."""
        return self.FindWindow("content").GetPaths()

    # -----------------------------------------------------------------------

    def GetPath(self):
        """Return the full path (directory and filename) of the currently selected file."""
        return self.FindWindow("content").GetPath()

    # -----------------------------------------------------------------------

    def GetFilterIndex(self):
        """Return the zero-based index of the currently selected filter."""
        return self.FindWindow("content").GetFilterIndex()

    # -----------------------------------------------------------------------

    def GetWildcard(self):
        """Return the current wildcard."""
        return self.FindWindow("content").GetWildcard()

    # -----------------------------------------------------------------------

    def SetWildcard(self, wild_card):
        return self.FindWindow("content").SetWildcard(wild_card)

    # -----------------------------------------------------------------------

    def SetPath(self, path):
        return self.FindWindow("content").SetPath(path)

    # -----------------------------------------------------------------------

    def SetDirectory(self, directory):
        """Set (change) the current directory displayed in the control."""
        return self.FindWindow("content").SetDirectory(directory)

    # -----------------------------------------------------------------------

    def ShowHidden(self, show):
        """Set whether hidden files and folders are shown or not."""
        return self.FindWindow("content").ShowHidden(show)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self, style):
        """Create the content of the file dialog."""
        fc = wx.FileCtrl(self, style=style)
        fc.SetMinSize(wx.Size(sppasDialog.fix_size(480),
                              sppasDialog.fix_size(320)))
        fc.SetBackgroundColour(self.GetBackgroundColour())
        fc.SetForegroundColour(self.GetForegroundColour())
        fc.SetFont(self.GetFont())
        fc.SetName("content")
        for c in fc.GetChildren():
            c.SetBackgroundColour(self.GetBackgroundColour())
            c.SetForegroundColour(self.GetForegroundColour())
            c.SetFont(self.GetFont())

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])
        self.Bind(wx.EVT_BUTTON, self._process_event)
        self.SetAffirmativeId(wx.ID_OK)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()
        if event_id == wx.ID_CANCEL:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Close()
        elif event_id == wx.ID_OK:
            self.EndModal(wx.ID_OK)

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelFileDialog(wx.Panel):

    def __init__(self, parent):
        super(TestPanelFileDialog, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS,
            name="Test File Dialogs")

        wx.Button(self, label="Select file or dir", pos=(10, 10), size=(128, 64), name="btn_file")
        wx.Button(self, label="Select audio file", pos=(210, 10), size=(128, 64), name="btn_audiofile")
        wx.Button(self, label="Select sample", pos=(410, 10), size=(128, 64), name="btn_sample")

        self.Bind(wx.EVT_BUTTON, self.process_event)

    # -----------------------------------------------------------------------

    def process_event(self, event):
        # Tested: ShowModal returns wx.OK or wx.CANCEL
        # Get filename or filenames or dirname or dirnames
        # Get them from GetPath() or GetPaths()
        # __enter__ should work
        # Set a WildCard
        obj = event.GetEventObject()
        name = obj.GetName()

        if name == "btn_file":
            dlg = sppasFileDialog(self)
            filenames = "None"
            if dlg.ShowModal() == wx.ID_OK:
                filenames = dlg.GetPaths()
            dlg.Destroy()
            wx.LogMessage(f"Selected: {filenames}")

        elif name == "btn_audiofile":
            with sppasFileDialog(self, title="Select audio file", style=wx.FD_SAVE) as dlg:
                dlg.SetWildcard("Wave (*.wav)|*.wav")
                if dlg.ShowModal() == wx.ID_CANCEL:
                    wx.LogMessage(f"No file selected: cancelled.")
                    return
                pathname = dlg.GetPath()
                if len(pathname) == 0:
                    wx.LogMessage("No file name selected.")
                    return
                if os.path.isfile(pathname) is False:
                    wx.LogMessage(f"Selection {pathname} is not a file.")
                    return
                wx.LogMessage(f"Selected: {pathname}")

        elif name == "btn_sample":
            dlg = sppasFileDialog(self, style=wx.FC_OPEN | wx.FC_NOSHOWHIDDEN)
            dlg.SetDirectory(paths.samples)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                wx.LogMessage(f"Selected: {filename}")
