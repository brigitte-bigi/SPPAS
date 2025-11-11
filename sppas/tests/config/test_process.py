#!/usr/bin/env python
# -*- coding : UTF-8 -*-
"""
:filename: sppas.tests.config.test_process.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  The test of SPPAS external process execution.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

from sys import platform
import unittest

from sppas.core.config import sppasExecProcess

# ---------------------------------------------------------------------------


WIN_COMMAND = "dir c:"
POSIX_COMMAND = "ls -l"

# ---------------------------------------------------------------------------


class TestExecProcess(unittest.TestCase):
    def test_test_command(self):
        # can handle a non-existing command when testing with 'test_command' method
        p = sppasExecProcess()
        self.assertFalse(p.test_command("non_existing_command"))
        # can handle an existing command when testing with 'test_command' method
        p = sppasExecProcess()
        if platform == "win32":
            self.assertTrue(p.test_command(WIN_COMMAND))
        else:
            self.assertTrue(p.test_command(POSIX_COMMAND))

    def test_run_popen_success(self):
        # can successfully execute a command using 'run_popen' method
        p = sppasExecProcess()
        if platform == "win32":
            p.run_popen(WIN_COMMAND)
        else:
            p.run_popen(POSIX_COMMAND)
        self.assertNotEqual(p.out(), "")

    def test_run_success(self):
        # can successfully execute a command using 'run' method
        p = sppasExecProcess()
        if platform == "win32":
            p.run(WIN_COMMAND)
        else:
            p.run(POSIX_COMMAND)
        self.assertNotEqual(p.out(), "")

    def test_out_success(self):
        # can retrieve the standard output of a command using 'out' method
        p = sppasExecProcess()
        p.run("echo 'Hello, World!'")
        self.assertEqual(p.out(), "Hello, World!\n")

    def test_status(self):
        # can handle a command that returns a non-zero exit code when using 'run' method
        p = sppasExecProcess()
        if platform == "win32":
            p.run("dir a:")
        else:
            p.run("ls non_existing_directory")
        self.assertNotEqual(p.status(), 0)
        # can handle a command that returns a zero exit code when using 'run' method
        p = sppasExecProcess()
        if platform == "win32":
            p.run(WIN_COMMAND)
        else:
            p.run(POSIX_COMMAND)
        self.assertEqual(p.status(), 0)
