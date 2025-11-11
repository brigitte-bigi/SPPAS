# -*- coding: UTF-8 -*-
"""
:filename: sppas.tests.anndata.test_media.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test sppasMedia() class.

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

from sppas.src.anndata.media import sppasMedia

# ---------------------------------------------------------------------------


class TestMedia(unittest.TestCase):
    """Generic representation of a media file.
    The audio file is not loaded.

    """
    def setUp(self):
        pass

    def test_media_audio(self):
        m = sppasMedia("toto.wav")
        self.assertEqual(m.get_filename(), "toto.wav")
        self.assertIn(m.get_mime_type(), ["audio/wav", "audio/x-wav"])
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_video(self):
        m = sppasMedia("toto.mp4")
        self.assertEqual(m.get_filename(), "toto.mp4")
        self.assertEqual(m.get_mime_type(), "video/mp4")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_mime_error(self):
        m = sppasMedia("toto.xxx")
        self.assertEqual(m.get_filename(), "toto.xxx")
        self.assertEqual(m.get_mime_type(), "audio/basic")
        self.assertEqual(len(m.get_meta('id')), 36)

    def test_media_metadata(self):
        m = sppasMedia("toto.wav")
        m.set_meta("channel", "1")
        self.assertEqual(m.get_meta("channel"), "1")
        self.assertEqual(m.get_meta("canal"), "")
