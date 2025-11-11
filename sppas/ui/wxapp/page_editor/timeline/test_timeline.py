# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.timeline.test_timeline.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Test Application for the timeline panels.

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
from sppas.ui.wxapp import sppasApp
from sppas.ui.wxapp.main_settings import WxAppSettings

import sppas.ui.wxapp.page_editor.timeline.rankfiles as rankfiles
import sppas.ui.wxapp.page_editor.timeline.baseview_risepanel as baseview
import sppas.ui.wxapp.page_editor.timeline.errorview_risepanel as errview
import sppas.ui.wxapp.page_editor.timeline.trsview_risepanel as trsview
import sppas.ui.wxapp.page_editor.timeline.audioview_risepanel as audioview
import sppas.ui.wxapp.page_editor.timeline.videoview_risepanel as videoview
import sppas.ui.wxapp.page_editor.timeline.smmpctrl_risepanel as smmpcview

import sppas.ui.wxapp.page_editor.timeline.timeline_panel as timepanel

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(
            self,
            parent,
            style=wx.BORDER_NONE | wx.TAB_TRAVERSAL | wx.WANTS_CHARS)

        p = rankfiles.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = baseview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = errview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = trsview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = audioview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = videoview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = smmpcview.TestPanel(self)
        self.AddPage(p, p.GetName())
        p = timepanel.TestPanel(self)
        self.AddPage(p, p.GetName())

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)

    # -----------------------------------------------------------------------

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # create the frame
        frm = wx.Frame(None, title='Test frame', size=wx.Size(800, 600))
        frm.SetMinSize(wx.Size(640, 480))
        self.SetTopWindow(frm)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(frm), 1, wx.EXPAND, 0)
        frm.SetSizer(sizer)

        # show result
        frm.Layout()
        frm.Show()

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

    # method required by sppasFrame instances which return an icon
    # uses the corresponding method of sppasApp as a delegate
    @staticmethod
    def get_icon(name, height=None, default="default"):
        return sppasApp.get_icon(name=name, height=height, default=default)

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
