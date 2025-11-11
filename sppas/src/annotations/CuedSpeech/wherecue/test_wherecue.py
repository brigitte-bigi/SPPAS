# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.test_wherecue.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Cued Speech where cue predictor.

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
import os

from sppas.core.config import paths
from sppas.src.imgdata import sppasSights
from .positions import WhereVowelPositionsPredictor

from .wherecueexc import sppasWhereCuedSightsValueError
from .wherecueexc import sppasCuedPredictorError
from .basepredictor import BaseWhereModelPredictor
from .angle.baseangle import BaseWhereAnglePredictor
from .angle.customs import WhereAnglePredictorCustoms
from .angle.observed import WhereAnglePredictorObserved
from .angle.unified import WhereAnglePredictorUnified
from .angles import WhereAnglesPredictor
from .position.baseposition import BaseWherePositionPredictor
from .position.baseposition import MSG_DESCRIPTION_BASE
from .position.customs import WherePositionPredictorCustoms
from .position.customs import MSG_DESCRIPTION_CUSTOMS
from .position.observed import WherePositionPredictorObserved
from .position.observed import MSG_DESCRIPTION_OBSERVED
from .position.unified import WherePositionPredictorUnified
from .position.unified import MSG_DESCRIPTION_UNIFIED
from .wherepositions import sppasWherePositionsPredictor
from .trajectory import Trajectory

# ---------------------------------------------------------------------------

DEMO_SIGHTS = os.path.join(paths.demo, "demo-sights.xra")

# ---------------------------------------------------------------------------


class TestWhereCueExceptions(unittest.TestCase):
    """Test the 'wherecue' package exceptions."""

    def test_value_error(self):
        try:
            raise sppasWhereCuedSightsValueError(5, 12)
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasWhereCuedSightsValueError))
            self.assertTrue("1332" in str(e))
            self.assertTrue(1332, e.status)

    def test_predictor_error(self):
        try:
            raise sppasCuedPredictorError()
        except ValueError as e:
            self.assertTrue(isinstance(e, sppasCuedPredictorError))
            self.assertTrue("1325" in str(e))
            self.assertTrue(1325, e.status)

# ---------------------------------------------------------------------------


class TestBaseModelPredict(unittest.TestCase):

    def test_init_(self):
        predictor = BaseWhereModelPredictor()
        self.assertEqual(predictor._models, {})
        self.assertEqual(predictor._model, None)
        self.assertEqual(predictor._version, 0)

    def test_version_number(self):
        p = BaseWhereModelPredictor()
        # No version number is allowed - because no model declared.
        with self.assertRaises(KeyError):
            p.set_version_number(30)
        with self.assertRaises(TypeError):
            p.set_version_number("toto")

    def test_vowels_codes(self):
        p = BaseWhereModelPredictor()
        self.assertEqual(p.vowel_codes(), ())

# ---------------------------------------------------------------------------


class TestBasePredictHandAngle(unittest.TestCase):

    def test_init_(self):
        predictor = BaseWhereAnglePredictor()
        self.assertGreater(len(predictor._description), 10)

    def test_radius(self):
        predictor = BaseWhereAnglePredictor()
        self.assertEqual(predictor.radius, 10)
        predictor.radius = 3
        self.assertEqual(predictor.radius, 3)

    def test_vowel_codes(self):
        predictor = BaseWhereAnglePredictor()
        codes = predictor.vowel_codes()
        self.assertIsInstance(codes, tuple)
        self.assertTrue("n" in codes)
        self.assertTrue("b" in codes)
        self.assertTrue("m" in codes)
        self.assertTrue("c" in codes)
        self.assertTrue("t" in codes)
        self.assertTrue("s" in codes)

    def test_check(self):
        predictor = BaseWhereAnglePredictor()
        vowels_to_check = ['b', 'c', 'n']
        try:
            predictor.check(vowels_to_check)
        except KeyError:
            self.fail("check() raised sppasKeyError unexpectedly!")

        vowels_to_check = []
        try:
            predictor.check(vowels_to_check)
        except KeyError:
            self.fail("check() raised sppasKeyError unexpectedly!")

        vowels_to_check = ['b', 'c', 'x']
        with self.assertRaises(KeyError):
            predictor.check(vowels_to_check)

    def test_get_angle(self):
        predictor = BaseWhereAnglePredictor()
        expected_angle = 80
        predictor._vowels = {"n": expected_angle}
        self.assertEqual(predictor.get_angle('n'), expected_angle)

        with self.assertRaises(KeyError):
            predictor.get_angle('x')

    def test_calculate(self):
        predictor = BaseWhereAnglePredictor()

        with self.assertRaises(KeyError):
            predictor.get_angle('b')

        predictor.predict_angle_values(predictor.vowel_codes())
        self.assertEqual(predictor.get_angle('n'), 60)
        self.assertEqual(predictor.get_angle('b'), 60)
        self.assertEqual(predictor.get_angle('c'), 60)
        self.assertEqual(predictor.get_angle('m'), 60)
        self.assertEqual(predictor.get_angle('s'), 60)
        self.assertEqual(predictor.get_angle('t'), 60)

