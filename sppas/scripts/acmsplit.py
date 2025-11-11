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

    scripts.acmsplit.py
    ~~~~~~~~~~~~~~~~~~~

    ... a script to split a hmmdefs file into individual hmm files.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Align.models.acm.acmodelhtkio import sppasHtkIO


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i hmmdef -o dir" % os.path.basename(PROGRAM),
                        description="... a script to split a hmmdef file into hmms.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input file name (hmmdefs) or directory (hmmdefs+monophones.repl)')

parser.add_argument("-o",
                    metavar="dir",
                    required=True,
                    help='Output directory name')

parser.add_argument("--nomap",
                    action='store_true',
                    help="Disable mapping the monophones")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

if not os.path.isdir(args.o):
    print("Error: {0} must be an existing directory.".format(args.o))
    sys.exit(1)

# ----------------------------------------------------------------------------

if args.quiet is False:
    print("Loading AC:")

acmodel1 = sppasHtkIO()
if os.path.isfile(args.i):
    acmodel1.read(os.path.dirname(args.i), os.path.basename(args.i))
else:
    acmodel1.read(folder=args.i)
if args.quiet is False:
    print("... done")

# ----------------------------------------------------------------------------

acmodel = acmodel1.extract_monophones()
if args.nomap is False:
    acmodel.replace_phones()

for hmm in acmodel.get_hmms():

    filename = os.path.join(args.o, hmm.name)
    filename = filename + ".hmm"
    if args.quiet is False:
        print("{:s}: {:s}".format(hmm.name, filename))
    sppasHtkIO.write_hmm(hmm, filename)
