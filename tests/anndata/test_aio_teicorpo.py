# -*- coding: UTF-8 -*-
"""
:filename: tests.anndata.test_aio_teicorpo.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Test the class sppasTEICORPO() to read and write TEI-Corpo files.

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
import os.path
import shutil

from sppas.src.anndata.aio.teicorpo import sppasTEICORPO
from sppas.src.anndata.ann.annlocation import sppasPoint

from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------------------


def canonical(filename):
    """Return the canonical content of a TEI-Corpo file.

    The canonical content is the whole information carried by the file,
    without its layout: the annotations with their resolved times, texts
    and identifiers, the target links, the declaration of the tiers, the
    speakers, the media and the revisions. Two files with the same
    canonical content carry exactly the same information.

    :param filename: (str) Name of the TEI-Corpo file.
    :return: (tuple) Blocks, spans, tiers, speakers, media, revisions.

    """
    import xml.etree.ElementTree as ET
    ns = "{http://www.tei-c.org/ns/1.0}"
    xml_id = "{http://www.w3.org/XML/1998/namespace}id"
    root = ET.parse(filename).getroot()

    times = dict()
    timeline = root.find(ns + "text/" + ns + "timeline")
    for when in timeline.findall(ns + "when"):
        if "absolute" in when.attrib:
            times[when.attrib.get(xml_id, "")] = float(when.attrib["absolute"])
    for when in timeline.findall(ns + "when"):
        if "interval" in when.attrib:
            interval = float(when.attrib["interval"])
            if interval < 0.:
                times[when.attrib.get(xml_id, "")] = None
            else:
                origin = times.get(when.attrib.get("since", "").lstrip("#"), 0.)
                if origin is None:
                    origin = 0.
                times[when.attrib.get(xml_id, "")] = interval + origin

    def resolve(ref):
        return times.get(ref.lstrip("#"), None)

    def canon_text(text):
        # Multiple whitespace can't survive sppas: it normalizes them
        # everywhere, whatever the format.
        return " ".join((text or "").split())

    def canon_node(node):
        children = tuple(canon_node(child) for child in node
                         if not child.tag.endswith("}spanGrp"))
        attrs = tuple(sorted(node.attrib.items()))
        return (node.tag, attrs, canon_text(node.text), children)

    blocks = list()
    spans = list()
    for block in root.iter(ns + "annotationBlock"):
        u_canon = tuple()
        u_node = block.find(ns + "u")
        if u_node is not None:
            u_canon = canon_node(u_node)
        blocks.append((block.attrib.get("who", ""),
                       resolve(block.attrib.get("start", "")),
                       resolve(block.attrib.get("end", "")),
                       u_canon,
                       block.attrib.get(xml_id, "")))
        for grp in block.iter(ns + "spanGrp"):
            for span in grp.findall(ns + "span"):
                spans.append((grp.attrib.get("type", ""),
                              resolve(span.attrib.get("from", "")),
                              resolve(span.attrib.get("to", "")),
                              span.attrib.get("target", ""),
                              canon_text(span.text),
                              span.attrib.get(xml_id, "")))

    tiers = dict()
    speakers = dict()
    header = root.find(ns + "teiHeader")
    for note in header.iter(ns + "note"):
        if note.attrib.get("type", "") != "TEMPLATE_DESC":
            continue
        for tier_note in note.findall(ns + "note"):
            declared = dict()
            for sub_note in tier_note.findall(ns + "note"):
                declared[sub_note.attrib.get("type", "")] = sub_note.text
            if "code" in declared:
                tiers[declared["code"]] = declared.get("parent", "-")
    for person in header.iter(ns + "person"):
        name_node = person.find(ns + "persName")
        name = name_node.text if name_node is not None else None
        for alt in person.iter(ns + "alt"):
            speakers[alt.attrib.get("type", "")] = name

    media = sorted(m.attrib.get("url", "")
                   for m in header.iter(ns + "media"))

    revisions = dict()
    for item in header.iter(ns + "item"):
        item_desc = item.find(ns + "desc")
        if item_desc is not None and item_desc.text is not None:
            revisions[item_desc.text] = item.text

    return (sorted(blocks), sorted(spans, key=lambda s: (s[0], s[5])),
            tiers, speakers, media, revisions)

# ---------------------------------------------------------------------------


class TestTEICORPO(unittest.TestCase):
    """Test the reader/writer of the TEI-Corpo files."""

    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------------

    def test_members(self):
        tei = sppasTEICORPO()
        self.assertTrue(tei.multi_tiers_support())
        self.assertTrue(tei.no_tiers_support())
        self.assertTrue(tei.metadata_support())
        self.assertFalse(tei.ctrl_vocab_support())
        self.assertTrue(tei.media_support())
        self.assertTrue(tei.hierarchy_support())
        self.assertTrue(tei.point_support())
        self.assertTrue(tei.interval_support())
        self.assertFalse(tei.disjoint_support())
        self.assertFalse(tei.alternative_localization_support())
        self.assertFalse(tei.alternative_tag_support())
        self.assertFalse(tei.tag_types_support())
        self.assertFalse(tei.tag_geometry_support())
        self.assertFalse(tei.radius_support())
        self.assertTrue(tei.gaps_support())
        self.assertTrue(tei.overlaps_support())

    # -----------------------------------------------------------------------

    def test_detect(self):
        self.assertTrue(sppasTEICORPO.detect(
            os.path.join(DATA, "sample.TextGrid.tei_corpo.xml")))
        self.assertFalse(sppasTEICORPO.detect(
            os.path.join(DATA, "sample.xra")))
        self.assertFalse(sppasTEICORPO.detect(
            os.path.join(DATA, "sample.TextGrid")))

    # -----------------------------------------------------------------------

    def test_read_textgrid_sample(self):
        """A single-tier TextGrid converted by TeiCorpo."""

        tei = sppasTEICORPO()
        tei.read(os.path.join(DATA, "sample.TextGrid.tei_corpo.xml"))

        # Tiers are declared in the header: P-Tones and transcription
        self.assertEqual(2, len(tei))
        self.assertIsNotNone(tei.find("P-Tones"))
        self.assertIsNotNone(tei.find("transcription"))

        transcription = tei.find("transcription")
        self.assertEqual(4, len(transcription))
        self.assertEqual(sppasPoint(0.), transcription.get_first_point())
        self.assertEqual(sppasPoint(2.328813), transcription.get_last_point())
        self.assertEqual("une classe entière qui a bien vu comment ça s'est passé",
                         transcription[0].serialize_labels())
        self.assertEqual("au2", transcription[0].get_meta("id"))

        # The P-Tones annotations have an aligned begin but their end
        # refers to the un-aligned time T2: they are points.
        tones = tei.find("P-Tones")
        self.assertEqual(2, len(tones))
        self.assertTrue(tones[0].location_is_point())
        self.assertEqual(sppasPoint(0.883), tones.get_first_point())
        self.assertEqual("L", tones[0].serialize_labels())
        self.assertEqual("H*", tones[1].serialize_labels())
        self.assertEqual("au0", tones[0].get_meta("id"))

        # A media is defined in the header
        self.assertEqual(1, len(tei.get_media_list()))

    # -----------------------------------------------------------------------

    def test_read_palign(self):
        """A multi-tier time-aligned TextGrid converted by TeiCorpo."""

        tei = sppasTEICORPO()
        tei.read(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid.tei_corpo.xml"))

        self.assertIsNotNone(tei.find("Transcription"))
        self.assertIsNotNone(tei.find("PhonAlign"))
        self.assertIsNotNone(tei.find("TokensAlign"))

        self.assertEqual(11, len(tei.find("Transcription")))
        self.assertTrue(len(tei.find("PhonAlign")) > 11)
        self.assertTrue(len(tei.find("TokensAlign")) > 11)

    # -----------------------------------------------------------------------

    def test_read_trs(self):
        """A Transcriber file converted by TeiCorpo, with speakers."""

        tei = sppasTEICORPO()
        tei.read(os.path.join(DATA, "20000410_0930_1030_rfi_fm_dga.trs.tei_corpo.xml"))

        # A tier for each speaker
        self.assertTrue(len(tei) > 10)

        # The names of the speakers are set to their tier
        spk = tei.find("spk43")
        self.assertIsNotNone(spk)
        self.assertEqual("Vincent Roux", spk.get_meta("speaker_name"))

    # -----------------------------------------------------------------------

    def test_read_eaf(self):
        """An ELAN file converted by TeiCorpo, with a target-based tier."""

        tei = sppasTEICORPO()
        tei.read(os.path.join(DATA, "sample.eaf.tei_corpo.xml"))

        self.assertIsNotNone(tei.find("W-RGU"))
        self.assertIsNotNone(tei.find("W-RGph"))
        self.assertIsNotNone(tei.find("W-RGMe"))

        # The W-RGMe annotations are attached to a W-RGph annotation
        # with a target: they share its localization and keep the link.
        rgme = tei.find("W-RGMe")
        self.assertTrue(len(rgme) > 0)
        self.assertTrue(rgme[0].is_meta_key("tei_target"))

        # Two media are defined in the header
        self.assertEqual(2, len(tei.get_media_list()))

    # -----------------------------------------------------------------------

    def test_write_read(self):
        """Write a read transcription and read it back."""

        tei = sppasTEICORPO()
        tei.read(os.path.join(DATA, "F_F_B003-P8-palign.TextGrid.tei_corpo.xml"))
        output = os.path.join(TEMP, "sample.tei")
        tei.write(output)

        self.assertTrue(sppasTEICORPO.detect(output))
        copy = sppasTEICORPO()
        copy.read(output)

        self.assertEqual(len(tei), len(copy))
        for tier, tier_copy in zip(tei, copy):
            self.assertEqual(tier.get_name(), tier_copy.get_name())
            self.assertEqual(len(tier), len(tier_copy))
            for ann, ann_copy in zip(tier, tier_copy):
                self.assertEqual(ann.get_location(), ann_copy.get_location())
                self.assertEqual(ann.serialize_labels(), ann_copy.serialize_labels())

    # -----------------------------------------------------------------------

    def test_zero_loss(self):
        """Read then write each sample: the canonical contents are equal."""

        for name in ("sample.TextGrid.tei_corpo.xml",
                     "F_F_B003-P8-palign.TextGrid.tei_corpo.xml",
                     "20000410_0930_1030_rfi_fm_dga.trs.tei_corpo.xml",
                     "sample.eaf.tei_corpo.xml"):
            tei = sppasTEICORPO()
            tei.read(os.path.join(DATA, name))
            output = os.path.join(TEMP, name + ".tei")
            tei.write(output)

            source = canonical(os.path.join(DATA, name))
            written = canonical(output)
            for i, part in enumerate(("blocks", "spans", "tiers",
                                      "speakers", "media", "revisions")):
                self.assertEqual(source[i], written[i],
                                 "{:s} differ in {:s}".format(part, name))
