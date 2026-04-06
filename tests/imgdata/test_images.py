"""
:filename: sppas.src.imgdata.tests.test_images.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of the sppasExtendedImage class.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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
import cv2
import numpy

from sppas.core.config import paths

from sppas.src.imgdata.image import sppasImage
from sppas.src.imgdata.images import sppasExtendedImage

# ---------------------------------------------------------------------------


class TestImages(unittest.TestCase):

    # a JPG image has no transparency, so shape is 3
    fn = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")

    def test_init(self):
        img = cv2.imread(TestImages.fn)
        self.assertEqual(len(img), 803)

        i1 = sppasExtendedImage(input_array=img)
        self.assertIsInstance(i1, numpy.ndarray)
        self.assertIsInstance(i1, sppasImage)
        self.assertIsInstance(i1, sppasExtendedImage)
        self.assertEqual(len(img), len(i1))
        self.assertTrue(i1 == img)

    # -----------------------------------------------------------------------

    def test_overlays(self):
        image = sppasExtendedImage(filename=TestImages.fn)
        sample = os.path.join(paths.resources, "cuedspeech", "hand-lfpc-1.png")
        if os.path.exists(sample) is False:
            sample = os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png")
        other = sppasImage(filename=sample)

        from_coords = (100, 0, 200, 200)
        to_coords = (800, 800, 600, 600)

        results = image.ioverlays(other, from_coords, to_coords, 10)
        fnc = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016-over")
        for i in range(len(results)):
            fnci = fnc + str(i+1) + ".jpg"
            results[i].write(fnci)
