"""
:filename: sppas.src.annotations.Formants.lpc_formants.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: LPC-based classes for F1/F2 formant estimators.

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

from __future__ import annotations

import numpy as np

from .base_formants import LPCFormantEstimator

# ---------------------------------------------------------------------------
# Auto Correlation method
# ---------------------------------------------------------------------------


class AutocorrelationLPCFormantEstimator(LPCFormantEstimator):
    """Formant estimator using autocorrelation LPC and NumPy roots.

    This estimator computes LPC coefficients using the autocorrelation method,
    then estimates formants by extracting resonant frequencies from roots.

    Recommended preprocessing pipeline is AudioProcessingPipeline() with:
        - AudioResampler(target_rate=8000)
        - PreEmphasis(coefficient=0.98)
        - Windowing(duration=0.025)

    """

    def compute(self, floor_freq: float = 90.):
        """Estimate the first two formant frequencies (F1, F2).

        The signal is pre-emphasized, windowed, LPC-analyzed, and the
        roots of the LPC polynomial are used to compute the resonant
        frequencies. Frequencies below 90 Hz are discarded.

        :param floor_freq: (float) Minimum frequency (in Hz) to consider a peak as a valid formant. Defaults to 90 Hz.
        :raises: ValueError: If LPC analysis fails or no valid roots are found.
        :return: (list|None) Estimated formant frequencies in Hz, usually [F1, F2].

        """
        # LPC coefficients from autocorrelation
        a, _ = self._compute_lpc_coefficients(self._signal, self._order)

        # Extract roots and filter complex half-plane
        roots = np.roots(a)
        roots = [r for r in roots if np.imag(r) >= 0.01]

        if len(roots) == 0:
            return None

        # Convert roots to formant frequencies
        angles = np.arctan2(np.imag(roots), np.real(roots))
        frequencies = sorted(angles * (self._sample_rate / (2 * np.pi)))

        # Filter out unrealistic values
        formants = [f for f in frequencies if f >= floor_freq]

        # Convert numpy.float64 to standard float values
        return [round(float(f), 3) for f in formants[:2]]

    # -----------------------------------------------------------------------


    @staticmethod
    def _compute_lpc_coefficients(signal: np.ndarray, order: int) -> np.ndarray:
        """Compute LPC coefficients using autocorrelation and Levinson-Durbin recursion.

        :param signal: (ndarray) Windowed, pre-emphasized signal.
        :param order: (int) LPC order, typically between 10 and 16.
        :raises: ValueError: If autocorrelation length is insufficient.
        :return: (ndarray) LPC coefficients including leading 1.

        """
        # autocorr = np.correlate(signal, signal, mode='full')
        # autocorr = autocorr[len(autocorr) // 2:]
        #
        # if len(autocorr) <= order:
        #     raise ValueError("Autocorrelation vector too short for requested LPC order.")
        #
        # autocorr_values = autocorr[:order + 1]
        # rhs = -autocorr_values[1:]
        # toeplitz_col = autocorr_values[:-1]
        # a = solve_toeplitz((toeplitz_col, toeplitz_col), rhs)
        #
        # return np.concatenate(([1.0], a))

        a = np.zeros(order + 1)

        autocorr = np.correlate(signal, signal, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        R = autocorr[:order + 1]

        e = R[0]
        if e == 0:
            return a, e

        a[0] = 1.0
        for i in range(1, order + 1):
            acc = R[i]
            for j in range(1, i):
                acc += a[j] * R[i - j]
            k = -acc / e
            a_old = a.copy()
            for j in range(1, i):
                a[j] = a_old[j] + k * a_old[i - j]
            a[i] = k
            e *= 1.0 - k * k
            if e <= 0:
                break
        return a, e

# ---------------------------------------------------------------------------
# Burg method
# ---------------------------------------------------------------------------


class BurgLPCFormantEstimator(LPCFormantEstimator):
    """Formant estimator using Burg LPC analysis with NumPy roots.

    This estimator applies the Burg algorithm to compute LPC
    coefficients and extract F1/F2 from the roots.

    Recommended preprocessing pipeline is AudioProcessingPipeline() with:
        - AudioResampler(16000),
        - PreEmphasis(0.97),
        - Windowing(0.030)

    """

    def compute(self, floor_freq=90.):
        """Estimate the first two formant frequencies (F1, F2).

        The signal is pre-emphasized, windowed, LPC-analyzed using
        the Burg method, and the roots of the LPC polynomial are used
        to compute resonant frequencies. Frequencies below 90 Hz are
        discarded.

        :param floor_freq: (float) Minimum frequency (in Hz) to consider as formant.
        :raises: ValueError: If Burg algorithm fails or no roots are found.
        :return: (list|None) Estimated formant frequencies in Hz (float values).

        """
        a = self._compute_burg_coefficients(self._signal, self._order)
        if a is None or len(a) == 0:
            return None

        roots = np.roots(a)
        roots = [r for r in roots if np.imag(r) >= 0.01]
        if len(roots) == 0:
            return None

        angles = np.arctan2(np.imag(roots), np.real(roots))
        frequencies = sorted(angles * (self._sample_rate / (2 * np.pi)))

        formants = [f for f in frequencies if f >= floor_freq]

        # Convert numpy.float64 to standard float values
        return [round(float(f), 3) for f in formants[:2]]

    # -----------------------------------------------------------------------

    @staticmethod
    def _compute_burg_coefficients(signal, order):
        """Compute LPC coefficients using the Burg algorithm.

        This method implements the Burg recursion, which minimizes
        forward and backward prediction errors. It is more stable
        than autocorrelation for short signals.

        :param signal: (np.array) The input signal, pre-emphasized and windowed.
        :param order: (int) LPC analysis order.
        :raises: ValueError: If signal is too short.
        :return: (np.array) LPC coefficients (leading 1 included).

        """
        # Create LPC coefficients and check signal length
        a = np.zeros(order + 1)
        n = len(signal)
        if n <= order:
            return a, 0.

        # Initialize LPC coefficient array with leading 1
        a[0] = 1.0

        # Initialize forward and backward prediction errors
        ef = signal[1:].copy()
        eb = signal[:-1].copy()

        # Total prediction error energy
        energy = np.dot(signal, signal) / n
        if energy <= 0.0:
            return None

        # Main Burg recursion loop
        for k in range(1, order + 1):

            # Compute reflection coefficient (minimizing error)
            num = -2.0 * np.dot(eb, ef)
            den = np.dot(ef, ef) + np.dot(eb, eb)
            if den == 0:
                # Cannot divide by zero, stop the recursion
                break
            gamma = num / den

            # Save previous coefficients before updating
            a_prev = a.copy()

            # Update LPC coefficients using the recursion formula:
            # a_j^{(i)} = a_j^{(i-1)} + k * a_{i-j}^{(i-1)} for j=1 to i-1
            for i in range(1, k):
                a[i] = a_prev[i] + gamma * a_prev[k - i]
            # Add the new coefficient at the current order
            a[k] = gamma

            # Update forward and backward errors for the next iteration
            ef, eb = ef[1:] + gamma * eb[1:], eb[:-1] + gamma * ef[:-1]

            # Update total error energy
            energy *= 1.0 - gamma ** 2
            if energy <= 0:
                break
            if energy <= 0.0:
                # Numerical instability or silence
                break

        return a


