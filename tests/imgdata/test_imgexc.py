# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.imgdata.tests.test_imgexc.py
:author:   Florian Hocquet, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of the exception classes.

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

import unittest

from sppas.src.imgdata.imgdataexc import *

# ---------------------------------------------------------------------------


class TestImagesExceptions(unittest.TestCase):

    def test_io_error(self):
        try:
            raise ImageReadError("the filename")
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            self.assertTrue("2610" in str(e))

        try:
            raise ImageWriteError("the filename")
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            self.assertTrue("2620" in str(e))

    def test_value_error(self):
        try:
            raise ImageBoundError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2330" in str(e))

        try:
            raise ImageWidthError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2332" in str(e))

        try:
            raise ImageHeightError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2334" in str(e))

        try:
            raise ImageEastingError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2336" in str(e))

        try:
            raise ImageNorthingError("observed", "reference")
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))
            self.assertTrue("2338" in str(e))
