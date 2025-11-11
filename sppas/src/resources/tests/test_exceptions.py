# -*- coding:utf-8 -*-
"""
:filename: sppas.src.resources.tests.test_exceptions.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test of the exceptions of the package.

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

from sppas.src.resources.resourcesexc import FileIOError
from sppas.src.resources.resourcesexc import FileFormatError
from sppas.src.resources.resourcesexc import NgramRangeError
from sppas.src.resources.resourcesexc import GapRangeError
from sppas.src.resources.resourcesexc import ScoreRangeError
from sppas.src.resources.resourcesexc import DumpExtensionError

# ---------------------------------------------------------------------------


class TestExceptions(unittest.TestCase):

    def test_file_exceptions(self):
        try:
            raise FileIOError("path/filename")
        except Exception as e:
            self.assertTrue(isinstance(e, FileIOError))
            self.assertTrue("5010" in str(e))

        try:
            raise FileFormatError(10, "wrong line content or filename")
        except Exception as e:
            self.assertTrue(isinstance(e, FileFormatError))
            self.assertTrue("5015" in str(e))

        try:
            raise DumpExtensionError(".doc")
        except Exception as e:
            self.assertTrue(isinstance(e, DumpExtensionError))
            self.assertTrue("5030" in str(e))

    def test_range_exceptions(self):
        try:
            raise NgramRangeError(100, 300)  # maximum, observed
        except Exception as e:
            self.assertTrue(isinstance(e, NgramRangeError))
            self.assertTrue("5020" in str(e))

        try:
            raise GapRangeError(100, 300)  # maximum, observed
        except Exception as e:
            self.assertTrue(isinstance(e, GapRangeError))
            self.assertTrue("5022" in str(e))

        try:
            raise ScoreRangeError(3.)  # observed
        except Exception as e:
            self.assertTrue(isinstance(e, ScoreRangeError))
            self.assertTrue("5024" in str(e))
