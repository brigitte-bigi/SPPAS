"""
:filename: tests.calculus.test_geometry.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests for geometry calculus

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

import unittest
import random

from sppas.src.calculus.geometry.distances import squared_euclidian
from sppas.src.calculus.geometry.distances import euclidian
from sppas.src.calculus.geometry.distances import manathan
from sppas.src.calculus.geometry.distances import minkowski
from sppas.src.calculus.geometry.distances import chi_squared
from sppas.src.calculus.geometry.distances import mahalanobis
from sppas.src.calculus.geometry.linear_fct import slope_intercept
from sppas.src.calculus.geometry.linear_fct import linear_fct
from sppas.src.calculus.geometry.linear_fct import linear_values
from sppas.src.calculus.calculusexc import VectorsError

# ---------------------------------------------------------------------------


def random_vectors(size):
    x = [random.randint(0, 100) for i in range(size)]
    y = [random.randint(0, 100) for i in range(size)]
    return x, y

# ---------------------------------------------------------------------------


class TestGeometryLinearFct(unittest.TestCase):

    def test_slope_intercept(self):
        """Returns the slope and the intercept."""

        a, b = slope_intercept(p1=(1, 1), p2=(3, 3))
        self.assertEqual(a, 1.)
        self.assertEqual(b, 0.)

        a, b = slope_intercept(p1=(1, 1), p2=(30., 30.))
        self.assertEqual(a, 1.)
        self.assertEqual(b, 0.)

        a, b = slope_intercept(p1=(1, 2), p2=(2., 3.))
        self.assertEqual(a, 1.)
        self.assertEqual(b, 1.)

        # errors
        with self.assertRaises(Exception):
            slope_intercept(p1=("a", "b"), p2=(30., 30.))

        a, b = slope_intercept(p1=(1, 1), p2=(1, 1))
        self.assertEqual(a, 0.)
        self.assertEqual(b, 1.)

    # -----------------------------------------------------------------------

    def test_linear_fct(self):
        """Return f(x) of the linear function f(x) = ax + b."""

        y = linear_fct(2, 1., 0.)
        self.assertEqual(y, 2.)

        y = linear_fct(2, 1., 2.)
        self.assertEqual(y, 4.)

    # -----------------------------------------------------------------------

    def test_linear_values(self):
        """Estimate the values between 2 points, step-by-step."""

        y_values = linear_values(2, p1=(2, 2), p2=(8., 8.))
        self.assertEqual(len(y_values), 4)
        self.assertEqual(y_values[0], 2.)
        self.assertEqual(y_values[1], 4.)
        self.assertEqual(y_values[2], 6.)
        self.assertEqual(y_values[3], 8.)

        y_values = linear_values(2.5, p1=(2, 2), p2=(8., 8.))
        self.assertEqual(len(y_values), 4)
        self.assertEqual(y_values[0], 2.)   # p1. x=2
        self.assertEqual(y_values[1], 4.5)  # p1+delta, x=4.5
        self.assertEqual(y_values[2], 7.)   # p2+delta, x=7
        self.assertEqual(y_values[3], 8.)   # p2. x=8.

        y_values = linear_values(0.01, p1=(0, 0), p2=(1., 1.))
        self.assertEqual(len(y_values), 101)
        self.assertEqual(y_values[100], 1.)

        y_values = linear_values(0.01, p1=(0, 0), p2=(20000., 20000.))
        self.assertEqual(len(y_values), 2000001)
        self.assertEqual(y_values[200000], 2000.)

# ---------------------------------------------------------------------------


class TestGeometryDistances(unittest.TestCase):

    def setUp(self):
        self.x = (1.0, 0.0)
        self.y = (0.0, 1.0)
        self.z = (1.0, 0.0, 1.0)

    def test_euclidian(self):
        self.assertEqual(round(euclidian(self.x, self.y), 3), 1.414)
        with self.assertRaises(VectorsError):
            euclidian(self.x, self.z)

    def test_squared_euclidian(self):
        self.assertEqual(squared_euclidian(self.x, self.y), 2.0)
        with self.assertRaises(VectorsError):
            squared_euclidian(self.x, self.z)

    def test_manathan(self):
        self.assertEqual(manathan(self.x, self.y), 2.0)
        with self.assertRaises(VectorsError):
            manathan(self.x, self.z)

    def test_minkowski(self):
        self.assertEqual(round(minkowski(self.x, self.y), 3), 1.414)
        with self.assertRaises(VectorsError):
            minkowski(self.x, self.z)

    def test_chi_squared(self):
        self.assertEqual(round(chi_squared(self.x, self.y), 3), 1.414)
        with self.assertRaises(VectorsError):
            chi_squared(self.x, self.z)

    def test_mahalanobis(self):
        cov = [[1.0, 0.0], [0.0, 1.0]]
        self.assertEqual(round(mahalanobis(self.x, self.y, cov), 3), 1.414)
        with self.assertRaises(VectorsError):
            mahalanobis(self.x, self.z, cov)

    # -----------------------------------------------------------------------

    def test_mahalanobis_correlated_formants(self):
      """Compare Mahalanobis and Euclidean distances on correlated F1/F2 formants.

      Simulates two correlated acoustic features (F1/F2). Because the covariance
      matrix encodes higher variance and correlation between dimensions, the
      Mahalanobis distance must be smaller than the Euclidean one.

      """
      x = (500, 1500)
      y = (600, 1700)
      covariance = [
        [10000, 2500],
        [2500, 90000]
      ]
      d_mahalanobis = mahalanobis(x, y, covariance)
      d_euclid = euclidian(x, y)
      self.assertLess(d_mahalanobis, d_euclid)

    # -----------------------------------------------------------------------

    def test_mahalanobis_outlier_filtering(self):
        """Simulate vowel class filtering using Mahalanobis distance with 3-sigma threshold."""
        from statistics import mean

        # Vowel tokens: (duration, F1, F2)
        tokens = [
            (0.10, 380, 2100),
            (0.12, 395, 2150),
            (0.11, 390, 2200),
            (0.09, 400, 2180),
            (0.10, 385, 2170)
        ]
        outlier = (0.25, 390, 2600)
        all_data = tokens + [outlier]

        # Mean of the non-outlier tokens
        mu = tuple(mean(vals) for vals in zip(*tokens))

        # Diagonal covariance matrix (manually estimated)
        covariance = [
            [0.0001, 0.0, 0.0],
            [0.0, 100.0, 0.0],
            [0.0, 0.0, 10000.0]
        ]

        threshold = 3.0
        for i, obs in enumerate(all_data):
            d = mahalanobis(obs, mu, covariance)
            if i < 5:
                self.assertLess(d, threshold)
            else:
                self.assertGreater(d, threshold)
