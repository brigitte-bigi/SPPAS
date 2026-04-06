"""
:filename: sppas.tests.config.test_appcfg.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Unittests for appcfg.py.

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

import os
import unittest

from sppas.core.config.appcfg import sppasAppConfig

# ---------------------------------------------------------------------------


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.__configuration = sppasAppConfig()

    # ---------------------------------------------------------------------------

    def test_cfg_filename(self):
        # Return the name of the config file.
        y = self.__configuration.cfg_filename()
        self.assertIn(".app~", y)

    # ---------------------------------------------------------------------------

    def test_get_set_deps(self):
        self.__configuration.set_feature("first", True)
        y = self.__configuration.get_feature_ids()
        self.assertTrue("first" in y)

        self.__configuration.set_feature("second", True)
        y = self.__configuration.get_feature_ids()
        self.assertTrue("second" in y)

    # ---------------------------------------------------------------------------

    def test_feature_installed(self):
        """Return True if a dependency is installed"""
        self.assertFalse(self.__configuration.feature_installed("aaaa"))
        if os.path.exists(self.__configuration.cfg_filename()) is True:
            self.assertTrue(self.__configuration.feature_installed("wxpython"))
            self.assertTrue(self.__configuration.feature_installed("julius"))
