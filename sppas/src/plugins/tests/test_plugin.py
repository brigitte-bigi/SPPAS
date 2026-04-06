"""
:filename: sppas.src.plugins.tests.test_plugin.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test the data structure of one plugin.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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
import os

from sppas.core.coreutils import u

from sppas.src.plugins.plugin import sppasPluginParam

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestPluginParam(unittest.TestCase):

    def setUp(self):
        self.param = sppasPluginParam(DATA, "plugin.json")

    def test_getters(self):
        self.assertEqual(self.param.get_key(), "pluginid")
        self.assertEqual(self.param.get_name(), "The Plugin Name")
        self.assertEqual(self.param.get_descr(), "Performs something on some files.")
        self.assertEqual(self.param.get_icon(), "")

        opt = self.param.get_options()
        self.assertEqual(len(opt), 3)

        self.assertEqual(opt[0].get_key(), "-b")
        self.assertEqual(opt[1].get_key(), "--show-progress")
        self.assertEqual(opt[2].get_key(), "-i")
        self.assertEqual(opt[2].get_value(), u('C:\Windows'))
