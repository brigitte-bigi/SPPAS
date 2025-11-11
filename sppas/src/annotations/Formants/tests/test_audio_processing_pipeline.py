"""
:filename: sppas.src.annotations.Formants.tests.tests_audio_processing_pipeline.py
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

from sppas.src.annotations.Formants.audio_processing_pipeline import AudioProcessingPipeline
from sppas.src.annotations.Formants.audio_processing_pipeline import Resampler
from sppas.src.annotations.Formants.audio_processing_pipeline import PreEmphasizer
from sppas.src.annotations.Formants.audio_processing_pipeline import RmsComputer
from sppas.src.annotations.Formants.audio_processing_pipeline import HammingWindow

# ---------------------------------------------------------------------------
# Helper: Simulate 440Hz sine wave, full scale

def generate_test_frames(duration_sec=0.03, sampwidth=2, sr=8000):
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    signal = np.sin(2 * np.pi * 440 * t).astype(np.float32)  # Full amplitude
    int_signal = (signal * (2**(8 * sampwidth - 1) - 1)).astype(np.int16)
    return int_signal.tobytes(), sampwidth, 1, sr

# ---------------------------------------------------------------------------


class TestAudioProcessingPipeline(unittest.TestCase):

    def setUp(self):
        self.frames, self.sampwidth, self.nchannels, self.sr = generate_test_frames()
    def test_pipeline_executes_successfully(self):
        pipeline = AudioProcessingPipeline([
            Resampler(8000),
            PreEmphasizer(),
            RmsComputer()
        ])
        signal, sr, rms = pipeline.run(self.frames, self.sampwidth, self.sr)

        self.assertIsInstance(signal, np.ndarray)
        self.assertEqual(sr, 8000)
        self.assertGreater(rms, 0.01)

    def test_invalid_frames_type_raises(self):
        pipeline = AudioProcessingPipeline([])
        with self.assertRaises(TypeError):
            pipeline.run(None, self.sampwidth, self.sr)

    def test_invalid_sample_width_raises(self):
        pipeline = AudioProcessingPipeline([])
        with self.assertRaises(ValueError):
            pipeline.run(self.frames, 0, self.sr)

    def test_invalid_sample_rate_raises(self):
        pipeline = AudioProcessingPipeline([])
        with self.assertRaises(ValueError):
            pipeline.run(self.frames, self.sampwidth, -16000)

    def test_preemphasis_behavior(self):
        signal = np.array([0.5, 0.4, 0.3, 0.2], dtype=np.float32)
        emphasized = PreEmphasizer(0.97).apply(signal)
        self.assertEqual(len(emphasized), len(signal))
        self.assertAlmostEqual(emphasized[0], signal[0], places=5)

    def test_resampler_identity(self):
        signal = np.array([1.0, -1.0] * 128, dtype=np.float32)
        resampled, sr = Resampler(8000).apply(signal, 8000)
        self.assertTrue(np.array_equal(signal, resampled))
        self.assertEqual(sr, 8000)

    def test_hamming_window_applies(self):
        signal = np.ones(10, dtype=np.float32)
        windowed = HammingWindow().apply(signal)
        self.assertEqual(len(windowed), 10)
        self.assertLess(windowed[0], 1.0)
        self.assertLess(windowed[-1], 1.0)

    def test_full_pipeline_with_hamming(self):
        pipeline = AudioProcessingPipeline([
            Resampler(8000),
            PreEmphasizer(),
            HammingWindow(),
            RmsComputer()
        ])
        signal, sr, rms = pipeline.run(self.frames, self.sampwidth, self.nchannels, self.sr)
        self.assertIsInstance(signal, np.ndarray)
        self.assertEqual(sr, 8000)

    def test_pipeline_with_invalid_step_raises(self):
        class BadStep:
            pass  # no apply()

        with self.assertRaises(TypeError):
            AudioProcessingPipeline([BadStep()])

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()

