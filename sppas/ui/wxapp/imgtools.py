# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.imgtools.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Get access to all images of the SPPAS package.

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

"""

import os
import wx

from sppas.core.config import paths

# -----------------------------------------------------------------------


class sppasImagesAccess:
    """Provide some access to image and icons of the package of SPPAS.

    """

    @staticmethod
    def get_image(name, default="default"):
        """Return the image corresponding to the name of an image or icon.

        :param name: (str) Name of an image or an icon.
        :param default: (str) Default icon if name is missing.
        :returns: (wx.Image)

        """
        img_name = sppasImagesAccess.get_image_filename(name, default)
        return wx.Image(img_name, wx.BITMAP_TYPE_ANY)

    # ------------------------------------------------------------------------

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
            # search in the images file names
            img_name = os.path.join(paths.images, name + ".png")
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

        """
        th = wx.GetApp().settings.icons_theme
        default_theme = wx.GetApp().settings.GetDefaultIconsTheme()

        # fix the icon file name with the current theme
        icon_name = os.path.join(paths.icons, th, name + ".png")

        # instead, find the icon in the default set
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(paths.icons, default_theme, name + ".png")

        # instead, use the given default icon
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(paths.icons, default_theme, default + ".png")

        # instead, use the default icon
        if os.path.exists(icon_name) is False:
            icon_name = os.path.join(paths.icons, default_theme, "default.png")

        if os.path.exists(icon_name) is False:
            raise OSError("SPPAS Package corrupted: Missing default image {:s}."
                          "".format(icon_name))

        return icon_name

    # ------------------------------------------------------------------------

    @staticmethod
    def rescale_image(img, height):
        """Rescale proportionally an image.

        :return: (int) width or -1 if failed.

        """
        w, h = img.GetSize()
        if w <= 0 or h <= 0:
            return -1
        proportion = float(height) / float(img.GetHeight())
        w = int(float(img.GetWidth()) * proportion)
        img.Rescale(w, height, wx.IMAGE_QUALITY_HIGH)
        return w

    # ------------------------------------------------------------------------

    @staticmethod
    def get_bmp_image(name, height=None):
        """Return the bitmap corresponding to the name of an image.

        :param name: (str) Name of an image or an icon.
        :param height: (int) Height of the bitmap, Width is proportional.
        :returns: (wx.Bitmap)

        """
        img = sppasImagesAccess.get_image(name)
        if height is not None:
            sppasImagesAccess.rescale_image(img, height)

        return wx.Bitmap(img)
