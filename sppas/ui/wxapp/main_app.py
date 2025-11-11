# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.main_app.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: This is the application for SPPAS, based on the Phoenix UI.

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

Create and run the application:

>>> app = sppasApp()
>>> app.run()

"""

import time
import datetime
import traceback
import wx
import logging
from os import path
from argparse import ArgumentParser

from sppas.core.config import sg
from sppas.core.config import cfg
from sppas.core.config import lgs

from .windows.splash import sppasSplashScreen
from .main_settings import WxAppSettings
from .main_window import sppasMainWindow
from .imgtools import sppasImagesAccess

# ---------------------------------------------------------------------------


class sppasApp(wx.App):
    """Create the SPPAS GUI application for wx4.

    """

    def __init__(self):
        """Wx Application initialization.

        Create the application for the GUI of SPPAS based on Phoenix.

        """
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=False,  # True => crash with anaconda
                        clearSigInt=True)

        self.SetAppName(sg.__name__)
        self.SetAppDisplayName(sg.__name__ + " " + sg.__version__)
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        wx.SystemOptions.SetOption("mac.listctrl.always_use_generic", 1)
        wx.SystemOptions.SetOption("msw.font.no-proof-quality", 0)

        # Fix logging level and settings
        # self.process_command_line_args()
        self.settings = WxAppSettings()

        # This catches events when the app is asked to activate
        # by some other process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    # -----------------------------------------------------------------------

    def InitLocale(self):
        """Override. Do not re-initialize the locale to 'C'.

        The base method:
        Python 3.8 is now setting the locale to what is defined by the system
        as the default locale. This causes problems with wxWidgets which
        expects to be able to manage the locale via the wx.Locale class,
        so the locale is reset here to be the default "C" locale settings.

        SPPAS is using the standard python locale instead of the wx one
        so we don't want it to be re-initialized to 'C'.

        """
        # We have to fix wx language and translation. SPPAS won't use it but
        # we have to fix it to not raise an exception under Windows:
        # wx._core.wxAssertionError: C++ assertion "strcmp(setlocale(0, 0), "C") == 0"
        # failed at ..\..\src\common\intl.cpp(1694) in wxLocale::GetInfo(): You probably
        # called setlocale() directly instead of using wxLocale and now there is a
        # mismatch between C/C++ and Windows locale.
        # Things are going to break, please only change locale by creating wxLocale
        # objects to avoid this!

        # so we create an un-used instance of wx.Locale()
        self.__unused_locale = wx.Locale(wx.LANGUAGE_ENGLISH)

    # -----------------------------------------------------------------------
    # MacOS specific methods to solve problems:
    #   - with the dock,
    #   - with raising the main window
    # -----------------------------------------------------------------------

    def BringWindowToFront(self):
        """For MacOS, required for the window to raise normally."""
        try:
            # it's possible for this event to come when the frame is closed
            self.GetTopWindow().Raise()
        except:
            pass

    def MacReopenApp(self):
        """For MacOS, called when the doc icon is clicked, and ???."""
        self.BringWindowToFront()

    def OnActivate(self, event):
        # For MacOS, to raise the window normally."""
        if event.GetActive():
            # if this is an activate event, rather than something else,
            # like iconize.
            self.BringWindowToFront()
        event.Skip()

    # -----------------------------------------------------------------------
    # Methods to configure and starts the app
    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """Process the command line.

        This is an opportunity for users to fix some args.

        """
        # create a parser for the command-line arguments
        parser = ArgumentParser(
            usage="{:s} [options]".format(path.basename(__file__)),
            description="... " + sg.__name__ + " " + sg.__title__)

        # add arguments here
        parser.add_argument("-l", "--log_level",
                            required=False,
                            type=int,
                            default=cfg.log_level,
                            help='Log level (default={:d}).'
                                 ''.format(cfg.log_level))

        # then parse
        args = parser.parse_args()

        # and do things with arguments
        cfg.log_level = args.log_level
        lgs.set_log_level(cfg.log_level)

    # -----------------------------------------------------------------------

    def _background_initialization(self):
        """Initialize the application and create the main window.

        :return: (wx.Window)

        """
        start_now = datetime.datetime.now()
        # Show the splash window
        splash = sppasSplashScreen(parent=None)
        splash.Show()
        wx.Yield()

        # Do background things??
        splash.Refresh()

        # Wait until the given delay -- update every 1 second
        delta = datetime.datetime.now() - start_now
        remaining = self.settings.splash_delay - delta.seconds
        while remaining > 0:
            time.sleep(0.04)
            splash.Refresh()
            delta = datetime.datetime.now() - start_now
            remaining = self.settings.splash_delay - delta.seconds
        splash.Refresh()
        splash.Close()

    # -----------------------------------------------------------------------

    def run(self):
        """Run the application and starts the main loop.

        A splash screen is displayed while a background initialization is
        doing things, then the main frame is created.

        :returns: (int) Exit status

        """
        status = 0
        try:
            window = sppasMainWindow()
            self.SetTopWindow(window)
            self._background_initialization()
            window.Show(True)
            self.MainLoop()
        except Exception as e:
            # All exception messages of SPPAS are normalized.
            # We assign the error number to the exit status
            msg = str(e)
            status = 1  # generic error status
            if msg.startswith(":ERROR "):
                logging.error(msg)
                try:
                    msg = msg[msg.index(" "):]
                    if ':' in msg:
                        msg = msg[:msg.index(":")]
                        status = int(msg)
                except:
                    pass
            else:
                logging.error(traceback.format_exc())

        return status

    # -----------------------------------------------------------------------
    # Methods provided by the application in order to get an access to some elements
    # -----------------------------------------------------------------------

    @staticmethod
    def get_icon(name, height=None, default="default"):
        """Return the bitmap corresponding to the name of an icon.

        :param name: (str) Name of an icon.
        :param height: (int) Height of the bitmap. Width=height.
        :param default: (str) Default icon if name is missing
        :returns: (wx.Bitmap)

        """
        try:
            img = sppasImagesAccess.get_image(name, default)
            w, h = img.GetSize()
            if w >= 0 and h >= 0 and height is not None:
                img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)
        except:
            img = sppasImagesAccess.get_image(default, default)
            if height is not None:
                img.Rescale(height, height, wx.IMAGE_QUALITY_HIGH)

        return wx.Bitmap(img)

    # -----------------------------------------------------------------------
    # End of the application
    # -----------------------------------------------------------------------

    def OnExit(self):
        """Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)
            - clicks on a custom 'exit' button

        In case of crash or SIGKILL (or bug!) this method is not invoked.

        """
        # Save settings
        self.settings.save()
        # Save current configuration
        cfg.save()

        if self.HasPendingEvents() is True:
            self.DeletePendingEvents()

        # then it will exit normally.
        # Return the exit status 0 = normal.
        return 0
