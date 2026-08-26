# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_aio_subtitles.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the reader/writer classes of the subtitle file formats.

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
import codecs

from sppas.src.anndata.aio.subtitle import sppasBaseSubtitles
from sppas.src.anndata.aio.subtitle import sppasSubRip
from sppas.src.anndata.aio.subtitle import sppasSubViewer
from sppas.src.anndata.aio.subtitle import sppasWebVTT
from sppas.src.anndata.aio.subtitle import sppasLRC

from sppas.src.anndata.transcription import sppasTranscription
from sppas.src.anndata.ann.annlabel import sppasTag
from sppas.src.anndata.ann.annlabel import sppasLabel
from sppas.src.anndata.ann.annlocation import sppasInterval
from sppas.src.anndata.ann.annlocation import sppasPoint
from sppas.src.anndata.ann.annotation import sppasAnnotation
from sppas.src.anndata.ann.annlocation import sppasLocation

from sppas.src.utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# ---------------------------------------------------------------------------


def create_transcription_with_silence():
    """Return a transcription with two speech and one silence annotations.

    :return: (sppasTranscription)

    """
    trs = sppasTranscription()
    tier = trs.create_tier(name="subtitles")
    tier.append(sppasAnnotation(
        sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))),
        sppasLabel(sppasTag("Lorem ipsum"))))
    tier.append(sppasAnnotation(
        sppasLocation(sppasInterval(sppasPoint(3.5), sppasPoint(5.))),
        sppasLabel(sppasTag("#"))))
    tier.append(sppasAnnotation(
        sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(7.))),
        sppasLabel(sppasTag("dolor sit amet"))))
    return trs

# ---------------------------------------------------------------------------


class TestBaseSubtitle(unittest.TestCase):
    """
    Base text is mainly made of utility methods.

    """
    def test_members(self):
        txt = sppasBaseSubtitles()
        self.assertFalse(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertFalse(txt.empty_tier_support())
        self.assertFalse(txt.metadata_support())
        self.assertFalse(txt.comments_support())
        self.assertFalse(txt.ctrl_vocab_support())
        self.assertFalse(txt.media_support())
        self.assertFalse(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------

    def test_make_point(self):
        """Convert data into the appropriate digit type, or not."""

        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3.0"))
        self.assertEqual(sppasPoint(3., 0.02), sppasBaseSubtitles.make_point("3."))
        self.assertEqual(sppasPoint(3), sppasBaseSubtitles.make_point("3"))
        with self.assertRaises(TypeError):
            sppasBaseSubtitles.make_point("3a")

    # -----------------------------------------------------------------

    def test_serialize_location(self):
        """Test location -> timestamps."""

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.),
                                                         sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,500\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1.)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1),
                                                         sppasPoint(3))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,000 --> 00:00:03,000\n")

        a2 = sppasAnnotation(sppasLocation(sppasPoint(1)))
        self.assertEqual(sppasSubRip._serialize_location(a2),
                         "00:00:01,000 --> 00:00:02,000\n")

        # precision is 1 ms by default:
        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.23456789),
                                                         sppasPoint(3.56719))))
        self.assertEqual(sppasSubRip._serialize_location(a1),
                         "00:00:01,235 --> 00:00:03,567\n")

    # -----------------------------------------------------------------

    def test_is_silence(self):
        """Test if the best tag of an annotation is a silence."""

        location = sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5)))

        a1 = sppasAnnotation(location, sppasLabel(sppasTag("#")))
        self.assertTrue(sppasBaseSubtitles._is_silence(a1))

        a2 = sppasAnnotation(location, sppasLabel(sppasTag("sil")))
        self.assertTrue(sppasBaseSubtitles._is_silence(a2))

        a3 = sppasAnnotation(location, sppasLabel(sppasTag("Lorem ipsum")))
        self.assertFalse(sppasBaseSubtitles._is_silence(a3))

        a4 = sppasAnnotation(location)
        self.assertFalse(sppasBaseSubtitles._is_silence(a4))

# ---------------------------------------------------------------------


