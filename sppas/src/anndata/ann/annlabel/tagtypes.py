# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.annlabel.tagtypes.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Represent custom types of tags (point/rect)

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

from ...anndataexc import AnnDataTypeError
from ...anndataexc import AnnDataNegValueError

# ---------------------------------------------------------------------------


class sppasFuzzyPoint(object):
    """Data structure to represent a point (x,y) with a radius (r).

    Mainly used to represent a point in an image with a vagueness around
    the midpoint. The fuzzy point is then representing a rectangle area.
    The radius is half of the vagueness.

        + - - - - - - - - +
        |                 |
        |       (x,y)     |
        |   r    .        |
        |<------>         |
        |                 |
        + - - - - - - - - +

    Two fuzzy points are equals if their area overlaps.

    """

    def __init__(self, coord, radius=None):
        """Create a sppasFuzzyPoint instance.

        The given coordinates of the midpoint can be a tuple of int values
        or a string representing it.

        :param coord: (int,int) x,y coords of the midpoint value.
        :param radius: (int) the radius around the midpoint.

        """
        super(sppasFuzzyPoint, self).__init__()

        self.__x = 0
        self.__y = 0
        self.__radius = None

        self.set_midpoint(coord)
        self.set_radius(radius)

    # -----------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasFuzzyPoint instance.

        :param other: (sppasFuzzyPoint)

        """
        if isinstance(other, sppasFuzzyPoint) is False:
            raise AnnDataTypeError(other, "sppasFuzzyPoint")

        self.__radius = None
        self.set_midpoint(other.get_midpoint())
        self.set_radius(other.get_radius())

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        return sppasFuzzyPoint((self.__x, self.__y), self.__radius)

    # -----------------------------------------------------------------------

    def get_midpoint(self):
        """Return the midpoint coords (x,y)."""
        return self.__x, self.__y

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(str_point):
        """Return a tuple (x,y) or (x,y,r).

        :param str_point: (str) A string representing a fuzzy point.

        """
        # remove the first and the last parenthesis
        tc = str_point.lower()[1:-1]
        # split at the comma to get only x, y and eventually the radius
        tab = tc.split(",")
        # create the point with (x,y)
        x = int(tab[0])
        y = int(tab[1])
        # set the radius, if any
        if len(tab) == 3:
            return x, y, int(tab[2])
        return x, y, None

    # -----------------------------------------------------------------------

    def set_midpoint(self, midpoint):
        """Set the midpoint value.

        :param midpoint: (tuple(int,int), str) the new midpoint coords.
        :raise: AnnDataTypeError

        """
        if isinstance(midpoint, str) is True:
            x, y, r = sppasFuzzyPoint.parse(midpoint)
            midpoint = (x, y)

        self.__check_coords(midpoint)
        self.__x = int(midpoint[0])
        self.__y = int(midpoint[1])

    # -----------------------------------------------------------------------

    def __check_coords(self, midpoint):
        """Check if given midpoint is a valid coord.

        """
        if isinstance(midpoint, tuple) is False:
            raise AnnDataTypeError(midpoint, "tuple")

        if len(midpoint) != 2:
            raise AnnDataTypeError(midpoint, "tuple(int, int)")
        if isinstance(midpoint[0], (int, float)) is False:
            raise AnnDataTypeError(midpoint, "tuple(int, int)")
        if isinstance(midpoint[1], (int, float)) is False:
            raise AnnDataTypeError(midpoint, "tuple(int, int)")

    # -----------------------------------------------------------------------

    def get_radius(self):
        """Return the radius value (float or None)."""
        return self.__radius

    # -----------------------------------------------------------------------

    def set_radius(self, radius=None):
        """Fix the radius value, ie. the vagueness of the point.

        The midpoint value must be set first.

        :param radius: (int, str, None) the radius value
        :raise: AnnDataTypeError, AnnDataNegValueError

        """
        if radius is not None:
            if isinstance(radius, str) is True:
                try:
                    radius = int(radius)
                except ValueError:
                    raise AnnDataTypeError(radius, "int")
            if isinstance(radius, (int, float)) is False:
                raise AnnDataTypeError(radius, "int")

        if radius is None:
            self.__radius = None
        else:
            self.__radius = int(radius)

    # -----------------------------------------------------------------------

    def contains(self, coord):
        """Check if the given midpoint is inside the vagueness of self.

        :param coord: (tuple) An (x, y) coordinates

        """
        self.__check_coords(coord)
        rs = self.__radius
        if self.__radius is None:
            rs = 0

        # x is too small
        if coord[0] < (self.__x - rs):
            return False
        # x is too high
        if coord[0] > (self.__x + rs):
            return False
        # y is too small
        if coord[1] < (self.__y - rs):
            return False
        # y is too high
        if coord[1] > (self.__y + rs):
            return False

        return True

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        if self.__radius is None:
            return "sppasFuzzyPoint: ({:d},{:d})".format(self.__x, self.__y)
        return "sppasFuzzyPoint: ({:d},{:d},{:d})) ".format(self.__x, self.__y, self.__radius)

    # -----------------------------------------------------------------------

    def __str__(self):
        if self.__radius is None:
            return "({:d},{:d})".format(self.__x, self.__y)
        return "({:d},{:d},{:d})".format(self.__x, self.__y, self.__radius)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Test equality of self with other.

        Two fuzzy points are equals if the midpoint of one of them is in the
        area of the other.

        """
        point = None
        if isinstance(other, str) is True:
            point = sppasFuzzyPoint.parse(other)
        elif isinstance(other, tuple) is True:
            if len(other) in (2, 3):
                point = sppasFuzzyPoint((other[0], other[1]))
                if len(other) == 3:
                    point.set_radius(other[2])
        elif isinstance(other, sppasFuzzyPoint) is True:
            point = other

        if point is None:
            raise AnnDataTypeError("sppasFuzzyPoint", "tuple(int,int)")

        other_x, other_y = point.get_midpoint()
        other_r = point.get_radius()
        # The other midpoint is inside our area
        if other_r is None:
            return self.contains((other_x, other_y))
        # One of the other "corner" is inside our area
        if self.contains((other_x - other_r, other_y - other_r)) is True:
            return True
        if self.contains((other_x - other_r, other_y + other_r)) is True:
            return True
        if self.contains((other_x + other_r, other_y - other_r)) is True:
            return True
        if self.contains((other_x + other_r, other_y + other_r)) is True:
            return True

        return False

    # -----------------------------------------------------------------------

    def __hash__(self):
        # use the hashcode of self (x,y,r) points
        return hash((self.__x, self.__y, self.__radius))

