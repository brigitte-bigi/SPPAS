# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ######   ########   ########      ###      ######
        ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
        ##        ##     ##  ##     ##   ##   ##   ##            annotation
         ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
        ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

        https://sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <https://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.ui.tests.test_wkps.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

import os
import unittest

from sppas.core.config import paths
from sppas.src.wkps.sppasWkps import sppasWkps


class TestSppasWorkspaces(unittest.TestCase):

    def setUp(self):
        return

    # -----------------------------------------------------------------------

    def test_init(self):
        wkps = sppasWkps()

        # At least the Blank workspace is stored into the list,
        # and the existing workspaces on the disk.
        self.assertGreaterEqual(len(wkps), 1)
        self.assertEqual(wkps.index("Blank"), 0)

    # -----------------------------------------------------------------------

    def test_new(self):
        """Create a workspace and append it to the SPPAS workspaces."""
        wkps = sppasWkps()

        # Attempt to create a workspace with the Blank name
        with self.assertRaises(ValueError):  # WkpIdValueError
            wkps.new("Blank")

        # Really create a new workspace
        wlen = len(wkps)
        n = wkps.new("test")
        self.assertEqual(len(wkps), wlen + 1)
        fn = os.path.join(paths.wkps, n + ".wjson")
        self.assertTrue(os.path.exists(fn))

        # Attempt to create a workspace with the same name
        with self.assertRaises(ValueError):  # WkpIdValueError
            wkps.new(n)

        os.remove(fn)

    # -----------------------------------------------------------------------

    def test_delete(self):
        wkps = sppasWkps()
        wlen = len(wkps)

        # Delete a workspace
        fn = os.path.join(paths.wkps, "test.wjson")
        n = wkps.new("test")
        i = wkps.index(n)
        wkps.delete(i)
        self.assertFalse(os.path.exists(fn))

        self.assertEqual(len(wkps), wlen)

    # -----------------------------------------------------------------------

    def test_rename(self):
        """Create, rename and delete a workspace in wkps folder."""
        wkps = sppasWkps()

        with self.assertRaises(IndexError):  # WkpRenameBlankError
            wkps.rename(0, "renamed")

        n = wkps.new("test")

        # Rename the workspace
        i = wkps.index(n)
        wkps.rename(i, "renamed")
        fn = os.path.join(paths.wkps, "renamed.wjson")
        self.assertTrue(os.path.exists(fn))

        # Delete a workspace
        wkps.delete(i)
        self.assertFalse(os.path.exists(fn))

    # -----------------------------------------------------------------------

    def test_update(self):
        """Re-scan the workspaces folder: files appear or disappear on disk."""
        wkps = sppasWkps()
        wlen = len(wkps)

        # A file appears on disk, created by another process (simulated by
        # writing it directly, bypassing wkps' own list): unknown to this
        # instance until update() is called.
        fn = os.path.join(paths.wkps, "external.wjson")
        other = sppasWkps()
        other.new("external")
        with self.assertRaises(ValueError):
            wkps.index("external")

        wkps.update()
        self.assertEqual(wkps.index("external"), wlen)
        self.assertEqual(len(wkps), wlen + 1)

        # The file disappears from disk, removed by another process.
        other.delete(other.index("external"))
        self.assertFalse(os.path.exists(fn))
        self.assertIn("external", list(wkps))

        wkps.update()
        with self.assertRaises(ValueError):
            wkps.index("external")
        self.assertEqual(len(wkps), wlen)

        # "Blank" always stays first.
        self.assertEqual(wkps.index("Blank"), 0)
