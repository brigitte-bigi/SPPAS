# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_aio_basetrsio.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the base class of the readers and writers of SPPAS.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

from sppas.src.anndata.aio.basetrsio import sppasBaseIO
from sppas.src.anndata.ctrlvocab import sppasCtrlVocab
from sppas.src.anndata.media import sppasMedia
from sppas.src.anndata.ann.annlocation import sppasLocation
from sppas.src.anndata.ann.annlocation import sppasInterval
from sppas.src.anndata.ann.annlocation import sppasPoint
from sppas.src.anndata.ann.annlabel import sppasLabel
from sppas.src.anndata.ann.annlabel import sppasTag

# ---------------------------------------------------------------------------


class TestBaseIO(unittest.TestCase):
    """
    Base of the readers and writers.
    """
    def test_members(self):
        trs = sppasBaseIO()
        self.assertFalse(trs.multi_tiers_support())
        self.assertFalse(trs.no_tiers_support())
        self.assertFalse(trs.empty_tier_support())
        self.assertFalse(trs.metadata_support())
        self.assertFalse(trs.comments_support())
        self.assertFalse(trs.ctrl_vocab_support())
        self.assertFalse(trs.media_support())

# ---------------------------------------------------------------------------


class TestUnsupported(unittest.TestCase):
    """
    The tier a format is using to hold what it does not support.
    """
    def setUp(self):
        """Create a transcription of a format holding nothing but tiers."""
        self.trs = sppasBaseIO("trs-unsupported")
        self.trs._accept_multi_tiers = True
        self.trs.set_meta("annotator_name", "Brigitte Bigi")
        self.tier = self.trs.create_tier("phonemes")
        self.tier.set_meta("speaker_name", "Marie")
        for begin, end, tag in ((1., 2., "a"), (2., 3., "b")):
            self.tier.create_annotation(
                sppasLocation(sppasInterval(sppasPoint(begin), sppasPoint(end))),
                sppasLabel(sppasTag(tag)))

        self.ctrl_vocab = sppasCtrlVocab("phones")
        self.ctrl_vocab.add(sppasTag("a"))
        self.ctrl_vocab.add(sppasTag("b"))
        self.trs.add_ctrl_vocab(self.ctrl_vocab)
        self.tier.set_ctrl_vocab(self.ctrl_vocab)

        self.media = sppasMedia("sample.wav", mime_type="audio/wav")
        self.trs.add_media(self.media)
        self.tier.set_media(self.media)

    # -----------------------------------------------------------------------

    def test_entries(self):
        """The entries are the information the format can't hold."""
        entries = self.trs.unsupported_entries()
        natures = [nature for (nature, owner, key, value) in entries]
        self.assertTrue("metadata" in natures)
        self.assertEqual(2, natures.count("ctrl_vocab"))
        self.assertEqual(1, natures.count("media"))
        self.assertTrue(("metadata", "", "annotator_name", "Brigitte Bigi")
                        in entries)
        self.assertTrue(("metadata", "phonemes", "speaker_name", "Marie")
                        in entries)
        self.assertTrue(("ctrl_vocab", "phonemes", "phones", "a") in entries)
        self.assertTrue(("media", "phonemes", "sample.wav", "audio/wav")
                        in entries)

    # -----------------------------------------------------------------------

    def test_entries_of_a_format_holding_all(self):
        """Nothing is to be preserved if the format holds it."""
        self.trs._accept_metadata = True
        self.trs._accept_ctrl_vocab = True
        self.trs._accept_media = True
        self.assertEqual(0, len(self.trs.unsupported_entries()))
        self.assertIsNone(self.trs.create_unsupported_tier())

    # -----------------------------------------------------------------------

    def test_entries_of_generated_metadata(self):
        """The metadata SPPAS generates by itself are not preserved."""
        trs = sppasBaseIO("trs-generated-only")
        trs._accept_multi_tiers = True
        tier = trs.create_tier("phonemes")
        tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))),
            sppasLabel(sppasTag("a")))
        self.assertEqual(0, len(trs.unsupported_entries()))
        self.assertIsNone(trs.create_unsupported_tier())

        # but a value SPPAS did not assign is an information
        trs.set_meta("language_code_0", "fra")
        entries = trs.unsupported_entries()
        self.assertEqual(1, len(entries))
        self.assertEqual(("metadata", "", "language_code_0", "fra"),
                         entries[0])

    # -----------------------------------------------------------------------

    def test_no_tier_of_a_mono_tier_format(self):
        """A format holding one tier only can\'t hold this one more."""
        self.trs._accept_multi_tiers = False
        self.assertTrue(len(self.trs.unsupported_entries()) > 0)
        self.assertIsNone(self.trs.create_unsupported_tier())

    # -----------------------------------------------------------------------

    def test_create_tier(self):
        """The created tier is holding the keyword, then the entries."""
        entries = self.trs.unsupported_entries()
        tier = self.trs.create_unsupported_tier()

        self.assertEqual("DoNotEdit", tier.get_name())
        self.assertEqual(len(entries) + 1, len(tier))
        self.assertEqual("Metadata",
                         tier[0].get_labels()[0].get_best().get_content())

        # the whole time span of the transcription is shared into intervals
        self.assertEqual(1., tier.get_first_point().get_midpoint())
        self.assertEqual(3., tier.get_last_point().get_midpoint())

        # each annotation is holding key, value, nature and owner
        labels = tier[1].get_labels()
        self.assertEqual(4, len(labels))
        nature, owner, key, value = entries[0]
        self.assertEqual(key, labels[0].get_best().get_content())
        self.assertEqual(value, labels[1].get_best().get_content())
        self.assertEqual(nature, labels[2].get_best().get_content())
        self.assertEqual(owner, labels[3].get_best().get_content())

    # -----------------------------------------------------------------------

    def test_parse_tier(self):
        """The entries of the tier are assigned back to the objects."""
        self.trs.create_unsupported_tier()

        # a format read the file: the information is only in the tier
        other = sppasBaseIO()
        other._accept_multi_tiers = True
        tier = other.create_tier("phonemes")
        for ann in self.trs.find("phonemes"):
            tier.create_annotation(ann.get_location().copy(),
                                   [l.copy() for l in ann.get_labels()])
        unsupported = other.create_tier("DoNotEdit")
        for ann in self.trs.find("DoNotEdit"):
            unsupported.create_annotation(ann.get_location().copy(),
                                          [l.copy() for l in ann.get_labels()])

        self.assertTrue(other.parse_unsupported_tier())

        # the tier was a way to write, not data
        self.assertIsNone(other.find("DoNotEdit"))
        self.assertEqual(1, len(other))

        self.assertEqual("Brigitte Bigi", other.get_meta("annotator_name"))
        tier = other.find("phonemes")
        self.assertEqual("Marie", tier.get_meta("speaker_name"))
        self.assertEqual("phones", tier.get_ctrl_vocab().get_name())
        self.assertTrue(tier.get_ctrl_vocab().contains(sppasTag("a")))
        self.assertTrue(tier.get_ctrl_vocab().contains(sppasTag("b")))
        self.assertEqual("sample.wav", tier.get_media().get_filename())
        self.assertEqual("audio/wav", tier.get_media().get_mime_type())

    # -----------------------------------------------------------------------

    def test_parse_no_tier(self):
        """Nothing is parsed if the tier is missing or not the expected one."""
        self.assertFalse(self.trs.parse_unsupported_tier())

        tier = self.trs.create_tier("DoNotEdit")
        tier.create_annotation(
            sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))),
            sppasLabel(sppasTag("something else")))
        self.assertFalse(self.trs.parse_unsupported_tier())
        self.assertIsNotNone(self.trs.find("DoNotEdit"))

    # -----------------------------------------------------------------------

    def test_fill_entry(self):
        """An entry is assigned to the object it belongs to."""
        trs = sppasBaseIO()
        trs._accept_multi_tiers = True
        trs.create_tier("phonemes")

        self.assertTrue(trs.fill_unsupported_entry(
            "metadata", "", "annotator_name", "Brigitte Bigi"))
        self.assertEqual("Brigitte Bigi", trs.get_meta("annotator_name"))

        self.assertTrue(trs.fill_unsupported_entry(
            "media", "phonemes", "sample.wav", "audio/wav"))
        self.assertEqual("sample.wav",
                         trs.find("phonemes").get_media().get_filename())

        # an unknown nature, or an unknown owner, is assigned to nothing
        self.assertFalse(trs.fill_unsupported_entry(
            "unknown", "", "key", "value"))
        self.assertFalse(trs.fill_unsupported_entry(
            "metadata", "unknown tier", "key", "value"))
