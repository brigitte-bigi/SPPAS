"""
:filename: sppas.src.annotations.Formants.audio_processing_pipeline.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Customizable pipeline of audio processing.

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

import logging
import numpy as np
from scipy.signal import resample_poly
from scipy.signal.windows import hamming

from audioopy import AudioConverter
from audioopy import AudioFrames

# ---------------------------------------------------------------------------
# Processing steps (each as a class with `apply()` method)
# ---------------------------------------------------------------------------


class Resampler:
    """Resample audio to a target sample rate.

    """

    def __init__(self, target_sr: int):
        self._target_sr = target_sr

    # -----------------------------------------------------------------------

    def apply(self, signal: np.array, orig_sr: int) -> tuple:
        """Resample the signal if needed.

        :param signal: (array) Input signal.
        :param orig_sr: (int) Original sample rate.
        :return: (array, int) Resampled signal and new sample rate.

        """
        if orig_sr == self._target_sr:
            return signal, orig_sr

        resampled = resample_poly(signal, self._target_sr, orig_sr)
        return resampled, self._target_sr

# ---------------------------------------------------------------------------


class PreEmphasizer:
    """Apply high-pass pre-emphasis filter."""

    def __init__(self, coeff: float = 0.97):
        self._coeff = coeff

    def apply(self, signal: np.array) -> np.array:
        """Apply pre-emphasis filter.

        :param signal: (array) Input signal.
        :return: (array) Emphasized signal.

        """
        return np.append(signal[0], signal[1:] - self._coeff * signal[:-1])

# ---------------------------------------------------------------------------


class HammingWindow:
    """Apply a Hamming window to the signal.

    This class is intended as a processing step in an audio pipeline,
    preparing the signal for spectral analysis or LPC estimation.

    """

    def apply(self, signal: np.ndarray) -> np.ndarray:
        """Return the windowed signal using a Hamming window.

        :param signal: (np.ndarray) Input signal to window.
        :return: (np.ndarray) Windowed signal.

        """
        return signal * hamming(len(signal))

# ---------------------------------------------------------------------------


class RmsComputer:
    """Compute RMS energy of frames.

    """

    def apply(self, frames: bytes) -> float:
        """Return root mean square energy.

        :param frames: (bytes) Audio segment.
        :return: (float) RMS value.

        """
        if type(frames) is bytes:
            a = AudioFrames(frames, sampwidth=2, nchannels=1)
            return a.rms()
        return 0.

# ---------------------------------------------------------------------------
# Orchestrator: AudioPipeline
# ---------------------------------------------------------------------------


class AudioProcessingPipeline:
    """Pipeline to apply audio transformations in sequence.

    """

    def __init__(self, steps: list):
        """Initialize the pipeline with a list of processing steps.

        :param steps: (list) List of step instances with `.apply(...)` method.
        :raises: TypeError: If any step is not callable via .apply.

        """
        for step in steps:
            if not hasattr(step, "apply") or not callable(step.apply):
                raise TypeError(f"Pipeline step {step.__class__.__name__} "
                                f"must define an 'apply' method.")
        self._steps = steps

    # -----------------------------------------------------------------------

    @staticmethod
    def frames_2_array(frames: bytes, sampwidth: int) -> np.ndarray:
        samples = AudioConverter.unpack_data(frames, sampwidth)
        signal = np.asarray(samples, dtype=np.float32).flatten()
        return signal

    # -----------------------------------------------------------------------

    def run(self, frames: bytes, sampwidth: int, orig_sr: int, *args, **kwargs) -> tuple:
        """Execute the pipeline with safety checks.

        :param frames: (bytes) Raw audio segment.
        :param sampwidth: (int) Sample width in bytes.
        :param orig_sr: (int) Original sample rate.
        :raises: TypeError, ValueError: If arguments are malformed.
        :return: (tuple) (processed_signal, final_sr, rms_value)

        """
        if type(frames) is not bytes or len(frames) == 0:
            raise TypeError("frames must be non-empty bytes.")

        if type(sampwidth) is not int or sampwidth <= 0:
            raise ValueError("sampwidth must be a strictly positive integer.")

        if type(orig_sr) is not int or orig_sr <= 0:
            raise ValueError("orig_sr must be a strictly positive integer.")

        rms = 0.
        for step in self._steps:
            if isinstance(step, RmsComputer) is True:
                rms = RmsComputer().apply(frames)
                break

        signal = self.frames_2_array(frames, sampwidth)

        sr = orig_sr
        for step in self._steps:
            if isinstance(step, Resampler) is True:
                signal, sr = step.apply(signal, orig_sr)

            elif isinstance(step, PreEmphasizer) is True:
                signal = step.apply(signal)

            elif isinstance(step, HammingWindow) is True:
                signal = step.apply(signal)

            elif isinstance(step, RmsComputer) is True:
                pass

            else:
                logging.error(f"Step {step.__class__.__name__} is not supported.")

        return signal, sr, rms
