"""
:filename: tests.annotations.test_facedetection.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of Face Detection automatic annotation.

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

import os
import unittest

from sppas.core.config import paths
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoordsImageWriter

from sppas.src.imgdata import HaarCascadeDetector
from sppas.src.imgdata import NeuralNetCaffeDetector
from sppas.src.imgdata import NeuralNetTensorFlowDetector

from sppas.src.annotations.FaceDetection.imgfacedetect import ImageFaceDetection
from sppas.src.annotations.FaceDetection.mpfacedetect import MediaPipeFaceDetector
from sppas.src.annotations.FaceDetection.yunetfacedetect import YuNetFaceDetector

# ---------------------------------------------------------------------------

MANUAL_CHECK_OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manual-check-out")

# ---------------------------------------------------------------------------


def setUpModule():
    if os.path.exists(MANUAL_CHECK_OUT) is False:
        os.mkdir(MANUAL_CHECK_OUT)




# ---------------------------------------------------------------------------


DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

NETCAFFE = os.path.join(paths.resources, "faces", "res10_300x300_ssd_iter_140000_fp16.caffemodel")
NETTS = os.path.join(paths.resources, "faces", "opencv_face_detector_uint8.pb")
HAAR1 = os.path.join(paths.resources, "faces", "haarcascade_profileface.xml")
HAAR2 = os.path.join(paths.resources, "faces", "haarcascade_frontalface_alt.xml")
HAAR3 = os.path.join(paths.resources, "faces", "lbpcascade_frontalface_improved.xml")
MPFACE = os.path.join(paths.resources, "faces", "blaze_face_short_range.tflite")
YUNET = os.path.join(paths.resources, "faces", "face_detection_yunet_2023mar.onnx")
# HAAR3 model seems to give worse results than the other ones...

# ---------------------------------------------------------------------------


class TestYuNetFaceDetection(unittest.TestCase):

    def test_init(self):
        d = YuNetFaceDetector()
        self.assertIsNone(d._detector)
        self.assertEqual(d.get_extension(), ".onnx")

    def test_instantiate(self):
        yd = YuNetFaceDetector()
        with self.assertRaises(IOError):
            yd.load_model("whatever")
        yd.load_model(YUNET)
        self.assertIsNotNone(yd._detector)

    def test_detection(self):
        yd = YuNetFaceDetector()
        yd.load_model(YUNET)

        # Nothing should be detected -- it's just the sea
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            yd.detect(fn)
        img = sppasImage(filename=fn)
        yd.detect(img)
        self.assertEqual(0, len(yd))

        # I should be detected...
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        img = sppasImage(filename=fn)
        yd.detect(img)
        self.assertEqual(1, len(yd))

    def test_montage_detection(self):
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)

        yd = YuNetFaceDetector()
        yd.load_model(YUNET)
        yd.set_min_ratio(0.01)
        yd.detect(img)
        coords = [c.copy() for c in yd]
        w = sppasCoordsImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces-yn.png")
        w.write(img, coords, fn)
        # There are 3 faces in the montage image. A weak false positive
        # remains detected, with a low squared score: the recall is
        # privileged, the fusion of the systems removes such detections.
        self.assertEqual(4, len(yd))
        self.assertEqual(3, len(yd.get_confidence(0.7)))

# ---------------------------------------------------------------------


class TestMediaPipeFaceDetection(unittest.TestCase):

    def test_init(self):
        d = MediaPipeFaceDetector()
        self.assertIsNone(d._detector)
        self.assertEqual(d.get_extension(), ".tflite")

    def test_set_detector(self):
        md = MediaPipeFaceDetector()
        md._set_detector(MPFACE)
        self.assertIsNotNone(md._detector)

    def test_instantiate(self):
        md = MediaPipeFaceDetector()
        with self.assertRaises(IOError):
            md.load_model("whatever")
        md.load_model(MPFACE)
        self.assertIsNotNone(md._detector)

    def test_detection(self):
        w = sppasCoordsImageWriter()
        w.set_options(tag=True)

        md = MediaPipeFaceDetector()
        md.load_model(MPFACE)

        # Nothing should be detected -- it's just the sea
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            md.detect(fn)
        img = sppasImage(filename=fn)
        md.detect(img)
        self.assertEqual(0, len(md))

        # I should be detected...
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        img = sppasImage(filename=fn)   # (w, h) = (1632, 916)
        md.detect(img)
        self.assertEqual(1, len(md))
        fn = os.path.join(MANUAL_CHECK_OUT, "BrigitteBigi-Slovenia2016-md.png")
        w.write(img, [md.get_best()], fn)

        # Kasia and I should be detected, but the picture was damaged.
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)   # (w, h) = (1632, 916)
        md.detect(img)
        self.assertEqual(0, len(md))  # should be 2

    def test_montage_detection(self):
        # MediaPipe
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)
        w = sppasCoordsImageWriter()
        w.set_options(tag=True)

        # Pictures extracted from a video. I'm moving, so my face is blurry!
        # I'm in the pictures three times, but Mediapipe fails to detect me once.
        md = MediaPipeFaceDetector()
        md.load_model(MPFACE)
        md.set_min_ratio(0.01)
        md.detect(img)
        coords = [c.copy() for c in md]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces-md.png")
        w.write(img, coords, fn)
        self.assertEqual(2, len(md))  # it should be 3

# ---------------------------------------------------------------------------


class TestHaarCascadeFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = ImageFaceDetection()
        fd.load_model(HAAR1)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # Nothing should be detected -- it's just the sea
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(0, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_one_face_good_img_quality(self):
        fd = ImageFaceDetection()
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        img = sppasImage(filename=fn)

        # Load HAAR1: the profile model.
        # No profile face in the image. Test with BGR and RGB images.
        fd.load_model(HAAR1)
        fd.detect(img)
        self.assertEqual(0, len(fd))
        fd.detect(img.ito_rgb())
        self.assertEqual(0, len(fd))

        # Load HAAR2: Only 1 frontal face in the image
        fd.load_model(HAAR2)
        fd.detect(img)
        self.assertGreaterEqual(1, len(fd))
        fd.detect(img.ito_rgb())
        self.assertGreaterEqual(1, len(fd))

        # Load HAAR3:  Only 1 frontal face in the image but 2 detected
        fd.load_model(HAAR3)
        fd.detect(img)
        self.assertGreaterEqual(2, len(fd))
        fd.detect(img.ito_rgb())
        self.assertGreaterEqual(2, len(fd))

        # Combining all cascade detectors
        fd.load_model(HAAR1, HAAR2, HAAR3)
        fd.set_min_ratio(0.1)
        fd.detect(img)
        self.assertEqual(1, len(fd))
        fd.detect(img.ito_rgb())
        self.assertEqual(1, len(fd))

        # use a range because depending on the system and cv2 version, results
        # can be different...
        self.assertTrue(fd[0].x in range(870, 880))
        self.assertTrue(fd[0].y in range(215, 225))
        self.assertTrue(fd[0].w in range(180, 200))
        self.assertTrue(fd[0].h in range(180, 198))

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        # 3 faces should be found: OK if img is BGR but worse result with RGB
        fd = ImageFaceDetection()
        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)
        w = sppasCoordsImageWriter()
        w.set_options(tag=True)

        # With the profile model
        # ----------------------
        fd.load_model(HAAR1)

        # with the default min score
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-haarprofilefaces.png")
        w.write(img, coords, fn)
        self.assertEqual(3, len(fd))

        # will detect the same because haar system is normalizing weights
        # with the min score
        fd.set_min_score(0.067)
        fd.detect(img)
        # coords = [c.copy() for c in fd]
        # fn = os.path.join(MANUAL_CHECK_OUT, "montage-haarprofilefaces.png")
        # w.write(img, coords, fn)
        self.assertEqual(3, len(fd))

        # With the frontal model 1
        # ------------------------
        fd.set_min_score(ImageFaceDetection.DEFAULT_MIN_SCORE)
        fd.load_model(HAAR2)
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-haarfrontfaces1.png")
        w.write(img, coords, fn)
        self.assertEqual(5, len(fd))

        # With the frontal model 2
        # ------------------------
        fd.load_model(HAAR3)
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-haarfrontfaces2.png")
        w.write(img, coords, fn)
        self.assertEqual(2, len(fd))

        # With both models 1 & 2
        # ----------------------
        fd.load_model(HAAR1, HAAR2)
        fd.detect(img)
        self.assertEqual(5, len(fd))

        # With both models 1 & 3: the expected result (3 faces)
        # ----------------------
        fd.load_model(HAAR1, HAAR3)
        fd.detect(img)
        self.assertEqual(3, len(fd))

        # With both models 2 & 3
        # ----------------------
        fd.load_model(HAAR3, HAAR2)
        fd.detect(img)
        self.assertEqual(5, len(fd))

        # With all 3 models: the expected result (3 faces)
        # ----------------------
        fd.load_model(HAAR1, HAAR2, HAAR3)
        fd.detect(img)

        w = sppasCoordsImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces.png")
        w.write(img, [c.copy() for c in fd], fn)
        self.assertEqual(3, len(fd))

# ---------------------------------------------------------------------------


class TestDNNCaffeFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # Nothing should be detected -- it's just the sea
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(0, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_one_face_good_img_quality(self):
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        self.assertEqual(0, len(fd))

        # only one face should be detected
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)

        # BGR image
        fd.detect(img)
        self.assertEqual(1, len(fd))
        coords = fd.get_best()
        self.assertTrue(coords.x in range(885, 895))
        self.assertTrue(coords.y in range(220, 228))
        self.assertTrue(coords.w in range(163, 178))
        self.assertTrue(coords.h in range(184, 195))
        self.assertGreater(coords.get_confidence(), 0.99)

        # RGB image
        fd.detect(img.ito_rgb())
        self.assertEqual(1, len(fd))
        coords = fd.get_best()
        self.assertTrue(coords.x in range(885, 895))
        self.assertTrue(coords.y in range(220, 228))
        self.assertTrue(coords.w in range(163, 178))
        self.assertTrue(coords.h in range(184, 195))
        self.assertGreater(coords.get_confidence(), 0.99)

        # ------------------------------------------------------------------------

    def test_detect_to_portrait(self):
        # The detected box depends on the opencv version: the exact
        # values of portrait() are asserted by test_to_portrait, here
        # only the application of portrait() to the detected coords.
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        fn = os.path.join(DATA, "BrigitteBigiSlovenie2016.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(1, len(fd))
        detected = fd.get_best().copy()

        fd.to_portrait(img)
        coords = fd.get_best()
        self.assertEqual(coords, detected.portrait(img))
        cropped = sppasImage(input_array=img.icrop(coords))

        fn_detected = os.path.join(MANUAL_CHECK_OUT, "BrigitteBigiSlovenie2016-portrait.jpg")
        cropped.write(fn_detected)

        face = sppasImage(filename=fn_detected)
        self.assertEqual(len(cropped), len(face))
        for r1, r2 in zip(cropped, face):
            self.assertEqual(len(r1), len(r2))
            for c1, c2 in zip(r1, r2):
                self.assertTrue(len(c1), 3)
                self.assertTrue(len(c2), 3)
                # we can't compare values, they are close but not equals!

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(3, len(fd))

        fd.detect(img.ito_rgb())
        coords = [c.copy() for c in fd]

        w = sppasCoordsImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-dnnfaces.png")
        w.write(img, coords, fn)
        self.assertEqual(3, len(fd))

# ---------------------------------------------------------------------------


class TestDNNTensorFlowFaceDetection(unittest.TestCase):

    def test_detect_nothing(self):
        fd = ImageFaceDetection()
        fd.load_model(NETTS)
        self.assertEqual(0, len(fd))

        # Nothing should be detected -- it's just the sea
        fn = os.path.join(DATA, "Slovenia2016Sea.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(0, len(fd))

    # ------------------------------------------------------------------------

    def test_detect_one_face_good_img_quality(self):
        fd = ImageFaceDetection()
        fd.load_model(NETTS)

        # only one face should be detected
        fn = os.path.join(DATA, "BrigitteBigi-Slovenie2016.jpg")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        self.assertEqual(1, len(fd))

        fd.detect(img.ito_rgb())
        self.assertEqual(1, len(fd))

        coords = fd.get_best()
        self.assertTrue(coords.x in range(885, 895))
        self.assertTrue(coords.y in range(210, 225))
        self.assertTrue(coords.w in range(160, 178))
        self.assertTrue(coords.h in range(180, 195))
        self.assertGreater(coords.get_confidence(), 0.99)

    # ------------------------------------------------------------------------

    def test_detect_montage(self):
        fd = ImageFaceDetection()
        fd.load_model(NETTS)
        # Nothing detected... we still didn't asked for
        self.assertEqual(0, len(fd))

        # The image we'll work on, with 3 faces to be detected
        fn = os.path.join(DATA, "montage.png")
        with self.assertRaises(TypeError):
            fd.detect(fn)
        img = sppasImage(filename=fn)
        fd.detect(img)
        coords = [c.copy() for c in fd]

        w = sppasCoordsImageWriter()
        w.set_options(tag=True)
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-dnnfaces.png")
        w.write(img, coords, fn)
        self.assertEqual(3, len(fd))

        fd.set_min_score(0.3)
        fd.detect(img)
        self.assertEqual(3, len(fd))

# ---------------------------------------------------------------------------


class TestFaceDetection(unittest.TestCase):

    def test_load_model(self):
        fd = ImageFaceDetection()
        self.assertIsNone(fd._detector)
        self.assertEqual(fd.get_nb_recognizers(), 0)

        with self.assertRaises(IOError):
            fd.load_model("toto.txt")

        fd.load_model(NETCAFFE)
        self.assertIsNotNone(fd._detector)
        self.assertEqual(len(fd._detector), 1)
        self.assertEqual(fd.get_nb_recognizers(), 1)
        names = fd.get_recognizer_names()
        self.assertIsInstance(fd.get_recognizer(names[0]), NeuralNetCaffeDetector)

        fd.load_model(NETTS)
        self.assertEqual(fd.get_nb_recognizers(), 1)
        names = fd.get_recognizer_names()
        self.assertIsInstance(fd.get_recognizer(names[0]), NeuralNetTensorFlowDetector)

        fd.load_model(HAAR1)
        self.assertIsNotNone(fd._detector)
        names = fd.get_recognizer_names()
        self.assertIsInstance(fd.get_recognizer(names[0]), HaarCascadeDetector)

        fd.load_model(MPFACE)
        self.assertIsNotNone(fd._detector)
        names = fd.get_recognizer_names()
        self.assertIsInstance(fd.get_recognizer(names[0]), MediaPipeFaceDetector)

        fd.load_model(YUNET)
        self.assertIsNotNone(fd._detector)
        names = fd.get_recognizer_names()
        self.assertIsInstance(fd.get_recognizer(names[0]), YuNetFaceDetector)

        fd.load_model(HAAR1, NETCAFFE, HAAR2)
        self.assertEqual(len(fd._detector), 3)
        self.assertEqual(fd.get_nb_enabled_recognizers(), 3)

        fd.load_model(HAAR3)
        self.assertEqual(len(fd._detector), 1)

    # ------------------------------------------------------------------------

    def test_enable_recognizers(self):
        fd = ImageFaceDetection()
        fd.load_model(HAAR1, HAAR2, HAAR3, NETCAFFE, NETTS)
        names = fd.get_recognizer_names()
        self.assertEqual(len(names), 5)
        self.assertEqual(fd.get_nb_enabled_recognizers(), 5)

        # disable HAAR2 and HAAR3
        fd.enable_recognizer(names[1], False)
        self.assertEqual(fd.get_nb_enabled_recognizers(), 4)
        fd.enable_recognizer("lbpcascade_frontalface_improved.xml", False)
        self.assertEqual(fd.get_nb_enabled_recognizers(), 3)

    # ------------------------------------------------------------------------

    def test_to_portrait(self):
        fd = ImageFaceDetection()
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)   # (w, h) = (1632, 916)

        # normal situation: scale (2.6, 3.0), xy ratio 0.875, y at top
        fd.invalidate()
        fd._coords.append(sppasCoords(200, 200, 150, 150))
        self.assertEqual(fd[0], sppasCoords(200, 200, 150, 150))
        fd.to_portrait(img)
        self.assertEqual(fd[0], sppasCoords(79, 125, 393, 450))

        # coords at top-left (can't fully shift x and y)
        fd.invalidate()
        fd._coords.append(sppasCoords(10, 10, 100, 100))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [0, 0, 262, 300])

        # coords at bottom-right (can't fully shift x and y)
        fd.invalidate()
        fd._coords.append(sppasCoords(1500, 850, 100, 60))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [1372, 619, 260, 297])

        # the 3rd face in montage.png
        fd.invalidate()
        fd._coords.append(sppasCoords(1546, 253, 276, 276))
        fd.to_portrait(img)
        self.assertEqual(fd[0], [908, 88, 724, 828])

    # ------------------------------------------------------------------------

    def test_contains(self):
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)
        fd.detect(img)
        # print(fd)
        self.assertFalse((0, 0, 97, 117) in fd)
        try:
            # Linux, Python 3.6, opencv 4.4.0
            # self.assertTrue(sppasCoords(927, 238, 97, 117) in fd)
            # Linux, Python 3.6, opencv 4.5.5
            self.assertTrue(sppasCoords(934, 244, 82, 104) in fd)
        except AssertionError:
            # Windows10, Python 3.8, opencv 4.2.0
            self.assertTrue(sppasCoords(925, 239, 97, 117) in fd)

    # ------------------------------------------------------------------------

    def test_getters(self):
        fd = ImageFaceDetection()
        fd.load_model(NETCAFFE)
        # The image we'll work on
        fn = os.path.join(DATA, "Slovenia2016.jpg")
        img = sppasImage(filename=fn)

        fd.detect(img)
        # The photo is damaged: only one of its two faces is detected.
        # The exact box depends on the opencv version.
        self.assertEqual(1, len(fd))

        # get best
        coords = fd.get_best()
        self.assertEqual(coords, fd[0])

        # get more coords than those detected
        coords = fd.get_best(3)
        self.assertEqual(coords[0], fd[0])
        self.assertIsNone(coords[1])
        self.assertIsNone(coords[2])

        # get confidence
        best_score = fd[0].get_confidence()
        coords = fd.get_confidence(best_score - 0.01)
        self.assertEqual(len(coords), 1)
        coords = fd.get_confidence(1.0)
        self.assertEqual(len(coords), 0)

    # ------------------------------------------------------------------------

    def test_multi_detect(self):
        fd = ImageFaceDetection()
        fd.load_model(NETTS, NETCAFFE, HAAR3, HAAR1, HAAR2, MPFACE)
        names = fd.get_recognizer_names()
        self.assertEqual(names[0], 'opencv_face_detector_uint8.pb')
        self.assertEqual(names[1], 'res10_300x300_ssd_iter_140000_fp16.caffemodel')
        self.assertEqual(names[2], 'lbpcascade_frontalface_improved.xml')
        self.assertEqual(names[3], 'haarcascade_profileface.xml')
        self.assertEqual(names[4], 'haarcascade_frontalface_alt.xml')
        self.assertEqual(names[5], 'blaze_face_short_range.tflite')

        fn = os.path.join(DATA, "montage.png")
        img = sppasImage(filename=fn)
        w = sppasCoordsImageWriter()
        w.set_options(tag=True)

        # All Artificial Neural Networks
        fd.enable_recognizer(names[0], True)
        fd.enable_recognizer(names[1], True)
        fd.enable_recognizer(names[2], False)
        fd.enable_recognizer(names[3], False)
        fd.enable_recognizer(names[4], False)
        fd.enable_recognizer(names[5], True)
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces-dnn.png")
        w.write(img, coords, fn)
        # There are 3 faces in the montage image.
        self.assertEqual(3, len(fd))

        # Haar cascade classifiers only
        fd.enable_recognizer(names[0], False)
        fd.enable_recognizer(names[1], False)
        fd.enable_recognizer(names[2], True)
        fd.enable_recognizer(names[3], True)
        fd.enable_recognizer(names[4], True)
        fd.enable_recognizer(names[5], False)
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces-haar.png")
        w.write(img, coords, fn)
        self.assertEqual(3, len(fd))

        # All models
        for name in names:
            fd.enable_recognizer(name, True)
        fd.detect(img)
        coords = [c.copy() for c in fd]
        fn = os.path.join(MANUAL_CHECK_OUT, "montage-faces-all.png")
        w.write(img, coords, fn)
        self.assertEqual(4, len(fd))  # Mickey Mouse is detected
