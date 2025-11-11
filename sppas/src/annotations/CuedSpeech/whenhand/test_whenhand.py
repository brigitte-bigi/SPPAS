# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.test_whenhand.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Unittests for Cued Speech hand transition predictor.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######  ########  ########     ###     ######
    ##    ## ##     ## ##     ##   ## ##   ##    ##     the automatic
    ##       ##     ## ##     ##  ##   ##  ##            annotation
     ######  ########  ########  ##     ##  ######        and
          ## ##        ##        #########       ##        analysis
    ##    ## ##        ##        ##     ## ##    ##         of speech
     ######  ##        ##        ##     ##  ######

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

    ---------------------------------------------------------------------

"""

import unittest
import os.path

from sppas.core.config import paths
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from ..whatkey import CuedSpeechKeys
from ..whatkey import sppasWhatKeyPredictor

from .transition import BaseWhenTransitionPredictor
from .transition import WhenTransitionPredictorDuchnowski1998
from .transition import WhenTransitionPredictorDuchnowski2000
from .transition import WhenTransitionPredictorAttina

from .transitions import WhenTransitionPredictor
from .whenhandtrans import sppasWhenHandTransitionPredictor
from .whenhandtrans import PredictedWhenHand

# ---------------------------------------------------------------------------


FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")

# ---------------------------------------------------------------------------


class TestWhenBasePredictor(unittest.TestCase):

    def setUp(self):
        self.p = BaseWhenTransitionPredictor()

    def test_properties(self):
        self.p.set_key_interval(1.0, 2.0)
        self.assertEqual(self.p.get_a1(), 1.0)
        self.assertEqual(self.p.get_a3(), 2.0)
        self.assertEqual(self.p.a1, 1.0)
        self.assertEqual(self.p.a3, 2.0)

    def test_set_key_interval(self):
        # normal situation
        self.assertIsNone(self.p.set_key_interval(2.3, 2.8))

        # un-usual ones
        with self.assertRaises(TypeError):
            self.p.set_key_interval("hello", 3.2)
        with self.assertRaises(TypeError):
            self.p.set_key_interval(3.2, "hello")
        with self.assertRaises(ValueError):
            self.p.set_key_interval(2.9, 2.8)

    def test_reset_and_avg(self):
        # Not enough known values
        self.assertEqual(0.3, self.p.get_a1a3_avg_duration())
        self.p.set_key_interval(1., 1.2)
        self.assertEqual(0.3, self.p.get_a1a3_avg_duration())
        self.p.set_key_interval(1.2, 1.4)
        self.assertEqual(0.233, round(self.p.get_a1a3_avg_duration(), 3))

        # Enough stored intervals to estimate average
        self.p.set_key_interval(1.4, 1.6)
        self.assertEqual(0.2, round(self.p.get_a1a3_avg_duration(), 2))

        self.p.reset_key_intervals()
        self.assertEqual(0.3, self.p.get_a1a3_avg_duration())

    def test_predict_m(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_position()

        self.p.set_key_interval(2.3, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(m1, 2.3)
        self.assertEqual(m2, 2.3)

        self.p.set_key_interval(2.8, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(m1, 2.8)
        self.assertEqual(m2, 2.8)

    def test_set_predict_d(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_shape()

        self.p.set_key_interval(2.3, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(d1, 2.3)
        self.assertEqual(d2, 2.3)

        self.p.set_key_interval(2.8, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(d1, 2.8)
        self.assertEqual(d2, 2.8)

# ---------------------------------------------------------------------------


class TestWhenDuchnowski1998Predictor(unittest.TestCase):

    def setUp(self):
        self.p = WhenTransitionPredictorDuchnowski1998()

    def test_predict_m(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_position()

        self.p.set_key_interval(2.3, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 1), 2.2)
        self.assertEqual(round(m2, 1), 2.2)

        self.p.set_key_interval(2.8, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 1), 2.7)
        self.assertEqual(round(m2, 1), 2.7)

        self.p.set_key_interval(0.05, 0.2)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 1), 0.)
        self.assertEqual(round(m2, 1), 0.)

    def test_set_predict_d(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_shape()

        self.p.set_key_interval(2.3, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 1), 2.2)
        self.assertEqual(round(d2, 1), 2.2)

        self.p.set_key_interval(2.8, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 1), 2.7)
        self.assertEqual(round(d2, 1), 2.7)

        self.p.set_key_interval(0.05, 0.2)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 1), 0.)
        self.assertEqual(round(d2, 1), 0.)

# ---------------------------------------------------------------------------


class TestWhenDuchnowski2000Predictor(unittest.TestCase):

    def setUp(self):
        self.p = WhenTransitionPredictorDuchnowski2000()

    def test_predict_m(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_position()

        self.p.set_key_interval(2.3, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 2), 2.05)
        self.assertEqual(round(m2, 2), 2.20)

        self.p.set_key_interval(2.8, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 2), 2.55)
        self.assertEqual(round(m2, 2), 2.7)

        self.p.set_key_interval(0.05, 0.2)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 1), 0.)
        self.assertEqual(round(m2, 1), 0.)

    def test_set_predict_d(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_shape()

        self.p.set_key_interval(2.3, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 2), 2.05)
        self.assertEqual(round(d2, 2), 2.2)

        self.p.set_key_interval(2.8, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 2), 2.55)
        self.assertEqual(round(d2, 2), 2.7)

        self.p.set_key_interval(0.05, 0.2)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 1), 0.)
        self.assertEqual(round(d2, 1), 0.)

# ---------------------------------------------------------------------------


class TestWhenAttinaPredictor(unittest.TestCase):

    def setUp(self):
        self.p = WhenTransitionPredictorAttina()

    def test_predict_m(self):
        with self.assertRaises(ValueError):
            self.p.predict_position()

        # CV key, or C- key
        self.p.set_key_interval(2.3, 2.8)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 3), 2.052)
        self.assertEqual(round(m2, 3), 2.34)

        # -V key
        self.p.set_key_interval(2.3, 2.8)
        m1, m2 = self.p.predict_position(is_nil_shape=True)
        self.assertEqual(round(m1, 3), 2.085)
        self.assertEqual(round(m2, 3), 2.398)

        self.p.set_key_interval(0.0, 0.01)
        m1, m2 = self.p.predict_position()
        self.assertEqual(round(m1, 3), 0.)
        self.assertEqual(round(m2, 3), 0.034)

    def test_set_predict_d(self):
        with self.assertRaises(ValueError):
            BaseWhenTransitionPredictor().predict_shape()

        self.p.set_key_interval(2.3, 2.8)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 3), 2.084)
        self.assertEqual(round(d2, 3), 2.3)

        self.p.set_key_interval(0.0, 0.01)
        d1, d2 = self.p.predict_shape()
        self.assertEqual(round(d1, 3), 0.)
        self.assertEqual(round(d2, 3), 0.)

# ---------------------------------------------------------------------------


class TestWhenTransitionsPrediction(unittest.TestCase):

    def test_init(self):
        versions = WhenTransitionPredictor.version_numbers()
        self.assertEqual(5, len(versions))
        for version_nb in versions:
            predictor = WhenTransitionPredictor(version_nb)
            self.assertEqual(version_nb, predictor.get_version_number())

    def test_predict_base(self):
        predictor = WhenTransitionPredictor(0)
        with self.assertRaises(ValueError):
            predictor.predict_m()
        with self.assertRaises(ValueError):
            predictor.predict_d()

        predictor.set_a(0, 2)
        self.assertEqual((0., 0.), predictor.predict_d())
        self.assertEqual((0., 0.), predictor.predict_m())

        predictor.set_a(2, 4)
        self.assertEqual((2., 2.), predictor.predict_d())
        self.assertEqual((2., 2.), predictor.predict_m())

    def test_predict_duchnowski(self):
        predictor = WhenTransitionPredictor(1)
        with self.assertRaises(ValueError):
            predictor.predict_m()
        with self.assertRaises(ValueError):
            predictor.predict_d()

        predictor.set_a(0, 2)
        self.assertEqual((0., 0.), predictor.predict_d())
        self.assertEqual((0., 0.), predictor.predict_m())

        predictor.set_a(2, 4)
        self.assertEqual((1.9, 1.9), predictor.predict_d())
        self.assertEqual((1.9, 1.9), predictor.predict_m())

        predictor = WhenTransitionPredictor(2)
        predictor.set_a(0, 2)
        self.assertEqual((0., 0.), predictor.predict_d())
        self.assertEqual((0., 0.), predictor.predict_m())

        predictor.set_a(2, 4)
        self.assertEqual((1.75, 1.9), predictor.predict_d())
        self.assertEqual((1.75, 1.9), predictor.predict_m())

    def test_predict_attina(self):
        predictor = WhenTransitionPredictor(3)
        with self.assertRaises(ValueError):
            predictor.predict_m()
        with self.assertRaises(ValueError):
            predictor.predict_d()

        predictor.set_a(0, 2)
        self.assertEqual((0., 0.), predictor.predict_d())
        m1, m2 = predictor.predict_m()
        self.assertEqual(0., m1)
        self.assertEqual(0.04, round(m2, 2))

        # Predict for a CV key
        predictor.set_a(2, 4)
        m1, m2 = predictor.predict_m()
        self.assertEqual(1.09, round(m1, 2))
        self.assertEqual(2.15, round(m2, 2))

        d1, d2 = predictor.predict_d()
        self.assertEqual(1.21, round(d1, 2))
        self.assertEqual(2.0, round(d2, 2))

        # Predict for a V- key
        predictor.set_a(2, 4)
        m1, m2 = predictor.predict_m(is_nil_shape=True)
        self.assertEqual(1.08, round(m1, 2))
        self.assertEqual(2.42, round(m2, 2))

        d1, d2 = predictor.predict_d(is_nil_shape=True)
        self.assertEqual(1.28, round(d1, 2))
        self.assertEqual(2., round(d2, 2))

    def test_predict_rules(self):
        predictor = WhenTransitionPredictor(4)
        with self.assertRaises(ValueError):
            predictor.predict_m()
        with self.assertRaises(ValueError):
            predictor.predict_d()

        predictor.set_a(2, 4)

        # This model predicts different values, if the current key is neutral
        m1, m2 = predictor.predict_m(rank=0)  # to neutral. so transition is shifted.
        self.assertEqual(2.06, round(m1, 2))
        self.assertEqual(2.3, round(m2, 2))
        d1, d2 = predictor.predict_d(rank=0)
        self.assertEqual(2.09, round(d1, 2))
        self.assertEqual(2.21, round(d2, 2))

        # predict m, d of the 1st key after a silence
        m1, m2 = predictor.predict_m(rank=1)
        self.assertEqual(1.50, round(m1, 2))
        self.assertEqual(1.94, round(m2, 2))
        d1, d2 = predictor.predict_d(rank=1)
        self.assertEqual(1.55, round(d1, 2))
        self.assertEqual(1.76, round(d2, 2))

        # predict m, d of the 2nd key after a silence
        m1, m2 = predictor.predict_m(rank=2)
        self.assertEqual(1.65, round(m1, 2))
        self.assertEqual(1.96, round(m2, 2))
        d1, d2 = predictor.predict_d(rank=2)
        self.assertEqual(1.7, round(d1, 2))
        self.assertEqual(1.8, round(d2, 2))

        # Predict for any other CV or C- or -V key
        m1, m2 = predictor.predict_m()
        self.assertEqual(1.73, round(m1, 2))
        self.assertEqual(1.99, round(m2, 2))
        d1, d2 = predictor.predict_d()
        self.assertEqual(1.76, round(d1, 2))
        self.assertEqual(1.85, round(d2, 2))

        # predict d when m is unknown.
        d1, d2 = predictor.predict_d(rank=0)
        self.assertEqual(2.09, round(d1, 2))
        self.assertEqual(2.21, round(d2, 2))

        # abnormal situation: a phoneme is starting at time 0.
        predictor.set_a(0, 2)
        self.assertEqual((0., 0.), predictor.predict_m(rank=1))
        self.assertEqual((0., 0.), predictor.predict_d(rank=1))
        self.assertEqual((0., 0.), predictor.predict_m(rank=2))
        self.assertEqual((0., 0.), predictor.predict_d(rank=2))
        self.assertEqual((0., 0.), predictor.predict_m(rank=3))
        self.assertEqual((0., 0.), predictor.predict_d(rank=3))

    def test_predict_revised_rules(self):
        predictor = WhenTransitionPredictor(5)
        with self.assertRaises(ValueError):
            predictor.predict_m()
        with self.assertRaises(ValueError):
            predictor.predict_d()
        with self.assertRaises(ValueError):
            # nil_shape and nil_pos cant be both True
            predictor.predict_m(rank=4, is_nil_shape=True, is_nil_pos=True)

        predictor.set_a(2, 4)

        # This model predicts different values, if the current key is neutral
        m1, m2 = predictor.predict_m(rank=0)  # to neutral. so transition is shifted.
        self.assertEqual(1.97, round(m1, 2))
        self.assertEqual(2.38, round(m2, 2))

        d1, d2 = predictor.predict_d(rank=0)
        self.assertEqual(2.12, round(d1, 2))
        self.assertEqual(2.21, round(d2, 2))

        # Predict m, d of the 1st key after a silence
        m1, m2 = predictor.predict_m(rank=1)
        self.assertEqual(1.40, round(m1, 2))
        self.assertEqual(1.97, round(m2, 2))
        d1, d2 = predictor.predict_d(rank=1)
        self.assertEqual(1.61, round(d1, 2))
        self.assertEqual(1.73, round(d2, 2))

        # Predict m, d of the 2nd key after a silence, key is CV
        m1, m2 = predictor.predict_m(rank=2)
        self.assertEqual(1.65, round(m1, 2))
        self.assertEqual(2., round(m2, 2))
        d1, d2 = predictor.predict_d(rank=2)
        self.assertEqual(1.76, round(d1, 2))
        self.assertEqual(1.82, round(d2, 2))

        # Predict for any CV key with rank > 2
        m1, m2 = predictor.predict_m()
        self.assertEqual(1.65, round(m1, 2))
        self.assertEqual(2.03, round(m2, 2))
        d1, d2 = predictor.predict_d()
        self.assertEqual(1.80, round(d1, 2))
        self.assertEqual(1.88, round(d2, 2))

        # Predict for any C- key with rank > 2
        m1, m2 = predictor.predict_m(is_nil_pos=True)
        self.assertEqual(1.5, round(m1, 2))
        self.assertEqual(1.91, round(m2, 2))
        d1, d2 = predictor.predict_d(is_nil_pos=True)
        self.assertEqual(1.66, round(d1, 2))
        self.assertEqual(1.83, round(d2, 2))

        # Predict for any V- key with rank > 2
        m1, m2 = predictor.predict_m(is_nil_shape=True)
        self.assertEqual(1.28, round(m1, 2))
        self.assertEqual(1.82, round(m2, 2))
        d1, d2 = predictor.predict_d(is_nil_shape=True)
        self.assertEqual(1.46, round(d1, 2))
        self.assertEqual(1.64, round(d2, 2))

        # A phoneme is starting at time 0.
        predictor.set_a(0., 2.)
        self.assertEqual((0., 0.), predictor.predict_m(rank=1))
        self.assertEqual((0., 0.), predictor.predict_d(rank=1))
        self.assertEqual((0., 0.), predictor.predict_m(rank=2))
        self.assertEqual((0., 0.), predictor.predict_d(rank=2))

        m1, m2 = predictor.predict_m()
        self.assertEqual(0., round(m1, 2))
        self.assertEqual(0.16, round(m2, 2))
        self.assertEqual((0., 0.), predictor.predict_d(rank=3))

        m1, m2 = predictor.predict_m(is_nil_pos=True)
        self.assertEqual(0., round(m1, 2))
        self.assertEqual(0., round(m2, 2))
        self.assertEqual((0., 0.), predictor.predict_d(rank=3))

        m1, m2 = predictor.predict_m(is_nil_shape=True)
        self.assertEqual(0., round(m1, 2))
        self.assertEqual(0., round(m2, 2))
        self.assertEqual((0., 0.), predictor.predict_d(rank=3))

# ---------------------------------------------------------------------------


class TestWhenCuedSpeechPredictor(unittest.TestCase):

    def setUp(self):
        self.rules = CuedSpeechKeys(FRA_KEYS)
        self.lpc = sppasWhatKeyPredictor(self.rules)
        self.hand = sppasWhenHandTransitionPredictor(self.rules)

        self.tier = sppasTier("PhonAlign")
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))),
            sppasLabel(sppasTag("v")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(2.), sppasPoint(2.8))),
            sppasLabel(sppasTag("j")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(2.8), sppasPoint(4.))),
            sppasLabel(sppasTag("o")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(4.), sppasPoint(5.))),
            sppasLabel(sppasTag("l")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
            sppasLabel(sppasTag("E")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(6.), sppasPoint(7.5))),
            sppasLabel(sppasTag("t")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(7.5), sppasPoint(10.))),
            sppasLabel(sppasTag("#")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(10.), sppasPoint(11.))),
            sppasLabel(sppasTag("v")))
        self.tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(11.), sppasPoint(12.))),
            sppasLabel(sppasTag("i")))

    # -----------------------------------------------------------------------

    def test_has_nil_shape(self):
        self.assertTrue(self.hand.has_nil_shape("i"))
        self.assertFalse(self.hand.has_nil_shape("p"))
        self.assertFalse(self.hand.has_nil_shape("p-i"))
        self.assertFalse(self.hand.has_nil_shape("any"))
        self.assertFalse(self.hand.has_nil_shape(""))

    # -----------------------------------------------------------------------

    def test_predicted_hand(self):
        # deal with degenerated intervals of prediction results
        p = PredictedWhenHand()
        p.append(2.300, 2.400, ("c", "s"), "a1", "a2")
        p.append(2.500, 2.500, ("s", "t"), "a2", "a3")
        p.append(2.400, 2.800, ("t", "m"), "a3", "a4")
        self.assertEqual(3, len(p))
        self.assertEqual(2.490, p[1][0])
        self.assertEqual(2.500, p[1][1])

        p = PredictedWhenHand()
        p.append(0.002, 0., ("c", "s"), "a1", "a2")
        self.assertEqual(0.002, p[0][0])
        self.assertEqual(0.012, p[0][1])
        self.assertEqual("0.002 0.012 ('c', 's') a1 a2", str(p))

        p.append(0.9999, 1., ("c", "s"), "a1", "a2")
        self.assertEqual(0.9899, p[1][0])
        self.assertEqual(1., p[1][1])

    # -----------------------------------------------------------------------

    def test_a1a3(self):
        self.assertEqual(0.3, self.hand.get_a1a3_avg_duration())
        with self.assertRaises(ValueError):
            self.hand.asset_a1a3(self.tier)
        result_phons = self.lpc.phons_to_segments(self.tier)
        result_keys, result_class, _ = self.lpc.segments_to_keys(
            result_phons, self.tier.get_first_point(), self.tier.get_last_point())
        self.hand.asset_a1a3(result_keys)
        self.assertEqual(1.7, self.hand.get_a1a3_avg_duration())

    # -----------------------------------------------------------------------

    def test_predict_transitions(self):
        result_phons = self.lpc.phons_to_segments(self.tier)
        result_keys, result_class, _ = self.lpc.segments_to_keys(
            result_phons, self.tier.get_first_point(), self.tier.get_last_point())

        self.hand.set_whenpredictor_version(2)
        moves, shapes = self.hand.predict_transitions(result_keys, result_phons)
        # m1 values
        self.assertEqual(1.750, moves[0][0])
        self.assertEqual(3.750, moves[1][0])
        self.assertEqual(5.750, moves[2][0])
        self.assertEqual(7.250, moves[3][0])
        self.assertEqual(9.750, moves[4][0])
        # m2 values
        self.assertEqual(1.900, moves[0][1])
        self.assertEqual(3.900, moves[1][1])
        self.assertEqual(5.900, moves[2][1])
        self.assertEqual(7.400, moves[3][1])
        self.assertEqual(9.900, moves[4][1])
        # d1 values
        self.assertEqual(1.750, shapes[0][0])
        self.assertEqual(3.750, shapes[1][0])
        self.assertEqual(5.750, shapes[2][0])
        self.assertEqual(7.250, shapes[3][0])
        self.assertEqual(9.750, shapes[4][0])
        # d2 values
        self.assertEqual(1.900, shapes[0][1])
        self.assertEqual(3.900, shapes[1][1])
        self.assertEqual(5.900, shapes[2][1])
        self.assertEqual(7.400, shapes[3][1])
        self.assertEqual(9.900, shapes[4][1])

        self.hand.set_whenpredictor_version(3)
        moves, shapes = self.hand.predict_transitions(result_keys, result_phons)
        # m1 values
        self.assertEqual(0.946, round(moves[0][0], 3))
        self.assertEqual(2.946, round(moves[1][0], 3))
        self.assertEqual(4.946, round(moves[2][0], 3))
        self.assertEqual(6.446, round(moves[3][0], 3))
        self.assertEqual(8.946, round(moves[4][0], 3))
        # m2 values
        self.assertEqual(2.170, round(moves[0][1], 3))
        self.assertEqual(4.170, round(moves[1][1], 3))
        self.assertEqual(6.170, round(moves[2][1], 3))
        self.assertEqual(7.670, round(moves[3][1], 3))
        self.assertEqual(10.170, round(moves[4][1], 3))
        # d1 values
        self.assertEqual(1.082, round(shapes[0][0], 3))
        self.assertEqual(3.082, round(shapes[1][0], 3))
        self.assertEqual(5.082, round(shapes[2][0], 3))
        self.assertEqual(6.582, round(shapes[3][0], 3))
        self.assertEqual(9.082, round(shapes[4][0], 3))
        # d2 values
        self.assertEqual(2.0, round(shapes[0][1], 3))
        self.assertEqual(4.0, round(shapes[1][1], 3))
        self.assertEqual(6.0, round(shapes[2][1], 3))
        self.assertEqual(7.50, round(shapes[3][1], 3))
        self.assertEqual(10.0, round(shapes[4][1], 3))

        self.hand.set_whenpredictor_version(4)
        moves, shapes = self.hand.predict_transitions(result_keys, result_phons)

        # m1 values
        self.assertEqual(0., round(moves[0][0], 3))
        self.assertEqual(2.3, round(moves[1][0], 3))
        self.assertEqual(4.47, round(moves[2][0], 3))
        self.assertEqual(7.56, round(moves[3][0], 3))
        self.assertEqual(7.875, round(moves[4][0], 3))
        # m2 values
        self.assertEqual(1.915, round(moves[0][1], 3))
        self.assertEqual(3.915, round(moves[1][1], 3))
        self.assertEqual(5.915, round(moves[2][1], 3))
        self.assertEqual(7.800, round(moves[3][1], 3))
        self.assertEqual(9.915, round(moves[4][1], 3))
        # d1 values
        self.assertEqual(0.13, round(shapes[0][0], 3))
        self.assertEqual(2.640, round(shapes[1][0], 3))
        self.assertEqual(4.81, round(shapes[2][0], 3))
        self.assertEqual(7.59, round(shapes[3][0], 3))
        self.assertEqual(8.13, round(shapes[4][0], 3))
        # d2 values
        self.assertEqual(1.32, round(shapes[0][1], 3))
        self.assertEqual(3.32, round(shapes[1][1], 3))
        self.assertEqual(5.32, round(shapes[2][1], 3))
        self.assertEqual(7.71, round(shapes[3][1], 3))
        self.assertEqual(9.32, round(shapes[4][1], 3))

    # -----------------------------------------------------------------------

    def test_predicted_to_tier(self):
        # The normal situation
        p = PredictedWhenHand()
        p.append(2.300, 2.400, (sppasLabel(sppasTag("c")), sppasLabel(sppasTag("s"))), "a1", "a2")
        p.append(2.490, 2.500, (sppasLabel(sppasTag("s")), sppasLabel(sppasTag("t"))), "a2", "a3")
        p.append(2.600, 2.800, (sppasLabel(sppasTag("t")), sppasLabel(sppasTag("m"))), "a3", "a4")
        t = self.hand.predicted_to_tier(p)
        self.assertEqual(len(p), len(t))
        for i in range(len(p)):
            self.assertEqual(p.get_start(i), t[i].get_location().get_lowest_localization())
            self.assertEqual(p.get_end(i), t[i].get_location().get_highest_localization())

        # with end/start overlap!
        p = PredictedWhenHand()
        p.append(2.300, 2.400, (sppasLabel(sppasTag("c")), sppasLabel(sppasTag("s"))), "a1", "a2")
        p.append(2.450, 2.500, (sppasLabel(sppasTag("s")), sppasLabel(sppasTag("t"))), "a2", "a3")
        p.append(2.490, 2.800, (sppasLabel(sppasTag("t")), sppasLabel(sppasTag("m"))), "a3", "a4")
        t = self.hand.predicted_to_tier(p)
        self.assertEqual(p.get_start(0), t[0].get_location().get_lowest_localization())
        self.assertEqual(p.get_end(0), t[0].get_location().get_highest_localization())
        self.assertEqual(p.get_start(1), t[1].get_location().get_lowest_localization())
        self.assertEqual(2.495, t[1].get_location().get_highest_localization())
        self.assertEqual(2.495, t[2].get_location().get_lowest_localization())
        self.assertEqual(p.get_end(2), t[2].get_location().get_highest_localization())

        # with two (start,end)/start overlaps!
        p = PredictedWhenHand()
        p.append(2.300, 2.400, (sppasLabel(sppasTag("c")), sppasLabel(sppasTag("s"))), "a1", "a2")
        p.append(2.490, 2.500, (sppasLabel(sppasTag("s")), sppasLabel(sppasTag("t"))), "a2", "a3")
        p.append(2.400, 2.800, (sppasLabel(sppasTag("t")), sppasLabel(sppasTag("m"))), "a3", "a4")
        t = self.hand.predicted_to_tier(p)
        self.assertEqual(p.get_start(0), t[0].get_location().get_lowest_localization())
        self.assertEqual(p.get_end(0), t[0].get_location().get_highest_localization())
        self.assertEqual(p.get_start(1), t[1].get_location().get_lowest_localization())
        self.assertEqual(2.5, t[1].get_location().get_highest_localization())  # radius is 0.005
        self.assertEqual(2.5, t[2].get_location().get_lowest_localization())   # radius is 0.005
        self.assertEqual(p.get_end(2), t[2].get_location().get_highest_localization())

    # -----------------------------------------------------------------------

    def test_phons_to_key_predictor(self):
        result_phons = self.lpc.phons_to_segments(self.tier)
        self.assertEqual(len(result_phons), 5)

        result_keys, result_class, _ = self.lpc.segments_to_keys(
            result_phons, self.tier.get_first_point(), self.tier.get_last_point())
        self.assertEqual(len(result_keys), 6)
        self.assertEqual(len(result_class), 6)
        for ann in result_keys:
            labels = ann.get_labels()
            self.assertTrue(len(labels), 2)
        for ann in result_class:
            labels = ann.get_labels()
            self.assertTrue(len(labels), 2)

        result_pos, result_shapes = self.hand.when_hands(result_keys, result_phons)
        for ann in result_pos:
            print(ann)
        self.assertEqual(len(result_pos), 5)

        for ann in result_shapes:
            print(ann)
        self.assertEqual(len(result_shapes), 5)
