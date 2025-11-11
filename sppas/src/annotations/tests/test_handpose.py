"""
:filename: sppas.src.annotations.tests.test_handpose.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Hand & Pose automatic annotation.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

import os
import unittest

from sppas.core.config import paths
from sppas.src.imgdata import sppasImage

from sppas.src.annotations.HandPose.imgsightswriter import sppasHandsSightsImageWriter
from sppas.src.annotations.HandPose.mphanddetect import MediaPipeHandPoseDetector

# ---------------------------------------------------------------------------

SAMPLES = os.path.join(paths.samples, "faces")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestMediaPipeHandDetection(unittest.TestCase):

    def test_init(self):
        d = MediaPipeHandPoseDetector()
        self.assertIsNone(d._detector)

        with MediaPipeHandPoseDetector() as mhp:
            self.assertIsInstance(mhp, MediaPipeHandPoseDetector)
            self.assertIsNone(mhp._detector)

    def test_set_detector(self):
        md = MediaPipeHandPoseDetector()
        md._set_detector()

    def test_instantiate(self):
        md = MediaPipeHandPoseDetector()
        md.load_model("whatever")

        with MediaPipeHandPoseDetector() as mhp:
            self.assertIsInstance(mhp, MediaPipeHandPoseDetector)
            self.assertIsNone(mhp._detector)
            mhp.load_model()
            self.assertIsNotNone(mhp._detector)

    def test_hand_detection(self):
        md = MediaPipeHandPoseDetector()
        md.load_model()

        # Only one hand in the image
        fn = os.path.join(DATA, "handcue-5.png")
        img = sppasImage(filename=fn)
        md.detect_hands(img)
        self.assertEqual(1, len(md))
        fn = os.path.join(DATA, "handcue-5-md.png")
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=False, csv=False)
        w.write(img, [md.get_hand_sights(i) for i in range(len(md))], fn)

        fn = os.path.join(SAMPLES, "BrigitteBigiSlovenie2016.jpg")
        img = sppasImage(filename=fn)
        md.detect_hands(img)
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-hand.png")
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=False, csv=False)
        img = w.write_tagged_img(img, [md.get_hand_sights(i) for i in range(len(md))], fn)
        w.write_tagged_img(img, [md.get_hand_coordinates(i) for i in range(len(md))], fn)
        self.assertEqual(1, len(md))

    def test_multihands_detection(self):
        md = MediaPipeHandPoseDetector()
        md.load_model()
        fn = os.path.join(SAMPLES, "BrigitteBigi_Aix2020.png")

        # Multi-speaker: many hands! (should be 6)
        img = sppasImage(filename=fn)
        md.detect_hands(img)
        fn = os.path.join(DATA, "BrigitteBigi_Aix2020-hand.png")
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=True, csv=True)
        # w.write(img, [[md.get_hand_sights(i) for i in range(len(md))], [md.get_hand_coordinates(i) for i in range(len(md))]], fn)
        img = w.write_tagged_img(img, [md.get_hand_sights(i) for i in range(len(md))], fn)
        w.write_tagged_img(img, [md.get_hand_coordinates(i) for i in range(len(md))], fn)
        self.assertEqual(4, len(md))

    def test_pose_detection(self):
        md = MediaPipeHandPoseDetector()
        md.load_model()

        fn = os.path.join(SAMPLES, "BrigitteBigiSlovenie2016.jpg")
        img = sppasImage(filename=fn)
        md.detect_pose(img)
        self.assertEqual(2, len(md))   # 1 pose == 2 hands!
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-pose.png")
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=False, csv=False)
        w.write(img, [md.get_pose_sights()], fn)

        fn = os.path.join(SAMPLES, "BrigitteBigi_Aix2020.png")
        img = sppasImage(filename=fn)
        md.detect_pose(img)
        self.assertEqual(2, len(md))   # 1 pose == 2 hands!
        fn = os.path.join(DATA, "BrigitteBigi_Aix2020-pose.png")
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=False, csv=False)
        w.write(img, [md.get_pose_sights()], fn)

    def test_detect(self):
        md = MediaPipeHandPoseDetector()
        md.load_model()
        w = sppasHandsSightsImageWriter()
        w.set_options(tag=True, xra=False, csv=False)

        fn = os.path.join(SAMPLES, "BrigitteBigi_Aix2020.png")
        img = sppasImage(filename=fn)
        success_value = md.detect(img)
        self.assertEqual(success_value, 2)   # 1 pose, 2 hands detected
        self.assertEqual(2, len(md))   # 1 pose == 2 hands!
        fn = os.path.join(DATA, "BrigitteBigi_Aix2020-poha.png")
        p = [md.get_pose_sights()]
        s = [md.get_hand_sights(i) for i in range(len(md))]
        c = [md.get_hand_coordinates(i) for i in range(len(md))]
        # p, s and c will have 3 different colors
        w.write(img, [p, s, c], fn)

        fn = os.path.join(SAMPLES, "BrigitteBigiSlovenie2016.jpg")
        img = sppasImage(filename=fn)
        success_value = md.detect(img)
        self.assertEqual(success_value, 1)   # 1 pose, 1 hand detected
        self.assertEqual(2, len(md))         # 1 pose == 2 hands!
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-poha.png")
        p = [md.get_pose_sights()]
        s = [md.get_hand_sights(i) for i in range(len(md))]
        c = [md.get_hand_coordinates(i) for i in range(len(md))]
        # p, s and c will have 3 different colors
        w.write(img, p+s+c, fn)
