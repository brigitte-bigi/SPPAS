# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_aio_xtrans.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the reader of SPPAS for Xtrans (tdf) files.

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

from sppas.src.anndata.aio.xtrans import sppasTDF
from sppas.src.anndata.ann.annlocation import sppasPoint

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------------------


class TestTDF(unittest.TestCase):
    """
    TDF reader.
    """
    def test_members(self):
        txt = sppasTDF()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
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

    # -----------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(3., 0.005), sppasTDF.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.005), sppasTDF.make_point("3"))
        with self.assertRaises(TypeError):
            sppasTDF.make_point("a")

    # -----------------------------------------------------------------

    def test_read(self):
        """Read a TDF file."""

        sample = os.path.join(DATA, "sample-irish.tdf")
        tdf = sppasTDF()
        tdf.read(sample)
        self.assertEqual(len(tdf), 2)     # 2 tiers (one per channel)
        self.assertEqual(len(tdf[0]), 5)  # 5 annotations in each tier
        self.assertEqual(len(tdf[1]), 5)  # 5 annotations in each tier
        self.assertEqual(sppasPoint(5.79874657439, 0.005), tdf[0].get_first_point())
        self.assertEqual(sppasPoint(7.88732394366, 0.005), tdf[1].get_first_point())
        self.assertTrue(tdf[0].is_meta_key('speaker_name'))
        self.assertTrue(tdf[1].is_meta_key('speaker_name'))
        # should be extended to test media, annotations, etc.
