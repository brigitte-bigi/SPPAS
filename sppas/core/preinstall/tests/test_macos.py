"""
:filename: sppas.src.preinstall.tests.test_macos.py
:author: Florian Hocquet, Brigitte Bigi
:contact: contact@sppas.org
:summary: Test of installer under mac os system

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

from sppas.core.coreutils import sppasInstallationError
from sppas.core.preinstall.installer import MacOsInstaller

# ---------------------------------------------------------------------------


class TestInstallerMacOs(unittest.TestCase):

    def setUp(self):
        """Initialisation."""
        self.__macos = MacOsInstaller()

    # ---------------------------------------------------------------------------

    def test_search_package(self):
        """Returns True if package is already installed."""
        self.assertFalse(self.__macos._search_package("juliuussssss"))
        self.assertFalse(self.__macos._search_package(4))

        # Only if brew is already install on the computer
        # self.assertTrue(self.__macos.search_package("brew"))

    # ---------------------------------------------------------------------------

    def test_install_package(self):
        """Install package."""
        with self.assertRaises(sppasInstallationError):
            self.assertFalse(self.__macos._install_package("juliuussssss"))
        with self.assertRaises(sppasInstallationError):
            self.assertFalse(self.__macos._install_package(4))

    # ---------------------------------------------------------------------------

    def test_version_package(self):
        """Returns True if package is up to date."""
        self.assertTrue(self.__macos._version_package("julius", ">;0.0"))
        self.assertTrue(self.__macos._version_package("flac", ">;0.0"))

        with self.assertRaises(IndexError):
            self.assertTrue(self.__macos._version_package("julius", "aaaa"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._version_package("julius", "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._version_package("julius", "=;4.2"))

    # ---------------------------------------------------------------------------

    def test_need_update_package(self):
        """Return True if the package need to be update."""
        x = "julius: stable 4.5 (bottled) \\r\\n" \
            "Two-pass large vocabulary continuous speech recognition engine \\r\\n" \
            "https://github.com/julius-speech/julius \\r\\n" \
            "/usr/local/Cellar/julius/4.5 (76 files, 3.6MB) * \\r\\n"

        y = "flac: stable 1.3.3 (bottled), HEAD \\r\\n" \
            "Free lossless audio codec \\r\\n" \
            "https://xiph.org/flac/ \\r\\n" \
            "/usr/local/Cellar/flac/1.3.3 (53 files, 2.4MB) * \n" \

        with self.assertRaises(IndexError):
            self.__macos._need_update_package("Bonjour", "aaaa")

        with self.assertRaises(IndexError):
            self.__macos._need_update_package(y, "aaaa")

        self.assertTrue(self.__macos._need_update_package(x, ">;4.6"))
        self.assertFalse(self.__macos._need_update_package(x, ">;4.0"))

        self.assertTrue(self.__macos._need_update_package(y, ">;1.4"))
        self.assertFalse(self.__macos._need_update_package(y, ">;1.0"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._need_update_package(x, "<;4.2"))

        with self.assertRaises(ValueError):
            self.assertTrue(self.__macos._need_update_package(y, "=;1.2"))

    # ---------------------------------------------------------------------------

    def test_update_package(self):
        """Update package."""
        with self.assertRaises(sppasInstallationError):
            self.assertFalse(self.__macos._update_package("wxpythonnnn", "4.0"))
        with self.assertRaises(sppasInstallationError):
            self.assertFalse(self.__macos._update_package(4, "4.0"))
