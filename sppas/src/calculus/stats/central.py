# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.stats.central.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A collection of basic statistical functions for python.

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

import math
import functools

# ---------------------------------------------------------------------------


def fsum(items):
    """Estimate the sum of a list of data values.

    :param items: (list) list of data values
    :returns: (float)

    """
    return math.fsum(items)

# ---------------------------------------------------------------------------


def fmult(items):
    """Estimate the product of a list of data values.

    :param items: (list) list of data values
    :returns: (float)

    """
    return functools.reduce(lambda x, y: x*y, items)

# ---------------------------------------------------------------------------


def fgeometricmean(items):
    """Calculate the geometric mean of the data values.

    n-th root of (x1 * x2 * ... * xn).

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) == 0:
        return 0.

    one_over_n = 1./len(items)
    m = 1.
    for item in items:
        m = m * pow(item, one_over_n)

    return m

# ---------------------------------------------------------------------------


def fharmonicmean(items):
    """Calculate the harmonic mean of the data values.

    C{n / (1/x1 + 1/x2 + ... + 1/xn)}.

    :param items: (list) list of data values
    :returns (float)

    """
    if len(items) == 0:
        return 0.

    # create a list with 1/xi values
    s = 0.
    for item in items:
        s += 1./item

    return float(len(items)) / s

# ---------------------------------------------------------------------------


def fmean(items):
    """Calculate the arithmetic mean of the data values.

    sum(items)/len(items)

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) == 0:
        return 0.

    return fsum(items) / float(len(items))

# ---------------------------------------------------------------------------


def fmedian(items):
    """Calculate the 'middle' score of the data values.

    If there is an even number of scores, the mean of the 2 middle scores
    is returned.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) == 0:
        return 0.

    middle = int(len(items) / 2)
    if len(items) % 2:
        return items[middle]

    newlist = sorted(items)
    return float(newlist[middle] + newlist[middle-1]) / 2.

# ---------------------------------------------------------------------------


def fmin(items):
    """Return the minimum of the data values.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) == 0:
        return 0.

    return min(items)

# ---------------------------------------------------------------------------


def fmax(items):
    """Return the maximum of the data values.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) == 0:
        return 0.

    return max(items)
