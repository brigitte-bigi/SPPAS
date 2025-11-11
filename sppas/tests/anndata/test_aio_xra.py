# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.tests.test_label.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unittests of the class sppasXRA() to read and write SPPAS XRA files.

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
import shutil

from sppas.core.config import paths
from sppas.src.utils.fileutils import sppasFileUtils
from sppas.src.anndata.aio.xra import sppasXRA

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(paths.etc, "xml")

# ---------------------------------------------------------------------------


class TestXRA(unittest.TestCase):
    """Represents an XRA file, the native format of SPPAS."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_members(self):
        xra = sppasXRA()
        self.assertTrue(xra.multi_tiers_support())
        self.assertTrue(xra.no_tiers_support())
        self.assertTrue(xra.metadata_support())
        self.assertTrue(xra.ctrl_vocab_support())
        self.assertTrue(xra.media_support())
        self.assertTrue(xra.hierarchy_support())
        self.assertTrue(xra.point_support())
        self.assertTrue(xra.interval_support())
        self.assertTrue(xra.disjoint_support())
        self.assertTrue(xra.alternative_localization_support())
        self.assertTrue(xra.alternative_tag_support())
        self.assertTrue(xra.radius_support())
        self.assertTrue(xra.gaps_support())
        self.assertTrue(xra.overlaps_support())

    # -----------------------------------------------------------------------

    def test_read1(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.1.xra"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read2(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.2.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2015-08-03")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_id("m1"))
        self.assertIsNotNone(xra3.get_media_from_id("m2"))
        self.assertIsNotNone(xra3.get_media_from_id("m3"))
        self.assertIsNone(xra3.get_media_from_id("m4"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 1)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read3(self):
        xra3 = sppasXRA()
        xra3.read(os.path.join(DATA, "sample-1.3.xra"))
        # Metadata
        self.assertEqual(xra3.get_meta("created"), "2017-03-06")
        self.assertEqual(xra3.get_meta("license"), "GPL v3")
        # Media
        self.assertEqual(len(xra3.get_media_list()), 3)
        self.assertIsNotNone(xra3.get_media_from_id("m1"))
        self.assertIsNotNone(xra3.get_media_from_id("m2"))
        self.assertIsNotNone(xra3.get_media_from_id("m3"))
        self.assertIsNone(xra3.get_media_from_id("m4"))
        # Tiers
        self.assertEqual(len(xra3), 3)
        # ... First Tier
        self.assertEqual(len(xra3[0]), 2)
        self.assertEqual(xra3.get_tier_index("Intonation"), 0)
        self.assertEqual(xra3[0].get_id(), "t1")
        self.assertTrue(xra3[0].is_point())
        # ... Second Tier
        self.assertEqual(len(xra3[1]), 3)
        self.assertEqual(xra3.get_tier_index("TokensAlign"), 1)
        self.assertEqual(xra3[1].get_id(), "t2")
        self.assertTrue(xra3[1].is_interval())
        # ... 3rd Tier
        self.assertEqual(len(xra3[2]), 1)
        self.assertEqual(xra3.get_tier_index("IPU"), 2)
        self.assertEqual(xra3[2].get_id(), "t3")
        self.assertTrue(xra3[2].is_interval())
        # Controlled vocabulary
        self.assertEqual(len(xra3.get_ctrl_vocab_list()), 2)
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("v0"))
        self.assertIsNotNone(xra3.get_ctrl_vocab_from_name("intensity"))
        # Hierarchy
        #self.assertEqual(len(xra3.hierarchy), 2)

    # -----------------------------------------------------------------------

    def test_read5(self):
        xra5 = sppasXRA()
        xra5.read(os.path.join(DATA, "sample-1.5.xra"))
        # 6 Tiers
        self.assertEqual(len(xra5), 7)
        # the tier VowelFacePoints
        self.assertEqual(xra5.get_tier_index("VowelFacePoints"), 6)
        self.assertEqual(xra5[5].get_id(), "t6")
        self.assertTrue(xra5[5].is_interval())
        self.assertEqual(len(xra5[5]), 2)
        self.assertEqual(xra5[5][0].get_id(), "faces_img4")
        self.assertEqual(xra5[5][1].get_id(), "faces_img8")

        labels_av1 = xra5[6][0].get_labels()
        labels_av2 = xra5[6][1].get_labels()
        self.assertEqual(len(labels_av1), 2)
        self.assertEqual(len(labels_av2), 2)

        tag1 = labels_av1[0].get_best()
        point1 = tag1.get_typed_content()
        self.assertEqual(point1.get_midpoint(), (234, 402))
        self.assertEqual(point1.get_radius(), 12)
        tag2 = labels_av1[1].get_best()
        point2 = tag2.get_typed_content()
        self.assertEqual(point2.get_midpoint(), (256, 802))
        self.assertIsNone(point2.get_radius())

    # -----------------------------------------------------------------------

    def test_read_write_4(self):
        xra = sppasXRA()
        xra.read(os.path.join(DATA, "sample-1.4.xra"))
        xra.write(os.path.join(TEMP, "sample-1.4.xra"))
        xra2 = sppasXRA()
        xra2.read(os.path.join(TEMP, "sample-1.4.xra"))

        # Compare annotations of original xra and xra2
        for t1, t2 in zip(xra, xra2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                # compare labels and location
                self.assertEqual(a1, a2)
                # compare metadata
                for key in a1.get_meta_keys():
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))

        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(xra, xra2):
            ctrl1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            ctrl2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(len(ctrl1), len(ctrl2))
            for entry in ctrl1:
                self.assertTrue(ctrl2.contains(entry))

    # -----------------------------------------------------------------------

    def test_read_write_5(self):
        xra = sppasXRA()
        xra.read(os.path.join(DATA, "sample-1.5.xra"))
        xra.write(os.path.join(TEMP, "sample-1.5.xra"))
        xra2 = sppasXRA()
        xra2.read(os.path.join(TEMP, "sample-1.5.xra"))

        # Compare annotations of original xra and xra2
        for t1, t2 in zip(xra, xra2):
            self.assertEqual(len(t1), len(t2))
            for a1, a2 in zip(t1, t2):
                # compare labels and location
                self.assertEqual(a1, a2)
                # compare metadata
                for key in a1.get_meta_keys():
                    self.assertEqual(a1.get_meta(key), a2.get_meta(key))

        # Compare media
        # Compare hierarchy
        # Compare controlled vocabularies
        for t1, t2 in zip(xra, xra2):
            ctrl1 = t1.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            ctrl2 = t2.get_ctrl_vocab()  # a sppasCtrlVocab() instance or None
            if ctrl1 is None and ctrl2 is None:
                continue
            self.assertEqual(len(ctrl1), len(ctrl2))
            for entry in ctrl1:
                self.assertTrue(ctrl2.contains(entry))
