"""
:filename: sppas.src.annotations.Formants.tests.tests_audio_segment_loader.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary:

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
from sppas.src.annotations.Formants.audio_segment_loader import SegmentLoader

# ---------------------------------------------------------------------------
# Mimics an audio reader minimalistic

class DummyAudioReader:
    def __init__(self, signal: np.array, sr: int = 8000, sampwidth: int = 2):
        self._signal = signal
        self._sr = sr
        self._sampwidth = sampwidth
        self._pos = 0

    def get_framerate(self):
        return self._sr

    def get_sampwidth(self):
        return self._sampwidth

    def seek(self, frame_index: int):
        self._pos = frame_index

    def read_frames(self, num_frames: int):
        end = self._pos + num_frames
        sliced = self._signal[self._pos:end]
        scaled = (sliced * 16000).astype(np.int16)
        return scaled.tobytes()

# ---------------------------------------------------------------------------
# Generate a sin signal for testing

def generate_signal(duration_sec=0.05, sr=8000, amp=0.9):
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    return amp * np.sin(2 * np.pi * 440 * t)

# ---------------------------------------------------------------------------


class TestSegmentLoader(unittest.TestCase):

    def setUp(self):
        signal = generate_signal()
        self.reader = DummyAudioReader(signal)
        self.pipeline = AudioProcessingPipeline([
            Resampler(8000),
            PreEmphasizer(),
            RmsComputer()
        ])
        self.loader = SegmentLoader(self.reader, self.pipeline)

    def test_load_segment_successfully(self):
        result = self.loader.load(0.0, 0.05, rms_threshold=0.)
        self.assertIsNotNone(result)
        signal, sr = result
        self.assertIsInstance(signal, np.ndarray)
        self.assertEqual(sr, 8000)
        self.assertGreater(len(signal), 0)

    def test_load_segment_below_threshold_returns_none(self):
        silent_reader = DummyAudioReader(np.zeros(400))
        pipeline = AudioProcessingPipeline([
            Resampler(8000),
            PreEmphasizer(),
            RmsComputer()
        ])
        loader = SegmentLoader(silent_reader, pipeline)
        result = loader.load(0.0, 0.05, rms_threshold=0.01)
        self.assertIsNone(result)

    def test_extract_segment_boundaries(self):
        frames, rate = self.loader.extract_segment(0.0, 0.05)
        self.assertIsInstance(frames, bytes)
        self.assertEqual(rate, 8000)
        self.assertGreater(len(frames), 0)

    def test_invalid_audio_reader_raises(self):
        class BadReader:
            pass
        with self.assertRaises(TypeError):
            SegmentLoader(BadReader(), self.pipeline)

    def test_invalid_pipeline_raises(self):
        with self.assertRaises(TypeError):
            SegmentLoader(self.reader, object())

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()