# ---------------------------------------------------------------------------


class TestPredictHandAngleCustoms(unittest.TestCase):

    def test_init_(self):
        predictor = WhereAnglePredictorCustoms()
        self.assertGreater(len(predictor._description), 10)

    def test_radius(self):
        predictor = WhereAnglePredictorCustoms()
        self.assertEqual(predictor.radius, 5)
        predictor.radius = 3
        self.assertEqual(predictor.radius, 3)

    def test_calculate(self):
        predictor = WhereAnglePredictorCustoms()

        with self.assertRaises(KeyError):
            predictor.get_angle('b')

        predictor.predict_angle_values(predictor.vowel_codes())
        self.assertEqual(predictor.get_angle('n'), 50)
        self.assertEqual(predictor.get_angle('b'), 75)
        self.assertEqual(predictor.get_angle('c'), 67)
        self.assertEqual(predictor.get_angle('m'), 73)
        self.assertEqual(predictor.get_angle('s'), 83)
        self.assertEqual(predictor.get_angle('t'), 58)

# ---------------------------------------------------------------------------


class TestPredictHandAngleObserved(unittest.TestCase):

    def test_init_(self):
        predictor = WhereAnglePredictorObserved()
        self.assertGreater(len(predictor._description), 10)

    def test_radius(self):
        predictor = WhereAnglePredictorObserved()
        self.assertEqual(predictor.radius, 5)
        predictor.radius = 3
        self.assertEqual(predictor.radius, 3)

    def test_calculate(self):
        predictor = WhereAnglePredictorObserved()

        with self.assertRaises(KeyError):
            predictor.get_angle('b')

        predictor.predict_angle_values(predictor.vowel_codes())
        self.assertEqual(predictor.get_angle('n'), 50)
        self.assertEqual(predictor.get_angle('b'), 62)
        self.assertEqual(predictor.get_angle('c'), 59)
        self.assertEqual(predictor.get_angle('m'), 56)
        self.assertEqual(predictor.get_angle('s'), 83)
        self.assertEqual(predictor.get_angle('t'), 49)

# ---------------------------------------------------------------------------


class TestPredictHandAngleUnified(unittest.TestCase):

    def test_init_(self):
        predictor = WhereAnglePredictorUnified()
        self.assertGreater(len(predictor._description), 10)

    def test_radius(self):
        predictor = WhereAnglePredictorUnified()
        self.assertEqual(predictor.radius, 5)
        predictor.radius = 3
        self.assertEqual(predictor.radius, 3)

    def test_calculate(self):
        predictor = WhereAnglePredictorUnified()

        with self.assertRaises(KeyError):
            predictor.get_angle('b')

        predictor.predict_angle_values(predictor.vowel_codes())
        self.assertEqual(predictor.get_angle('n'), 45)
        self.assertEqual(predictor.get_angle('b'), 63)
        self.assertEqual(predictor.get_angle('c'), 57)
        self.assertEqual(predictor.get_angle('m'), 60)
        self.assertEqual(predictor.get_angle('s'), 70)
        self.assertEqual(predictor.get_angle('t'), 50)

