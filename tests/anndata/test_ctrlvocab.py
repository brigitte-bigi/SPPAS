# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_ctrlvovab.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test sppasCtrlVocab() class.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from sppas.core.coreutils import u
from sppas.src.anndata.anndataexc import AnnDataTypeError
from sppas.src.anndata.ctrlvocab import sppasCtrlVocab
from sppas.src.anndata.ann.annlabel import sppasTag

# ---------------------------------------------------------------------------


class TestCtrlVocab(unittest.TestCase):
    """A controlled Vocabulary is a set of tags."""

    def setUp(self):
        pass

    # -----------------------------------------------------------------------

    def test_identifier(self):
        voc = sppasCtrlVocab("être être")
        self.assertEqual(voc.get_name(), u("être_être"))

    # -----------------------------------------------------------------------

    def test_add(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertEqual(len(voc), 0)
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.add(sppasTag("comparison")))
        self.assertTrue(voc.add(sppasTag("gap filling with sound")))
        self.assertFalse(voc.add(sppasTag("definition")))
        self.assertEqual(len(voc), 4)
        with self.assertRaises(AnnDataTypeError):
            voc.add("bla")

        voc_int = sppasCtrlVocab("Intensity")
        self.assertTrue(voc_int.add(sppasTag(1, "int")))
        self.assertTrue(voc_int.add(sppasTag(2, "int")))
        self.assertFalse(voc_int.add(sppasTag(1, "int")))
        with self.assertRaises(AnnDataTypeError):
            # 1 is converted into "str" type by sppasTag. (we expect 'int')
            voc_int.add(sppasTag(1))
        with self.assertRaises(AnnDataTypeError):
            voc_int.add(2)

    # -----------------------------------------------------------------------

    def test_contains(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.add(sppasTag("comparison")))
        self.assertTrue(voc.add(sppasTag("gap filling with sound")))
        self.assertFalse(voc.add(sppasTag(" gap filling with sound ")))
        self.assertTrue(voc.add(sppasTag("contrast")))
        self.assertFalse(voc.add(sppasTag("definition")))
        self.assertTrue(voc.contains(sppasTag("definition")))
        self.assertTrue(voc.contains(sppasTag("   \t  definition\r\n")))
        with self.assertRaises(AnnDataTypeError):
            voc.contains("definition")

        voc_int = sppasCtrlVocab("Intensity")
        self.assertTrue(voc_int.add(sppasTag(1, "int")))
        self.assertTrue(voc_int.add(sppasTag(2, "int")))
        self.assertTrue(voc_int.contains(sppasTag(2, "int")))
        self.assertFalse(voc_int.contains(sppasTag(2, "str")))
        self.assertFalse(voc_int.contains(sppasTag(2)))

    # -----------------------------------------------------------------------

    def test_remove(self):
        voc = sppasCtrlVocab("Verbal Strategies")
        self.assertTrue(voc.add(sppasTag("definition")))
        self.assertTrue(voc.add(sppasTag("example")))
        self.assertTrue(voc.remove(sppasTag("example")))
        self.assertFalse(voc.remove(sppasTag("example")))
        with self.assertRaises(AnnDataTypeError):
            voc.remove("definition")
