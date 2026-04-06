# -*- coding:utf-8 -*-
"""
:filename: sppas.src.config.appcfg.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Unittests of the application workspace manager.

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

import sppas

from sppas.src.wkps.fileref import sppasRefAttribute, sppasCatReference
from sppas.src.wkps.workspace import sppasWorkspace
from sppas.src.wkps.filestructure import FileName, FileRoot
from sppas.src.wkps.filebase import States

# ----------------------------------------------------------------------------


class TestWorkspace(unittest.TestCase):

    def setUp(self):
        self.data = sppasWorkspace()
        self.data.add_file(__file__)
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-jpn', 'JPA_M16_JPA_T02.TextGrid'))
        self.data.add_file(os.path.join(sppas.paths.samples, 'samples-cat', 'TB-FE1-H1_phrase1.TextGrid'))

        self.r1 = sppasCatReference('SpeakerAB')
        self.r1.set_type('SPEAKER')
        self.r1.append(sppasRefAttribute('initials', 'AB'))
        self.r1.append(sppasRefAttribute('sex', 'F'))
        self.r2 = sppasCatReference('SpeakerCM')
        self.r2.set_type('SPEAKER')
        self.r2.append(sppasRefAttribute('initials', 'CM'))
        self.r2.append(sppasRefAttribute('sex', 'F'))
        self.r3 = sppasCatReference('Dialog1')
        self.r3.set_type('INTERACTION')
        self.r3.append(sppasRefAttribute('when', '2003', 'int', 'Year of recording'))
        self.r3.append(sppasRefAttribute('where', 'Aix-en-Provence', descr='Place of recording'))

    # ---------------------------------------------------------------------------

    def test_init(self):
        data = sppasWorkspace()
        self.assertEqual(36, len(data.id))
        self.assertEqual(0, len(data.get_paths()))

    # ---------------------------------------------------------------------------

    def test_state(self):
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().CHECKED, self.data.get_paths()[0].state)
        self.assertEqual(States().CHECKED, self.data.get_paths()[1].state)
        self.assertEqual(States().CHECKED, self.data.get_paths()[2].state)
        self.assertEqual(States().CHECKED, self.data.get_paths()[3].state)

    # ---------------------------------------------------------------------------

    def test_wrong_way_to_set_state(self):
        """This is exactly what We WILL NEVER DO."""
        wkp = sppasWorkspace()
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        for fp in wkp.get_paths():
            for fr in fp:
                for fn in fr:
                    fn.set_state(States().CHECKED)
                    self.assertEqual(fn.state, States().CHECKED)
                    fn.set_state(States().UNUSED)
                    self.assertEqual(fn.state, States().UNUSED)
                    # but... file is existing
                    fn.set_state(States().MISSING)
                    self.assertNotEqual(fn.state, States().MISSING)
                    fn.set_state(States().CHECKED)
                    self.assertEqual(fn.state, States().CHECKED)
        # ... BUT fp and fr were not updated! So our workspace is CORRUPTED.
        # WE EXPECT STATE OF FR AND FN TO BE **checked** AND THEY ARE NOT:
        for fp in wkp.get_paths():
            self.assertEqual(fp.state, States().UNUSED)
            for fr in fp:
                self.assertEqual(fr.state, States().UNUSED)

    # ---------------------------------------------------------------------------

    def test_right_way_to_set_state(self):
        # USE THIS INSTEAD:
        wkp = sppasWorkspace()
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        wkp.set_object_state(States().CHECKED, fn)
        for fp in wkp.get_paths():
            self.assertEqual(fp.state, States().CHECKED)
            for fr in fp:
                self.assertEqual(fr.state, States().CHECKED)

    # ---------------------------------------------------------------------------

    def test_lock_all(self):
        # Lock all files
        self.data.set_object_state(States().LOCKED)
        self.assertEqual(States().LOCKED, self.data.get_paths()[0].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[1].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[2].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[3].state)

        # as soon as a file is locked, the "set_object_state()" does not work anymore
        self.data.set_object_state(States().CHECKED)
        self.assertEqual(States().LOCKED, self.data.get_paths()[0].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[1].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[2].state)
        self.assertEqual(States().LOCKED, self.data.get_paths()[3].state)

        # only the unlock method has to be used to unlock files
        self.data.unlock()

    # ---------------------------------------------------------------------------

    def test_lock_filename(self):
        # Lock a single file
        filename = os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier')
        fn = self.data.get_object(filename)
        self.assertIsInstance(fn, FileName)
        self.data.set_object_state(States().LOCKED, fn)
        self.assertEqual(States().LOCKED, fn.state)

        self.assertEqual(States().UNUSED, self.data.get_paths()[0].state)
        self.assertEqual(States().AT_LEAST_ONE_LOCKED, self.data.get_paths()[1].state)

        # unlock a single file
        n = self.data.unlock([fn])
        self.assertEqual(1, n)
        self.assertEqual(States().CHECKED, fn.state)
        self.assertEqual(States().AT_LEAST_ONE_CHECKED, self.data.get_paths()[1].state)

    # ---------------------------------------------------------------------------

    def test_ref(self):
        self.data.add_ref(self.r1)
        self.assertEqual(1, len(self.data.get_refs()))
        self.data.add_ref(self.r2)
        self.assertEqual(2, len(self.data.get_refs()))
        self.r1.set_state(States().CHECKED)
        self.r2.set_state(States().CHECKED)
        self.data.remove_refs(States().CHECKED)
        self.assertEqual(0, len(self.data.get_refs()))

    # ---------------------------------------------------------------------------

    def test_assocations(self):
        self.data.add_ref(self.r1)
        self.data.set_object_state(States().CHECKED)

        for ref in self.data.get_refs():
            self.data.set_object_state(States().CHECKED, ref)

        self.data.associate()

        for fp in self.data.get_paths():
            for fr in fp:
                self.assertTrue(self.r1 in fr.get_references())

        self.data.dissociate()

        for fp in self.data.get_paths():
            for fr in fp:
                self.assertEqual(0, len(fr.get_references()))

    # ---------------------------------------------------------------------------

    def test_get_parent(self):
        filename = os.path.join(sppas.paths.samples, 'samples-fra', 'AC track_0379.PitchTier')
        fr = self.data.get_object(FileRoot.root(filename))
        self.assertIsNotNone(fr)
        fn = self.data.get_object(filename)
        self.assertIsNotNone(fn)
        self.assertEqual(fr, self.data.get_parent(fn))

    # ---------------------------------------------------------------------------

    def test_remove(self):
        # Create a workspace and add 6 files (3 roots, 2 paths)
        wkp = sppasWorkspace()
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'), brothers=True)
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-pol', '0002.txt'), brothers=True)
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-eng', 'oriana1.txt'))
        wkp.add_file(os.path.join(sppas.paths.samples, 'samples-eng', 'oriana1.wav'))

        # Check 4 of the files
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-pol', '0001.wav'))
        self.assertIsNotNone(fn)
        wkp.set_object_state(States().CHECKED, fn)
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-pol', '0001.txt'))
        self.assertIsNotNone(fn)
        wkp.set_object_state(States().CHECKED, fn)
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-eng', 'oriana1.wav'))
        self.assertIsNotNone(fn)
        wkp.set_object_state(States().CHECKED, fn)
        fn = wkp.get_object(os.path.join(sppas.paths.samples, 'samples-eng', 'oriana1.txt'))
        self.assertIsNotNone(fn)
        wkp.set_object_state(States().CHECKED, fn)
        nb_files = 0
        nb_roots = 0
        for fp in wkp.get_paths():
            nb_roots += len(fp)
            for fr in fp:
                nb_files += len(fr)
        self.assertEqual(nb_files, 6)
        self.assertEqual(nb_roots, 3)
        self.assertEqual(len(wkp.get_paths()), 2)

        # Remove checked files. we expect that the workspace contains 4 files
        wkp.remove_files(States().CHECKED)
        nb_files = 0
        nb_roots = 0
        for fp in wkp.get_paths():
            nb_roots += len(fp)
            for fr in fp:
                nb_files += len(fr)
        self.assertEqual(nb_files, 2)
        self.assertEqual(nb_roots, 3)
        self.assertEqual(len(wkp.get_paths()), 2)

        # Remove empty roots and paths
        wkp.remove_empties()
        nb_files = 0
        nb_roots = 0
        for fp in wkp.get_paths():
            nb_roots += len(fp)
            for fr in fp:
                nb_files += len(fr)
        self.assertEqual(nb_files, 2)
        self.assertEqual(nb_roots, 1)
        self.assertEqual(len(wkp.get_paths()), 1)
