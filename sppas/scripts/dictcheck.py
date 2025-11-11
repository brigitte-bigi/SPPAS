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

    scripts.dictcheck.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to detect pronunciation anomalies into a dictionary.

"""

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import separators
from sppas.src.resources import sppasDictPron

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -o file [options]" % os.path.basename(PROGRAM),
                        description="... a script to detect pronunciation anomalies into a dictionary.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input dictionary file name (as many as wanted)')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

args = parser.parse_args()

pron_dict = sppasDictPron(args.i, nodump=True)

for entry in pron_dict:

    prons = pron_dict.get_pron(entry)
    nb_chars = float(len(entry))

    for pron in prons.split(separators.variants):

        phonetization = pron.split(separators.phonemes)
        nb_phones = float(len(phonetization))

        if nb_phones < nb_chars * 0.5:
            print("{:s}\t{:s}\tsmall".format(entry, pron))

        elif nb_phones > nb_chars * 1.8:
            print("{:s}\t{:s}\tlarge".format(entry, pron))

        elif nb_phones > nb_chars * 1.4:
            print("{:s}\t{:s}\tbig".format(entry, pron))
