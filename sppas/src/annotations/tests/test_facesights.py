"""
:filename: sppas.src.annotations.tests.test_facesights.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Face lanmarks automatic annotation.

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

import os
import unittest

from sppas.core.config import paths
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoords

from sppas.src.annotations.FaceDetection import ImageFaceDetection
from sppas.src.annotations.FaceSights.imgsightswriter import sppasFaceSightsImageWriter
from sppas.src.annotations.FaceSights.imgfacemark import ImageFaceLandmark
from sppas.src.annotations.FaceSights.videofacemark import VideoFaceLandmark
from sppas.src.annotations.FaceSights.opencvmark import OpenCVFaceMark
from sppas.src.annotations.FaceSights.basemark import BasicFaceMark
from sppas.src.annotations.FaceSights.mpmark import MediaPipeFaceMesh

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL_LBF68 = os.path.join(paths.resources, "faces", "lbfmodel68.yaml")
MODEL_DAT = os.path.join(paths.resources, "faces", "kazemi_landmark.dat")
# --> not efficient: os.path.join(paths.resources, "faces", "aam.xml")

NET = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
HAAR1 = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR2 = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")

# ---------------------------------------------------------------------------


class TestBasicFaceMark(unittest.TestCase):

    def test_init(self):
        d = BasicFaceMark()
        self.assertIsNone(d._detector)
        with self.assertRaises(TypeError):
            d.detect_sights("a filename", sppasCoords(0, 0, 0, 0))

    def test_detection(self):
        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        img = sppasImage(filename=fn)

        # Face detection
        fd = ImageFaceDetection()
        fd.load_model(HAAR2)
        fd.detect(img)
        coords = fd.get_best()

        # Basic Face Mark
        fl = BasicFaceMark()
        success = fl.detect_sights(img, coords)
        self.assertTrue(success)

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-basicmark.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(img, [c for c in fl.get_sights()], fn)

# ---------------------------------------------------------------------------


class TestMediaPipeFaceMark(unittest.TestCase):

    def test_init(self):
        d = MediaPipeFaceMesh()
        self.assertIsNotNone(d._detector)

    def test_detection_nothing(self):
        md = MediaPipeFaceMesh()
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            md.detect_sights(fn)
        img = sppasImage(filename=fn)
        success = md.detect_sights(img)
        self.assertFalse(success)

    def test_detection(self):
        fl = MediaPipeFaceMesh()

        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        img = sppasImage(filename=fn)

        success = fl.detect_sights(img)
        self.assertTrue(success)
        self.assertIsNone(fl.get_mesh())

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-mpmark.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(img, [c for c in fl.get_sights()], fn)

# ---------------------------------------------------------------------------


class TestMediaPipeFaceMesh(unittest.TestCase):

    def test_detection(self):
        fl = MediaPipeFaceMesh()
        self.assertIsNotNone(fl._detector)
        fl.enable_mesh()

        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        img = sppasImage(filename=fn)

        success = fl.detect_sights(img)
        self.assertTrue(success)
        self.assertIsNotNone(fl.get_mesh())

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-mpmesh.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(img, [c for c in fl.get_mesh()], fn)

# ---------------------------------------------------------------------------


class TestOpenCVFaceMark(unittest.TestCase):

    def setUp(self):
        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        self.img = sppasImage(filename=fn)

        # Face detection
        fd = ImageFaceDetection()
        fd.load_model(HAAR2)
        fd.detect(self.img)
        self.coords = fd.get_best()

    def test_detection_yaml(self):
        fl = OpenCVFaceMark(MODEL_LBF68)
        success = fl.detect_sights(self.img, self.coords)
        self.assertTrue(success)

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-yamlmark.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(self.img, [c for c in fl.get_sights()], fn)

    def test_detection_dat(self):
        fl = OpenCVFaceMark(MODEL_DAT)
        success = fl.detect_sights(self.img, self.coords)
        self.assertTrue(success)

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-datmark.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(self.img, [c for c in fl.get_sights()], fn)

# ---------------------------------------------------------------------------


class TestImageFaceLandmark(unittest.TestCase):

    def test_load_resources(self):
        fl = ImageFaceLandmark()
        self.assertEqual(68, len(fl))
        with self.assertRaises(IOError):
            fl.add_model("toto.txt")

        fl.add_model(MODEL_LBF68)
        fl.add_model(MODEL_DAT)
        self.assertTrue(fl.get_nb_recognizers(), 4)

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = ImageFaceLandmark()
        # access to the private list of landmarks and set a point
        fd._sights.set_sight(0, 124, 235)
        self.assertTrue((124, 235, None) in fd)
        self.assertFalse((24, 35, None) in fd)
        self.assertTrue((124, 235) in fd)
        self.assertTrue([124, 235, None, 0] in fd)
        self.assertFalse((24, 35, 0, 0) in fd)

    # ------------------------------------------------------------------------

    def test_mark_nothing(self):
        # Nothing should be marked. No face in the image
        fl = ImageFaceLandmark()
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        img = sppasImage(filename=fn)

        # MediaPipe only
        success = fl.detect_sights(img, sppasCoords(0, 0, 100, 100))
        self.assertFalse(success)

        # OpenCV
        fl.add_model(MODEL_LBF68)
        fl.add_model(MODEL_DAT)
        success = fl.detect_sights(img, sppasCoords(0, 0, 100, 100))
        # this should be false but OpenCV always returns sights -- because
        # it doesn't do the face detection!
        self.assertTrue(success)

    # ------------------------------------------------------------------------

    def test_mark_normal(self):
        fd = ImageFaceDetection()
        fd.load_model(HAAR2)
        fl = ImageFaceLandmark()
        fl.add_model(MODEL_LBF68)
        fl.add_model(MODEL_DAT)

        # The image we'll work on
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-portrait.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)
        coords = fd.get_best()
        fl.detect_sights(img, coords)

        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016-sights.jpg")
        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        w.write(img, [c for c in fl], fn)

    # ------------------------------------------------------------------------

    def test_mark_montage(self):
        fl = ImageFaceLandmark()
        fl.add_model(MODEL_LBF68)

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)

        fd = ImageFaceDetection()
        fd.load_model(HAAR1, HAAR2, NET)
        fd.detect(img)
        self.assertEqual(len(fd), 4)

        w = sppasFaceSightsImageWriter()
        w.set_options(tag=True)
        for i, coord in enumerate(fd):
            try:
                fn = os.path.join(DATA, "montage_{:d}-sights.jpg".format(i))
                fl.detect_sights(img, coord)
                w.write(img, [c for c in fl], fn)
            except Exception as e:
                print("Error for coords {}: {}".format(i, str(e)))

# ---------------------------------------------------------------------------


class TestVideoFaceLandmark(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    # -----------------------------------------------------------------------

    def test_detect(self):
        fld = ImageFaceDetection()
        fld.load_model(NET)
        fli = ImageFaceLandmark()
        fli.add_model(MODEL_LBF68)
        fli.add_model(MODEL_DAT)

        # no valid faces
        flv = VideoFaceLandmark(fli)
        with self.assertRaises(Exception):
            flv.video_face_sights(TestVideoFaceLandmark.VIDEO)
        with self.assertRaises(Exception):
            flv.video_face_sights(TestVideoFaceLandmark.VIDEO, csv_faces="toto.csv")

        flv = VideoFaceLandmark(fli, fld)
        results = flv.video_face_sights(TestVideoFaceLandmark.VIDEO)
