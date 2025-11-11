# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.imgdata.tests.test_imgfilter.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests of the image filters.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

import os
import unittest

from sppas.core.config import paths

from sppas.src.imgdata import sppasImage

# ---------------------------------------------------------------------------


class TestImageFilter(unittest.TestCase):

    def setUp(self):
        self.img = sppasImage(filename=os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg"))

    # ---------------------------------------------------------------------------

    def test_img_color_quantization(self):
        # test basic filter parameter
        img_process = self.img.iquantization_color()
        img_process.write("test_quantization_1.jpg")

        # upgrade the number of down samp that increase the blur
        img_process = self.img.iquantization_color(nb_down_samp=5)
        img_process.write("test_quantization_2.jpg")

    # ---------------------------------------------------------------------------

    def test_cartoonize(self):
        # normal cartoon filter
        img_process = self.img.icartoon()
        img_process.write("test_cartoonize.jpg")

        # cartoon filter in black and white
        img_process = self.img.icartoon(colorize=False)
        img_process.write("test_cartoonize_2.jpg")

    # ---------------------------------------------------------------------------

    def test_invert_filter(self):
        img_process = self.img.iinvert()
        img_process.write("test_invert.jpg")

    # ---------------------------------------------------------------------------

    def test_color_overlay(self):
        # green overlay
        img_process = self.img.ioverlay_color((10, 240, 10))
        img_process.write("test_color_overlay.jpg")

        # red overlay with an intensity increase
        img_process = self.img.ioverlay_color((230, 0, 10), intensity=0.8)
        img_process.write("test_color_overlay_2.jpg")
