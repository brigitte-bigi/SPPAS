"""
:filename: sppas.src.annotations.Formants.base_formants.py
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

from __future__ import annotations

import numpy as np
from scipy.signal.windows import hamming

from .audio_preprocessing import AudioPreprocessor

# ---------------------------------------------------------------------------


class BaseFormantEstimator(AudioPreprocessor):
    """Base class for all formant estimators.

    This abstract class provides the interface and common attributes
    for all formant estimation methods. Subclasses must implement the
    `compute()` method to return formant frequencies for the signal.

    """

    def __init__(self, signal: np.array | None = None, sample_rate: int = 16000, *args, **kwargs):
        """Initialize the formant estimator.

        :param signal: (array) The input audio signal.
        :param sample_rate: (int) The sampling rate of the signal.
        :raises: TypeError: If `signal` is not a numpy array.
        :raises: ValueError: If `signal` is not a one-dimensional.
        :raises: ValueError: If sample_rate is not a positive integer.

        """
        super().__init__(signal, sample_rate)

    # -----------------------------------------------------------------------

    def compute(self, *args, **kwargs):
        """Compute formant frequencies.

        Subclasses must override this method. It should return a list
        of formant frequencies, typically starting with F1 and F2.

        :return: (list of floats) A list of formant frequencies.

        """
        raise NotImplementedError("Subclasses must implement this method.")

# ---------------------------------------------------------------------------


class LPCFormantEstimator(BaseFormantEstimator):
    """Base class for LPC-based formant estimators.

    Adds LPC-specific attributes and utilities such as order and
    pre-emphasis to the generic base class.

    """

    # Maximum bandwidth of a pole to be a formant, in Hz. A resonance of the
    # vocal tract is narrow: a wider pole is modeling the spectral slope.
    MAX_BANDWIDTH = 400.

    # -----------------------------------------------------------------------

    def __init__(self, signal: np.array, sample_rate: int, *args, **kwargs):
        """Initialize an LPC-based formant estimator.

        The LPC analysis order determines how many poles (i.e., spectral
        peaks) the model can represent. A higher order increases frequency
        resolution but also the risk of modeling spurious peaks. The optimal
        value depends on the sampling rate and phonetic content.
        Recommended value is (sample_rate / 1000) + 2. For a sample rate at
        8000 Hz, an order value of 10–12 is common.

        :param signal: (np.array) 1-D NumPy array representing the audio signal.
        :param sample_rate: (int) Sampling rate of the signal, in Hz.
        :param order: (int) LPC analysis order (default: 12).
        :raises: ValueError: Invalid given LPC-order argument.

        """
        if len(signal) < 128:
            raise ValueError("Signal too short for autocorrelation LPC.")
        if len(signal) > 10000:
            raise ValueError(f"Signal too long ({len(signal)} samples) for safe LPC autocorrelation.")

        super().__init__(signal, sample_rate)

        self._order = 12
        self.set_order(kwargs.get("order", 12))

    # -----------------------------------------------------------------------

    def set_order(self, order: int):
        order = int(order)
        if order < 6 or order > self._sample_rate // 100:
            raise ValueError(f"LPC order {order} is out of acceptable range"
                             f" [6, {self._sample_rate // 100}]")
        self._order = order

    # -----------------------------------------------------------------------

    def get_order(self) -> int:
        return self._order

    # -----------------------------------------------------------------------

    def _roots_to_formants(self, roots, floor_freq: float, formants: tuple) -> list:
        """Return the frequencies of the given formants from the LPC roots.

        Each root of the LPC polynomial is a pole of the modeled spectrum,
        but only the resonances of the vocal tract are formants: a pole with
        a large bandwidth is modeling the spectral slope or the noise, so it
        is discarded. The rank of a formant is its position among the sorted
        frequencies of the remaining poles.

        :param roots: (list) Roots of the LPC polynomial
        :param floor_freq: (float) Minimum frequency of a formant, in Hz
        :param formants: (tuple) Ranks of the formants to be returned, i.e. (1, 2)
        :return: (list) Estimated formant frequencies in Hz

        """
        estimated = list()
        for root in roots:
            # Only the poles of the upper complex half-plane are used: the
            # conjugated ones are the same resonances.
            if np.imag(root) < 0.01:
                continue

            frequency = np.arctan2(np.imag(root), np.real(root)) * (self._sample_rate / (2 * np.pi))
            if frequency < floor_freq:
                continue

            bandwidth = -(self._sample_rate / np.pi) * np.log(np.abs(root))
            if abs(bandwidth) > LPCFormantEstimator.MAX_BANDWIDTH:
                continue

            estimated.append(frequency)

        estimated = sorted(estimated)

        return [round(float(estimated[rank-1]), 3) for rank in formants
                if rank <= len(estimated)]

# ---------------------------------------------------------------------------


class SpectralFormantEstimator(BaseFormantEstimator):
    """Base class for spectral (non-LPC) formant estimators.

    Provides window size configuration for spectral analysis methods.

    """

    def __init__(self, signal: np.array, sample_rate: int, *args, **kwargs):
        """Initialize the formant estimator.

        :param signal: (np.array) 1-D NumPy array representing the audio signal.
        :param sample_rate: (int) Sampling rate of the signal, in Hz.
        :param window_size: (float) Analysis window size in seconds (default: 0.025).
        :raises: ValueError: Window size is not a valid value.

        """
        super().__init__(signal, sample_rate)

        window_size = kwargs.get("window_size", 0.025)
        if type(window_size) not in (int, float) or not (0.005 <= window_size <= 0.05):
            raise ValueError("Window size must be a float between 0.005 and 0.05 seconds.")
        self._window_size = window_size

