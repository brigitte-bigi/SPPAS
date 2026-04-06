#!/usr/bin/env python
# -*- coding : UTF-8 -*-
"""
:filename: sppas.tests.config.test_iso639.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The test of SPPAS ISO manager.

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

from sppas.core.coreutils import LanguageNotFoundError
from sppas.core.coreutils.iso639 import ISO639

# ---------------------------------------------------------------------------


class TestISO639(unittest.TestCase):

    def test_iso639_valid_code(self):
        iso = ISO639()
        language_info = iso.get_language_info('eng')
        self.assertEqual(language_info.iso639_1_code, 'en')
        self.assertEqual(language_info.language_name, 'English')

    def test_iso639_invalid_code(self):
        iso = ISO639()
        with self.assertRaises(LanguageNotFoundError) as context:
            iso.get_language_info('xyz')

        self.assertIn("0350", str(context.exception))