# ---------------------------------------------------------------------------


class TestPredictHandAngles(unittest.TestCase):

    def test_init_(self):
        p = WhereAnglesPredictor()

    def test_version_number(self):
        p = WhereAnglesPredictor()
        self.assertEqual(p.model_version, p.DEFAULT_VERSION)
        p.set_version_number(0)
        self.assertEqual(p.model_version, 0)
        p.set_version_number("1")
        self.assertEqual(p.model_version, 1)

    def test_predict(self):
        # Instantiate the unified model
        p = WhereAnglesPredictor(version_number=3)
        # By default, predict only for neutral
        p.predict_angle_values()
        with self.assertRaises(KeyError):
            p.get_angle('b')
        # Get angle. By default, the "use_face" option is False
        self.assertEqual(p.get_angle('n'), 45)
        self.assertEqual(p.get_angle('n', face_angle=None), 45)
        self.assertEqual(p.get_angle('n', face_angle=90), 45)
        self.assertEqual(p.get_angle('n', face_angle=95), 45)
        self.assertEqual(p.get_angle('n', face_angle=85), 45)

    def test_predict_with_use_face(self):
        # Instantiate the base model
        p = WhereAnglesPredictor(version_number=0)
        # By default, predict only for neutral
        p.predict_angle_values()
        self.assertEqual(p.get_angle('n', face_angle=90), 60)
        self.assertEqual(p.get_angle('n', face_angle=95), 60)
        self.assertEqual(p.get_angle('n', face_angle=85), 60)

        p.use_face = True
        self.assertEqual(p.get_angle('n'), 60)
        self.assertEqual(p.get_angle('n', face_angle=90), 60)
        self.assertEqual(p.get_angle('n', face_angle=95), 62)
        self.assertEqual(p.get_angle('n', face_angle=85), 57)

# ---------------------------------------------------------------------------


class TestPredictPositions(unittest.TestCase):

    def test_init_(self):
        p = WhereVowelPositionsPredictor()

    def test_version_number(self):
        p = WhereVowelPositionsPredictor()
        self.assertEqual(p.model_version, p.DEFAULT_VERSION)
        p.set_version_number(0)
        self.assertEqual(p.model_version, 0)
        p.set_version_number("1")
        self.assertEqual(p.model_version, 1)

    def test_predict(self):
        pass

# ---------------------------------------------------------------------------


class TestBasePredictVowelPosition(unittest.TestCase):

    def test_init_(self):
        predictor = BaseWherePositionPredictor()
        self.assertEqual(predictor.get_sights_dim(), 68)
        self.assertEqual(predictor._description, MSG_DESCRIPTION_BASE)

        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=50)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights=None)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights="invalid")
        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=-1)

    def test_vowel_codes(self):
        predictor = BaseWherePositionPredictor()
        codes = predictor.vowel_codes()
        self.assertIsInstance(codes, tuple)
        self.assertTrue("n" in codes)
        self.assertTrue("b" in codes)
        self.assertTrue("m" in codes)
        self.assertTrue("c" in codes)
        self.assertTrue("t" in codes)
        self.assertTrue("s" in codes)

    def test_get_dim(self):
        predictor = BaseWherePositionPredictor()
        num_sights = predictor.get_sights_dim()
        self.assertEqual(num_sights, 68)

    def test_set_sights_and_predict_coords(self):
        predictor = BaseWherePositionPredictor()
        sights = sppasSights()
        predictor.set_sights_and_predict_coords(sights)
        self.assertEqual(predictor._BaseVowelPosition__sights, sights)

        sights = sppasSights(nb=100)
        # Assuming 100 is not the expected dimension
        with self.assertRaises(NotImplementedError):
            predictor.set_sights_and_predict_coords(sights)

    def test_get_vowel_coords(self):
        predictor = BaseWherePositionPredictor()
        expected_coords = (80, 160, 0)
        predictor._vowels = {"n": expected_coords}
        self.assertEqual(predictor.get_vowel_coords('n'), expected_coords)

        with self.assertRaises(KeyError):
            predictor.get_vowel_coords('x')

    def test_check(self):
        predictor = BaseWherePositionPredictor()
        vowels_to_check = ['b', 'c', 'n']
        try:
            predictor.check(vowels_to_check)
        except KeyError:
            self.fail("check() raised sppasKeyError unexpectedly!")

        vowels_to_check = []
        try:
            predictor.check(vowels_to_check)
        except KeyError:
            self.fail("check() raised sppasKeyError unexpectedly!")

        vowels_to_check = ['b', 'c', 'x']
        with self.assertRaises(KeyError):
            predictor.check(vowels_to_check)

    def test_calculate(self):
        # Default position of each vowel in a standard 2D face of a
        # 1000 x 1000 pixels face
        predictor = BaseWherePositionPredictor()
        predictor.set_sights_and_predict_coords()

        x, y, r = predictor.get_vowel_coords('n')
        self.assertEqual((500, 2000), (x, y))
        self.assertEqual(0, r)

        x, y, r = predictor.get_vowel_coords('b')
        self.assertEqual((190, 255), (x, y))
        self.assertEqual(0, r)

        x, y, r = predictor.get_vowel_coords('c')
        self.assertEqual((500, 950), (x, y))
        self.assertEqual(0, r)

        x, y, r = predictor.get_vowel_coords('m')
        self.assertEqual((249, 635), (x, y))
        self.assertEqual(0, r)

        x, y, r = predictor.get_vowel_coords('s')
        self.assertEqual((-333, 633), (x, y))
        self.assertEqual(0, r)

        x, y, r = predictor.get_vowel_coords('t')
        self.assertEqual((500, 1300), (x, y))
        self.assertEqual(0, r)

