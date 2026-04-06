# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.image.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Easier access to wx images for the application.

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

# ---------------------------------------------------------------------------


def ColorizeImage(img, current, colour):
    """Set new foreground to an image.

    :param img: (wx.Image)
    :param current: (wx.Colour) Current color
    :param colour: (wx.Colour) New colour

    """
    r = current.Red()
    g = current.Green()
    b = current.Blue()
    rr = colour.Red()
    gg = colour.Green()
    bb = colour.Blue()

    for i in range(0, 10):
        img.Replace(max(r - i, 0),
                    max(g - i, 0),
                    max(b - i, 0),
                    max(rr - i, 0),
                    max(gg - i, 0),
                    max(bb - i, 0))
        img.Replace(min(r + i, 255),
                    min(g + i, 255),
                    min(b + i, 255),
                    min(rr + i, 255),
                    min(gg + i, 255),
                    min(bb + i, 255))

# ---------------------------------------------------------------------------


class sppasStaticBitmap(wx.StaticBitmap):

    def __init__(self, parent, bmp_name, height=None):

        if height is None:
            height = int(parent.GetSize()[1]) - 2
        bmp = wx.GetApp().get_icon(bmp_name, height)

        super(sppasStaticBitmap, self).__init__(
            parent=parent,
            id=wx.ID_ANY,
            bitmap=bmp,
            name=bmp_name
        )

    # -----------------------------------------------------------------------

    def SetForegroundColour(self, colour):
        """Override. Apply fg colour to the image.

        :param colour: (wx.Colour)

        """
        try:
            bmp = self.GetBitmap()
            img = bmp.ConvertToImage()
            current = self.GetForegroundColour()
            ColorizeImage(img, current, colour)
            self.SetBitmap(wx.Bitmap(img))
        except:
            wx.LogDebug('SetForegroundColour not applied to image'
                        'for button {:s}'.format(self.GetName()))

        wx.StaticBitmap.SetForegroundColour(self, colour)
