#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017-2024  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# phonemesmapping.py
# ---------------------------------------------------------------------------

import sys
import os
import codecs
from argparse import ArgumentParser
from collections import OrderedDict

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM))))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found.")
    sys.exit(1)
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.wkps import FileName
from sppas.src.wkps import FileRoot
from sppas.src.annotations.Align.models.tiermapping import sppasMappingTier

# ---------------------------------------------------------------------------
# Verify and extract args:
# ---------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -m table" %
                        os.path.basename(PROGRAM),
                        description="... a program to classify phonemes.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name.')

parser.add_argument("-m",
                    metavar="file",
                    required=True,
                    help='Mapping table file name.')

parser.add_argument("-s",
                    metavar="symbol",
                    required=False,
                    default="*",
                    help='Symbol for unknown phonemes (default: *).')

parser.add_argument("-t",
                    metavar="tier",
                    required=False,
                    default="PhonAlign",
                    help="Name of the tier indicating the time-aligned phonemes. (default: PhonAlign)")

parser.add_argument("-o",
                    metavar="file",
                    required=False,
                    help='Output annotated file name.')

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity")

parser.add_argument("--symbols",
                    action='store_true',
                    help="Map the non-speech symbols (silence, pause, laughter...)")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ---------------------------------------------------------------------------
# Load input data

# read file content and get the tier with phonemes
parser = sppasTrsRW(args.i)
trs_input = parser.read()
tier = trs_input.find(args.t, case_sensitive=False)
if tier is None:
    print("ERROR: Tier not found. A tier with name {:s} was required in "
          "file {:s}.".format(args.t, args.i))
    sys.exit(1)

# read the table
if not args.quiet:
    print("Loading...")

mappings = OrderedDict()
with codecs.open(args.m, "r", sg.__encoding__) as fp:
    first_line = fp.readline()
    tier_names = first_line.split(";")
    tier_names.pop(0)

    for name in tier_names:
        mapping = sppasMappingTier()
        mapping.set_reverse(False)       # from PhonAlign to articulatory direction
        mapping.set_keep_miss(False)     # keep unknown entries as given
        mapping.set_miss_symbol(args.s)  # mapping symbol in case of unknown entry
        mapping.set_delimiters([])
        if args.symbols:
            mapping.set_map_symbols(True)
        mappings[name] = mapping

    for line in fp.readlines():
        phones = line.split(";")
        phoneme = phones[0]
        phones.pop(0)
        if not args.quiet:
            if len(phones) != len(mappings):
                print("{:s} (ignored) ".format(phoneme))
            else:
                print("{:s} ".format(phoneme))

        for name, value in zip(tier_names, phones):
            mappings[name].add(phoneme, value)

    fp.close()

if not args.quiet:
    print("\n ... done.")

# ---------------------------------------------------------------------------
# Convert input file

trs = sppasTranscription(name="PhonemesClassification")

if not args.quiet:
    print("Classifying...")
for name in mappings.keys():
    if not args.quiet:
        print(" - {:s}".format(name))
    new_tier = mappings[name].map_tier(tier)
    new_tier.set_name(name)
    trs.append(new_tier)
print(" ... done.")

# ---------------------------------------------------------------------------
# Write converted tiers

if not args.quiet:
    print("Saving...")
if args.o:
    filename = args.o
else:
    pattern = FileRoot.pattern(args.i)
    _, fe = os.path.splitext(args.i)
    filename = FileRoot.root(args.i) + "-pclass" + fe

parser = sppasTrsRW(filename)
parser.write(trs)
print(" ... created file {:s}.\n".format(filename))
