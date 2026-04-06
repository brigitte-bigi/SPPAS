"""
:filename: sppas.src.annotations.Formants.tests.tests_lpc_formants.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base classes for all formant estimators whatever the method.

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
import numpy as np

from sppas.src.annotations.Formants.lpc_formants import AutocorrelationLPCFormantEstimator
from sppas.src.annotations.Formants.lpc_formants import BurgLPCFormantEstimator

# ---------------------------------------------------------------------------
# Utility: Generate a test signal
# ---------------------------------------------------------------------------

def generate_test_signal(freq=440., sample_rate=8000, duration=0.03):
    """Generate a short sine wave as test input."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)

# ---------------------------------------------------------------------------
# Unit tests for Autocorrelation LPC
# ---------------------------------------------------------------------------

class TestAutocorrelationLPC(unittest.TestCase):
    """Unit tests for AutocorrelationLPCFormantEstimator."""

    def setUp(self):
        """Set up a test signal and estimator instance."""
        self.sample_rate = 8000
        self.signal = generate_test_signal()
        self.estimator = AutocorrelationLPCFormantEstimator(self.signal, self.sample_rate, order=12)

    def test_compute_lpc_coefficients(self):
        coeffs, err = self.estimator._compute_lpc_coefficients(self.signal, 12)
        self.assertEqual(len(coeffs), 13)
        self.assertIsInstance(err, float)

    def test_compute_formants_default(self):
        result = self.estimator.compute()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(all(f >= 90.0 for f in result))

    def test_compute_formants_custom_params(self):
        result = self.estimator.compute(floor_freq=100.0)
        self.assertIsInstance(result, list)
        self.assertTrue(all(f >= 100.0 for f in result))

    def test_compute_formants_no_roots(self):
        # Crée un signal plat qui ne produit pas de racines utiles
        flat_signal = np.zeros(256)
        estimator = AutocorrelationLPCFormantEstimator(flat_signal, self.sample_rate, order=12)
        result = estimator.compute()
        self.assertIsNone(result)

# ---------------------------------------------------------------------------
# Unit tests for Burg LPC
# ---------------------------------------------------------------------------

class TestBurgLPC(unittest.TestCase):
    """Unit tests for BurgLPCFormantEstimator."""

    def setUp(self):
        """Set up a test signal and estimator instance."""
        self.sample_rate = 8000
        self.signal = generate_test_signal()
        self.estimator = BurgLPCFormantEstimator(self.signal, self.sample_rate, order=12)

    def test_compute_burg_coefficients(self):
        coeffs = self.estimator._compute_burg_coefficients(self.signal, 12)
        self.assertEqual(len(coeffs), 13)
        self.assertAlmostEqual(coeffs[0], 1.0, places=5)

    def test_compute_formants_default(self):
        result = self.estimator.compute()
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertTrue(all(f >= 90.0 for f in result))

    def test_compute_formants_custom_params(self):
        result = self.estimator.compute(floor_freq=120.0)
        self.assertIsInstance(result, list)
        self.assertTrue(all(f >= 120.0 for f in result))

    def test_compute_formants_no_roots(self):
        flat_signal = np.zeros(256)
        estimator = BurgLPCFormantEstimator(flat_signal, self.sample_rate, order=12)
        result = estimator.compute()
        self.assertIsNone(result)

# ---------------------------------------------------------------------------
# Test invalid data
# ---------------------------------------------------------------------------

class TestLPCFormantEstimatorValidation(unittest.TestCase):
    """Unit tests for validating input constraints of LPCFormantEstimator."""

    def setUp(self):
        self.sample_rate = 8000

    def test_too_short_signal(self):
        short_signal = np.random.rand(64)
        with self.assertRaises(ValueError) as ctx:
            AutocorrelationLPCFormantEstimator(short_signal, self.sample_rate, order=12)
        self.assertIn("too short", str(ctx.exception))

    def test_too_long_signal(self):
        long_signal = np.random.rand(12000)
        with self.assertRaises(ValueError) as ctx:
            BurgLPCFormantEstimator(long_signal, self.sample_rate, order=12)
        self.assertIn("too long", str(ctx.exception))

    def test_invalid_order_too_low(self):
        signal = generate_test_signal()
        with self.assertRaises(ValueError) as ctx:
            AutocorrelationLPCFormantEstimator(signal, self.sample_rate, order=2)
        self.assertIn("LPC order", str(ctx.exception))

    def test_invalid_order_too_high(self):
        signal = generate_test_signal()
        max_order = self.sample_rate // 100 + 1
        with self.assertRaises(ValueError) as ctx:
            BurgLPCFormantEstimator(signal, self.sample_rate, order=max_order)
        self.assertIn("LPC order", str(ctx.exception))

    def test_valid_order_boundaries(self):
        signal = generate_test_signal()
        # Lower bound
        estimator_low = AutocorrelationLPCFormantEstimator(signal, self.sample_rate, order=6)
        self.assertIsInstance(estimator_low, AutocorrelationLPCFormantEstimator)
        # Upper bound
        estimator_high = BurgLPCFormantEstimator(signal, self.sample_rate, order=self.sample_rate // 100)
        self.assertIsInstance(estimator_high, BurgLPCFormantEstimator)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
