# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.tests.test_rms.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of RMS automatic annotation.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

import audioopy.aio

from ..RMS.irms import IntervalsRMS
from ..RMS.sppasrms import sppasRMS

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestIntervalsRMS(unittest.TestCase):
    """Test of the rms estimator on intervals.

    """

    def setUp(self):
        audio_speech = audioopy.aio.open(
            os.path.join(DATA, "oriana1.wav")
        )
        n = audio_speech.get_nchannels()
        if n != 1:
            raise IOError("An audio file with only one channel is expected. "
                          "Got {:d} channels.".format(n))

        # Extract the channel and set it to the RMS estimator
        idx = audio_speech.extract_channel(0)
        self.channel = audio_speech.get_channel(idx)

    def test_estimator(self):
        estimator = IntervalsRMS()
        self.assertEqual(0, estimator.get_rms())
        self.assertEqual(list(), estimator.get_values())

        estimator.set_channel(self.channel)
        self.assertEqual(0, estimator.get_rms())
        self.assertEqual(list(), estimator.get_values())

        estimator.estimate(0., self.channel.get_duration())
        self.assertEqual(359.631, round(estimator.get_mean(), 3))
        self.assertEqual(696, round(estimator.get_rms(), 3))

        # only on silence (at the beginning)
        estimator.estimate(0., 0.7)
        self.assertEqual(2, estimator.get_rms())
        self.assertEqual(1.757, round(estimator.get_mean(), 3))
        estimator.estimate(0., 1.4)
        self.assertEqual(2, estimator.get_rms())
        self.assertEqual(1.757, round(estimator.get_mean(), 3))

        # only speech
        estimator.estimate(1.4, 2.4)
        self.assertEqual(1069, estimator.get_rms())
        self.assertEqual(633.21, round(estimator.get_mean(), 3))
        estimator.estimate(2.4, 3.4)
        self.assertEqual(1228, estimator.get_rms())
        self.assertEqual(953.83, round(estimator.get_mean(), 3))

    def test_sppasrms(self):
        rms = sppasRMS()
        rms.set_tiername("Tokens")
        audio_file = os.path.join(DATA, "oriana1.wav")
        trs_file = os.path.join(DATA, "oriana1-token.xra")
        out = rms.run([audio_file, trs_file])
