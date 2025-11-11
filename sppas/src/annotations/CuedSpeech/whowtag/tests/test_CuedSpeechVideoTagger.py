# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videocued.py
:author:   Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Unit tests for tag a video in cued speech.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

    ---------------------------------------------------------------------

"""

import os
import unittest

from sppas.core.config import paths
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasIOError
from sppas.src.anndata import sppasTrsRW

from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag.whowtagvideo import CuedSpeechVideoTagger

# -----------------------------------------------------------------------

FRA_KEYS = os.path.join(paths.resources, "cuedspeech", "cueConfig-fra.txt")
HANDS_SET_PREFIX = "brigitte"

VIDEO_FILE = os.path.join(paths.demo, "demo.mp4")
TRANSCRIPTION_FILE = os.path.join(paths.demo, "demo-coords.xra")

# -----------------------------------------------------------------------


class TestVideoTagger(unittest.TestCase):
    """Unit tests class of the CuedSpeechVideoTagger class."""

    def setUp(self) -> None:
        self.cues = CuedSpeechKeys(FRA_KEYS)

    # -----------------------------------------------------------------------
    # Test Constructor
    # -----------------------------------------------------------------------

    def test_instance(self):
        # wrong parameter type case
        with self.assertRaises(sppasTypeError):
            CuedSpeechVideoTagger(4.98)

        # correct case
        CuedSpeechVideoTagger(self.cues)

    # -----------------------------------------------------------------------
    # Test Getters & Setters
    # -----------------------------------------------------------------------

    def test_close_video(self):
        video_tagger = CuedSpeechVideoTagger(self.cues)
        video_tagger.load(VIDEO_FILE)

        self.assertTrue(video_tagger.is_loaded())
        video_tagger.close()
        self.assertFalse(video_tagger.is_loaded())

    # -----------------------------------------------------------------------

    def test_input_video(self):
        video_tagger = CuedSpeechVideoTagger(self.cues)

        # no video load yet
        self.assertFalse(video_tagger.is_loaded())

        video_tagger.load(VIDEO_FILE)
        # input video loaded
        self.assertTrue(video_tagger.is_loaded())

        video_tagger.close()
        # input video closed
        self.assertFalse(video_tagger.is_loaded())

    # -----------------------------------------------------------------------

    def test_hands_load(self):
        video_tagger = CuedSpeechVideoTagger(self.cues)

        # wrong prefix case
        with self.assertRaises(sppasIOError):
            video_tagger.load_hands("coucou")

        # correct case
        video_tagger.load_hands(HANDS_SET_PREFIX)  # raise nothing

    # -----------------------------------------------------------------------
    # Test Tag Video
    # -----------------------------------------------------------------------

    def test_video_tag(self):
        parser = sppasTrsRW(TRANSCRIPTION_FILE)
        transcription = parser.read()

        video_tagger = CuedSpeechVideoTagger(self.cues)
        video_tagger.load(VIDEO_FILE)

        # tagged normal video
        video_tagger.tag_with_keys(transcription, "test_cued_speech_1")

        # tagged video with options
        video_tagger.set_option("handsset", "cartoonhandcue")
        video_tagger.set_option("handsfilter", "cartoon")

        video_tagger.set_option("infotext", True)
        video_tagger.set_option("vowelspos", True)

        video_tagger.tag_with_keys(transcription, "test_cued_speech_2")
