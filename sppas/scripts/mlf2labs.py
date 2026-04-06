#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
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

    scripts.mlf2labs.py
    ~~~~~~~~~~~~~~~~~~~~~~

    ... a script to split a .mlf file into several lab files.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(
    usage="%(prog)s [options]",
    description="Split a .mlf file into several lab files.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input MLF file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

basefolder, _ = os.path.splitext(args.i)
out_folder = os.path.join(os.path.dirname(args.i), basefolder)
os.mkdir(out_folder)
filename = ""
out_fp = None

with open(args.i, "r") as fp:
    line = fp.readline()
    if "MLF" not in line:
        raise IOError("A MLF file should contain the MLF header in its 1st line.")

    for line in fp.readlines():
        if line.startswith('"'):
            # fix new filename
            filename = os.path.basename(line.replace('"', ""))
            filename = filename.replace("\r", "")
            filename = filename.replace("\n", "")
            # to be convenient with SPPAS requirements
            f, e = os.path.splitext(filename)
            if "-palign" not in filename:
                filename = f.replace("-", "_") + "-palign" + e
            # open the file
            out_fp = open(os.path.join(out_folder, filename), "w")
        elif line.startswith('.'):
            out_fp.close()
        else:
            out_fp.write(line)