# ---------------------------------------------------------------------------


class TestPredictVowelPositionCustoms(unittest.TestCase):

    def test_init_(self):
        predictor = WherePositionPredictorCustoms()
        self.assertEqual(predictor.get_sights_dim(), 68)
        self.assertEqual(predictor._description, MSG_DESCRIPTION_CUSTOMS)

        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=50)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights=None)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights="invalid")
        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=-1)

    # -----------------------------------------------------------------------

    def test_calculate(self):
        # Default position of each vowel in a standard 2D face of a
        # 1000 x 1000 pixels face
        predictor = WherePositionPredictorCustoms()
        predictor.set_sights_and_predict_coords()

        x, y, r = predictor.get_vowel_coords('n')
        self.assertEqual((469, 2000), (x, y))
        self.assertEqual(200, r)

        x, y, r = predictor.get_vowel_coords('b')
        self.assertEqual((123, 300), (x, y))
        self.assertEqual(114, r)

        x, y, r = predictor.get_vowel_coords('c')
        self.assertEqual((500, 950), (x, y))
        self.assertEqual(62, r)

        x, y, r = predictor.get_vowel_coords('m')
        self.assertEqual((249, 635), (x, y))
        self.assertEqual(94, r)

        x, y, r = predictor.get_vowel_coords('s')
        self.assertEqual((-333, 695), (x, y))
        self.assertEqual(180, r)

        x, y, r = predictor.get_vowel_coords('t')
        self.assertEqual((500, 1300), (x, y))
        self.assertEqual(140, r)

# ---------------------------------------------------------------------------


class TestPredictVowelPositionObserved(unittest.TestCase):

    def test_init_(self):
        predictor = WherePositionPredictorObserved()
        self.assertEqual(predictor.get_sights_dim(), 68)
        self.assertEqual(predictor._description, MSG_DESCRIPTION_OBSERVED)

        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=50)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights=None)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights="invalid")
        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=-1)

    # -----------------------------------------------------------------------

    def test_calculate(self):
        # Default position of each vowel in a standard 2D face of a
        # 1000 x 1000 pixels face
        predictor = WherePositionPredictorObserved()
        predictor.set_sights_and_predict_coords()

        x, y, r = predictor.get_vowel_coords('n')
        self.assertEqual((469, 2000), (x, y))
        self.assertEqual(200, r)

        x, y, r = predictor.get_vowel_coords('b')
        self.assertEqual((80, 384), (x, y))  # 79,381
        self.assertEqual(44, r)  # 44

        x, y, r = predictor.get_vowel_coords('c')
        self.assertEqual((437, 917), (x, y))  # 438,916
        self.assertEqual(59, r)  # 57

        x, y, r = predictor.get_vowel_coords('m')
        self.assertEqual((255, 695), (x, y))  # 255,695
        self.assertEqual(44, r)  # 43

        x, y, r = predictor.get_vowel_coords('s')
        self.assertEqual((-425, 656), (x, y))  # -432,658
        self.assertEqual(140, r)  # 140

        x, y, r = predictor.get_vowel_coords('t')
        self.assertEqual((454, 1392), (x, y))  # 454,1392
        self.assertEqual(100, r)  # 100

