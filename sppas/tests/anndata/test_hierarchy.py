# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_hierarchy.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test sppasHoerarchy() class.

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

from sppas.src.anndata.ann.annlabel import sppasLabel
from sppas.src.anndata.ann.annlabel import sppasTag
from sppas.src.anndata.ann.annlocation import sppasPoint
from sppas.src.anndata.ann.annlocation import sppasInterval
from sppas.src.anndata.ann.annlocation import sppasLocation

from sppas.src.anndata.ann.annotation import sppasAnnotation
from sppas.src.anndata.tier import sppasTier
from sppas.src.anndata.transcription import sppasTranscription

# ---------------------------------------------------------------------------


class TestHierarchy(unittest.TestCase):

    def test_add_hierarchy_link(self):
        trs = sppasTranscription()
        ref_tier = trs.create_tier('reftier')
        sub_tier = trs.create_tier('subtier')
        out_tier = sppasTier('Out')

        ref_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.),
                                                               sppasPoint(1.5))))
        ref_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5),
                                                               sppasPoint(2.))))
        ref_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.),
                                                               sppasPoint(2.5))))
        ref_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.5),
                                                               sppasPoint(3.))))

        sub_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.),
                                                               sppasPoint(2.))))
        sub_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.),
                                                               sppasPoint(3.))))

        out_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.),
                                                               sppasPoint(2.1))))

        # Errors:
        with self.assertRaises(TypeError):
            trs.add_hierarchy_link("Toto", ref_tier, sub_tier)
        with self.assertRaises(Exception):
            trs.add_hierarchy_link("TimeAlignment", ref_tier, ref_tier)
        with self.assertRaises(Exception):
            trs.add_hierarchy_link("TimeAlignment", ref_tier, out_tier)
        with self.assertRaises(Exception):
            trs.add_hierarchy_link("TimeAssociation", ref_tier, out_tier)

        trs.append(out_tier)
        with self.assertRaises(Exception):
            trs.add_hierarchy_link("TimeAlignment", ref_tier, out_tier)
        with self.assertRaises(Exception):
            trs.add_hierarchy_link("TimeAssociation", ref_tier, out_tier)

        # Normal:
        trs.add_hierarchy_link("TimeAlignment", ref_tier, sub_tier)

        # Modification of parent's/children:
        ref_tier[3].get_highest_localization().set(sppasPoint(4.))
        self.assertEqual(ref_tier[3].get_highest_localization(), sppasPoint(3.))

        # we can't modify a parent if it's invalidate the hierarchy
        with self.assertRaises(Exception):
            ref_tier[3].set_best_localization(sppasInterval(sppasPoint(2.5),
                                                            sppasPoint(4.)))
        self.assertEqual(ref_tier[3].get_highest_localization(), sppasPoint(3.))

        # we can't modify a child if it's invalidate the hierarchy
        with self.assertRaises(Exception):
            sub_tier[1].set_best_localization(sppasInterval(sppasPoint(2.),
                                                            sppasPoint(4.)))

    # -----------------------------------------------------------------------

    def test_append_annotation_if_hierarchy(self):
        trs = sppasTranscription()
        ref_tier = trs.create_tier('reftier')
        sub_tier = trs.create_tier('subtier')

        trs.add_hierarchy_link("TimeAlignment", ref_tier, sub_tier)

        with self.assertRaises(Exception):
            sub_tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))

        ref_tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        ref_tier.append(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        self.assertEqual(len(ref_tier), 2)

        self.assertTrue(sub_tier.is_empty())
        sub_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))))
        self.assertEqual(len(sub_tier), 1)

    # -----------------------------------------------------------------------

    def test_add(self):
        trs = sppasTranscription()
        reftier = trs.create_tier('reftier')
        subtier = trs.create_tier('subtier')

        trs.add_hierarchy_link("TimeAlignment", reftier, subtier)

        reftier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5)))))
        reftier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(2.)))))
        self.assertTrue(len(reftier), 2)

        subtier.add(sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.)))))
        self.assertEqual(len(subtier), 1)

    # -----------------------------------------------------------------------

    def test_trs(self):
        trs = sppasTranscription("test")
        phonemes = trs.create_tier('phonemes')
        tokens = trs.create_tier('tokens')
        syntax = trs.create_tier('syntax')

        for i in range(0, 11):
            ann = phonemes.create_annotation(
                   sppasLocation(sppasInterval(sppasPoint(i * 0.1),
                                               sppasPoint(i * 0.1 + 0.1))),
                   sppasLabel(sppasTag("phon %d" % i))
            )
        for i in range(0, 5):
            ann = syntax.create_annotation(
                   sppasLocation(sppasInterval(sppasPoint(i * 0.2),
                                               sppasPoint(i * 0.2 + 0.2))),
                   sppasLabel(sppasTag("syntax label"))
            )
            ann = tokens.create_annotation(
                   sppasLocation(sppasInterval(sppasPoint(i * 0.2),
                                               sppasPoint(i * 0.2 + 0.2))),
                   sppasLabel(sppasTag("token label"))
            )

        self.assertTrue(phonemes.is_superset(tokens))
        self.assertTrue(tokens.is_superset(syntax))

        self.assertTrue(phonemes.is_superset(tokens))
        self.assertTrue(tokens.is_superset(syntax))

        trs.add_hierarchy_link("TimeAlignment", phonemes, tokens)
        trs.add_hierarchy_link("TimeAssociation", tokens, syntax)
