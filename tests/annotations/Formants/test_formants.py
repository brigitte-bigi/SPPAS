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
import os

from sppas.src.anndata import sppasTrsRW
from sppas.src.annotations.searchtier import sppasFindTier
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

# ---------------------------------------------------------------------------


DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")

# ---------------------------------------------------------------------------


class TestEstimatedTiers(unittest.TestCase):
    """Test of the tiers the estimator is creating.

    """

    def setUp(self):
        self.audio_filename = os.path.join(DATA, "F_F_B003-P8.wav")
        parser = sppasTrsRW(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid"))
        self.palign_tier = sppasFindTier.aligned_phones(parser.read())

    # -----------------------------------------------------------------------

    def test_no_enabled_method(self):
        estimator = FormantsEstimator()
        with self.assertRaises(ValueError):
            estimator.estimate(self.audio_filename, self.palign_tier)

    # -----------------------------------------------------------------------

    def test_a_tier_of_each_formant(self):
        # One enabled method: no tier of the method is created
        estimator = FormantsEstimator("mean")
        estimator.enable_method("burg", True)
        tiers = estimator.estimate(self.audio_filename, self.palign_tier)

        self.assertEqual(["F1", "F2"], [tier.get_name() for tier in tiers])
        self.assertEqual(len(tiers[0]), len(tiers[1]))
        self.assertGreater(len(tiers[0]), 0)

    # -----------------------------------------------------------------------

    def test_a_tier_of_each_formant_and_method(self):
        estimator = FormantsEstimator("mean")
        estimator.enable_method("burg", True)
        estimator.enable_method("autocorrelation", True)
        tiers = estimator.estimate(self.audio_filename, self.palign_tier)

        # The tiers of the formants, then the ones of each method
        self.assertEqual(["F1", "F2", "F1-burg", "F2-burg",
                          "F1-autocorrelation", "F2-autocorrelation"],
                         [tier.get_name() for tier in tiers])

        # The 1st value of a formant is the one of the 1st enabled method
        tier_f1 = tiers[0]
        tier_f1_burg = tiers[2]
        self.assertEqual(len(tier_f1), len(tier_f1_burg))
        for ann, ann_burg in zip(tier_f1, tier_f1_burg):
            self.assertEqual(ann.get_labels()[0][0][0].get_typed_content(),
                             ann_burg.get_best_tag().get_typed_content())

    # -----------------------------------------------------------------------

    def test_derived_order_of_each_method(self):
        estimator = FormantsEstimator("mean")
        estimator.enable_method("burg", True)
        estimator.enable_method("autocorrelation", True)
        tiers = estimator.estimate(self.audio_filename, self.palign_tier)

        # 12kHz for burg and 8kHz for autocorrelation: 2*kHz+2
        self.assertEqual("26", tiers[2].get_meta("lpc_order"))
        self.assertEqual("18", tiers[4].get_meta("lpc_order"))
        # The tiers of a formant have several methods, so no single order
        self.assertEqual("", tiers[0].get_meta("lpc_order", default=""))
