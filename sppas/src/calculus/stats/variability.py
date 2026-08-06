# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.stats.variability.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: variance estimators.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

from .central import fmean
from .central import fsum

# ----------------------------------------------------------------------------


def lunbiasedvariance(items):
    """Calculate the unbiased sample variance of the data values, for a sample.

    It means that the estimation is using N-1 for the denominator.
    The variance is a measure of dispersion near the mean.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.
    mn = fmean(items)

    return fsum(pow(i-mn, 2) for i in items) / (len(items)-1)

# ----------------------------------------------------------------------------


def lvariance(items):
    """Calculate the variance of the data values, for a population.

    It means that the estimation is using N for the denominator.
    The variance is a measure of dispersion near the mean.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.
    mn = fmean(items)

    return fsum(pow(i-mn, 2) for i in items) / (len(items))

# ----------------------------------------------------------------------------


def lcovariance(vectors):
    """Calculate the covariance matrix of the data vectors, for a population.

    It means that the estimation is using N for the denominator, like the
    lvariance function does. Each vector is an observation and all of them
    must have the same number of values, i.e. the dimension of the space.
    The value at row i and column j of the returned matrix is the covariance
    of the dimensions i and j.

    :param vectors: (list) list of lists of data values
    :raises: ValueError: Vectors are not all of the same dimension
    :returns: (list) 2D list of float values

    """
    if len(vectors) < 2:
        return list()

    _dimension = len(vectors[0])
    for vector in vectors:
        if len(vector) != _dimension:
            raise ValueError("Expected vectors of dimension {:d}. Got {:d} instead."
                             "".format(_dimension, len(vector)))

    _means = [fmean([vector[i] for vector in vectors]) for i in range(_dimension)]

    _matrix = list()
    for i in range(_dimension):
        _row = list()
        for j in range(_dimension):
            _row.append(fsum((v[i]-_means[i]) * (v[j]-_means[j]) for v in vectors) / len(vectors))
        _matrix.append(_row)

    return _matrix

# ----------------------------------------------------------------------------


def lunbiasedstdev(items):
    """Calculate the standard deviation of the data values, for a sample.

    The standard deviation is the positive square root of the variance.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.

    return math.sqrt(lunbiasedvariance(items))

# ----------------------------------------------------------------------------


def lstdev(items):
    """Calculate the standard deviation of the data values, for a population.

    The standard deviation is the positive square root of the variance.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.

    return math.sqrt(lvariance(items))

# ----------------------------------------------------------------------------


def lsterr(items):
    """Calculate the standard error of the data values.

    :param items: (list) list of data values
    :returns: (float)

    """
    return lstdev(items) / float(math.sqrt(len(items)))

# ----------------------------------------------------------------------------


def lz(items, score):
    """Calculate the z-score for a given input score.

    given that score and the data values from which that score came.

    The z-score determines the relative location of a data value.

    :param items: (list) list of data values
    :param score: (float) a score of any items
    :returns: (float)

    """
    if len(items) < 2:
        return 0.

    return (score - fmean(items)) / lstdev(items)

# ----------------------------------------------------------------------------


def lzs(items):
    """Calculate a list of z-scores, one for each score in the data values.

    :param items: (list) list of data values
    :returns: (list)

    """
    return [lz(items, i) for i in items]

# ----------------------------------------------------------------------------


def rPVI(items):
    """Calculate the Raw Pairwise Variability Index.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.
    n = len(items) - 1
    sumd = fsum([math.fabs(items[i]-items[i+1]) for i in range(n)])

    return sumd / n

# ----------------------------------------------------------------------------


def nPVI(items):
    """Calculate the Normalized Pairwise Variability Index.

    :param items: (list) list of data values
    :returns: (float)

    """
    if len(items) < 2:
        return 0.
    n = len(items) - 1
    sumd = 0.
    for i in range(n):
        d1 = items[i]
        d2 = items[i+1]
        delta = math.fabs(d1 - d2)
        meand = (d1 + d2) / 2.
        sumd += delta / meand

    return 100. * sumd / n