# ---------------------------------------------------------------------------


class TestPredictVowelPositionUnified(unittest.TestCase):

    def test_init_(self):
        predictor = WherePositionPredictorUnified()
        self.assertEqual(predictor.get_sights_dim(), 68)
        self.assertEqual(predictor._description, MSG_DESCRIPTION_UNIFIED)

        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=50)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights=None)
        with self.assertRaises(TypeError):
            BaseWherePositionPredictor(nb_sights="invalid")
        with self.assertRaises(NotImplementedError):
            BaseWherePositionPredictor(nb_sights=-1)

    # -----------------------------------------------------------------------

    def test_calculate(self):
        # Default position of each vowel in a standard 2D face of a
        # 1000 x 1000 pixels face
        predictor = WherePositionPredictorUnified()
        predictor.set_sights_and_predict_coords()

        x, y, r = predictor.get_vowel_coords('n')
        self.assertEqual((0, 2000), (x, y))
        self.assertEqual(200, r)

        x, y, r = predictor.get_vowel_coords('b')
        self.assertEqual((144, 396), (x, y))  # 144,397
        self.assertEqual(80, r)  # 81

        x, y, r = predictor.get_vowel_coords('c')
        self.assertEqual((425, 941), (x, y))  # 425,888
        self.assertEqual(94, r)

        x, y, r = predictor.get_vowel_coords('m')
        self.assertEqual((260, 683), (x, y))  # 260,682
        self.assertEqual(85, r)

        x, y, r = predictor.get_vowel_coords('s')
        self.assertEqual((-192, 633), (x, y))  # -193,635
        self.assertEqual(237, r)

        x, y, r = predictor.get_vowel_coords('t')
        self.assertEqual((434, 1416), (x, y))  # 435,1419
        self.assertEqual(183, r)

# ---------------------------------------------------------------------------


class TestTrajectoryCoords(unittest.TestCase):

    def test_init(self):
        c = Trajectory([(2, 2), (2, 4)])
        with self.assertRaises(ValueError):
            course = Trajectory([])
        with self.assertRaises(ValueError):
            course = Trajectory([(1, 2)])

    def test_straight(self):
        course = Trajectory([(2, 2), (2, 2)])
        self.assertEqual(0, len(course.straight()))
        course = Trajectory([(2, 2), (3, 2)])
        self.assertEqual(0, len(course.straight()))

        course = Trajectory([(2, 2), (4, 2)])
        coords = course.straight()
        self.assertEqual(1, len(coords))
        self.assertEqual(3, coords[0].x)
        self.assertEqual(2, coords[0].y)

        course = Trajectory([(100, 100), (200, 200)])
        coords = course.straight()
        self.assertEqual(99, len(coords))
        self.assertEqual(101, coords[0].x)
        self.assertEqual(101, coords[0].y)
        self.assertEqual(151, coords[50].x)
        self.assertEqual(151, coords[50].y)

    def test_steps(self):
        course = Trajectory([(100, 100), (200, 200)])
        coords = course.steps(1)
        self.assertEqual(1, len(coords))
        self.assertEqual(150, coords[0].x)
        self.assertEqual(150, coords[0].y)
        coords = course.steps(2)
        self.assertEqual(2, len(coords))
        self.assertEqual(134, coords[0].x)
        self.assertEqual(134, coords[0].y)
        self.assertEqual(167, coords[1].x)
        self.assertEqual(167, coords[1].y)
