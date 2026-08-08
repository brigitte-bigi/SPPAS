"""
:filename: tests.annotations.Formants.test_formants.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tests of the analysis passes of the formants estimation methods.

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

import unittest

from sppas.src.annotations.Formants.formants import FormantsPass
from sppas.src.annotations.Formants.formants import MethodFormantsEstimator
from sppas.src.annotations.Formants.formants import MethodFormantsFactory
from sppas.src.annotations.Formants.formants import FormantsEstimator
from sppas.src.annotations.Formants.audio_processing_pipeline import AudioProcessingPipeline
from sppas.src.annotations.Formants.audio_processing_pipeline import Resampler
from sppas.src.annotations.Formants.audio_processing_pipeline import PreEmphasizer

# ---------------------------------------------------------------------------


class TestFormantsPass(unittest.TestCase):
    """Test of an analysis pass of a formants estimation method.

    """

    def test_pass(self):
        pipeline = AudioProcessingPipeline([Resampler(target_sr=8000), PreEmphasizer(0.97)])
        a_pass = FormantsPass(pipeline, (1, 2))

        self.assertEqual(pipeline, a_pass.get_pipeline())
        self.assertEqual((1, 2), a_pass.get_formants())
        self.assertEqual(8000, a_pass.get_sample_rate())

    # -----------------------------------------------------------------------

    def test_pass_without_pipeline(self):
        # A Praat-based method has no pipeline: its sample rate is unknown
        a_pass = FormantsPass(None, (1, 2))
        self.assertIsNone(a_pass.get_pipeline())
        self.assertEqual(0, a_pass.get_sample_rate())

    # -----------------------------------------------------------------------

    def test_invalid_pass(self):
        with self.assertRaises(TypeError):
            FormantsPass("pipeline", (1, 2))
        with self.assertRaises(ValueError):
            FormantsPass(None, tuple())

    # -----------------------------------------------------------------------

    def test_pipeline_without_resampler(self):
        pipeline = AudioProcessingPipeline([PreEmphasizer(0.97)])
        self.assertEqual(0, pipeline.get_target_sr())

# ---------------------------------------------------------------------------


class TestMethodFormantsEstimator(unittest.TestCase):
    """Test of a formants estimation method and its passes.

    """

    def test_method(self):
        method = MethodFormantsEstimator(object, [FormantsPass(None, (1, 2)),
                                                  FormantsPass(None, (3, 4))])
        self.assertEqual(2, len(method.get_passes()))
        self.assertEqual((1, 2, 3, 4), method.get_formants())

    # -----------------------------------------------------------------------

    def test_invalid_method(self):
        with self.assertRaises(TypeError):
            MethodFormantsEstimator(None, [FormantsPass(None, (1,))])
        with self.assertRaises(TypeError):
            MethodFormantsEstimator(object, ["pass"])

    # -----------------------------------------------------------------------

    def test_all_methods_estimate_f1_and_f2(self):
        methods = MethodFormantsFactory.create_all()
        for name in methods:
            self.assertEqual((1, 2), methods[name].get_formants())
            self.assertGreater(len(methods[name].get_passes()), 0)

        # The sample rate of the self-implemented methods is the one of
        # their resampling step.
        self.assertEqual(8000, methods["autocorrelation"].get_passes()[0].get_sample_rate())
        self.assertEqual(12000, methods["burg"].get_passes()[0].get_sample_rate())
        self.assertEqual(0, methods["praat_burg"].get_passes()[0].get_sample_rate())

# ---------------------------------------------------------------------------


class TestDerivedOrder(unittest.TestCase):
    """Test of the LPC order derived from the sample rate.

    """

    def test_derived_order(self):
        estimator = FormantsEstimator()
        # Two poles for each formant of the analyzed band, plus two ones
        self.assertEqual(18, estimator.get_order(8000))
        self.assertEqual(26, estimator.get_order(12000))
        self.assertEqual(FormantsEstimator.DEFAULT_ORDER, estimator.get_order(0))

    # -----------------------------------------------------------------------

    def test_fixed_order(self):
        estimator = FormantsEstimator()
        estimator.set_order(14)
        # A fixed order is used whatever the sample rate
        self.assertEqual(14, estimator.get_order(8000))
        self.assertEqual(14, estimator.get_order(12000))
        self.assertEqual(14, estimator.get_order())

        # Zero restores the derived order
        estimator.set_order(0)
        self.assertEqual(18, estimator.get_order(8000))

    # -----------------------------------------------------------------------

    def test_invalid_order(self):
        estimator = FormantsEstimator()
        with self.assertRaises(TypeError):
            estimator.set_order(12.5)
        with self.assertRaises(ValueError):
            estimator.set_order(5)
