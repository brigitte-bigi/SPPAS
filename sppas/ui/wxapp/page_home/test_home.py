# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_home.test_home.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test Application for the page 'Home' of the GUI.

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

import wx
import logging

from sppas.core.config import sppasAppConfig

from sppas.ui.wxapp.main_settings import WxAppSettings
from sppas.ui.wxapp.page_home.welcome import TestPanelWelcome
from sppas.ui.wxapp.page_home.links import TestPanelLinksButton
from sppas.ui.wxapp.page_home.home import TestPanelHome

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(
            self,
            parent,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)

        # self.SetBackgroundColour(wx.Colour(100, 100, 100))
        # self.SetForegroundColour(wx.Colour(0, 0, 10))

        # Make the bunch of test panels for the choice book
        panels = list()
        panels.append(TestPanelWelcome(self))
        panels.append(TestPanelLinksButton(self))
        panels.append(TestPanelHome(self))

        for p in panels:
            self.AddPage(p, p.GetName())

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)

    # -----------------------------------------------------------------------

    def _process_key_event(self, event):
        """Process a key event.

        :param event: (wx.Event)

        """
        key_code = event.GetKeyCode()
        # logging.debug('Test panel received the key event {:d}'.format(key_code))

        # Keeps on going the event to the current page of the book.
        event.Skip()

    # -----------------------------------------------------------------------

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    # -----------------------------------------------------------------------

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestFrame(wx.Frame):

    def __init__(self):
        super(TestFrame, self).__init__(None, title="Test Home Frame")
        self.SetSize(wx.Size(900, 600))
        self.SetMinSize(wx.Size(640, 480))

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(self), 1, wx.EXPAND, 0)
        self.SetSizer(sizer)

        # show result
        self.Layout()
        self.Show()

# ----------------------------------------------------------------------------


class TestApp(wx.App):
    """Application to test a TestPanel.

    """

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)
        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

        frm = TestFrame()
        self.SetTopWindow(frm)

    @staticmethod
    def setup_debug_logging():
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logging.debug('Logging set to DEBUG level')

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
