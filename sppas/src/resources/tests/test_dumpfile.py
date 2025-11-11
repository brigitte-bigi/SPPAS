# -*- coding: utf8 -*-
"""
:filename: sppas.src.resources.tests.test_dumpfile.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test of dumping dictionaries.

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

from sppas.src.resources.dumpfile import sppasDumpFile
from sppas.src.resources.resourcesexc import DumpExtensionError

# ---------------------------------------------------------------------------


class TestDumpFile(unittest.TestCase):

    def test_extension(self):
        dp = sppasDumpFile("E://data/toto.txt")
        self.assertEqual(dp.get_dump_extension(), sppasDumpFile.DUMP_FILENAME_EXT)
        dp.set_dump_extension(".DUMP")
        self.assertEqual(dp.get_dump_extension(), ".DUMP")
        dp.set_dump_extension("DUMP")
        self.assertEqual(dp.get_dump_extension(), ".DUMP")
        dp.set_dump_extension()
        self.assertEqual(dp.get_dump_extension(), sppasDumpFile.DUMP_FILENAME_EXT)
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension(".txt")
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension(".TXT")
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension("TXT")

    def test_filename(self):
        dp = sppasDumpFile("E://data/toto.txt")
        self.assertEqual(dp.get_dump_filename(), "E://data/toto.dump")
        self.assertFalse(dp.has_dump())
