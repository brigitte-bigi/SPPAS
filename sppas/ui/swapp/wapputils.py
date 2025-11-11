"""
:filename: sppas.ui.swapp.wapputils.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Utilities for SPPAS Web-based applications.

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

    Copyright (C) 2011-2023 Brigitte Bigi
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
import logging

from .wappsg import wapp_settings

# ---------------------------------------------------------------------------


class sppasImagesAccess:
    """Provide some access to image and icons of SPPAS web-based apps.

    ... because the path to icons is different depending on the theme.

    Notice that os.path.join() is not used; "/" is used instead, because it
    is relevant in this situation (HTTPD protocol).

    """

    @staticmethod
    def get_image_filename(name, default="default"):
        """Return the filename matching the given name or the default.

        :param name: (str) Name of an image or an icon.
        :param default: (str) Default icon if name is missing.

        """
        # Given "name" is already a filename
        if os.path.exists(name):
            img_name = name
        else:
            img_path = wapp_settings.images
            # search in the images file names
            img_name = img_path + "/" + name + ".png"

            if os.path.exists(img_name) is False:
                # fix the image file name with the current icon's theme
                img_name = sppasImagesAccess.get_icon_filename(name, default)

        return img_name

    # ------------------------------------------------------------------------

    @staticmethod
    def get_icon_filename(name, default="default"):
        """Return the icon filename matching the given name or the default.

        :param name: (str) Name of an icon.
        :param default: (str) Default icon if name is missing.
        :return: (str|None) The icon filename or None.

        """
        default_theme = wapp_settings.default_icons_theme()
        icon_path = wapp_settings.icons

        icon_name = icon_path + "/" + wapp_settings.icons_theme + "/" + name + ".png"

        # instead, find the icon in the default set
        if os.path.exists(icon_name) is False:
            icon_name = icon_path + "/" + default_theme + "/" + name + ".png"

        # instead, use the given default icon
        if os.path.exists(icon_name) is False:
            logging.warning("Missing icon {:s} in the SPPAS Package.".format(icon_name))
            icon_name = icon_path + "/" + default_theme + "/" + default + ".png"

        # instead, use the default icon
        if os.path.exists(icon_name) is False:
            icon_name = icon_path + "/" + default_theme + "/default.png"

        if os.path.exists(icon_name) is False:
            logging.error("Missing default icon in the SPPAS Package.")
            icon_name = None

        return icon_name
