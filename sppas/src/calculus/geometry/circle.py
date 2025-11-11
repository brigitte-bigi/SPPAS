"""
:filename: sppas.src.calculus.geometry.circle.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A collection of basic estimators in a circle.

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

import math

from ..calculusexc import VectorsError

from .distances import euclidian

# ---------------------------------------------------------------------------


def observed_angle(a: tuple, b: tuple) -> int:
    """Return angle value in the unit circle.

                      S1(x1,y1)
                    /     |
                 /        |
              /           |
           /              |
        /alpha            |
    S0(x0,y0)-----------A(x1,y0)

    Definitions:

    - hypotenuse = [S0S1]
    - adjacent = [AS0]
    - opposite = [AS1]
    - sinus(any_angle) = opposite / hypotenuse, so sinus(alpha) = AS1 / S0S1

    :param a: (tuple(int, int)) S0 x-axis coordinate
    :param b: (tuple(int, int)) S1 x-axis coordinate
    :return: (int) Angle in degrees in the unit circle

    Angle value is given relatively to the horizontal axis, like in the
    following unit circle:

                    +90°
                     |
       +180°         |
             ------- + ------- 0°
       -180°         |
                     |
                    -90°

    """
    if len(a) != len(b):
        raise VectorsError

    x0, y0 = a
    x1, y1 = b
    # test types
    try:
        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
    except:
        raise

    # Hypotenuse is S0-S1 euclidian distance
    hypotenuse = euclidian((x0, y0), (x1, y1))

    # Opposite is A-S1 distance
    opposite = abs(y0 - y1)

    # Angle in the S0AS1 triangle
    angle = math.degrees(math.asin(opposite / hypotenuse))

    # Angle in the unit circle
    if y0 > y1:
        # S1 is at top / S0 at bottom
        if x0 < x1:
            # S0 is at left / S1 is at right
            return int(round(angle, 0))
        else:
            return 180 - int(round(angle, 0))
    else:
        # S1 is at bottom / S0 at top
        if x0 < x1:
            # S0 is at left / S1 is at right
            return int(round(-angle, 0))
        else:
            return int(round(-angle, 0)) - 180
