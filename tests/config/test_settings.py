"""
:filename: sppas.tests.config.test_settings.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The test of SPPAS settings.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######  ########  ########     ###     ######
    ##    ## ##     ## ##     ##   ## ##   ##    ##     the automatic
    ##       ##     ## ##     ##  ##   ##  ##            annotation
     ######  ########  ########  ##     ##  ######        and
          ## ##        ##        #########       ##        analysis
    ##    ## ##        ##        ##     ## ##    ##         of speech
     ######  ##        ##        ##     ##  ######

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

from sppas.core.config.settings import sppasBaseSettings
from sppas.core.config.settings import sppasPathSettings
from sppas.core.config.settings import sppasGlobalSettings
from sppas.core.config.settings import sppasSymbolSettings
from sppas.core.config.settings import sppasSeparatorSettings
from sppas.core.config.settings import sppasAnnotationsSettings
from sppas.core.config.settings import sppasExtensionsSettings

# ---------------------------------------------------------------------------


class TestBaseSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasBaseSettings()
        self.assertEqual(settings.__dict__, {})

    def test_enter(self):
        with sppasBaseSettings() as settings:
            self.assertEqual(settings.__dict__, {})

    def test_add_attribute(self):
        settings = sppasBaseSettings()
        settings.__dict__['key'] = 'value'
        self.assertEqual(settings.key, 'value')
        settings.new_key = 'new_value'
        self.assertEqual(settings.new_key, 'new_value')

# ---------------------------------------------------------------------------


class TestPathSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasPathSettings()
        self.assertEqual(len(settings.__dict__), 21)
        self.assertEqual(settings._is_frozen, True)

    def test_enter(self):
        with sppasPathSettings() as settings:
            self.assertEqual(len(settings.__dict__), 21)

    def test_immutable(self):
        settings = sppasPathSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings._is_frozen

# ---------------------------------------------------------------------------


class TestGlobalSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasGlobalSettings()
        self.assertEqual(settings.__name__, "SPPAS")
        self.assertEqual(len(settings.__dict__), 12)
        self.assertEqual(settings._is_frozen, True)

    def test_enter(self):
        with sppasGlobalSettings() as settings:
            self.assertEqual(len(settings.__dict__), 12)

    def test_immutable(self):
        settings = sppasGlobalSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings.__name__

# ---------------------------------------------------------------------------


class TestSymbolSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasSymbolSettings()
        self.assertEqual(settings.unk, "dummy")
        self.assertEqual(len(settings.__dict__), 5)
        self.assertEqual(settings._is_frozen, True)

    def test_enter(self):
        with sppasSymbolSettings() as settings:
            self.assertEqual(len(settings.__dict__), 5)

    def test_immutable(self):
        settings = sppasSymbolSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings.unk

# ---------------------------------------------------------------------------


class TestSeparatorSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasSeparatorSettings()
        print(settings.__dict__)
        self.assertEqual(settings.phonemes, "-")
        self.assertEqual(settings.syllables, ".")
        self.assertEqual(settings.variants, "|")
        self.assertEqual(settings._is_frozen, True)
        self.assertEqual(len(settings.__dict__), 4)

    def test_enter(self):
        with sppasSeparatorSettings() as settings:
            self.assertEqual(len(settings.__dict__), 4)

    def test_immutable(self):
        settings = sppasSeparatorSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings.phonemes

# ---------------------------------------------------------------------------


class TestAnnotationSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasAnnotationsSettings()
        print(settings.__dict__)
        self.assertEqual(settings.ok, 0)
        self.assertEqual(settings._is_frozen, True)
        self.assertEqual(len(settings.__dict__), 15)

    def test_enter(self):
        with sppasAnnotationsSettings() as settings:
            self.assertEqual(len(settings.__dict__), 15)

    def test_immutable(self):
        settings = sppasAnnotationsSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings.ok

# ---------------------------------------------------------------------------


class TestExtensionsSettings(unittest.TestCase):
    def test_init(self):
        settings = sppasExtensionsSettings()
        print(settings.__dict__)
        self.assertEqual(settings.audio_extension, ".wav")
        self.assertEqual(settings._is_frozen, True)
        self.assertEqual(len(settings.__dict__), 8)

    def test_enter(self):
        with sppasExtensionsSettings() as settings:
            self.assertEqual(len(settings.__dict__), 8)

    def test_immutable(self):
        settings = sppasExtensionsSettings()
        with self.assertRaises(AttributeError):
            settings.key = 'value'
        with self.assertRaises(AttributeError):
            del settings.audio_extension
