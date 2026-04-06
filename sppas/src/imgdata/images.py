# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.images.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Extended image data structure.

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

from sppas.src.calculus.geometry.linear_fct import slope_intercept
from sppas.src.calculus.geometry.linear_fct import linear_fct

from .image import sppasImage
from .coordinates import sppasCoords

# ----------------------------------------------------------------------------


class sppasExtendedImage(sppasImage):
    """Manipulate images represented by a numpy.ndarray of BGR colors.

    Extend sppasImage with methods returning a sequence of images.

    """

    def __new__(cls, *args, **kwargs):
        img = sppasImage(*args, **kwargs)
        return img.view(sppasExtendedImage)

    # -----------------------------------------------------------------------

    def ioverlays(self, other, coord1, coord2, nb_img=0, blur=False):
        """Return a list of the image with other overlaid between coords.

        :param other: (sppasImage) Image to overlay
        :param coord1: (sppasCoords) Position and optionally size to overlay - src
        :param coord2: (sppasCoords) Position and optionally size to overlay - dest
        :param nb_img: (int) Total number of images
        :param blur: (bool)
        :return: (list of sppasImage)

        """
        images = list()
        coord1 = sppasCoords.to_coords(coord1)
        coord2 = sppasCoords.to_coords(coord2)

        # Add the image with other pasted at coord1
        images.append(self.ioverlay(other, coord1))

        # Add nb intermediate images
        if nb_img > 2:
            a, b = slope_intercept((coord1.x, coord1.y), (coord2.x, coord2.y))
            step_x = (coord2.x - coord1.x) / float(nb_img + 1)
            step_y = (coord2.y - coord1.y) / float(nb_img + 1)
            step_w = (coord2.w - coord1.w) / float(nb_img)
            step_h = (coord2.h - coord1.h) / float(nb_img)
            prev_c = coord1
            if blur is True:
                blur_other = other.iblur()
                tr_other = blur_other.ialpha(196, direction=-1)
            for i in range(1, nb_img+1):
                pimg = self.copy()
                # coords where to put other in self
                x = max(0, coord1.x + int(step_x * i))
                if coord1.x != coord2.x:
                    y = int(linear_fct(x, a, b))
                else:
                    y = max(0, coord1.y + int(step_y * i))
                w = max(0, coord1.w + int(step_w * i))
                h = max(0, coord1.h + int(step_h * i))
                c = sppasCoords(x, y, w, h)

                # put 3 times other in transparent from prev to cur
                if blur is True and prev_c.x != c.x and prev_c.y != c.y:
                    tr_step_x = (c.x - prev_c.x) // 3
                    tr_step_y = (c.y - prev_c.y) // 3
                    pimg = self.ioverlay(tr_other, (prev_c.x + tr_step_x, prev_c.y + tr_step_y, prev_c.w, prev_c.h))
                    pimg = pimg.ioverlay(tr_other, (prev_c.x + 2*tr_step_x, prev_c.y + 2*tr_step_y, prev_c.w, prev_c.h))
                    pimg = pimg.ioverlay(tr_other, (prev_c.x + 3*tr_step_x, prev_c.y + 3*tr_step_y, prev_c.w, prev_c.h))

                # put other
                pimg = pimg.ioverlay(other, c)
                images.append(pimg)
                prev_c = c

        # Add the image with other pasted at coord2
        images.append(self.ioverlay(other, coord2))

        return images

    # -----------------------------------------------------------------------

    def irotates(self, angle1, angle2, center=None, scale=1.0, nb_img=0):
        """Return a list of the image rotated ranging the given angles.

        :param angle1: (float) Angle start
        :param angle2: (float) Angle end
        :param center: (tuple) (x,y) position of the rotating center
        :param scale: (float) Scale value
        :param nb_img: (int) Total number of images
        :return: (list of sppasImage)

        """
        images = list()

        # Add the image rotated with angle1 and not scaled
        images.append(self.irotate(angle1, center, scale=1.0))

        # Add nb intermediate images
        if nb_img > 2:
            # if scale is 1, no step scale.
            if 0.99 < scale < 1.01:
                step_scale = 0.
            else:
                step_scale = (scale-1.0) / float(nb_img + 1)

            step_angle = (angle2 - angle1) / float(nb_img + 1)
            for i in range(1, nb_img+1):
                s = 1.0 + (i*step_scale)
                a = angle1 + (i*step_angle)
                pimg = self.irotate(a, center, s)
                images.append(pimg)

        # Add the image rotated with angle2 and scaled
        images.append(self.irotate(angle2, center, scale))

        return images

    # -----------------------------------------------------------------------

    def iscales(self, scale=1.0, nb_img=0):
        """Return a list of the image scaled ranging from 1 to the value.

        :param scale: (float) Scale value
        :param nb_img: (int) Total number of images
        :return: (list of sppasImage)

        """
        return self.irotates(0, 0, None, scale, nb_img)

    # -----------------------------------------------------------------------

    def ifade_in(self, nb_img=0, color=(255, 255, 255)):
        """Fade in the image in nb times from the given color.

        :param nb_img: (int) Total number of images of the sequence
        :param color: BGR of the color
        :return: (list of sppasImage)

        """
        images = list()
        img = self.__back.ialpha(value=0, direction=-1)
        w, h = img.size()
        colored_img = sppasImage(0).blank_image(w, h, white=False, alpha=0)
        colored_img = colored_img.iblue(color[0])
        colored_img = colored_img.igreen(color[1])
        colored_img = colored_img.ired(color[2])

        for i in range(nb_img):
            alpha_color = colored_img.ialpha(i * (255//nb_img))
            trimg = img.ioverlay(alpha_color, (0, 0, w, h))
            images.append(trimg)

        return images
