# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.trajectory.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Generate coordinates from given points and angles.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from sppas.src.calculus.geometry.linear_fct import slope_intercept
from sppas.src.calculus.geometry.linear_fct import linear_fct
from sppas.src.imgdata import sppasCoords

# ---------------------------------------------------------------------------


class Trajectory(object):
    """Define coordinates all along a trajectory between points.

    """

    def __init__(self, points):
        """Estimate a trajectory between points.

        :param points: (list) At least 2 points, a start and a stop

        """
        if len(points) < 2:
            raise ValueError
        self.__points = points

    # -----------------------------------------------------------------------

    def straight(self) -> list:
        """Estimate all points of a straight line between start and stop.

        Start and stop coordinates are not in the result.

        :return: (list) Coordinates (x,y) for all 'x' between p1 and p2.

        """
        # Turn the given points into coordinates
        coord1 = sppasCoords.to_coords(self.__points[0])
        coord2 = sppasCoords.to_coords(self.__points[-1])

        # Number of coordinates to be evaluated
        nb = abs(coord2.x - coord1.x) - 1
        if nb == 0:
            return list()

        # Create the resulting list with "empty" points
        coords = [sppasCoords(0, 0) for i in range(nb)]
        # Create the function f(x) = ax + b
        a, b = slope_intercept((coord1.x, coord1.y), (coord2.x, coord2.y))

        # Estimate all points between p1 and p2
        for i, x in enumerate(range(coord1.x, coord2.x)):
            if i > 0:
                coords[i-1].x = x
                coords[i-1].y = max(0, int(linear_fct(x, a, b)))

        return coords

    # -----------------------------------------------------------------------

    def steps(self, nb) -> list:
        """Estimate nb points between start and stop with a regular interval.

        :param nb: (int) Number of expected points between p1 and p2
        :return: (list) Coordinates (x,y) for all 'x' between p1 and p2.

        """
        # Get all coordinates between start and stop
        all_coords = self.straight()

        # Get coordinates for nb points, i.e/ nb+1 intervals
        coords = [sppasCoords(0, 0) for i in range(nb)]
        interval = len(all_coords) // (nb+1)

        # Get coords at the nb steps
        for i in range(nb):
            coords[i].x = all_coords[interval + (i * interval)].x
            coords[i].y = all_coords[interval + (i * interval)].y
        return coords

    # -----------------------------------------------------------------------
