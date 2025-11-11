"""
:filename: sppas.src.plugins.test.test_manager.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test of the plugins manager.

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

from sppas.core.config import paths

from sppas.src.plugins.manager import sppasPluginsManager

# ---------------------------------------------------------------------------

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
soxplugin = os.path.join(DATA, "soxplugintest.zip")
sample = os.path.join(paths.samples, "samples-eng", "oriana1.wav")

# ---------------------------------------------------------------------------


class TestPluginsManager(unittest.TestCase):

    def setUp(self):
        self.manager = sppasPluginsManager()

    def test_all(self):

        # some plugins are already installed in the package of SPPAS
        plg = 2   # audioseg is now distributed with the release
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))

        # Install a plugin
        soxid = self.manager.install(soxplugin, "SoX")
        self.assertEqual(plg+1, len(self.manager.get_plugin_ids()))

        # Use it!
        output = sample.replace('.wav', '-converted.wav')
        p = self.manager.get_plugin(soxid)
        message = self.manager.run_plugin(soxid, [sample])

        # Delete it...
        self.manager.delete(soxid)
        self.assertEqual(plg, len(self.manager.get_plugin_ids()))

        # Test result of the run
        self.assertGreater(len(message), 0)
        self.assertTrue(os.path.exists(output))
        os.remove(output)