class TestSubRip(unittest.TestCase):
    """
    Represents a SubRip reader/writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_read(self):
        """Test of reading a SRT sample file."""

        txt = sppasSubRip()
        txt.read(os.path.join(DATA, "sample.srt"))
        self.assertEqual(len(txt), 1)
        self.assertEqual(len(txt[0]), 4)
        self.assertEqual(sppasPoint(0.), txt[0].get_first_point())
        self.assertEqual(sppasPoint(15.), txt[0].get_last_point())
        self.assertTrue(txt[0][2].is_meta_key('position_pixel_X1'))

        # multi-lines: 2 sppasLabel() created in the same annotation
        self.assertEqual(len(txt[0][1].get_labels()), 2)
        self.assertFalse("<i>" in txt[0][1].get_labels()[0].get_best().get_content())
        self.assertTrue("une classe" in txt[0][1].get_labels()[0].get_best().get_content())
        self.assertTrue("bien vu" in txt[0][1].get_labels()[1].get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_metadata(self):
        """Test metadata -> position."""

        a1 = sppasAnnotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(3.5))))
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X1", "10")
        a1.set_meta("position_pixel_Y1", "20")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "")
        a1.set_meta("position_pixel_X2", "100")
        a1.set_meta("position_pixel_Y2", "200")
        self.assertEqual(sppasSubRip._serialize_metadata(a1), "X1:10 Y1:20 X2:100 Y2:200\n")

    # -----------------------------------------------------------------

    def test_write(self):
        """Test of writing a SRT file: silences are not written."""

        txt = sppasSubRip()
        txt.set(create_transcription_with_silence())
        output = os.path.join(TEMP, "sample.srt")
        txt.write(output)

        with codecs.open(output, "r", "utf-8") as fp:
            content = fp.read()

        self.assertTrue("1\n00:00:01,000 --> 00:00:03,500\nLorem ipsum\n" in content)
        self.assertTrue("2\n00:00:05,000 --> 00:00:07,000\ndolor sit amet\n" in content)
        self.assertFalse("#" in content)

# ---------------------------------------------------------------------


class TestWebVTT(unittest.TestCase):
    """
    Represents a WebVTT writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_write(self):
        """Test of writing a VTT file: header, timestamps, no silence."""

        txt = sppasWebVTT()
        txt.set(create_transcription_with_silence())
        output = os.path.join(TEMP, "sample.vtt")
        txt.write(output)

        with codecs.open(output, "r", "utf-8") as fp:
            content = fp.read()

        self.assertTrue(content.startswith("WEBVTT\n\n"))
        self.assertTrue("1\n00:00:01.000 --> 00:00:03.500\nLorem ipsum\n" in content)
        self.assertTrue("2\n00:00:05.000 --> 00:00:07.000\ndolor sit amet\n" in content)
        self.assertFalse("#" in content)
        self.assertFalse("," in content)

# ---------------------------------------------------------------------


class TestSubViewer(unittest.TestCase):
    """
    Represents a SubViewer reader/writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_read(self):
        """Test of reading a SUB sample file."""

        txt = sppasSubViewer()
        txt.read(os.path.join(DATA, "sample.sub"))
        self.assertEqual(txt.get_meta('annotator_name'), "FK")

        self.assertEqual(1, len(txt))
        self.assertEqual(6, len(txt[0]))
        self.assertEqual(sppasPoint(22.5), txt[0].get_first_point())
        self.assertEqual(sppasPoint(34.80), txt[0].get_last_point())
        self.assertFalse("[br]" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("Lorem ipsum dolor sit amet" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("consectetur adipiscing elit" in txt[0][0].get_labels()[1].get_best().get_content())

        self.assertTrue("Lorem ipsum dolor sit amet" in txt[0][0].get_labels()[0].get_best().get_content())
        self.assertTrue("consectetur adipiscing elit" in txt[0][0].get_labels()[1].get_best().get_content())

    # -----------------------------------------------------------------

    def test_serialize_header(self):
        """Test metadata -> header."""

        txt = sppasSubViewer()
        header = txt._serialize_header()
        self.assertEqual(len(header.split('\n')), 14)

    # -----------------------------------------------------------------

    def test_write(self):
        """Test of writing a SUB file: silences are not written."""

        txt = sppasSubViewer()
        txt.set(create_transcription_with_silence())
        output = os.path.join(TEMP, "sample.sub")
        txt.write(output)

        with codecs.open(output, "r", "utf-8") as fp:
            content = fp.read()

        self.assertTrue("00:00:01.000,00:00:03.500\nLorem ipsum\n" in content)
        self.assertTrue("00:00:05.000,00:00:07.000\ndolor sit amet\n" in content)
        self.assertFalse("#" in content)

# ---------------------------------------------------------------------


class TestLRC(unittest.TestCase):
    """
    Represents a LRC reader/writer.

    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    # -----------------------------------------------------------------

    def test_read(self):
        """Test of reading a LRC sample file."""

        txt = sppasLRC()
        txt.read(os.path.join(DATA, "sample.lrc"))

        self.assertEqual(txt.get_meta("lrc_artist"), "The Artist")
        self.assertEqual(txt.get_meta("lrc_title"), "The Title")

        self.assertEqual(len(txt), 2)
        self.assertEqual(txt[0].get_name(), "Transcription")
        self.assertEqual(txt[1].get_name(), "Tokens")
        self.assertEqual(len(txt[0]), 3)
        self.assertEqual(len(txt[1]), 5)

        self.assertEqual(sppasPoint(12.), txt[0].get_first_point())
        self.assertEqual(sppasPoint(23.5), txt[0].get_last_point())

        self.assertEqual("Lorem ipsum dolor sit amet",
                         " ".join(label.get_best().get_content() for label in txt[0][0].get_labels()))
        self.assertEqual("sed", txt[1][2].get_best_tag().get_content())
        self.assertEqual(sppasPoint(21.8), txt[1][3].get_lowest_localization())

    # -----------------------------------------------------------------

    def test_write(self):
        """Test of writing a LRC file: header, line and word timestamps."""

        txt = sppasLRC()
        txt.read(os.path.join(DATA, "sample.lrc"))
        output = os.path.join(TEMP, "sample.lrc")
        txt.write(output)

        with codecs.open(output, "r", "utf-8") as fp:
            content = fp.read()

        self.assertTrue("[ar:The Artist]" in content)
        self.assertTrue("[ti:The Title]" in content)
        self.assertTrue("[00:12.00]Lorem ipsum dolor sit amet" in content)
        self.assertTrue("[00:17.20]consectetur adipiscing elit" in content)
        self.assertTrue("[00:21.10]<00:21.10>sed <00:21.80>do <00:22.50>eiusmod" in content)
