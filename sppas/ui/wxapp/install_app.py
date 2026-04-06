# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.main_app.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  This is the application for SPPAS, based on the Phoenix API.

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

This is an application to install external optionnal programs or packages.
Create and run the application with:

>>> app = sppasInstallApp()
>>> app.run()

"""

import wx
import logging

from sppas.core.config import sg
from sppas.core.config import cfg
from sppas.core.config import lgs
from sppas.core.coreutils import sppasLogFile

from .main_settings import WxAppSettings
from .install_window import sppasInstallWindow
from .imgtools import sppasImagesAccess

# ---------------------------------------------------------------------------


class sppasInstallApp(wx.App):
    """Create the installer application.

    """

    def __init__(self):
        """Wx Application initialization.

        Create the application for the GUI Install of SPPAS dependencies.

        """
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=False,
                        clearSigInt=True)

        self.SetAppName(sg.__name__)
        self.SetAppDisplayName(sg.__name__ + " " + sg.__version__)
        wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
        wx.SystemOptions.SetOption("mac.listctrl.always_use_generic", 1)
        wx.SystemOptions.SetOption("msw.font.no-proof-quality", 0)

        # Fix logging & settings
        log_report = sppasLogFile(pattern="install_ui")
        lgs.file_handler(log_report.get_filename())
        self.settings = WxAppSettings()

        # This catches events when the app is asked to activate
        # by some other process
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    # -----------------------------------------------------------------------

    def InitLocale(self):
        """Override. Do not re-initialize the locale to 'C'.

        """
        # we create an un-used instance of wx.Locale()
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
    # Public methods
    # -----------------------------------------------------------------------

    def run(self):
        """Run the application and starts the main loop.

        :returns: (int) Exit status

        """
        status = 0
        try:
            # Create the main frame of the application and show it.
            window = sppasInstallWindow()
            self.SetTopWindow(window)
            self.MainLoop()
        except Exception as e:
            # All exception messages of SPPAS are normalized.
            # We assign the error number at the exit status
            msg = str(e)
            status = 1  # generic error status
            if msg.startswith(":ERROR "):
                logging.error(msg)
                try:
                    msg = msg[msg.index(" "):]
                    if ':' in msg:
                        msg = msg[:msg.index(":")]
                        status = int(msg)
                except Exception as e:
                    logging.error(str(e))
                    pass
            else:
                logging.error(str(e))

        return status

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)
            - click on a custom 'exit' button

        In case of crash or SIGKILL (or bug!) this method is not invoked.

        """
        if self.HasPendingEvents() is True:
            self.DeletePendingEvents()

        # Save settings
        self.settings.save()
        # Save current configuration
        cfg.save()

        # then it will exit. Return the exit status.
        return 0
