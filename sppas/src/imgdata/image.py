# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.image.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Image data structure is a numpy array.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

import logging
import os
import cv2
import numpy

from sppas.core.coreutils import sppasIOError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import NegativeValueError

from .coordinates import sppasCoords
from .imgdataexc import ImageReadError
from .imgdataexc import ImageWriteError

# ----------------------------------------------------------------------------


class sppasImage(numpy.ndarray):
    """Manipulate images represented by a numpy.ndarray of BGR colors.

    :Example:
        >>> # explicit constructor to create an image
        >>> img1 = sppasImage(shape=(3,))
        >>> # read the image from a file
        >>> img2 = sppasImage(filename=os.path.join("some image file"))
        >>> # construct from an existing ndarray
        >>> img3 = sppasImage(input_array=img1)
        >>> # construct a blank image
        >>> black = sppasImage(0).blank(w=100, h=100, white=False)

    An image of width=320 and height=200 is represented by len(img)=200;
    each of these 200 rows contains 320 lists of [b,g,r] values.

    Important:
    When the image file is read with the OpenCV function imread(),
    the order of colors is BGR (blue, green, red), and the same with
    imwrite. This class is then using BGR colors in a ndarray.

    It ignores alpha values even if specified in the original image.

    """

    def __new__(cls, shape=0, dtype=numpy.uint8, buffer=None, offset=0,
                strides=None, order=None, input_array=None, filename=None):
        """Return the instance of this class.

        Image is created either with the given input array, or with the
        given filename or with the given shape in order of priority.

        :param shape: (int)
        :param dtype: (type)
        :param buffer: (any)
        :param offset: (int)
        :param strides:
        :param order:
        :param input_array: (numpy.ndarray) Array representing an image
        :param filename: (str) Name of a file to read the image
        :raises: (sppasIOError) if given filename
        :raises: (sppasTypeError) if given input_array
        :raises: (ImageReadError) if given filename

        :Example:
            >>> img1 = sppasImage(shape=(3,), input_array=img, filename="name")
            >>> assert(img1 == img)
            >>> # get image size
            >>> w, h = img1.size()
            >>> # Assigning colors to each pixel
            >>> for i in range(h):
            >>>     for j in range(w):
            >>>         img1[i, j] = [i%256, j%256, (i+j)%256]

        """
        # Priority is given to the given already created array
        if input_array is not None:
            if isinstance(input_array, numpy.ndarray) is False:
                raise sppasTypeError(input_array, "sppasImage, numpy.ndarray")

        else:
            if filename is not None:
                if os.path.exists(filename) is False:
                    raise sppasIOError(filename)

                # imread() decodes the image into a matrix with the color channels
                # stored in the order of Blue, Green, Red and optionally A (Transparency) respectively.
                input_array = cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED)
                if input_array is None:
                    raise ImageReadError(filename)
            else:
                # Create the ndarray instance of our type, given the usual
                # ndarray input arguments. This will call the standard
                # ndarray constructor, but return an object of our type.
                input_array = numpy.ndarray.__new__(cls, shape, dtype, buffer, offset, strides, order)

        # Finally, we must return the newly created object.
        # Return a view of it in order to set it to the right type.
        frame = input_array.view(sppasImage)
        if len(frame.shape) == 2:
            return sppasImage(input_array=cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR))
        return frame

    # -----------------------------------------------------------------------

    @staticmethod
    def _to_image(entry):
        """Return a sppasImage from the given entry.

        :param entry: (numpy.ndarray or filename)
        :return: (sppasImage)

        """
        if isinstance(entry, sppasImage) is True:
            return entry

        if isinstance(entry, numpy.ndarray):
            return sppasImage(input_array=entry)

        return sppasImage(filename=entry)

    # -----------------------------------------------------------------------

    @property
    def width(self):
        """Return the width (int) of the image."""
        w = self.shape[1]
        return w

    # -----------------------------------------------------------------------

    @property
    def height(self):
        """Return the height (int) of the image."""
        h = self.shape[0]
        return h

    # -----------------------------------------------------------------------

    @property
    def channel(self):
        """Return the number of channels (int) of the image."""
        if len(self.shape) > 2:
            _, _, c = self.shape
        else:
            c = 0
        return c

    # -----------------------------------------------------------------------
    
    @property
    def center(self):
        """Return the position tuple(x, y) of the center of the image."""
        (w, h) = self.size()
        return w // 2, h // 2

    # -----------------------------------------------------------------------

    def size(self):
        """Return the size of the image as tuple(width, height)."""
        # grab the dimensions of the image
        (h, w) = self.shape[:2]
        # return in the right order (!)
        return w, h

    # -----------------------------------------------------------------------

    def euclidian_distance(self, other):
        """Return the euclidian distance with the image.

        :param other: (sppasImage) an image with the same shape

        """
        w, h = self.size()
        d = numpy.linalg.norm(self - other, axis=1)
        return sum(sum(d)) / (w * h * 3)

    # ------------------------------------------------------------------------

    def get_proportional_size(self, width=0, height=0):
        """Return the size of the image or a proportional size.

        :param width: (int) Force the image to the width
        :param height: (int) Force the image to the height
        :return: tuple(int, int) Width and height

        """
        if len(self) == 0:
            return 0, 0
        width = sppasCoords.to_dtype(width)
        height = sppasCoords.to_dtype(height)
        if width < 0:
            raise NegativeValueError(width)
        if height < 0:
            raise NegativeValueError(height)

        (h, w) = self.shape[:2]
        if width+height == 0:
            return w, h

        prop_width = prop_height = 0
        propw = proph = 1.
        if width != 0:
            prop_width = width
            propw = float(width) / float(w)
        if height != 0:
            prop_height = height
            proph = float(height) / float(h)
        if width == 0:
            prop_width = int(float(w) * proph)
        if height == 0:
            prop_height = int(float(h) * propw)

        return prop_width, prop_height

    # -----------------------------------------------------------------------

    def surround_coord(self, coord, color, thickness, text=""):
        """Add a square surrounding the given coordinates.

        :param coord: (sppasCoords) Area to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle.
            Negative values, like CV_FILLED , mean that the function has to
            draw a filled rectangle.
        :param text: (str) Add text

        """
        coord = sppasCoords.to_coords(coord)

        cv2.rectangle(self,
                      (coord.x, coord.y),
                      (coord.x + coord.w, coord.y + coord.h),
                      color,
                      thickness)
        if len(text) > 0:
            (h, w) = self.shape[:2]
            font_scale = (float(w * h)) / (1920. * 1080.)
            th = abs(thickness//2)
            text_size = cv2.getTextSize(text, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                        fontScale=font_scale*2, thickness=th)

            if thickness < 0:
                # The background is using our color... change for foreground
                r, g, b = color
                r = (r + 128) % 255
                g = (g + 128) % 255
                b = (b + 128) % 255
                color = (r, g, b)
            cv2.putText(self, text,
                        (coord.x + (3*th), coord.y + (3*th) + text_size[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, color, th)

    # ----------------------------------------------------------------------------

    def put_text(self, coord, color, thickness, text):
        """Put a text at the given coords.

        :param coord: (sppasCoords) Area to put the text
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle.
            Negative values, like CV_FILLED , mean that the function has to
            draw a filled rectangle.
        :param text: (str) Add text

        """
        w, _ = self.size()
        coord = sppasCoords.to_coords(coord)
        font_scale = max(1., float(w) / 1024.)

        if thickness < 0:
            # The background is using our color... change for foreground
            r, g, b = color
            r = (r + 128) % 255
            g = (g + 128) % 255
            b = (b + 128) % 255
            color = (r, g, b)
        cv2.putText(self, text, (coord.x, coord.y), cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness)

    # ----------------------------------------------------------------------------

    def surround_point(self, point, color, thickness, radius=None):
        """Add a circle surrounding the given point.

        :param point: (sppasCoords, list, tuple) (x,y) values to surround
        :param color: (int, int, int) Rectangle color or brightness (if grayscale image).
        :param thickness: (int) Thickness of lines that make up the rectangle.
            Negative values, like CV_FILLED , mean that the function has to
            draw a filled rectangle.
        :param radius: (int) Radius of the circle

        """
        if isinstance(point, sppasCoords) is False:
            if isinstance(point, (tuple, list)) and len(point) >= 2:
                try:
                    point = sppasCoords(point[0], point[1])
                except Exception:
                    pass
        if isinstance(point, sppasCoords) is False:
            sppasTypeError(point, "sppasCoords, tuple, list")

        thickness = max(2, thickness)
        if radius is None:
            radius = thickness // 2

        cv2.circle(self, (point.x, point.y), radius, color, thickness)

    # -----------------------------------------------------------------------
    # Return a copy of the image. Do not change the image itself.
    # -----------------------------------------------------------------------

    def blank_image(self, w=0, h=0, white=False, alpha=None, dtype=numpy.uint8):
        """Create and return an image with black pixels only.

        :param w: (int) Image width. 0 means to use the current image width.
        :param h: (int) Image height. 0 means to use the current height.
        :param white: (bool) Return a white image instead of a black one.
        :param alpha: (int | None) Add alpha channel with the given int value
        :param dtype: (numpy.dtype) Image data type
        :return: (sppasImage) Fully black BGR image

        """
        if w < 0:
            raise NegativeValueError(w)
        if h < 0:
            raise NegativeValueError(h)
        if w == 0:
            w = self.width
        if h == 0:
            h = self.height

        # Creation of array
        t = (h, w, 3)
        nparray = numpy.zeros(t, dtype=dtype)
        if white is True:
            nparray[:, :, (0, 1, 2)] = 255

        img = sppasImage(input_array=nparray)
        if alpha is not None:
            return img.ialpha(alpha)

        return img

    # -----------------------------------------------------------------------

    def ired(self, value=0):
        """Return a copy of the image in red-color.
        
        :param value: (int) Fixed red value ranging (0, 255)
        :return: (sppasImage)
        
        """
        value = int(value)
        value = value % 255
        img = self.copy()
        img[:, :, (0, 1)] = value
        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------
    
    def igreen(self, value=0):
        """Return a copy of the image in green-color.
        
        :param value: (int) Fixed green value ranging (0, 255)
        :return: (sppasImage)
        
        """
        value = int(value)
        value = value % 255
        img_green = self.copy()
        img_green[:, :, (0, 2)] = value
        return sppasImage(input_array=img_green)

    # -----------------------------------------------------------------------

    def iblue(self, value=0):
        """Return a copy of the image in blue-color.
        
        :param value: (int) Fixed blue value ranging (0, 255)
        :return: (sppasImage)
        
        """
        value = int(value)
        value = value % 255
        img = self.copy()
        img[:, :, (1, 2)] = value
        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def ialpha(self, value=0, direction=0):
        """Return a copy of the image in RGBA colors.

        Do nothing if no channel defined.

        :param value: (int) Alpha value for transparency (0-255)
        :param direction: (int) 0 means to assign the value to each pixel, but
        -1 means to only assign the value to pixels if the existing transparency
        is higher than value (lowers are un-changed) and +1 means to assign
        alpha value if the existing one is lower (higher values are unchanged).
        :return: (sppasImage)

        """
        if self.channel == 3:
            imga = sppasImage(input_array=cv2.cvtColor(self, cv2.COLOR_RGB2RGBA))
        else:
            imga = self.copy()

        if imga.channel == 4:
            value = int(value)
            value = value % 255
            if direction == 0:
                imga[:, :, 3] = value
            elif direction < 0:
                numpy.clip(imga[:, :, 3], 0, value, out=imga[:, :, 3])
            else:
                numpy.clip(imga[:, :, 3], value, 255, out=imga[:, :, 3])

        return imga

    # -----------------------------------------------------------------------

    def ibgr(self, bgr):
        """Return a copy of the image with given in BGR/BGRA color values.

        :param bgr: (tuple) A tuple(b, g, r) or tuple(b, g, r, a) color.
        :return: (sppasImage)

        """
        if len(bgr) < 3:
            raise ValueError("Expected a (b, g, r) or (b, g, r, a) color. Got {} instead.".format(bgr))
        img = self.copy()
        # Blue
        value = int(bgr[0])
        value = value % 255
        img[:, :, 0] = value
        # Green
        value = int(bgr[1])
        value = value % 255
        img[:, :, 1] = value
        # Red
        value = int(bgr[2])
        value = value % 255
        img[:, :, 2] = value
        # Alpha
        if len(bgr) == 4:
            return img.ialpha(bgr[3])

        return img

    # -----------------------------------------------------------------------

    def ibgra_to_bgr(self):
        """Return a copy of the image without the alpha channel.

        :return: (sppasImage)

        """
        return sppasImage(input_array=cv2.cvtColor(self, cv2.COLOR_BGRA2BGR))

    # -----------------------------------------------------------------------

    def igray(self):
        """Return a copy of the image in grayscale.

        :return: (sppasImage)

        """
        # The formula is Y = 0.2989 R + 0.5870 G + 0.1140 B
        # Reminder: our image is BGR or BGRA
        if self.channel == 4:
            avg = numpy.average(self, weights=[0.114, 0.587, 0.2989, 1], axis=2)
        elif self.channel == 3:
            avg = numpy.average(self, weights=[0.114, 0.587, 0.2989], axis=2)
        else:
            return self.copy()

        gray = self.copy()
        gray[:, :, 0] = avg
        gray[:, :, 1] = avg
        gray[:, :, 2] = avg

        return sppasImage(input_array=gray)

    # -----------------------------------------------------------------------

    def inegative(self):
        """Return a copy of the image in negative/positive colors.

        :return: (sppasImage)

        """
        img = 255 - self
        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def ireduction(self, value=128):
        """Return a copy of the image with a color-reduction applied.

        :param value: (int) Reduction value in range(0, 255)
        :return: (sppasImage)

        """
        value = int(value)
        if value < 0:
            return self.copy()
        coeff = value % 255
        img = self // coeff * coeff
        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def igamma(self, coeff=1.0):
        """Return a copy of the image with lightness changed.

        :param coeff: (float) Set a value in range (0, 1) to increase
            lightness, or a value > 1 to increase darkness.
        :return: (sppasImage)

        """
        if coeff < 0.:
            coeff = 0.
        img = 255.0 * (self / 255.0) ** coeff
        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def ito_rgb(self):
        """Return a copy of the image representing RGB colors.

        Remove alpha channel if any.

        :raises: TypeError
        :return: (sppasImage) an RGB image

        """
        img = self.copy()
        if self.channel > 2:
            return img[:, :, [2, 1, 0]]

        raise sppasTypeError("image", "BGR/BGRA sppasImage")

    # -----------------------------------------------------------------------

    def ishadow(self, x=5, y=20):
        """Return a copy of image with a shadow added.

        :param x: (int) Shadow width
        :param y: (int) Shadow height
        :return: (sppasImage)

        """
        tmp = self.igray()
        tmp = tmp.ishift(x, y)

        return tmp.ioverlay(self, (0, 0))

    # -----------------------------------------------------------------------
    # Modify size
    # -----------------------------------------------------------------------

    def icrop(self, coord):
        """Return a trimmed part of the image at given coordinates.

        :param coord: (sppasCoords) crop to these x, y, w, h values.
        :return: (sppasImage)

        """
        coord = sppasCoords.to_coords(coord)
        x1 = coord.x
        x2 = coord.x + coord.w
        y1 = coord.y
        y2 = coord.y + coord.h
        cropped = self[y1:y2, x1:x2]

        return sppasImage(input_array=cropped)

    # ------------------------------------------------------------------------

    def itrim(self, coord):
        """Return a cropped part of the image.

        :param coord: (tuple or sppasCoords)
        :return: (sppasImage)

        """
        return self.icrop(coord)

    # ------------------------------------------------------------------------

    def iresize(self, width=0, height=0):
        """Return a copy of the image with the specified width and height.

        :param width: (int) The width to resize to (0=proportional to height)
        :param height: (int) The height to resize to (0=proportional to width)
        :return: (sppasImage)

        """
        if width == 0 and height == 0:
            return self.copy()

        prop_width, prop_height = self.get_proportional_size(width, height)
        if prop_width+prop_height == 0:
            return self.copy()

        # Choose the interpolation method
        dif = self.height if self.height > self.width else self.width
        interpol = cv2.INTER_AREA if dif > (width + height) // 2 else cv2.INTER_CUBIC

        image = cv2.resize(self, (prop_width, prop_height), interpolation=interpol)

        return sppasImage(input_array=image)

    # ------------------------------------------------------------------------

    def izoom(self, width, height):
        """Return a zoomed copy of the image.

        Resize and crop the image to zoom it to the given size.
        Keep the original aspect ratio of the image, but crop if necessary.

        :param width: (int) The width to resize to
        :param height: (int) The height to resize to
        :return: (sppasImage)

        """
        aspect_ratio = int(100. * float(self.width) / float(self.height)) / 100.
        res_aspect_ratio = int(100. * float(width) / float(height)) / 100.

        if aspect_ratio > res_aspect_ratio:
            img_w = int(aspect_ratio * float(height))
            img_h = height
            img = self.iresize(img_w, img_h)
            x1 = int((float(img_w - width)) / 2.)
            x2 = x1 + width
            img = img[:, x1:x2, :]

        elif aspect_ratio < res_aspect_ratio:
            img_w = width
            img_h = int(float(width) / aspect_ratio)
            img = self.iresize(img_w, img_h)
            y1 = int(float(img_h - height) / 2.)
            y2 = y1 + height
            img = img[y1:y2, :, :]

        else:
            # aspect_ratio == res_aspect_ratio:
            img = self.iresize(width, height)

        return sppasImage(input_array=img)

    # ------------------------------------------------------------------------

    def icenter(self, width, height):
        """Return a copy of the image centered in an image of given size.

        Center the image into a blank image of the given size.
        Keep the original aspect ratio of the image, crop if necessary or
        add a black border all around.

        :param width: (int) The width to resize to
        :param height: (int) The height to resize to
        :return: (sppasImage)

        """
        # Crop the image if the expected width/height are smaller
        coord = sppasCoords(0, 0, width, height)
        if self.width > width:
            # the image width must be cropped
            coord.x = (self.width - width) // 2
        if self.height > height:
            # the image width must be cropped
            coord.y = (self.height - height) // 2
        img = self.icrop(coord)

        # Create a blank image of the expected width and height
        if self.channel == 4:
            mask = sppasImage(0).blank_image(width, height, white=False, alpha=0)
        else:
            mask = sppasImage(0).blank_image(width, height)

        # Fix the position of the image into the mask
        x_pos = (width - img.width) // 2
        y_pos = (height - img.height) // 2

        # Replace (BGR) values of the mask by the ones of the image
        mask[y_pos:y_pos + img.height, x_pos:x_pos + img.width, :] = img[:img.height, :img.width, :]

        return sppasImage(input_array=mask)

    # ------------------------------------------------------------------------

    def iextend(self, width, height):
        """Return an extended copy of the image of given size.

        Scale the image to match the given size, keeping aspect ratio.
        Keep the original aspect ratio of the image, add a black border.

        :param width: (int) The width to resize to
        :param height: (int) The height to resize to
        :return: (sppasImage)

        """
        # our image aspect ratio
        aspect_ratio = int(100. * float(self.width) / float(self.height)) / 100.
        # the expected aspect ratio
        res_aspect_ratio = int(100. * float(width) / float(height)) / 100.

        if aspect_ratio == res_aspect_ratio:
            return self.iresize(width, height)
        elif aspect_ratio > res_aspect_ratio:
            coeff = float(width) / float(self.width)
            img = self.iresize(width, int(coeff * float(self.height)))
        else:
            coeff = float(height) / float(self.height)
            img = self.iresize(int(coeff * float(self.width)), height)

        # Add a black border where it's missing
        return img.icenter(width, height)

    # ------------------------------------------------------------------------

    def irotate(self, angle, center=None, scale=1.0, redimension=True):
        """Return a rotated copy of the image with the given angle.

        This method is part of imutils under the terms of the MIT License (MIT)
        Copyright (c) 2015-2016 Adrian Rosebrock, http://www.pyimagesearch.com
        See here for details:
        https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/

        :param angle: (float) Rotation angle in degrees.
        :param center: (int) Center of the rotation in the source image.
        :param scale: (float) Isotropic scale factor.
        :param redimension: (bool) Scale the image to fit in the previous square
        :return: (sppasImage)

        """
        # grab the dimensions of the image and then determine the center
        (h, w) = self.shape[:2]
        if center is None:
            center = (w // 2, h // 2)

        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        matrix = cv2.getRotationMatrix2D(center, -angle, scale)
        if redimension is True:
            cos = numpy.abs(matrix[0, 0])
            sin = numpy.abs(matrix[0, 1])
            # compute the new bounding dimensions of the image
            new_width = int((h * sin) + (w * cos))
            new_height = int((h * cos) + (w * sin))
            # adjust the rotation matrix to take into account translation
            matrix[0, 2] += (new_width // 2) - center[0]
            matrix[1, 2] += (new_height // 2) - center[1]
        else:
            new_width = w
            new_height = h
        # perform the actual rotation and return the image
        rotated = cv2.warpAffine(self, matrix, (new_width, new_height))

        return sppasImage(input_array=rotated)

    # ------------------------------------------------------------------------
    # move content
    # ------------------------------------------------------------------------

    def ishift(self, x, y):
        """Return a shifted copy of the image at given coordinates.

        Shift the content at left/right and/or top/bottom.

        :param x: (int)
        :param y: (int)
        :return: (sppasImage)

        """
        # grab the dimensions of the image
        (h, w) = self.shape[:2]

        # create a translation matrix
        matrix = numpy.float32([
            [1, 0, x],
            [0, 1, y]
        ])
        shifted = cv2.warpAffine(self, matrix, (w, h))

        return sppasImage(input_array=shifted)

    # ------------------------------------------------------------------------

    def iflip(self, flip_code=-1):
        """Return a flipped copy of the image.

        flip_code = 0: flip vertically
        flip_code > 0: flip horizontally
        flip_code < 0: flip vertically and horizontally

        :param flip_code: (int) Indicate the way to flip the image
        :return: (sppasImage)

        """
        if flip_code == 0:
            # Flip up-down
            img = numpy.flipud(self)
        elif flip_code > 0:
            # Flip left-right
            img = numpy.fliplr(self)
        else:
            img = numpy.flip(self, (0, 1))

        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def imask(self, other):
        """Return a copy of the image masked with the other given image.

        :param other: (sppasImage) Image to mask (black areas)
        :return: (sppasImage)

        """
        w, h = self.size()
        other = other.iresize(w, h)
        dst = self * other / 255
        dst.astype(numpy.uint8)

        return sppasImage(input_array=dst)

    # -----------------------------------------------------------------------

    def iblur(self, value=51, method="gaussian"):
        """Return a copy of the image with smoothed borders.

        :param value: (int) Kernel value, from 0 to 51.
        :param method: (str) One of: None, "gaussian" or "median"
        :return: (sppasImage)

        """
        if method is None:
            mask_blur = cv2.blur(self, (value, value))
        elif method.lower() == "median":
            mask_blur = cv2.medianBlur(self, value)
        else:
            mask_blur = cv2.GaussianBlur(self, (value, value), cv2.BORDER_DEFAULT)

        return sppasImage(input_array=mask_blur)

    # -----------------------------------------------------------------------

    def icontours(self, threshold=128, color=(0, 255, 0)):
        """Return a blank image with the contours of the image in color.

        :param threshold: (int) value which is used to classify the pixel values (0-255)
        :param color: (tuple) BGR values of the color to draw the contours
        :return: (sppasImage)

        """
        if self.channel < 2:
            logging.error("Invalid image to draw a contour.")
            return self

        # convert image to grey
        img_grey = cv2.cvtColor(self, cv2.COLOR_BGR2GRAY)

        # get threshold image
        _, thresh_img = cv2.threshold(img_grey, threshold, 255, cv2.THRESH_BINARY)

        # find contours
        contours, _ = cv2.findContours(thresh_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # create an empty image for contours
        img_contours = numpy.zeros(self.shape)
        # draw the contours on the empty image
        cv2.drawContours(img_contours, contours, -1, color, 3)

        return sppasImage(input_array=img_contours)

    # -----------------------------------------------------------------------
    # Tag the image at coords
    # -----------------------------------------------------------------------

    def ipaste(self, other, coord):
        """Return a copy of the image with other paste on it at given coords.

        Replace the current image with the given one at given coords.

        :param other: (sppasImage) Image to paste
        :param coord: (sppasCoords) Position and optionally size to paste
        :return: (sppasImage)

        """
        img = self.copy()
        other = sppasImage(input_array=other)
        coord = sppasCoords.to_coords(coord)

        if other.channel != self.channel:
            if other.channel == 3 and self.channel == 4:
                # Add alpha channel to other
                other = other.ialpha(0)
            if other.channel == 4 and self.channel == 3:
                # Add alpha channel to the self-copied image
                img = self.ialpha(0)

        # Create the image to paste -- resize
        if coord.w > 0 and coord.h > 0:
            paste_img = other.iresize(coord.w, coord.h)
        else:
            paste_img = other
            w, h = other.size()
            coord.w = w
            coord.h = h

        # Create the image to paste -- crop to the appropriate size
        w, h = self.size()
        to_crop = False
        if coord.x + coord.w > w:
            new_w = w - coord.x
            coord.w = new_w
            to_crop = True
        if coord.y + coord.h > h:
            new_h = h - coord.y
            to_crop = True
            coord.h = new_h
        if to_crop is True:
            paste_img = paste_img.icrop((0, 0, coord.w, coord.h))

        # Paste into a copied image
        x1 = coord.x
        x2 = coord.x + coord.w
        y1 = coord.y
        y2 = coord.y + coord.h
        img[y1:y2, x1:x2] = paste_img

        return img

    # -----------------------------------------------------------------------

    def iblend(self, other, coord=None, weight1=0.5, weight2=0.5):
        """Return a copy of the image with the other image added or blended.

        :param other: (sppasImage) Image to blend with
        :param coord: (sppasCoord) Blend only the given area of self with other
        :param weight1: (float) coeff on the image
        :param weight2: (float) coeff on the other image
        :return: (sppasImage)

        """
        w, h = self.size()
        img = self.copy()

        if coord is None:
            other = other.iresize(w, h)
        else:
            blank = sppasImage(0).blank_image(w, h, white=False, alpha=0)
            if other.channel == 3:
                other = other.ialpha(254)
            other = blank.ipaste(other, coord)
            if self.channel == 3:
                img = self.ialpha(254)

        blended = cv2.addWeighted(img, weight1, other, weight2, 0)
        return sppasImage(input_array=blended)

    # -----------------------------------------------------------------------

    def ioverlay(self, other, coord):
        """Return a copy of the image with the other image added.

        :param other: (sppasImage) Image to blend with
        :param coord: (sppasCoord) Overlay in the given area of self with other
        :return: (sppasImage)

        """
        back_image = self.copy()
        w, h = self.size()
        over_image = sppasImage(input_array=other)
        coord = sppasCoords.to_coords(coord)

        if over_image.channel == 3:
            # Add alpha channel to other
            over_image = over_image.ialpha(254)
        if back_image.channel == 3:
            # Add alpha channel to the self-copied image
            back_image = self.ialpha(254)

        # Resize the over image to the appropriate size
        if coord.w > 0 and coord.h > 0:
            over_image = over_image.iresize(coord.w, coord.h)
        cols, rows = over_image.shape[:2]
        x = coord.x
        y = coord.y
        # Change the values if the other image goes out of the back image
        if x + rows > w:
            rows = w - x
        if y + cols > h:
            cols = h - y

        # create an over image with the same size of the back one
        tmp = sppasImage(0).blank_image(w, h, white=False, alpha=254)
        over_image = tmp.ipaste(over_image, (x, y))

        # normalize alpha channels from 0-255 to 0-1
        alpha_background = back_image[:, :, 3] / 255.0
        alpha_foreground = over_image[:, :, 3] / 255.0

        # set adjusted colors
        roi_over = back_image.copy()
        for color in range(0, 3):
            roi_over[:, :, color] = alpha_foreground * over_image[:, :, color] + \
                               alpha_background * roi_over[:, :, color] * (1 - alpha_foreground)

        # set adjusted alpha and denormalize back to 0-255
        roi_over[:, :, 3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255

        # make the ROI in black into the background
        if rows > 0 and cols > 0:
            black = sppasImage(0).blank_image(rows, cols, white=False, alpha=254)
            back_image = back_image.ipaste(black, (x, y))
        # else:
        #    logging.warning("Invalid rows = {}, cols = {}".format(rows, cols))

        combined = cv2.add(back_image, roi_over)
        return sppasImage(input_array=combined)

    # -----------------------------------------------------------------------

    def isurround(self, coords, color=(50, 100, 200), thickness=2, score=False):
        """Return a new image with a square surrounding all the given coords.

        :param coords: (List of sppasCoords) Areas to surround
        :param color: (int, int, int) Rectangle color
        :param thickness: (int) Thickness of lines that make up the rectangle.
            Negative values, like CV_FILLED , mean that the function has to
            draw a filled rectangle.
        :param score: (bool) Add the confidence score of the coords
        :return: (sppasImage)

        """
        img = self.copy()
        for c in coords:
            c = sppasCoords.to_coords(c)
            if c.w > 0 and c.h > 0:
                # Draw the square and eventually the confidence inside the square
                text = ""
                if score is True and c.get_confidence() > 0.:
                    text = "{:.3f}".format(c.get_confidence())
                img.surround_coord(c, color, thickness, text)
            else:
                img.surround_point(c, color, thickness)

        return img

    # -----------------------------------------------------------------------
    # Tag the image in a range of coords
    # -----------------------------------------------------------------------

    def icartoon(self, colorize=True):
        """Applied a filter on the image to create a cartoon effect.

        :param colorize: (bool) If we want our image in only black and
            white (False) or with colors (True).
        :return: (sppasImage) The image with the filter applied on it

        """
        alpha_image = None

        if self.channel == 4:
            # normalize alpha channels from 0-255 to 0-1
            alpha_image = self[:, :, 3] / 255.0
            # get the image without the alpha channel
            img = self.ibgra_to_bgr()
        else:
            img = self.copy()

        # Apply some Median blur on the image
        img_blur = cv2.medianBlur(img, 5)
        # Apply a bilateral filter on the image
        # d – Diameter of each pixel neighborhood that is used during filtering.
        # sigmaColor – Filter sigma in the color space. A larger value of the
        #   parameter means that farther colors within the pixel neighborhood
        #   will be mixed together, resulting in larger areas of semi-equal color.
        # sigmaSpace – Filter sigma in the coordinate space. A larger value of
        #   the parameter means that farther pixels will influence each other as
        #   long as their colors are close enough.
        # img_bf = cv2.bilateralFilter(img_blur, d=5, sigmaColor=80, sigmaSpace=80)
        img_bf = cv2.bilateralFilter(img_blur, d=3, sigmaColor=50, sigmaSpace=50)

        # Use the laplace filter to detect edges.
        # For each of the Laplacian filters we use a kernel size of 5.
        # 7 => Too many edges; 3 => not enough edges
        # 'CV_8U' means that we are using 8 bit values (0–255).
        img_lp_al = cv2.Laplacian(img_bf, cv2.CV_8U, ksize=5)

        # Laplacian of the original image detected a lot of noise.
        # The image with all the filters is the sharpest, which comes in handy in
        # a bit. This is however not yet what we want. We need an image preferably
        # black and white that we can use as a mask.
        # Convert the image to greyscale (1D)
        img_lp_al_grey = cv2.cvtColor(img_lp_al, cv2.COLOR_BGR2GRAY)

        # Each variable now contains a 1-dimensional array instead of a 3-dimensional
        # array. Next we are going to use image thresholding to set values that are
        # near black to black and set values that are near white to white.
        # Manual image thresholding
        # _, tresh_al = cv2.threshold(img_lp_al_grey, 127, 255, cv2.THRESH_BINARY)
        # Remove some additional noise
        blur_al = cv2.GaussianBlur(img_lp_al_grey, (5, 5), 0)
        # Apply a threshold (Otsu)
        _, tresh_al = cv2.threshold(blur_al, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # We now have a black image with white edges, we only have to invert the black
        # and the white for our mask.
        # Invert the black and the white
        inverted_bilateral = cv2.subtract(255, tresh_al)

        if colorize is True:
            # Turn colors of the image into cartoon style
            img_color = cv2.bilateralFilter(img, d=8, sigmaColor=250, sigmaSpace=250)
            img_color = sppasImage(input_array=cv2.bitwise_and(img_color, img_color, mask=inverted_bilateral))

            if alpha_image is not None:
                # create alpha channel and restore original image alpha
                img_color = img_color.ialpha(254)
                img_color[:, :, 3] = alpha_image * 255

            return img_color

        if alpha_image is not None:
            # create alpha channel and restore original image alpha
            img = sppasImage(input_array=inverted_bilateral).ialpha(254)
            img[:, :, 3] = alpha_image * 255

            return img

        else:
            return sppasImage(input_array=inverted_bilateral)

    # ---------------------------------------------------------------------------

    def iquantization_color(self, nb_down_samp=2):
        """Smooth colors, down-sample and Up-sample the original image colors.

        :param nb_down_samp: (int) number of downscaling steps

        :return: (sppasImage) The image with the filter applied on it

        """
        img_color = self.copy()

        # downsample image using Gaussian pyramid
        for _ in range(nb_down_samp):
            img_color = cv2.pyrDown(img_color)

        # repeatedly apply small bilateral filter instead of applying one large filter
        for _ in range(50):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)

        # upsample image to original size
        for _ in range(nb_down_samp):
            img_color = cv2.pyrUp(img_color)

        return sppasImage(input_array=img_color)

    # ---------------------------------------------------------------------------

    def iinvert(self):
        """Applied an invert filter on the image.

        :return: (sppasImage) The image with the filter applied on it

        """
        # code for transparent image (cued speech hands) but invert filter on hands image doesn't work :(
        """
        alpha_image = None

        # image doesn't have an alpha channel
        if self.channel == 3:
            img = self.copy()
        else:
            # normalize alpha channels from 0-255 to 0-1
            alpha_image = self[:, :, 3] / 255.0
            # get the image without the alpha channel
            img = self.ibgra_to_bgr()

        # apply the invert filter
        invert_array = cv2.bitwise_not(img)

        if alpha_image is not None:
            # create alpha channel and restore original image alpha
            img = sppasImage(input_array=invert_array).ialpha(254)
            img[:, :, 3] = alpha_image * 255
        
        return img
        """
        invert_array = cv2.bitwise_not(self.copy())
        return sppasImage(input_array=invert_array)

    # ----------------------------------------------------------------------------

    def ioverlay_color(self, color_overlay, intensity=0.2):
        """Applied an overlay with a specified color on the image.

        :param color_overlay: (tuple[int, int, int]) The color of the overlay on the rgb format
        :param intensity: (float) The intensity

        :return: (sppasImage) The image with the filter applied on it

        """
        # initialize variables
        image = cv2.cvtColor(self.copy(), cv2.COLOR_BGR2BGRA)
        image_height, image_width, _ = image.shape

        # reverse color to transform rgb to bgr and add alpha value
        color_bgra = color_overlay[::-1] + (1,)

        # create and applied the overlay
        overlay = numpy.full((image_height, image_width, 4), color_bgra, dtype="uint8")
        cv2.addWeighted(overlay, intensity, image, 1.0, 0, image)
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        return sppasImage(input_array=image)

    # ----------------------------------------------------------------------------

    def iuint8(self):
        """Return a copy of the image with dtype=numpy.uint8."""
        img = self / self.max()
        img = 255 * img
        return img.astype(numpy.uint8)

    # -----------------------------------------------------------------------
    # Save image on disk
    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write the image on disk.

        :param filename: (str) Name of the image file
        :raises: (ImageWriteError)

        """
        try:
            cv2.imwrite(filename, self)
        except cv2.error as e:
            logging.error("Error when writing file {}: {}"
                          "".format(filename, str(e)))
            raise ImageWriteError(filename)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Allows to write img1 == img2."""
        if len(self) != len(other):
            return False
        for l1, l2 in zip(self, other):
            if len(l1) != len(l2):
                return False
            # the color of the pixel
            for c1, c2 in zip(l1, l2):
                if len(c1) != len(c2):
                    return False
                r1, g1, b1 = c1
                r2, g2, b2 = c2
                if r1 != r2 or g1 != g2 or b1 != b2:
                    return False
        return True

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        """Allows to write img1 != img2."""
        return not self.__eq__(other)
