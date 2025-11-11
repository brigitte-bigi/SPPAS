# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_annotate.annotate.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Main panel of the page to annotate of the GUI

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

One of the main pages of the wx4-based GUI of SPPAS: the one to annotate.
It's content is organized with a wxSimpleBook() with:
    - a page to fix parameters then run, then save the report,
    - 3 pages with the lists of annotations to select and configure,
    - a page with the progress bar and the procedure outcome report.

"""

import wx

from ..events import sb
from ..events import sppasDataChangedEvent
from ..windows.panels import sppasPanel

from .annotbook import sppasAnnotateBook

# ---------------------------------------------------------------------------


class sppasAnnotatePanel(sppasPanel):
    """Create a panel to annotate automatically the checked files.

    Allows to install new resources.

    """

    TOOLBAR_COLOUR = wx.Colour(250, 120, 50, 196)

    # ------------------------------------------------------------------------

    def __init__(self, parent):
        super(sppasAnnotatePanel, self).__init__(
            parent=parent,
            name="page_annotate",
            style=wx.BORDER_NONE
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
        return self._annbook.get_data()

    # ------------------------------------------------------------------------

    def set_data(self, data):
        """Assign new data to this page.

        :param data: (sppasWorkspace)

        """
        self._annbook.set_data(data)

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
        """Create the main content."""
        # The view of the Editor page
        main_panel = sppasAnnotateBook(self)

        # The toolbar & the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(main_panel, 1, wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    @property
    def _annbook(self):
        return self.FindWindow("annotate_book")

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
        # This event is sent by the tabs manager or by the parent
        self.Bind(sb.EVT_DATA_CHANGED, self._process_data_changed)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()

        if event.AltDown() is True:
            if key_code == 82:  # alt+r Run
                pass

        event.Skip()

    # -----------------------------------------------------------------------

    def _process_data_changed(self, event):
        """Process a change of data.

        Set the data of the event to the other panels.

        :param event: (wx.Event)

        """
        emitted = event.GetEventObject()
        if emitted is self._annbook:
            # Re-Post to the parent.
            wx.LogDebug("The Annotate page is sending a DataChanged event.")
            evt = sppasDataChangedEvent(self.GetId())
            evt.SetEventObject(self)
            evt.SetWorkspace(self._annbook.get_data())
            wx.PostEvent(self.GetParent(), evt)
        else:
            try:
                # data = event.data
                data = event.GetWorkspace()
            except AttributeError:
                wx.LogError('Page Annotate: Data were not sent in the event emitted by {:s}'
                            '.'.format(emitted.GetName()))
                return
            self.set_data(data)
