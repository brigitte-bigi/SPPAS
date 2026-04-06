"""
:filename: sppas.src.annotations.Formants.audio_preprocessing.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Audio pre-processing, repuired by any formant estimator.

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

# ---------------------------------------------------------------------------


class AudioPreprocessor:
    """Audio segment preprocessing for formant estimation.

    This class provides utilities to extract a centered audio segment
    and to compute its RMS energy. It is designed to be inherited or
    used directly before signal analysis.

    """

    def __init__(self, signal: np.array | str | None = None, sample_rate: int = 16000, *args, **kwargs):
        """Initialize the preprocessor.

        :param signal: (np.array|None) Full 1-D audio signal or None.
        :param sample_rate: (int) Sampling rate of the signal in Hz.
        :raises: TypeError: If signal is not a NumPy array.
        :raises: ValueError: If signal is not mono or sample_rate invalid.

        """
        if type(sample_rate) is not int or sample_rate <= 0:
            raise ValueError("Sample rate must be a strictly positive integer."
                             "Got {} instead.".format(sample_rate))

        if signal is not None and isinstance(signal, str) is False:
            if type(signal) is not np.ndarray:
                raise TypeError("Signal must be a NumPy array. Got {} instead."
                                "".format(str(type(signal))))
            if signal.ndim != 1:
                raise ValueError("Signal must be one-dimensional. Got dim={} instead."
                                 "".format(signal.ndim))

        self._signal = signal
        self._sample_rate = sample_rate

    # -----------------------------------------------------------------------


    def extract_segment(self, start_time: float, end_time: float, win_dur: float = 0.025) -> np.array:
        """Return a centered segment around the annotation.

        :param start_time: (float) Start time of the annotation.
        :param end_time: (float) End time of the annotation.
        :param win_dur: (float) Window duration in seconds (default: 25ms).
        :return: (array) Segment of the signal.

        """
        center = (start_time + end_time) / 2
        start = int((center - win_dur / 2) * self._sample_rate)
        end = int((center + win_dur / 2) * self._sample_rate)
        return self._signal[start:end]

    # -----------------------------------------------------------------------


    def rms(self, segment: np.array) -> float:
        """Compute the root mean square of the given segment.

        :param segment: (array) A slice of the signal.
        :return: (float) RMS energy value.
        """
        return float(np.sqrt(np.mean(np.square(segment))))

