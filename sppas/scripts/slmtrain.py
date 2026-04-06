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

    scripts.slmtrain.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to train a statistical language model.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Align.models import sppasNgramsModel
from sppas.src.annotations.Align.models import sppasArpaIO


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file " % os.path.basename(PROGRAM),
                        description="... a script to train a statistical language model.")

parser.add_argument("-i",
                    metavar="input",
                    action='append',
                    help='Input file name of the training corpus.')

parser.add_argument("-r",
                    metavar="vocab",
                    required=False,
                    help='List of known words.')

parser.add_argument("-n",
                    metavar="order",
                    required=False,
                    default=3,
                    type=int,
                    help='N-gram order value (default=1).')

parser.add_argument("-m",
                    metavar="method",
                    required=False,
                    default="logml",
                    type=str,
                    help='Method to estimates probabilities (one of: raw, lograw, ml, logml).')

parser.add_argument("-o",
                    metavar="output",
                    help='Output file name.')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

# ---------------------------------
# 1. Create a sppasNgramsModel

model = sppasNgramsModel(args.n)
if args.r:
    model.set_vocab(args.r)

if args.i:
    if not args.o:
        print("-o is required if -i option is used.")
        sys.exit(1)

    # ---------------------------------
    # 2. Estimate counts of each n-gram
    model.count(*(args.i))

    # ---------------------------------
    # 3. Estimate probabilities
    probas = model.probabilities(args.m)

    # ---------------------------------
    # 4. Write in an ARPA file
    arpaio = sppasArpaIO()
    arpaio.set(probas)
    arpaio.save(args.o)

else:

    # ---------------------------------
    # 2. Get sentences from stdin
    all_lines = list()
    for line in sys.stdin:
        line = line.strip()
        all_lines.append(line)

    # ---------------------------------
    # 3. Estimate counts of each n-gram
    model.append_sentences(all_lines)
    probas = model.probabilities(args.m)

    for t in probas[args.n-1]:
        print("{:s}\t{:d}".format(t[0], t[1]))
