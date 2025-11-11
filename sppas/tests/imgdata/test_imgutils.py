"""
:filename: sppas.src.imgdata.tests.test_imgutils.py
:author:   Florian Hocquet, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of the image utility class.

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

from sppas.src.imgdata.image import sppasImage
from sppas.src.imgdata.imageutils import sppasImageCompare

# ---------------------------------------------------------------------------


class TestImageCompare(unittest.TestCase):

    IMAGE1 = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
    IMAGE2 = os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png")

    def test_compare_distance(self):
        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = sppasImage(filename=TestImageCompare.IMAGE2)

        comp = sppasImageCompare(img1, img2)
        # print(comp.compare_with_distance())
        # print(comp.compare_with_mse())
        # print(comp.compare_with_kld())
        # print(comp.compare_areas())
        # print(comp.compare_sizes())

    def test_compare_areas(self):
        img1 = sppasImage(0).blank_image(w=100, h=100)

        # 2 identical areas: score=1.
        img2 = img1.copy()
        self.assertEqual(1., sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=10, h=1000)
        self.assertEqual(1., sppasImageCompare(img1, img2).compare_areas())

        # two different sizes, with img is large
        img1 = sppasImage(0).blank_image(w=1000, h=1000)

        img2 = sppasImage(0).blank_image(w=10, h=10)
        self.assertEqual(0.0001, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=200, h=200)
        self.assertEqual(0.04, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=800, h=800)
        self.assertEqual(0.64, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=1200, h=1200)
        self.assertEqual(0.69, round(sppasImageCompare(img1, img2).compare_areas(), 2))

        # two different sizes, with img is small
        img1 = sppasImage(0).blank_image(w=64, h=64)
        img2 = sppasImage(0).blank_image(w=16, h=16)
        self.assertEqual(0.0625, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=48, h=48)
        self.assertEqual(0.5625, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=128, h=128)
        self.assertEqual(0.25, sppasImageCompare(img1, img2).compare_areas())
        img2 = sppasImage(0).blank_image(w=1024, h=128)
        self.assertEqual(0.03125, sppasImageCompare(img1, img2).compare_areas())

    def test_compare_sizes(self):
        img1 = sppasImage(0).blank_image(w=100, h=100)

        # 2 identical sizes: score=1.
        img2 = img1.copy()
        self.assertEqual(1., sppasImageCompare(img1, img2).compare_sizes())

        # one very small, one big
        img2 = sppasImage(0).blank_image(w=10, h=1000)
        self.assertEqual(0.1, sppasImageCompare(img1, img2).compare_sizes())

        # one side identical, the other very different
        img2 = sppasImage(0).blank_image(w=100, h=1000)
        self.assertEqual(0.55, sppasImageCompare(img1, img2).compare_sizes())

        # two approaching sides
        img2 = sppasImage(0).blank_image(w=80, h=80)
        self.assertEqual(0.8, sppasImageCompare(img1, img2).compare_sizes())
        img2 = sppasImage(0).blank_image(w=120, h=120)
        self.assertEqual(0.833, round(sppasImageCompare(img1, img2).compare_sizes(), 3))

    def test_mse(self):
        img1 = sppasImage(0).blank_image(w=100, h=100)
        img2 = img1.copy()
        result = sppasImageCompare(img1, img2).mse()
        self.assertEqual(0., result)

        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = sppasImage(filename=TestImageCompare.IMAGE1)
        self.assertEqual(0., sppasImageCompare(img1, img2).mse())

        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        self.assertEqual(30697, int(sppasImageCompare(img1, img1.ired()).mse()))
        self.assertEqual(47176, int(sppasImageCompare(img1, img1.iblue()).mse()))
        self.assertEqual(10410, int(sppasImageCompare(img1, img1.igreen()).mse()))

        img2 = sppasImage(filename=TestImageCompare.IMAGE2)
        self.assertEqual(32221, int(sppasImageCompare(img2, img2.ired()).mse()))
        self.assertEqual(45220, int(sppasImageCompare(img2, img2.iblue()).mse()))
        self.assertEqual(6518, int(sppasImageCompare(img2, img2.igreen()).mse()))
        #
        # self.assertEqual(5817, int(sppasImageCompare(img1, img2).mse()))
        #
        # self.assertEqual(13742, int(sppasImageCompare(img1, img2.ired()).mse()))
        # self.assertEqual(17356, int(sppasImageCompare(img1, img2.iblue()).mse()))
        # self.assertEqual(6499, int(sppasImageCompare(img1, img2.igreen()).mse()))
        # self.assertEqual(10764, int(sppasImageCompare(img2, img1.ired()).mse()))
        # self.assertEqual(14563, int(sppasImageCompare(img2, img1.iblue()).mse()))
        # self.assertEqual(6013, int(sppasImageCompare(img2, img1.igreen()).mse()))

        # image is cropped
        w1, h1 = img1.size()
        self.assertEqual(2548, int(sppasImageCompare(img1, img1.icrop([12, 8, w1-20, h1+20])).mse()))

    def test_compare_with_mse(self):
        # 2 identical images: score=1.
        img1 = sppasImage(0).blank_image(w=100, h=100)
        img2 = img1.copy()
        result = sppasImageCompare(img1, img2).compare_with_mse()
        self.assertEqual(1., result)

        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = sppasImage(filename=TestImageCompare.IMAGE1)
        self.assertEqual(1., sppasImageCompare(img1, img2).compare_with_mse())

        # 2 close images: score is good or pretty good
        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        w1, h1 = img1.size()
        img2 = img1.icrop([12, 8, w1 - 20, h1 + 20])
        self.assertEqual(0.78, round(sppasImageCompare(img1, img2).compare_with_mse(), 2))
        img2 = img1.icrop([50, 88, w1 - 70, h1 + 20])
        self.assertEqual(0.29, round(sppasImageCompare(img1, img2).compare_with_mse(), 2))

        # 2 very different images: score is very low
        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = sppasImage(filename=TestImageCompare.IMAGE2)
        self.assertEqual(0.03, round(sppasImageCompare(img1, img2).compare_with_mse(), 2))

        # The same image but gamma changed: score is pretty good
        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = img1.igamma(1.5)
        self.assertEqual(0.33, round(sppasImageCompare(img1, img2).compare_with_mse(), 2))

    def test_compare_with_kld(self):
        img1 = sppasImage(filename=TestImageCompare.IMAGE1)
        img2 = sppasImage(filename=TestImageCompare.IMAGE2)

        # Identical images:
        result = sppasImageCompare(img1, img1).compare_with_kld()
        self.assertGreater(result, 0.95)
        print("* img1 vs img1: {}".format(result))
        result = sppasImageCompare(img2, img2).compare_with_kld()
        self.assertGreater(result, 0.95)
        print("* img2 vs img2: {}".format(result))

        # Different images:
        result1 = sppasImageCompare(img1, img2).compare_with_kld()
        print("* img1 vs img2: {}".format(result1))
        result2 = sppasImageCompare(img2, img1).compare_with_kld()
        self.assertEqual(result1, result2)
        self.assertLess(result1, 0.5)

        result = sppasImageCompare(img1, img1.inegative()).compare_with_kld()
        print("* img1 vs neg-img1: {}".format(result))
        result = sppasImageCompare(img2, img2.inegative()).compare_with_kld()
        print("* img2 vs neg-img2: {}".format(result))
