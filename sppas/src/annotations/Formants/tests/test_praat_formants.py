"""
:filename: sppas.src.annotations.Formants.tests.test_praat_formants.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Praat-based classes for formant estimators through 'parselmouth'.

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
import os
import numpy as np

try:
    import parselmouth
    PARSELMOUTH_AVAILABLE = True
except ImportError:
    PARSELMOUTH_AVAILABLE = False

from sppas.src.annotations.Formants.praat_formants import BasePraatParselmouthFormantsEstimator
from sppas.src.annotations.Formants.praat_formants import PraatBurgFormantsEstimator
from sppas.src.annotations.Formants.praat_formants import PraatKeepAllFormantsEstimator
from sppas.src.annotations.Formants.praat_formants import PraatSLFormantsEstimator


# ---------------------------------------------------------------------------
# Utilities for tests
# ---------------------------------------------------------------------------

def generate_dummy_audio(filename: str, duration: float = 0.03, sample_rate: int = 8000):
    """Generate a sine wave file for testing."""
    import wave
    import struct

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t)

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in signal:
            wf.writeframes(struct.pack('<h', int(s * 32767)))


# ---------------------------------------------------------------------------
# Base to provide duplicate
# ---------------------------------------------------------------------------

class BasePraatEstimatorTest(unittest.TestCase):
    """Base test class for all Praat estimators."""

    def setUp(self):
        """Set up a test .wav file and common parameters."""
        self.sample_rate = 8000
        self.test_wav = "_test_praat.wav"
        generate_dummy_audio(self.test_wav, sample_rate=self.sample_rate)
        self.signal = np.zeros(100)
        self.start_time = 0.01
        self.end_time = 0.025

    def tearDown(self):
        """Clean up generated audio file."""
        if os.path.exists(self.test_wav):
            os.remove(self.test_wav)


# ---------------------------------------------------------------------------
# Tests PraatBurgEstimator
# ---------------------------------------------------------------------------

@unittest.skipUnless(PARSELMOUTH_AVAILABLE, "Parselmouth is not installed.")
class TestPraatBurgEstimator(BasePraatEstimatorTest):

    def test_compute_formants_burg(self):
        estimator = PraatBurgFormantsEstimator(self.test_wav, self.sample_rate)
        formants = estimator.compute(self.start_time, self.end_time)
        self.assertEqual(len(formants), 2)
        self.assertTrue(all(isinstance(f, float) for f in formants))
        self.assertTrue(all(f >= 0.0 for f in formants))

# ---------------------------------------------------------------------------
# Tests PraatKeepAllEstimator
# ---------------------------------------------------------------------------

@unittest.skipUnless(PARSELMOUTH_AVAILABLE, "Parselmouth is not installed.")
class TestPraatKeepAllEstimator(BasePraatEstimatorTest):

    def test_compute_formants_keep_all(self):
        estimator = PraatKeepAllFormantsEstimator(self.test_wav, self.sample_rate)
        formants = estimator.compute(self.start_time, self.end_time)
        self.assertEqual(len(formants), 2)
        self.assertTrue(all(isinstance(f, float) for f in formants))
        self.assertTrue(all(f >= 0.0 for f in formants))

# ---------------------------------------------------------------------------
# Tests PraatSLEstimator
# ---------------------------------------------------------------------------

@unittest.skipUnless(PARSELMOUTH_AVAILABLE, "Parselmouth is not installed.")
class TestPraatSLEstimator(BasePraatEstimatorTest):

    def test_compute_formants_sl(self):
        estimator = PraatSLFormantsEstimator(self.test_wav, self.sample_rate)
        formants = estimator.compute(self.start_time, self.end_time)
        self.assertEqual(len(formants), 2)
        self.assertTrue(all(isinstance(f, float) for f in formants))
        self.assertTrue(all(f >= 0.0 for f in formants))

# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

@unittest.skipUnless(PARSELMOUTH_AVAILABLE, "Parselmouth is not installed.")
class TestPraatFormantsValidation(BasePraatEstimatorTest):
    """Tests for edge cases and errors in Praat formant estimators."""

    def test_invalid_audio_path(self):
        with self.assertRaises(RuntimeError):
            PraatBurgFormantsEstimator("invalid_path.wav", self.sample_rate,
                                       self.start_time, self.end_time)

    def test_empty_signal_array(self):
        empty_signal = np.array([])
        with self.assertRaises(RuntimeError):
            PraatKeepAllFormantsEstimator(empty_signal, self.sample_rate,
                                          self.start_time, self.end_time)

    def test_invalid_time_window(self):
        estimator = PraatSLFormantsEstimator(self.test_wav, self.sample_rate)
        formants = estimator.compute(10.0, 15.0)
        self.assertTrue(all(np.isnan(f) or f == 0.0 for f in formants))

    def test_praat_command_must_be_implemented(self):
        class DummyEstimator(BasePraatParselmouthFormantsEstimator):
            def _praat_command(self): return super()._praat_command()

        with self.assertRaises(RuntimeError):
            DummyEstimator(self.test_wav, self.sample_rate,
                           self.start_time, self.end_time)

# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()



