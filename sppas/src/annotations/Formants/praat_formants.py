"""
:filename: sppas.src.annotations.Formants.praat_formants.py
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

from __future__ import annotations

import numpy as np
import parselmouth

from .base_formants import BaseFormantEstimator

# ---------------------------------------------------------------------------


class BasePraatParselmouthFormantsEstimator(BaseFormantEstimator):
    """Base class for formant estimators using Praat via Parselmouth.

    This class handles common behavior for Praat-based estimators:
    sound loading, error handling, and time-window configuration.

    Subclasses must implement the `_praat_command()` method and can
    override `compute()` if needed.

    Recommended preprocessing pipeline: NullPipeline()

    """

    def __init__(self, signal: np.array | str | None = None, sample_rate: int = 16000, *args, **kwargs):
        """Initialize the estimator.

        :param signal: (np.array|str|None) The audio signal or its filename or None.
        :param sample_rate: (int) The sample rate of the audio in Hz.
        :raises: ImportError: If Parselmouth is not available.

        """
        super().__init__(signal, sample_rate)
        try:
            sound = parselmouth.Sound(signal)
            self._formant_obj = parselmouth.praat.call(
                sound,
                self._praat_command(),
                0.01, 5, 5500, 0.025, 50.
            )

        except Exception as e:
            raise RuntimeError("Praat failed to compute formants.") from e

    # -----------------------------------------------------------------------

    def compute(self, start_time: float, end_time: float):
        """Compute F1 and F2 using a Praat command via Parselmouth.

        :param start_time: (float) Start time of the analysis window (in seconds).
        :param end_time: (float) End time of the analysis window (in seconds).
        :return: (list) Estimated formant frequencies [F1, F2] in Hz of the segment.
        :raises: RuntimeError: If Praat fails to process the audio.

        """
        f1 = parselmouth.praat.call(
            self._formant_obj, "Get mean", 1, start_time, end_time, "hertz"
        )
        f2 = parselmouth.praat.call(
            self._formant_obj, "Get mean", 2, start_time, end_time, "hertz"
        )

        return [round(f1, 3), round(f2, 3)]

    # -----------------------------------------------------------------------

    def _praat_command(self):
        """Return the Praat method name to be used.

        Subclasses must override this to specify the desired method.

        :return: (str) The Praat function name.
        :raises: NotImplementedError: Always raised by base class.

        """
        raise NotImplementedError("Subclasses must implement _praat_command().")

# ---------------------------------------------------------------------------


class PraatBurgFormantsEstimator(BasePraatParselmouthFormantsEstimator):
    """Formant estimator using Praat 'To Formant (burg)' command.

    """

    def _praat_command(self):
        """Return the Praat command name.

        :return: (str) Praat function name.

        """
        return "To Formant (burg)"

# ---------------------------------------------------------------------------


class PraatKeepAllFormantsEstimator(BasePraatParselmouthFormantsEstimator):
    """Formant estimator using Praat 'To Formant (keep all)' command.

    """

    def _praat_command(self):
        """Return the Praat command name.

        :return: (str) Praat function name.

        """
        return "To Formant (keep all)"

# ---------------------------------------------------------------------------


class PraatSLFormantsEstimator(BasePraatParselmouthFormantsEstimator):
    """Formant estimator using Praat 'To Formant (sl)' command.

    """

    def _praat_command(self):
        """Return the Praat command name.

        :return: (str) Praat function name.

        """
        return "To Formant (sl)"
