# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.stats.linear_fct.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Linear functions

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

A linear function from the real numbers to the real numbers is a function
whose graph - in Cartesian coordinates with uniform scales, is a line in
the plane.

The equation y = ax + b is referred to as the slope-intercept form of a
linear equation.

"""

import math

# ---------------------------------------------------------------------------


def slope(p1, p2):
    """Estimate the slope between 2 points.

    :param p1: (tuple) first point as (x1, y1)
    :param p2: (tuple) second point as (x2, y2)
    :returns: float value

    """
    # test types
    try:
        x1 = float(p1[0])
        y1 = float(p1[1])
        x2 = float(p2[0])
        y2 = float(p2[1])
    except:
        raise

    # test values (p1 and p2 must be different)
    if x1 == x2:
        return 0.

    x_diff = x2 - x1
    y_diff = y2 - y1

    return y_diff / x_diff

# ---------------------------------------------------------------------------


def intercept(p1, p2):
    """Estimate the intercept between 2 points.

    :param p1: (tuple) first point as (x1, y1)
    :param p2: (tuple) second point as (x2, y2)
    :returns: float value

    """
    a = slope(p1, p2)
    b = float(p2[1]) - (a * float(p2[0]))

    return b

# ---------------------------------------------------------------------------


def slope_intercept(p1, p2):
    """Return the slope and the intercept.

    :param p1: (tuple) first point as (x1, y1)
    :param p2: (tuple) second point as (x2, y2)
    :returns: tuple(slope,intercept)

    """
    a = slope(p1, p2)
    # if a == 0.:
        # we should raise a warning
        # return 0., 0.
    b = float(p2[1]) - (a * float(p2[0]))

    return a, b

# ---------------------------------------------------------------------------


def linear_fct(x, a, b):
    """Return f(x) of the linear function f(x) = ax + b.

    :param x: (float) X-coord
    :param a: (float) slope
    :param b: (float) intercept

    """
    x = float(x)
    a = float(a)
    b = float(b)
    return (a * x) + b

# ---------------------------------------------------------------------------


def reflect_point_from_points(px, py, x1, y1, x2, y2):
    """Reflect a point (px, py) across the line passing through (x1, y1) and (x2, y2).

    x1, y1, x2, y2 -- Coordinates of two points defining the reflection axis.

    :param px: (int or float) x-axes coordinate of the point to reflect
    :param py: (int or float) y-axes coordinate of the point to reflect
    :param x1: (int or float) x-axes coordinate of the 1st point defining the reflection axis
    :param y1: (int or float) y-axes coordinate of the 1st point defining the reflection axis
    :param x2: (int or float) x-axes coordinate of the 2nd point defining the reflection axis
    :param y2: (int or float) y-axes coordinate of the 2nd point defining the reflection axis

    :return: (tuple) Reflected point coordinates.

    """
    # Line equation coefficients: ax + by + c = 0
    a = y2 - y1
    b = x1 - x2
    c = x2 * y1 - x1 * y2

    # Compute reflected point
    factor = 2 * (a * px + b * py + c) / (a**2 + b**2)
    xr = px - factor * a
    yr = py - factor * b

    return xr, yr

# ---------------------------------------------------------------------------


def reflect_point(px, py, slope, intercept):
    """Reflect a point (px, py) across the line defined by y = slope * x + intercept.

    :param px: (int or float) x-axes coordinate of the point to reflect
    :param py: (int or float) y-axes coordinate of the point to reflect
    :param slope: (float) Slope of the reflection axis
    :param intercept: (float) Y-intercept of the reflection axis

    :return: (tuple) Reflected point coordinates.

    """
    # Line equation coefficients: ax + by + c = 0
    a = slope
    b = -1
    c = intercept

    # Compute reflected point
    factor = 2 * (a * px + b * py + c) / (a**2 + b**2)
    xr = px - factor * a
    yr = py - factor * b

    return xr, yr

# ---------------------------------------------------------------------------


def ylinear_fct(y, a, b):
    """Return x of the linear function y = ax + b.

    :param y: (float) Y-coord
    :param a: (float) slope
    :param b: (float) intercept

    """
    y = float(y)
    a = float(a)
    b = float(b)
    return (y - b) / a

# ---------------------------------------------------------------------------


def linear_values(delta, p1, p2, rounded=6):
    """Estimate the values between 2 points, step-by-step.

    Two different points p1=(x1,y1) and p2=(x2,y2) determine a line. It is
    enough to substitute two different values for 'x' in the linear function
    and determine 'y' for each of these values.

        a = y2 − y1 / x2 − x1    <= slope
        b = y1 - a * x1          <= intercept

    Values for p1 and p2 are added into the result.

    :param delta: (float) Step range between values.
    :param p1: (tuple) first point as (x1, y1)
    :param p2: (tuple) second point as (x2, y2)
    :param rounded: (int) round floats
    :returns: list of float values, i.e. all the y, including the ones of p1 and p2
    :raises: MemoryError could be raised if too many values have to be \
    returned.

    """
    delta = float(delta)
    # linear function parameters
    a, b = slope_intercept(p1, p2)

    x1 = float(p1[0])
    x2 = float(p2[0])
    d = round((x2-x1), rounded)   # hack

    # number of values to add in the array
    steps = int(math.ceil(d / delta)) + 1
    array = [0.] * steps

    # values to add in the array, from p1 to previous-p2
    for step in range(1, steps):
        x = (step*delta) + x1
        y = linear_fct(x, a, b)
        array[step] = round(y, rounded)

    # first and last values (i.e. p1 and p2)
    y = linear_fct(x1, a, b)
    array[0] = round(y, rounded)
    y = linear_fct(x2, a, b)
    array[-1] = round(y, rounded)

    return array
