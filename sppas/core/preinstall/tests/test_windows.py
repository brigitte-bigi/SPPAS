"""
:filename: sppas.src.preinstall.tests.test_windows.py
:author: Florian Hocquet, Brigitte Bigi
:contact: contact@sppas.org
:summary: Test of install under windows

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

from sppas.core.preinstall.installer import WindowsInstaller
from sppas.ui.term.textprogress import ProcessProgressTerminal

# ---------------------------------------------------------------------------


class TestInstallerWin(unittest.TestCase):

    def setUp(self):
        """Initialisation des tests.

        """
        p = ProcessProgressTerminal()
        self.__windows = WindowsInstaller()

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Test if the method search_package from the class WindowsInstaller works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows._search_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Test if the method install_package from the class WindowsInstaller works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows._install_package("aaaa")

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Test if the method version_package from the class WindowsInstaller works well.

        """
        self.assertTrue(self.__windows._version_package("aaaa", "aaaa"))

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Test if the method need_update_package from the class WindowsInstaller works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows._need_update_package("aaaa", "aaaa")

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Test if the method update_package from the class WindowsInstaller works well.

        """
        with self.assertRaises(NotImplementedError):
            self.__windows._update_package("aaaa", "4.0")
