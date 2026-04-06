# -*- coding:utf-8 -*-
"""
:filename: sppas.src.models.test.test_rw.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Tests of reading and writing acoustic models.

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
import os.path
import shutil
import glob

from sppas.core.config import symbols
from sppas.core.config import paths
from sppas.src.utils.fileutils import sppasFileUtils
from sppas.src.utils.compare import sppasCompare

from ..acm.acmbaseio import sppasBaseIO
from ..acm.readwrite import sppasACMRW
from ..modelsexc import MioFolderError
from ..modelsexc import MioFileFormatError

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
MODEL_PATH = os.path.join(paths.resources, "models")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SIL_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("silence")]
LAUGH_PHON = list(symbols.phone.keys())[list(symbols.phone.values()).index("laugh")]
SIL_ORTHO = list(symbols.ortho.keys())[list(symbols.ortho.values()).index("silence")]

# ---------------------------------------------------------------------------


class TestMRW(unittest.TestCase):

    def test_base_io(self):
        rw = sppasBaseIO()
        self.assertEqual(len(rw.get_name()), 36)  # a GUID
        self.assertTrue(rw.is_ascii())
        self.assertFalse(rw.is_binary())

    def test_base_rw(self):
        rw = sppasBaseIO()
        with self.assertRaises(NotImplementedError):
            rw.read(TEMP)
        with self.assertRaises(NotImplementedError):
            rw.write(TEMP)
        with self.assertRaises(NotImplementedError):
            rw.write_hmm_proto(25, TEMP)

    def test_rw(self):
        rw = sppasACMRW(DATA)
        with self.assertRaises(MioFolderError):
            rw.read()
        with self.assertRaises(MioFileFormatError):
            rw.write(None, format="toto")


class TestMIO(unittest.TestCase):

    def setUp(self):
        if os.path.exists(TEMP) is True:
            shutil.rmtree(TEMP)
        os.mkdir(TEMP)
        shutil.copytree(os.path.join(DATA, "protos"), os.path.join(TEMP, "protos"))

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_read_htk(self):
        # Read separated macros and hmm files
        rw = sppasACMRW(os.path.join(TEMP, "protos"))
        model = rw.read()
        self.assertEqual(len(model), 3)
        with self.assertRaises(ValueError):
            model.get_hmm("toto")
        laughter = model.get_hmm(LAUGH_PHON)
        proto = model.get_hmm("proto")
        silence = model.get_hmm(SIL_PHON)

        # Read macros, hmmdefs, monophones.repl
        rw = sppasACMRW(os.path.join(MODEL_PATH, "models-cat"))
        model = rw.read()
        self.assertEqual(len(model), 41)

        # Read macros, hmmdefs, monophones.repl and tiedlist
        # rw = sppasACMRW(os.path.join(MODEL_PATH, "models-fra"))
        # model = rw.read()
        # self.assertEqual(len(model), 1368)   # monophones, biphones, triphones

    def test_load_save(self):
        self._test_load_save(os.path.join(MODEL_PATH, "models-jpn"))
        self._test_load_save(os.path.join(MODEL_PATH, "models-nan"))

    # This one takes too much time to be tested each time...
    def test_load_all_models(self):
        models_dir = glob.glob(os.path.join(MODEL_PATH, "models-*"))
        for folder in models_dir:
            self._test_load_save(folder)

    def _test_load_save(self, folder):
        """Test to read and write an acoustic model of the given directory."""
        # Read the acoustic model (monophone)
        parser = sppasACMRW(folder)
        acmodel = parser.read()

        # Save temporarily the loaded model
        parser.set_folder(os.path.join(TEMP))
        parser.write(acmodel)

        # Load the temporary file into a new model
        acmodel_copy = parser.read()

        sp = sppasCompare()

        # Compare original and copy
        self.assertEqual(len(acmodel.get_hmms()), len(acmodel_copy.get_hmms()))
        for hmm, hmmcopy in zip(acmodel.get_hmms(), acmodel_copy.get_hmms()):
            self.assertEqual(hmm.get_name(), hmmcopy.get_name())
            self.assertTrue(sp.equals(hmm.get_definition(), hmmcopy.get_definition()))
        self.assertTrue(sp.equals(acmodel.get_macros(), acmodel_copy.get_macros()))
