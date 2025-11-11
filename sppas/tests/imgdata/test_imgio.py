"""
:filename: sppas.src.imgdata.tests.test_imgio.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of the coords reader/writer.

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
from sppas.src.anndata import sppasXRA
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoordsReader
from sppas.src.imgdata import sppasCoordsImageWriter

# a JPG image has no transparency, so shape is 3
IMAGE = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")

# ---------------------------------------------------------------------------


class TestCoordsReaderWriter(unittest.TestCase):

    def tearDown(self):
        if os.path.exists("test.csv"):
            os.remove("test.csv")
        if os.path.exists("test.xra"):
            os.remove("test.xra")

    def test_write_param(self):
        img = sppasImage(filename=IMAGE)
        c = sppasCoords(10, 20, 640, 480, 0.6)
        w = sppasCoordsImageWriter()
        with self.assertRaises(TypeError):
            w.write(IMAGE, [c], "yyy")
        with self.assertRaises(TypeError):
            w.write(img, "coords", "yyy")

        # disable all outputs
        w.set_options(csv=False, xra=False, tag=False, crop=False, width=None, height=None)
        # Appropriate parameters
        w.write(img, [c], "any.jpg")

    def test_write_csv(self):
        img = sppasImage(filename=IMAGE)
        c1 = sppasCoords(10, 20, 640, 480, 0.6)
        w = sppasCoordsImageWriter()
        w.set_options(csv=True, xra=False, tag=False, crop=False, width=None, height=None)

        # Create a CSV file and write one coords
        w.write(img, [c1], "test.jpg")
        self.assertTrue(os.path.exists("test.csv"))
        with open("test.csv", "r") as f:
            lines = f.readlines()
        self.assertEqual(1, len(lines))
        tab = lines[0].split(w.get_csv_sep())
        self.assertEqual(8, len(tab))
        self.assertEqual(0.6, float(tab[1]))
        self.assertEqual("10", tab[2])
        self.assertEqual("20", tab[3])
        self.assertEqual("640", tab[4])
        self.assertEqual("480", tab[5])
        self.assertEqual("test.jpg", tab[6])

        # Append a new line into the same file
        c2 = sppasCoords(15, 25, 640, 480, 0.66)
        w.write(img, [c2], "test.jpg")
        with open("test.csv", "r") as f:
            lines = f.readlines()
        self.assertEqual(2, len(lines))
        tab = lines[1].split(w.get_csv_sep())
        self.assertEqual(8, len(tab))
        self.assertEqual(0.66, float(tab[1]))
        self.assertEqual("15", tab[2])
        self.assertEqual("25", tab[3])
        self.assertEqual("640", tab[4])
        self.assertEqual("480", tab[5])
        self.assertEqual("test.jpg", tab[6])

    def test_write_xra(self):
        img = sppasImage(filename=IMAGE)
        c1 = sppasCoords(10, 20, 640, 480, 0.6)
        w = sppasCoordsImageWriter()
        w.set_options(csv=False, xra=True, tag=False, crop=False, width=None, height=None)

        # Create an XRA file and write one coords
        w.write(img, [c1], "test.jpg")
        self.assertTrue(os.path.exists("test.xra"))

        # Append a new coord into the same file
        c2 = sppasCoords(15, 25, 640, 480, 0.66)
        w.write(img, [c2], "test.jpg")

        # Read content and check it
        xra = sppasXRA("test")
        xra.read("test.xra")
        self.assertEqual(len(xra), 1)     # one tier
        self.assertEqual(len(xra[0]), 2)  # 2 annotations in the tier
        t1 = xra[0][0].get_labels()[0].get_best()  # sppasTag
        p1 = t1.get_typed_content()                # sppasFuzzyRect
        self.assertEqual(p1.get_midpoint(), (10, 20, 640, 480))
        s1 = xra[0][0].get_labels()[0].get_score(t1)
        self.assertEqual(s1, 0.6)
        t2 = xra[0][1].get_labels()[0].get_best()
        p2 = t2.get_typed_content()  # sppasFuzzyRect
        self.assertEqual(p2.get_midpoint(), (15, 25, 640, 480))
        s1 = xra[0][1].get_labels()[0].get_score(t2)
        self.assertEqual(s1, 0.66)

    def test_write_read_csv(self):
        img = sppasImage(filename=IMAGE)
        c1 = sppasCoords(10, 20, 640, 480, 0.6)
        c2 = sppasCoords(15, 25, 640, 480, 0.66)

        w = sppasCoordsImageWriter()
        w.set_options(csv=True, xra=False, tag=False, crop=False, width=None, height=None)
        w.write(img, [c1], "test.jpg")
        w.write(img, [c2], "test.jpg")
        w.write(img, [c1, c2], "test")
        self.assertTrue(os.path.exists("test.csv"))
        reader = sppasCoordsReader("test.csv")
        self.assertEqual(len(reader.coords), 4)
        self.assertEqual(len(reader.names), 4)
        self.assertEqual(reader.coords[0], c1)
        self.assertEqual(reader.coords[1], c2)
        self.assertEqual(reader.coords[2], c1)
        self.assertEqual(reader.coords[3], c2)

    def test_write_read_xra(self):
        img = sppasImage(filename=IMAGE)
        c1 = sppasCoords(10, 20, 640, 480, 0.6)
        c2 = sppasCoords(15, 25, 640, 480, 0.66)

        w = sppasCoordsImageWriter()
        w.set_options(csv=False, xra=True, tag=False, crop=False, width=None, height=None)
        w.write(img, [c1], "test.jpg")
        w.write(img, [c2], "test.jpg")
        w.write(img, [c1, c2], "test")
        self.assertTrue(os.path.exists("test.xra"))
        reader = sppasCoordsReader("test.xra")
        self.assertEqual(len(reader.coords), 4)
        self.assertEqual(len(reader.names), 4)
        self.assertEqual(reader.coords[0], c1)
        self.assertEqual(reader.coords[1], c2)
        self.assertEqual(reader.coords[2], c1)
        self.assertEqual(reader.coords[3], c2)
