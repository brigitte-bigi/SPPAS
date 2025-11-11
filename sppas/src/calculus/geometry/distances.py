"""
:filename: sppas.src.calculus.geometry.distances.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A collection of basic distance estimators.

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

Distance axioms:
    - d(x,y) = 0 iff x = y
    - d(x,y) = d(y,x)
    - d(x,z) <= d(x,y) + d(y,z)

"""

from ..calculusexc import VectorsError

# ---------------------------------------------------------------------------


def manathan(x, y):
    """Estimate the Manathan distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :returns: (float)

    x and y must have the same length.

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> manathan(x, y)
    >>> 2.0

    """
    if len(x) != len(y):
        raise VectorsError

    return sum([abs(a-b) for (a, b) in zip(x, y)])

# ---------------------------------------------------------------------------


def euclidian(x, y):
    """Estimate the Euclidian distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :returns: (float)

    x and y must have the same length.

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> round(euclidian(x, y), 3)
    >>> 1.414

    """
    if len(x) != len(y):
        raise VectorsError

    return pow(squared_euclidian(x, y), 0.5)

# ---------------------------------------------------------------------------


def squared_euclidian(x, y):
    """Estimate the Squared Euclidian distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :returns: (float)

    x and y must have the same length.

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> squared_euclidian(x, y)
    >>> 2.0

    """
    if len(x) != len(y):
        raise VectorsError

    return sum([(a-b)**2 for (a, b) in zip(x, y)])

# ---------------------------------------------------------------------------


def minkowski(x, y, p=2):
    """Estimate the Minkowski distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :param p: power value (p=2 corresponds to the euclidian distance)
    :returns: (float)

    x and y must have the same length.

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> round(minkowski(x, y), 3)
    >>> 1.414

    """
    if len(x) != len(y):
        raise VectorsError

    summ = 0.
    for (a, b) in zip(x, y):
        summ += pow((a-b), p)

    return pow(summ, 1./p)

# ---------------------------------------------------------------------------


def chi_squared(x, y):
    """Estimate the Chi-squared distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :return: (float)

    x and y must have the same length.

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> round(chi_squared(x, y), 3)
    >>> 1.414

    """
    if len(x) != len(y):
        raise VectorsError

    summ = 0.
    for (a, b) in zip(x, y):
        summ += (float((a-b)**2) / float((a+b)))

    return pow(summ, 0.5)

# ---------------------------------------------------------------------------


def mahalanobis(x, y, covariance):
    """Estimate the Mahalanobis distance between two tuples.

    :param x: a tuple of float values
    :param y: a tuple of float values
    :param covariance: a 2D list representing the covariance matrix
    :return: (float)

    >>> x = (1.0, 0.0)
    >>> y = (0.0, 1.0)
    >>> cov = [[1.0, 0.0], [0.0, 1.0]]
    >>> round(mahalanobis(x, y, cov), 3)
    >>> 1.414

    """
    if len(x) != len(y):
        raise VectorsError

    n = len(x)
    diff = [a - b for a, b in zip(x, y)]

    def invert_matrix(m):
        size = len(m)
        identity = [[float(i == j) for i in range(size)] for j in range(size)]
        mat = [row[:] for row in m]

        for i in range(size):
            pivot = mat[i][i]
            if pivot == 0.:
                raise VectorsError
            for j in range(size):
                mat[i][j] /= pivot
                identity[i][j] /= pivot
            for k in range(size):
                if k != i:
                    factor = mat[k][i]
                    for j in range(size):
                        mat[k][j] -= factor * mat[i][j]
                        identity[k][j] -= factor * identity[i][j]
        return identity

    try:
        inv_cov = invert_matrix(covariance)
    except Exception:
        raise VectorsError

    # diff^T * inv_cov * diff
    total = 0.
    for i in range(n):
        for j in range(n):
            total += diff[i] * inv_cov[i][j] * diff[j]

    return total ** 0.5
