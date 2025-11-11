# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_aio_phonedit.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the reader/writer of SPPAS for MRK files.

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
import os.path

from sppas.core.coreutils import u

from sppas.src.anndata.aio.phonedit import sppasBasePhonedit
from sppas.src.anndata.aio.phonedit import sppasMRK
from sppas.src.anndata.aio.phonedit import sppasSignaix

from sppas.src.anndata.ann.annlocation import sppasPoint

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------------------


class TestBasePhonedit(unittest.TestCase):
    """
    Base Phonedit is mainly made of utility methods.

    """
    def test_members(self):
        txt = sppasBasePhonedit()
        self.assertTrue(txt.multi_tiers_support())
        self.assertFalse(txt.no_tiers_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertTrue(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertTrue(txt.overlaps_support())

# ---------------------------------------------------------------------------


class TestMRK(unittest.TestCase):
    """
    Test reader/writer of MRK files.

    """
    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.mrk'):
                self.assertTrue(sppasMRK.detect(f))
            else:
                self.assertFalse(sppasMRK.detect(f))

    # -----------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(3., 0.0005), sppasMRK.make_point("3000."))
        self.assertEqual(sppasPoint(3., 0.0005), sppasMRK.make_point("3000."))
        self.assertEqual(sppasPoint(3), sppasMRK.make_point("3000"))
        with self.assertRaises(TypeError):
            sppasMRK.make_point("3a")

    # -----------------------------------------------------------------

    def test_read(self):
        """Sample mrk."""

        mrk = sppasMRK()
        mrk.read(os.path.join(DATA, "sample.mrk"))
        self.assertEqual(len(mrk), 2)
        self.assertEqual(len(mrk.get_media_list()), 0)
        self.assertEqual(mrk[0].get_name(), u("transcription"))
        self.assertEqual(mrk[1].get_name(), u("ipus"))
        self.assertEqual(len(mrk[0]), 11)
        self.assertEqual(len(mrk[1]), 11)
        for i, ann in enumerate(mrk[1]):
            if i % 2:
                ipu_index = int(i/2) + 1
                self.assertEqual(ann.get_labels()[0].get_best().get_content(),
                                 u("ipu_"+str(ipu_index)))
            else:
                self.assertEqual(ann.get_labels()[0].get_best().get_content(),
                                 u("#"))

# ---------------------------------------------------------------------------


class TestSignaix(unittest.TestCase):
    """
    Test reader/writer of MRK files.

    """
    def test_detect(self):
        """Test the file format detection method."""

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith('.hz'):
                self.assertTrue(sppasSignaix.detect(f))
            else:
                self.assertFalse(sppasSignaix.detect(f))

    # -----------------------------------------------------------------------

    def test_members(self):

            txt = sppasSignaix()
            self.assertFalse(txt.multi_tiers_support())
            self.assertFalse(txt.no_tiers_support())
            self.assertFalse(txt.metadata_support())
            self.assertFalse(txt.ctrl_vocab_support())
            self.assertFalse(txt.media_support())
            self.assertFalse(txt.hierarchy_support())
            self.assertTrue(txt.point_support())
            self.assertFalse(txt.interval_support())
            self.assertFalse(txt.disjoint_support())
            self.assertFalse(txt.alternative_localization_support())
            self.assertFalse(txt.alternative_tag_support())
            self.assertFalse(txt.radius_support())
            self.assertFalse(txt.gaps_support())
            self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------------

    def test_read(self):
        """Test file reader."""

        hz = sppasSignaix()
        hz.read(os.path.join(DATA, "sample.hz"))
        self.assertEqual(len(hz), 1)
        self.assertEqual(len(hz.get_media_list()), 0)
        self.assertEqual(hz[0].get_name(), u("PitchHz"))
        self.assertTrue(hz[0].is_point())
        self.assertTrue(hz[0].is_float())
