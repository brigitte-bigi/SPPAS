"""
:filename: sppas.src.videodata.tests.test_videocoords.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  test video coordinates buffer.

.. _This file is part of SPPAS: <https://sppas.org/>
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

import unittest
import os

from sppas.core.config import paths
from sppas.src.anndata import sppasXRA
from sppas.src.imgdata import sppasCoords
from sppas.src.videodata import sppasCoordsVideoBuffer
from sppas.src.videodata import sppasVideoReaderBuffer
from sppas.src.videodata import sppasBufferVideoWriter
from sppas.src.videodata import sppasCoordsVideoWriter
from sppas.src.videodata import sppasCoordsVideoReader

# ---------------------------------------------------------------------------


class TestVideoCoords(unittest.TestCase):

    VIDEO = os.path.join(paths.samples, "faces", "video_sample.mp4")

    def tearDown(self):
        if os.path.exists("test.csv"):
            os.remove("test.csv")
        if os.path.exists("test.xra"):
            os.remove("test.xra")

    # -----------------------------------------------------------------------

    def test_init(self):
        bv = sppasCoordsVideoBuffer()
        self.assertFalse(bv.is_opened())
        self.assertEqual(bv.get_buffer_overlap(), sppasVideoReaderBuffer.DEFAULT_BUFFER_OVERLAP)
        self.assertFalse(bv.is_opened())
        self.assertEqual(0., bv.get_framerate())
        self.assertEqual(0, bv.tell())

    # -----------------------------------------------------------------------

    def test_coords(self):
        bv = sppasCoordsVideoBuffer(TestVideoCoords.VIDEO, size=50)

        # Add coords but buffer is empty
        # with self.assertRaises(ValueError):
        #    bv.append_coordinate(10, sppasCoords(10, 10))

        # Fill in the first buffer of images
        res = bv.next()
        self.assertEqual(50, bv.tell())
        self.assertEqual(50, len(bv))
        self.assertEqual((0, 49), bv.get_buffer_range())
        self.assertTrue(res)  # we did not reached the end of the video

        # Add/Get coord
        c = sppasCoords(10, 10, 100, 100)
        bv.append_coordinate(10, c)
        c_ret = bv.get_coordinate(10, 0)
        self.assertTrue(c is c_ret)

        # Pop coord
        bv.pop_coordinate(10, 0)
        coords = bv.get_coordinates(10)
        self.assertEqual(0, len(coords))

        # Remove coord
        bv.append_coordinate(10, c)
        coords = bv.get_coordinates(10)
        self.assertEqual(1, len(coords))
        bv.remove_coordinate(10, c)
        coords = bv.get_coordinates(10)
        self.assertEqual(0, len(coords))

    # -----------------------------------------------------------------------

    def test_xra(self):
        bv = sppasCoordsVideoBuffer(TestVideoCoords.VIDEO, size=50)
        bv.next()
        # Add coordinates in some of the images
        for i in range(1, 51):
            c = sppasCoords(10+i, 10+i, 100+i, 100+i)
            if (i % 8) == 0:
                c1 = sppasCoords(10+i, 10+i, 100+i, 100+i, 0.8)
                c2 = sppasCoords(20+i, 20+i, 120+i, 120+i, 0.4)
                bv.set_coordinates(i-1, [c1, c2])
            elif (i % 7) != 0:
                bv.set_coordinates(i-1, [c])

        w = sppasCoordsVideoWriter()
        self.assertIsInstance(w, sppasBufferVideoWriter)
        w.set_options(csv=False, xra=True, tag=False, crop=False, width=None, height=None, folder=False)
        w.write(bv, "test.mp4")
        bv.close()
        # really write the XRA file when 'w' is closed
        w.close()
        self.assertTrue(os.path.exists("test.xra"))

        # Read content and check it
        xra = sppasXRA("test")
        xra.read("test.xra")
        self.assertEqual(len(xra), 1)      # one tier
        self.assertEqual(len(xra[0]), 50)  # 50 annotations in the tier

        # more tests here

    # -----------------------------------------------------------------------

    def test_rw_csv_xra(self):
        bv = sppasCoordsVideoBuffer(TestVideoCoords.VIDEO, size=50)
        bv.next()
        # Add coordinates in some of the images
        for i in range(1, 51):
            c = sppasCoords(10 + i, 10 + i, 100 + i, 100 + i)
            if (i % 8) == 0:
                c1 = sppasCoords(10 + i, 10 + i, 100 + i, 100 + i, 0.8)
                c2 = sppasCoords(20 + i, 20 + i, 120 + i, 120 + i, 0.4)
                bv.set_coordinates(i - 1, [c1, c2])
            elif (i % 7) != 0:
                bv.set_coordinates(i - 1, [c])

        # WRITE both CSV and XRA
        w = sppasCoordsVideoWriter()
        w.set_options(csv=True, xra=True, tag=False, crop=False, width=None, height=None, folder=False)
        w.write(bv, "test.mp4")
        bv.close()
        # really write the XRA file when 'w' is closed
        w.close()
        self.assertTrue(os.path.exists("test.xra"))
        self.assertTrue(os.path.exists("test.csv"))

        # READ both CSV and XRA. Expected equal coords.
        csv_reader = sppasCoordsVideoReader("test.csv")
        xra_reader = sppasCoordsVideoReader("test.xra")
        self.assertEqual(50, len(csv_reader.coords))
        self.assertEqual(50, len(xra_reader.coords))
        for i in range(50):
            self.assertEqual(csv_reader.coords[i], xra_reader.coords[i])
