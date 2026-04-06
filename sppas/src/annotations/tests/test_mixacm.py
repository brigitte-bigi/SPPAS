#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
:filename: sppas.src.models.test.test_mix.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Tests of combining acoustic models.

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

from sppas.core.config import paths
from sppas.src.annotations.Align.models.acm.acmodel import sppasAcModel
from sppas.src.annotations.Align.models.acm.hmm import sppasHMM
from sppas.src.annotations.Align.modelmixer import sppasModelMixer
from sppas.src.annotations.Align.models.acm.readwrite import sppasACMRW

# ---------------------------------------------------------------------------

MODELDIR = os.path.join(paths.resources, "models")

# ---------------------------------------------------------------------------


class TestModelMixer(unittest.TestCase):

    def setUp(self):
        # a French speaker reading an English text...
        self._model_L2dir = os.path.join(MODELDIR, "models-eng")
        self._model_L1dir = os.path.join(MODELDIR, "models-fra")

    def testMix(self):
        acmodel1 = sppasAcModel()
        hmm1 = sppasHMM()
        hmm1.create_proto(25)
        hmm1.set_name("y")
        acmodel1.append_hmm(hmm1)
        acmodel1.get_repllist().add("y", "j")

        acmodel2 = sppasAcModel()
        hmm2 = sppasHMM()
        hmm2.create_proto(25)
        hmm2.set_name("j")
        hmm3 = sppasHMM()
        hmm3.create_proto(25)
        hmm3.name = "y"
        acmodel2.get_hmms().append(hmm2)
        acmodel2.get_hmms().append(hmm3)
        acmodel2.get_repllist().add("y", "y")
        acmodel2.get_repllist().add("j", "j")

        modelmixer = sppasModelMixer()
        modelmixer.set_models(acmodel1, acmodel2)

        outputdir = os.path.join(MODELDIR, "models-test")
        modelmixer.mix(outputdir, gamma=1.)
        self.assertTrue(os.path.exists(outputdir))
        model = sppasACMRW(outputdir).read()
        shutil.rmtree(outputdir)

    def testMixData(self):
        modelmixer = sppasModelMixer()
        modelmixer.read(self._model_L2dir, self._model_L1dir)
        outputdir = os.path.join(MODELDIR, "models-eng-fra")
        modelmixer.mix(outputdir, gamma=0.5)
        self.assertTrue(os.path.exists(outputdir))
        acmodel1 = sppasACMRW(self._model_L2dir).read()
        acmodel1_mono = acmodel1.extract_monophones()
        acmodel2 = sppasACMRW(os.path.join(MODELDIR, "models-eng-fra")).read()
        shutil.rmtree(outputdir)
