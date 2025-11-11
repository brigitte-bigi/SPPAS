"""
:filename: sppas.src.imgdata.tests.test_imgsightsreader.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Tests of the image sights reader class.

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

from sppas.core.config import paths
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasIOError
from sppas.core.coreutils import sppasExtensionReadError

from sppas.src.imgdata import sppasSights
from sppas.src.imgdata import sppasImageSightsReader

# ---------------------------------------------------------------------------

XRA_FILE = os.path.join(paths.resources, "cuedspeech", "brigitte_1-hands.xra")
CSV_FILE = os.path.join(paths.resources, "cuedspeech", "brigitte_1-hands.csv")

# ---------------------------------------------------------------------------


class TestImageSightsReader(unittest.TestCase):

    # ---------------------------------------------------------------------------
    # Exceptions
    # ---------------------------------------------------------------------------

    def test_init_exceptions(self):
        # input file parameter wrong type case
        with self.assertRaises(sppasTypeError):
            sppasImageSightsReader(4)

        # csv separator parameter wrong type case
        with self.assertRaises(sppasTypeError):
            sppasImageSightsReader(CSV_FILE, csv_separator=4)

        # input file doesn't exist
        with self.assertRaises(sppasIOError):
            sppasImageSightsReader("ghost_file.xra")

        # input file wrong file extension case
        with self.assertRaises(sppasExtensionReadError):
            sppasImageSightsReader(os.path.join(paths.demo, "demo.mp4"))

    # ---------------------------------------------------------------------------
    # XRA file
    # ---------------------------------------------------------------------------

    def test_load_xra_file(self):
        image_sights = sppasImageSightsReader(XRA_FILE)

        self.assertNotEqual(0, len(image_sights.sights))

        for current_sight in image_sights.sights:
            self.assertIsInstance(current_sight, sppasSights)

    # ---------------------------------------------------------------------------
    # CSV file
    # ---------------------------------------------------------------------------

    def test_load_csv_file(self):
        image_sights = sppasImageSightsReader(CSV_FILE)

        self.assertNotEqual(0, len(image_sights.sights))

        for current_sight in image_sights.sights:
            self.assertIsInstance(current_sight, sppasSights)
