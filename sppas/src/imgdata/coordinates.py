# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.coordinates.py
:author: Brigitte Bigi
:contributor: Florian Hocquet
:contact: contact@sppas.org
:summary: Data structure to represent an area with a confidence score.

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

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

from __future__ import annotations
import logging

from sppas.core.coreutils import (sppasTypeError)
from sppas.core.coreutils import IntervalRangeException
from sppas.src.calculus.geometry.distances import euclidian

from .imgdataexc import ImageEastingError
from .imgdataexc import ImageNorthingError
from .imgdataexc import ImageWidthError
from .imgdataexc import ImageHeightError

# ---------------------------------------------------------------------------


class sppasCoords:
    """Represents the coordinates of an area in an image.

    It has 5 parameters:

    - x: coordinate on the x-axis
    - y: coordinate on the y-axis
    - w: width of the visage
    - h: height of the visage
    - an optional confidence score

    :Example:

    >>> c = sppasCoords(143, 17, 150, 98, 0.7)
    >>> c.get_confidence()
    >>> 0.7
    >>> c.get_x()
    >>> 143
    >>> c.get_y()
    >>> 17
    >>> c.get_w()
    >>> 150
    >>> c.get_h()
    >>> 98

    """

    MAX_W = 30720
    MAX_H = 30720

    # -----------------------------------------------------------------------

    def __init__(self, x=0, y=0, w=0, h=0, confidence=None, unsigned=True):
        """Create a new sppasCoords instance.

        Allows to represent a point (x,y), or a size(w,h) or both, with an
        optional confidence score ranging [0.0,1.0].
        When unsigned is True, the (x,y) coordinates are positive values only.

        :param x: (int) The x-axis value
        :param y: (int) The y-axis value
        :param w: (int) The width value
        :param h: (int) The height value
        :param confidence: (float) An optional confidence score ranging [0,1]
        :param unsigned: (bool) Whether the coordinates are unsigned or not.

        """
        self.__unsigned = bool(unsigned)

        self.__x = 0
        self.__set_x(x)

        self.__y = 0
        self.__set_y(y)

        self.__w = 0
        self.__set_w(w)

        self.__h = 0
        self.__set_h(h)

        # Save memory by using None instead of float if confidence is not set
        self.__confidence = None
        self.set_confidence(confidence)

    # -----------------------------------------------------------------------

    @staticmethod
    def to_dtype(value, dtype=int, unsigned: bool = True):
        """Convert a value to int or raise the appropriate exception.

        """
        try:
            v = dtype(value)
            if dtype is int:
                value = int(round(value))
            else:
                value = v
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        if unsigned is True:
            if value < 0:
                raise sppasTypeError(value, "unsigned " + str(dtype))

        return value

    # -----------------------------------------------------------------------

    @staticmethod
    def to_coords(coord) -> sppasCoords:
        """Check the given coord and return it as a sppasCoords instance.

        :param coord: (list or tuple) The coordinates to convert.
        :return: (sppasCoords) The converted coordinates.

        """
        if isinstance(coord, sppasCoords) is False:
            if isinstance(coord, (tuple, list)) is True:
                if len(coord) == 2:
                    try:
                        # Given coordinates are representing a point
                        coord = sppasCoords(coord[0], coord[1], w=0, h=0)
                    except:
                        pass
                elif len(coord) == 3:
                    try:
                        # Given coordinates are representing a point with a score
                        coord = sppasCoords(coord[0], coord[1], 0, 0, coord[2])
                    except:
                        pass
                elif len(coord) == 4:
                    try:
                        # Given coordinates are representing an area (point+size)
                        coord = sppasCoords(coord[0], coord[1], coord[2], coord[3])
                    except:
                        pass
                elif len(coord) > 4:
                    try:
                        # Given coordinates are representing an area (point+size)
                        # with a confidence score
                        coord = sppasCoords(coord[0], coord[1], coord[2], coord[3], coord[4])
                    except:
                        pass

        if isinstance(coord, sppasCoords) is False:
            raise sppasTypeError(coord, "sppasCoords")

        return coord

    # -----------------------------------------------------------------------
    # Getters & Setters
    # -----------------------------------------------------------------------

    def get_confidence(self) -> float:
        """Return the confidence value (float)."""
        if self.__confidence is None:
            return 0.
        return self.__confidence

    # -----------------------------------------------------------------------

    def set_confidence(self, value) -> None:
        """Set confidence value.

        :param value: (float) The new confidence value ranging [0, 1].
        :raises: TypeError:
        :raises: ValueError:

        """
        if value is None:
            self.__confidence = None
        else:
            value = self.to_dtype(value, dtype=float, unsigned=False)
            if value < 0. or value > 1.:
                raise IntervalRangeException(value, 0, 1)
            self.__confidence = value

    # -----------------------------------------------------------------------

    def get_unsigned(self) -> bool:
        """Return whether the coordinates are unsigned or not."""
        return self.__unsigned

    # -----------------------------------------------------------------------

    def get_x(self) -> int:
        """Return x-axis value (int)."""
        return self.__x

    # -----------------------------------------------------------------------

    def __set_x(self, value):
        """Set x-axis value.

        :param value: (int) The new x-axis value.
        :raises: TypeError:
        :raises: ValueError:

        """
        value = self.to_dtype(value, unsigned=self.__unsigned)
        if value > sppasCoords.MAX_W:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_W)
        self.__x = value

    # -----------------------------------------------------------------------

    def get_y(self):
        """Return y-axis value (int)."""
        return self.__y

    # -----------------------------------------------------------------------

    def __set_y(self, value):
        """Set y-axis value.

        :param value: (int) The new y-axis value.
        :raises: TypeError:
        :raises: ValueError:

        """
        value = self.to_dtype(value, unsigned=self.__unsigned)
        if value > sppasCoords.MAX_H:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_H)
        self.__y = value

    # -----------------------------------------------------------------------

    def get_w(self) -> int:
        """Return width value (int)."""
        return self.__w

    # -----------------------------------------------------------------------

    def __set_w(self, value: int):
        """Set width value.

        :param value: (int) The new width value.
        :raises: TypeError:
        :raises: ValueError:

        """
        value = self.to_dtype(value)
        if value > sppasCoords.MAX_W:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_W)
        self.__w = value

    # -----------------------------------------------------------------------

    def get_h(self) -> int:
        """Return height value (int)."""
        return self.__h

    # -----------------------------------------------------------------------

    def __set_h(self, value):
        """Set height value.

        :param value: (int) The new height value.
        :raises: TypeError:
        :raises: ValueError:

        """
        value = self.to_dtype(value)
        if value > sppasCoords.MAX_H:
            raise IntervalRangeException(value, 0, sppasCoords.MAX_H)
        self.__h = value

    # -----------------------------------------------------------------------

    def area(self) -> int:
        """Return the area of the rectangle."""
        return self.__w * self.__h

    # -----------------------------------------------------------------------

    def copy(self) -> sppasCoords:
        """Return a deep copy of the current sppasCoords."""
        return sppasCoords(self.__x, self.__y, self.__w, self.__h,
                           self.__confidence)

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------

    x = property(get_x, __set_x)
    y = property(get_y, __set_y)
    w = property(get_w, __set_w)
    h = property(get_h, __set_h)

    # -----------------------------------------------------------------------
    # Utility Methods to manipulate coordinates
    # -----------------------------------------------------------------------

    def portrait(self, image=None, scale=(2.6, 3.0), xy_ratio=0.875):
        """Return a copy of the coordinates converted to the portrait scale.

        A xy ratio can be forced, for example, to force a 4:5 image, ie
        proprtionnal to width=4 and height=5, set xy_ratio to 0.8.

        :param image: (sppasImage) The original image.
        :param scale: (float or tuple) Scale factor.
        :param xy_ratio: (float or None) Force a xy ratio. Default is 14:16.
        :return: (sppasCoords)

        >>> # Scale the coords to fit a default portrait size
        >>> coordinates.portrait(image)
        >>> # Scale the coords to be larger than a portrait, like a selfie
        >>> coordinates.portrait(image, scale=4.8)
        >>> # Scale coords to a custom portrait size
        >>> coordinates.portrait(image, scale=(2.6, 3.4))

        """
        coord = self.copy()

        # Scale the image. Shift values indicate how to shift x,y to get
        # the face exactly at the center of the new coordinates.
        # The scale is done without matter of the image size.
        if isinstance(scale, (tuple, list)):
            shift_x = coord.scale_x(scale[0])
            shift_y = coord.scale_y(scale[1])
        elif isinstance(scale, (float, int)):
            shift_x, shift_y = coord.scale(scale)
        else:
            raise sppasTypeError(type(scale), 'int, float, tuple, list')

        # Force a xy ratio to a given value
        if xy_ratio is not None and coord.w * coord.h > 0:
            current_ratio = float(coord.w) / float(coord.h)
            if current_ratio > xy_ratio:
                sy = coord.scale_y(current_ratio / xy_ratio)
                shift_y += sy
            elif current_ratio < xy_ratio:
                sx = coord.scale_x(xy_ratio / current_ratio)
                shift_x += sx

        # the face is at top, not at the middle
        shift_y = int(float(shift_y) * 0.5)
        if image is None:
            coord.shift(shift_x, shift_y)
        else:
            try:
                coord.shift(shift_x, 0, image)
                shifted_x = True
            except:
                shifted_x = False

            try:
                coord.shift(0, shift_y, image)
                shifted_y = True
            except:
                shifted_y = False

            w, h = image.size()
            if coord.x + coord.w > w or shifted_x is False:
                coord.x = max(0, w - coord.w)

            if coord.y + coord.h > h or shifted_y is False:
                coord.y = max(0, h - coord.h)

        return coord

    # -----------------------------------------------------------------------

    def scale(self, coeff, image=None):
        """Multiply width and height values with given coefficient value.

        :param coeff: (int) The value to multiply with.
        :param image: (numpy.ndarray or sppasImage) An image to check w, h.
        :returns: Returns the value of the shift to use on the axis,
        according to the value of the scale in order to keep the same center.
        :raises: TypeError, IntervalRangeException, ImageWidthError, ImageHeightError

        """
        try:
            coeff = float(coeff)
        except:
            raise sppasTypeError(type(coeff), "int, float")
        if coeff < 0.25 or coeff > 20.:
            logging.error("Invalid scale value for coordinates."
                          "Accepted range is [0.25; 20]. Got {:.3f}.".format(coeff))
            raise IntervalRangeException(coeff, 0.25, 20.)

        coeff = self.to_dtype(coeff, dtype=float, unsigned=False)
        new_w = int(float(self.__w) * coeff)
        new_h = int(float(self.__h) * coeff)

        # Check new values with the width and height of the given image
        if image is not None:
            (height, width) = image.shape[:2]
            if new_w > width:
                raise ImageWidthError(new_w, width)
            if new_h > height:
                raise ImageHeightError(new_h, height)

        shift_x = int(float(self.__w - new_w) / 2.)
        shift_y = int(float(self.__h - new_h) / 2.)
        self.__w = new_w
        self.__h = new_h
        return shift_x, shift_y

    # -----------------------------------------------------------------------

    def scale_x(self, coeff, image=None):
        """Multiply width value with given coefficient value.

        :param coeff: (int) The value to multiply with.
        :param image: (numpy.ndarray or sppasImage) An image to check w, h.
        :returns: Returns the value of the shift to use on the x-axis,
        according to the value of the scale in order to keep the same center.
        :raise: TypeError, ScaleWidthError

        """
        if coeff <= 0.:
            raise ValueError("Invalid X-scale value {:f}.".format(coeff))

        coeff = self.to_dtype(coeff, dtype=float, unsigned=False)
        new_w = int(float(self.__w) * coeff)

        # Check new values with the width and height of the given image
        if image is not None:
            (height, width) = image.shape[:2]
            if new_w > width:
                raise ImageWidthError(new_w, width)

        shift_x = int(float(self.__w - new_w) / 2.)
        self.__w = new_w
        return shift_x

    # -----------------------------------------------------------------------

    def scale_y(self, coeff, image=None):
        """Multiply height value with given coefficient value.

        :param coeff: (int) The value to multiply with.
        :param image: (numpy.ndarray or sppasImage) An image to check w, h.
        :returns: Returns the value of the shift to use on the y-axis,
        according to the value of the scale in order to keep the same center.
        :raise: TypeError, ScaleHeightError

        """
        if coeff <= 0.:
            raise ValueError("Invalid Y-scale value {:f}.".format(coeff))

        coeff = self.to_dtype(coeff, dtype=float, unsigned=False)
        new_h = int(float(self.__h) * coeff)

        # Check new values with the width and height of the given image
        if image is not None:
            (height, width) = image.shape[:2]
            if new_h > height:
                raise ImageHeightError(new_h, height)

        shift_y = int(float(self.__h - new_h) / 2.)
        self.__h = new_h
        return shift_y

    # -----------------------------------------------------------------------

    def shift(self, x_value=0, y_value=0, image=None):
        """Shift position of (x,y) values.

        :param x_value: (int) The value to add to x-axis value.
        :param y_value: (int) The value to add to y-axis value.
        :param image: (numpy.ndarray or sppasImage) An image to check coords.
        :raise: TypeError

        """
        # Check and convert given shift values
        x_value = self.to_dtype(x_value, unsigned=False)
        y_value = self.to_dtype(y_value, unsigned=False)

        new_x = self.__x + x_value
        if new_x < 0 and self.__unsigned is True:
            new_x = 0

        new_y = self.__y + y_value
        if new_y < 0 and self.__unsigned is True:
            new_y = 0

        if image is not None:
            # Get the width and height of image
            (max_h, max_w) = image.shape[:2]
            if x_value > 0:
                if new_x > max_w:
                    raise ImageEastingError(new_x, max_w)
                elif new_x + self.__w > max_w:
                    delta = (new_x + self.__w) - max_w
                    new_x = new_x - delta
                    # raise ImageBoundError(new_x + self.__w, max_w)
            if y_value > 0:
                if new_y > max_h:
                    raise ImageNorthingError(new_y, max_h)
                elif new_y + self.__h > max_h:
                    delta = (new_y + self.__h) - max_h
                    new_y = new_y - delta
                    # raise ImageBoundError(new_y + self.__h, max_h)

        self.__x = new_x
        self.__y = new_y

    # -----------------------------------------------------------------------
    # Compare coordinates with another one
    # -----------------------------------------------------------------------

    def intersection_area(self, other):
        """Return the intersection area of two rectangles.

        :param other: (sppasCoords)

        """
        if isinstance(other, sppasCoords) is False:
            raise sppasTypeError(other, "sppasCoords")
        self_xmax = self.__x + self.__w
        other_xmax = other.x + other.w
        dx = min(self_xmax, other_xmax) - max(self.__x, other.x)

        self_ymax = self.__y + self.__h
        other_ymax = other.y + other.h
        dy = min(self_ymax, other_ymax) - max(self.__y, other.y)

        if dx >= 0 and dy >= 0:
            return dx * dy
        return 0

    # -----------------------------------------------------------------------

    def overlap(self, other):
        """Return the 2 percentage of overlaps.

        1. the overlapped area is overlapping other of XX percent of its area.
        2. the overlapped area is overlapping self of XX percent of my area.

        :param other: (sppasCoords)
        :returns: percentage of overlap of self in other and of other in self.

        """
        in_area = self.intersection_area(other)
        if in_area == 0:
            return 0., 0.
        my_area = float(self.area())
        other_area = float(other.area())
        return (in_area/other_area)*100., (in_area/my_area)*100.

    # -----------------------------------------------------------------------

    def intermediate(self, other):
        """Return the coordinates with the intermediate position and size.

        :param other: (sppasCoords)
        :return: (sppasCoords)

        """
        if isinstance(other, sppasCoords) is False:
            raise sppasTypeError(other, "sppasCoords")

        # estimate the middle point
        x = self.__x + ((other.x - self.x) // 2)
        y = self.__y + ((other.y - self.y) // 2)
        # estimate the intermediate size
        w = (self.__w + other.w) // 2
        h = (self.__h + other.h) // 2
        # average score
        c = (self.get_confidence() + other.get_confidence()) / 2.

        return sppasCoords(x, y, w, h, c)

    # -----------------------------------------------------------------------

    def euclidian_distance(self, other):
        """Return the euclidian distance between self and other.

        :param other: (sppasCoords)
        :return: (int)

        """
        if isinstance(other, sppasCoords) is False:
            raise sppasTypeError(other, "sppasCoords")
        if other is self:
            return 0
        d = euclidian((self.__x, self.__y), (other.get_x(), other.get_y()))
        return int(round(d, 0))

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __str__(self):
        s = "({:d},{:d})".format(self.__x, self.__y)
        if self.__w > 0 or self.__h > 0:
            s += " ({:d},{:d})".format(self.__w, self.__h)
        if self.__confidence is not None:
            s += ": {:f}".format(self.__confidence)
        return s

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Return true if self equal other (except for confidence score)."""
        if isinstance(other, (list, tuple)):
            if len(other) >= 4:
                other = sppasCoords(other[0], other[1], other[2], other[3])
            else:
                return False
        if isinstance(other, sppasCoords) is False:
            return False
        if self.__x != other.x:
            return False
        if self.__y != other.y:
            return False
        if self.__w != other.w:
            return False
        if self.__h != other.h:
            return False
        return True

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        return not self.__eq__(other)

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__x,
                     self.__y,
                     self.__w,
                     self.__h))

    # -----------------------------------------------------------------------

    def __contains__(self, item):
        """Return True if the coords fully contains the given item.

        Notice that __contains__ does not mean overlaps...
        If item overlaps, False is returned.

        :param item: (sppasCoords, tuple, list)

        """
        cc = sppasCoords.to_coords(item)
        if cc.w > self.__w:
            return False
        if cc.h > self.__h:
            return False

        if cc.x < self.__x:
            return False
        if cc.y < self.__y:
            return False

        if cc.x + cc.w > self.__x + self.w:
            return False
        if cc.y + cc.h > self.__y + self.h:
            return False

        return True