# ---------------------------------------------------------------------------


class sppasFuzzyRect(object):
    """Data structure to represent an area (x,y,w,h) with a radius (r).

    Mainly used to represent a rectangle in an image with a vagueness around
    the midpoint, which is a rectangle.
    The radius is half of the vagueness.

    """

    def __init__(self, coord, radius=None):
        """Create a sppasFuzzyRect instance.

        The given coordinates of the midpoint can be a tuple of int values
        or a string representing it.

        :param coord: (int,int,int,int) x,y,w,h coords of the midpoint value.
        :param radius: (int) the radius around the midpoint.

        """
        super(sppasFuzzyRect, self).__init__()

        self.__x = 0
        self.__y = 0
        self.__w = 0
        self.__h = 0
        self.__radius = None

        self.set_midpoint(coord)
        self.set_radius(radius)

    # -----------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasFuzzyRect instance.

        :param other: (sppasFuzzyRect)

        """
        if isinstance(other, sppasFuzzyRect) is False:
            raise AnnDataTypeError(other, "sppasFuzzyRect")

        self.__radius = None
        self.set_midpoint(other.get_midpoint())
        self.set_radius(other.get_radius())

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        return sppasFuzzyRect((self.__x, self.__y, self.__w, self.__h), self.__radius)

    # -----------------------------------------------------------------------

    def get_midpoint(self):
        """Return the midpoint coords (x,y,w,h)."""
        return self.__x, self.__y, self.__w, self.__h

    # -----------------------------------------------------------------------

    @staticmethod
    def parse(str_rect):
        """Return a tuple (x,y,w,h) or (x,y,w,h,r).

        :param str_rect: (str) A string representing a fuzzy rect.

        """
        # remove the first and the last parenthesis
        tc = str_rect.lower()[1:-1]
        # split at the comma to get only x, y, w, h and eventually the radius
        tab = tc.split(",")
        # create the rect with (x,y,w,h)
        x = int(tab[0])
        y = int(tab[1])
        w = int(tab[2])
        h = int(tab[3])
        # set the radius, if any
        if len(tab) == 5:
            return x, y, w, h, int(tab[4])
        return x, y, w, h, None

    # -----------------------------------------------------------------------

    def set_midpoint(self, midpoint):
        """Set the midpoint value.

        :param midpoint: (tuple(int,int,int,int), str) the new midpoint coords.
        :raise: AnnDataTypeError

        """
        if isinstance(midpoint, str) is True:
            x, y, w, h, r = sppasFuzzyRect.parse(midpoint)
            midpoint = (x, y, w, h)

        self.__check_coords(midpoint)
        self.__x = int(midpoint[0])
        self.__y = int(midpoint[1])
        self.__w = int(midpoint[2])
        self.__h = int(midpoint[3])

    # -----------------------------------------------------------------------

    def __check_coords(self, midpoint):
        if isinstance(midpoint, tuple) is False:
            raise AnnDataTypeError(midpoint, "tuple")

        if len(midpoint) != 4:
            raise AnnDataTypeError(midpoint, "tuple(int, int, int, int)")
        for i in range(4):
            if isinstance(midpoint[i], (int, float)) is False:
                raise AnnDataTypeError(midpoint, "tuple(int, int, int, int)")
            if midpoint[i] < 0:
                raise AnnDataNegValueError(midpoint[i])

    # -----------------------------------------------------------------------

    def get_radius(self):
        """Return the radius value (float or None)."""
        return self.__radius

    # -----------------------------------------------------------------------

    def set_radius(self, radius=None):
        """Fix the radius value, ie. the vagueness of the point.

        The midpoint value must be set first.

        :param radius: (int, str, None) the radius value
        :raise: AnnDataTypeError, AnnDataNegValueError

        """
        if radius is not None:
            if isinstance(radius, str) is True:
                try:
                    radius = int(radius)
                except ValueError:
                    raise AnnDataTypeError(radius, "int")
            if isinstance(radius, int) is False:
                raise AnnDataTypeError(radius, "int")

        self.__radius = radius

    # -----------------------------------------------------------------------

    def contains(self, coord):
        """Check if the given point is inside the vagueness of self.

        :param coord: (tuple) An (x, y) coordinates

        """
        # test if coord is of an appropriate type
        p = sppasFuzzyPoint(coord)
        cx, cy = p.get_midpoint()

        r = self.__radius
        if self.__radius is None:
            r = 0
        # coord_x is too small
        if cx < (self.__x - r):
            return False
        # coord_x is too high
        if cx > (self.__x + self.__w + r):
            return False
        # coord_y is too small
        if cy < (self.__y - r):
            return False
        # coord_y is too high
        if cy > (self.__y + self.__h + r):
            return False

        return True

    # -----------------------------------------------------------------------
    # overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        if self.__radius is None:
            return "sppasFuzzyRect: ({:d},{:d},{:d},{:d})" \
                   "".format(self.__x, self.__y, self.__w, self.__h)
        return "sppasFuzzyRect: ({:d},{:d},{:d},{:d},{:d})) " \
               "".format(self.__x, self.__y, self.__w, self.__h, self.__radius)

    # -----------------------------------------------------------------------

    def __str__(self):
        if self.__radius is None:
            return "({:d},{:d},{:d},{:d})".format(self.__x, self.__y, self.__w, self.__h)
        return "({:d},{:d},{:d},{:d},{:d})".format(self.__x, self.__y, self.__w, self.__h, self.__radius)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Test equality of self with other.

        Two fuzzy points are equals if the midpoint of one of them is in the
        area of the other.

        """
        rect = None
        if isinstance(other, str) is True:
            rect = sppasFuzzyRect.parse(other)
        elif isinstance(other, tuple) is True:
            if len(other) in (4, 5):
                rect = sppasFuzzyRect((other[0], other[1], other[2], other[3]))
                if len(other) == 5:
                    rect.set_radius(other[4])
        elif isinstance(other, sppasFuzzyRect) is True:
            rect = other

        if rect is None:
            raise AnnDataTypeError("sppasFuzzyRect", "tuple(int,int,int,int)")

        other_x, other_y, other_w, other_h = rect.get_midpoint()
        other_r = rect.get_radius()
        if other_r is None:
            other_r = 0

        # One of the other "corner" is inside our area
        if self.contains((other_x - other_r, other_y - other_r)) is True:
            return True
        if self.contains((other_x - other_r, other_y + other_h + other_r)) is True:
            return True
        if self.contains((other_x + other_w + other_r, other_y - other_r)) is True:
            return True
        if self.contains((other_x + other_w + other_r, other_y + other_h + other_r)) is True:
            return True

        return False
