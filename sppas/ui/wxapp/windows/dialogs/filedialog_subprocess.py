# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.dialogs.filedialog.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unified replacement for sppasFileDialog using filechooser subprocess.

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

import wx
import os

from sppas.core.config import paths
from sppas.core.coreutils import msg
from sppas.ui.agnostic.filechooser.filechooser_mixin import FileChooserMixin

MSG_TITLE = msg("Files and directories selection", "ui")
MSG_ALL_FILES = msg("All files", "ui")

# ----------------------------------------------------------------------------


class sppasFileDialog:
    """Create a dialog with a file chooser.

    This version emulates the wx-based file dialog API, but calls the
    filechooser_worker via subprocess, making it compatible with both
    wxPython and Web interfaces.

    """
    def __init__(self, parent=None, title=MSG_TITLE, style=None):
        self._style = style
        if self._style is None:
            self._style = wx.FC_OPEN | wx.FC_MULTIPLE | wx.FC_NOSHOWHIDDEN
        if self._style and self._style & wx.FD_SAVE:
            self._mode = "savefile"
        else:
            self._mode = "openfile"
        self._title = title
        self._wildcard = "*.*"
        self._directory = None
        self._paths = []
        self._launch_dialog()

    def _launch_dialog(self):
        multiple = bool(self._style & wx.FC_MULTIPLE)
        result = FileChooserMixin().ask_file(
            mode=self._mode,
            title=self._title,
            multiple=multiple,
            filetypes=[(MSG_ALL_FILES, self._wildcard)]
        )
        print(result)
        self._paths = result if isinstance(result, list) else [result]
        print(self._paths)

    def GetPaths(self):
        return self._paths

    def GetPath(self):
        return self._paths[0] if self._paths else ""

    def GetFilenames(self):
        return [os.path.basename(p) for p in self._paths]

    def GetFilename(self):
        return self.GetFilenames()[0] if self._paths else ""

    def GetFilterIndex(self):
        return 0  # not applicable

    def GetWildcard(self):
        return self._wildcard

    def SetWildcard(self, wild_card):
        self._wildcard = wild_card.replace("|", " ").split(" ")[-1]

    def SetPath(self, path):
        self._paths = [path]

    def SetDirectory(self, directory):
        self._directory = directory

    def ShowHidden(self, show):
        pass  # not yet supported

    def Destroy(self):
        pass

    def ShowModal(self):
        """Return either wx.ID_OK or wx.ID_CANCEL."""
        path = self.GetPath()
        print(path)
        return wx.ID_OK if path else wx.ID_CANCEL

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Destroy()

# ----------------------------------------------------------------------------
# Panels to test
# ----------------------------------------------------------------------------


class TestPanelFileTkinterDialog(wx.Panel):

    def __init__(self, parent):
        super(TestPanelFileTkinterDialog, self).__init__(
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
                print(filenames)
            else:
                wx.LogMessage(f"No file selected: cancelled.")
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
