# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.sights.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Data structure to store the n sights of an object.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from __future__ import annotations

from sppas.core.coreutils import NegativeValueError
from sppas.core.coreutils import IndexRangeException
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasValueError
from sppas.src.imgdata import sppasCoords

# ---------------------------------------------------------------------------


class sppasSights:
    """Data structure to store sights.

    This class is storing nb sights; each sight is made of 4 values:
        - x: (int) coordinate on the x-axis, initialized to 0
        - y: (int) coordinate on the y-axis, initialized to 0
        - z: (int) an optional coordinate on the z-axis, initialized to None
        - an optional confidence score (float), initialized to None

    Notice that each of the sight parameter is stored into a list of 'nb'
    values, instead of storing a single list of 'nb' lists of values, because:

    - 2 lists of 'nb' int and 1 of float = [x1,x2,...] [y1,y2,...] [s1,s2,...]
        are: 3*64 + 2*68*24 + 1*68*24 = 5088
    - 1 list of 'nb' lists of 2 int and 1 float = [[x1,y1,s1], [x2,y2,s2]...]
        are: 64 + 68*64 + 2*68*24 + 1*68*24 = 9312

    """

    def __init__(self, nb=68):
        """Constructor of the sppasSights class.

        :param nb: (int) Number of expected sights
        :raises: sppasTypeError: If the number parameter is not an integer

        """
        # Number of sights to store
        self.__nb = sppasCoords.to_dtype(nb, int, unsigned=True)

        # 2D-axis values
        self.__x = [0]*nb
        self.__y = [0]*nb
        # 3D-axis -- None to save memory when not used
        self.__z = None

        # Confidence scores -- None to save memory when not used
        self.__confidence = None

    # -----------------------------------------------------------------------
    # GETTERS
    # -----------------------------------------------------------------------

    def get_x(self) -> list:
        """Return the list of x values.

        :return: (list) The list that contains all x values

        """
        # shallow copy (and not deep copy) because int object are by default copied by value
        return self.__x.copy()

    # -----------------------------------------------------------------------

    def get_y(self) -> list:
        """ Return the list of y values.

        :return: (list) The list that contains all y values

        """
        # shallow copy (and not deep copy) because int object are by default copied by value
        return self.__y.copy()

    # -----------------------------------------------------------------------

    def get_z(self) -> list:
        """Return the list of z values or None.

        :return: (list or None) The list that contains all z values,
        or None if 3D axis is not set.

        """
        if self.__z is None:
            return None

        # shallow copy (and not deep copy) because int objects are by default
        # copied by value
        return self.__z.copy()

    # -----------------------------------------------------------------------

    def get_score(self) -> list:
        """Return the list of confidence score values or None.

        :return: (list or None) The list that contains all score values,
        or None if scores are not set.

        """
        if self.__confidence is None:
            return None

        # shallow copy (and not deep copy) because int object are by default copied by value
        return self.__confidence.copy()

    # -----------------------------------------------------------------------

    def x(self, index: int) -> int:
        """Return the x-axe value of the sight at the given index.

        :param index: (int) Index of the sight
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (int) The x value

        """
        checked_index = self.check_index(index)
        return self.__x[checked_index]

    # -----------------------------------------------------------------------

    def y(self, index: int) -> int:
        """Return the y-axe value of the sight at the given index.

        :param index: (int) Index of the sight
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (int) The y value

        """
        checked_index = self.check_index(index)
        return self.__y[checked_index]

    # -----------------------------------------------------------------------

    def z(self, index: int) -> int:
        """Return the z-axe value of the sight at the given index or None.

        :param index: (int) Index of the sight
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (int or None) The z value or None if 3D axis is not set

        """
        if self.__z is None:
            return None

        checked_index = self.check_index(index)
        return self.__z[checked_index]

    # -----------------------------------------------------------------------

    def score(self, index: int) -> float:
        """Return the score of the sight at the given index or None.

        :param index: (int) Index of the sight
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (float or None) The score value or None if scores are not set

        """
        if self.__confidence is None:
            return None

        checked_index = self.check_index(index)
        return self.__confidence[checked_index]

    # -----------------------------------------------------------------------

    def get_sight(self, index: int) -> tuple:
        """Return the (x, y, z, s) of the given sight.

        :param index: (int) Index of the sight
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (tuple[int, int, int, float]) The data of the sight associated with the given index

        """
        checked_index = self.check_index(index)
        return self.__x[checked_index], self.__y[checked_index], self.z(checked_index), self.score(checked_index)

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_sight(self, index: int, x: int, y: int, z=None, score=None):
        """Set the sight at the given index.

        :param index: (int) Index of the sight
        :param x: (int) pixel position on the x-axis (width)
        :param y: (int) pixel position on the y-axis (height)
        :param z: (int or None) pixel position on the z axis
        :param score: (float or None) An optional confidence score
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights

        """
        # Check the given parameters
        checked_index = self.check_index(index)
        checked_x = sppasCoords.to_dtype(x, int, unsigned=True)
        checked_y = sppasCoords.to_dtype(y, int, unsigned=True)

        # Assign values to our data structures
        self.__x[checked_index] = checked_x
        self.__y[checked_index] = checked_y
        self.set_sight_z(checked_index, z)
        self.set_sight_score(checked_index, score)

    # -----------------------------------------------------------------------

    def set_sight_z(self, index: int, z: int):
        """Set a z value to the sight at the given index.

        :param index: (int) Index of the sight
        :param z: (int or None) An optional z value
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights

        """
        checked_index = self.check_index(index)

        # If a score is not assigned
        if z is None:
            if self.__z is not None:
                # A z is not set, but we already have some. Clear the
                # one that is already existing.
                self.__z[checked_index] = None
        else:
            checked_z = sppasCoords.to_dtype(z, int, unsigned=False)

            if self.__z is None:
                # hum... we never assigned a z... create the list now
                self.__z = [None] * self.__nb

            self.__z[checked_index] = checked_z

    # -----------------------------------------------------------------------

    def set_sight_score(self, index: int, score: float):
        """Set a score to the sight at the given index.

        :param index: (int) Index of the sight
        :param score: (float or None) An optional confidence score
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights

        """
        checked_index = self.check_index(index)

        # If a score is not assigned
        if score is None:
            if self.__confidence is not None:
                # A score is not set, but we already have some. Clear the
                # one that is already existing.
                self.__confidence[checked_index] = None
        else:
            checked_sight = sppasCoords.to_dtype(score, float, unsigned=False)

            if self.__confidence is None:
                # hum... we never assigned a score... create the list now
                self.__confidence = [None] * self.__nb

            self.__confidence[checked_index] = checked_sight

    # -----------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------

    def reset(self):
        """Reset all values to their default."""
        # 2D-axis values
        self.__x = [0]*self.__nb
        self.__y = [0]*self.__nb
        # 3D-axis -- save memory when not used
        self.__z = None

        # Confidence scores -- save memory when not used
        self.__confidence = None

    # -----------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of the current sppasSights instance.

        :return: (sppasSights) The copy of the instance

        """
        copied = sppasSights(nb=self.__nb)

        for i in range(self.__nb):
            x, y, z, s = self.get_sight(i)
            copied.set_sight(i, x, y, z, s)

        return copied

    # -----------------------------------------------------------------------

    def check_index(self, value: int):
        """Raise an exception if the given index is not valid.

        :param value: (int) The index to check
        :raises: sppasTypeError: If the index is not an integer
        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of sights
        :return: (int) The value given

        """
        # Check if the given value is an integer
        if not isinstance(value, int):
            raise sppasTypeError(value, "int")

        # Check if the given value is in the range [0,nb]
        if value < 0:
            raise NegativeValueError(value)
        if self.__nb < value:
            raise IndexRangeException(value, 0, self.__nb)

        # The given value is good
        return value

    # -----------------------------------------------------------------------

    def get_mean_score(self):
        """Return the mean score or None.

        :return: (float or None) The mean score or None if no score is set

        """
        if self.__confidence is None:
            return None

        # get all scores
        values = [v for v in self.__confidence if v is not None]
        if len(values) == 0:
            return None

        return sum(values) / len(values)

    # -----------------------------------------------------------------------

    def intermediate(self, other):
        """Return the sights with the intermediate positions.

        :param other: (sppasSights) The other instance of sights
        :return: (sppasSights) The computed intermediate sights

        """
        if isinstance(other, sppasSights) is False:
            raise sppasTypeError(other, "sppasSights")

        if len(other) != self.__nb:
            raise sppasValueError(self.__nb, len(other))

        intermediate_sights = sppasSights(self.__nb)
        i = 0
        for s1, s2 in zip(self, other):  # s1 = (x1, y1, z1, c1) & s2 = (x2, y2, z2, c2)
            # estimate the (x,y) middle point
            intermediate_x = s1[0] + ((s2[0] - s1[0]) // 2)
            intermediate_y = s1[1] + ((s2[1] - s1[1]) // 2)

            # estimate the z middle point
            intermediate_z = None
            if s1[2] is not None and s2[2] is not None:
                intermediate_z = s1[2] + ((s2[2] - s1[2]) // 2)

            # estimate the average score
            intermediate_score = None
            if s1[3] is not None and s2[3] is not None:
                intermediate_score = (s1[3] + s2[3]) / 2.

            # Then set the sight position and score
            intermediate_sights.set_sight(i, intermediate_x, intermediate_y, intermediate_z, intermediate_score)
            i += 1

        return intermediate_sights

    # -----------------------------------------------------------------------

    def center(self) -> tuple:
        """Return the center of the sights."""
        x_min = min(self.__x)
        x_max = max(self.__x)
        y_min = min(self.__y)
        y_max = max(self.__y)
        x_center = x_min + ((x_max - x_min) // 2)
        y_center = y_min + ((y_max - y_min) // 2)
        if self.__z is not None:
            z_min = min(self.__z)
            z_max = max(self.__z)
            z_center = z_min + ((z_max - z_min) // 2)
            return x_center, y_center, z_center
        else:
            return x_center, y_center

    # -----------------------------------------------------------------------

    def scale(self, center: int, factor: float = 2.0):
        """Apply a scaling transformation with respect to a given center.

        The scaling operation enlarges or shrinks the distance between the
        point and the center by a given factor, without affecting the center
        itself. The transformation is applied using the following formula:

            x' = x_c + factor * (x - x_c)
            y' = y_c + factor * (y - y_c)
            z' = z_c + factor * (z - z_c)

        where:
        - (x, y, z) are the original coordinates of the point,
        - (x_c, y_c, z_c) are the coordinates of the center,
        - factor is the scaling factor.

        This ensures that:
        - If the point is to the left of the center (x < x_c), it moves further left when factor > 1.
        - If the point is to the right of the center (x > x_c), it moves further right when factor > 1.
        - The same logic applies to y and z coordinates, ensuring consistent scaling in all directions.

        :param factor: (float) Scaling factor
        :param center: (int) Index of the center point
        :raises: sppasTypeError: If factor or center is not a valid number
        :raises: IndexRangeException: If center index is out of range

        """
        center_x = self.x(center)
        center_y = self.y(center)
        center_z = self.z(center) if self.__z is not None else None

        for i in range(self.__nb):
            if self.__x[i] < center_x:
                self.__x[i] = center_x - int(factor * (center_x - self.__x[i]))
            elif self.__x[i] > center_x:
                self.__x[i] = center_x + int(factor * (self.__x[i] - center_x))

            if self.__y[i] < center_y:
                self.__y[i] = center_y - int(factor * (center_y - self.__y[i]))
            elif self.__y[i] > center_y:
                self.__y[i] = center_y + int(factor * (self.__y[i] - center_y))

            if self.__z is not None and center_z is not None:
                if self.__z[i] < center_z:
                    self.__z[i] = center_z - int(factor * (center_z - self.__z[i]))
                elif self.__z[i] > center_z:
                    self.__z[i] = center_z + int(factor * (self.__z[i] - center_z))

    # -----------------------------------------------------------------------
    # Overloads Methods
    # -----------------------------------------------------------------------

    def __str__(self):
        string_builder = "sppasSights["

        for i in range(self.__nb):
            string_builder += "({0},{1}".format(self.__x[i], self.__y[i])

            if self.__z is not None:
                string_builder += ",{0}".format(self.__z[i])

            if self.__confidence is not None and self.__confidence[i] is not None:
                string_builder += ": {0}), ".format(self.__confidence[i])

            string_builder += "]"

        return string_builder

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # ------------------------------------------------------------------------

    def __len__(self):
        """Return the number of sights."""
        return self.__nb

    # ------------------------------------------------------------------------

    def __iter__(self):
        """Browse the current sights."""
        for i in range(self.__nb):
            yield self.get_sight(i)

    # ------------------------------------------------------------------------

    def __getitem__(self, item):
        if isinstance(item, slice):
            # Get the start, stop, and step from the slice
            return [self.get_sight(ii) for ii in range(*item.indices(len(self)))]

        return self.get_sight(item)

    # -----------------------------------------------------------------------

    def __contains__(self, other):
        """Return true if value in sights -- score is ignored.

        :param other: A list/tuple of (x,y,...)

        """
        if isinstance(other, (list, tuple)) is True:
            if len(other) < 2:
                return False
            c = sppasSights(1)
            c.set_sight(0, other[0], other[1])
            if len(other) > 2:
                if isinstance(other[2], int):
                    c.set_sight_z(0, other[2])
            other = c

        if isinstance(other, sppasSights) is False:
            return False

        for i in range(self.__nb):
            if self.__x[i] == other.x(0) and self.__y[i] == other.y(0) and self.z(i) == other.z(0):
                return True

        return False
