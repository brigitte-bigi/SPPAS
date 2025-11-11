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

    scripts.tieraligntophon.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi, CNRS
:summary:      a script to a time-aligned phonemes tier to its
phonetization tier.

"""

import sys
import os.path
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import lgs
from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata.aio.aioutils import unalign
from sppas.src.annotations import sppasFindTier

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------


parser = ArgumentParser(usage="{:s} -i file -o file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to convert time-aligned "
                                    "phonemes into their phonetization.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output file name')

parser.add_argument("--tok",
                    action='store_true',
                    help="Convert time-aligned tokens into their tokenization.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# Redirect all messages to logging
# --------------------------------

if args.quiet:
    lgs.set_log_level(30)


# ----------------------------------------------------------------------------
# Read

logging.info("Read input: {:s}".format(args.i))
parser = sppasTrsRW(args.i)
trs_input = parser.read()

trs_out = sppasTranscription()

# ----------------------------------------------------------------------------
# Transform the PhonAlign tier to a Phonetization tier

try:
    align_tier = sppasFindTier.aligned_phones(trs_input)
    logging.info("PhonAlign tier found.")
    phon_tier = unalign(align_tier)
    phon_tier.set_name("Phones")
    trs_out.append(phon_tier)
except IOError:
    logging.error("PhonAlign tier not found.")

# ----------------------------------------------------------------------------
# Transform the TokensAlign tier to a Tokenization tier

if args.tok:
    try:
        align_tier = sppasFindTier.aligned_tokens(trs_input)
        logging.info("TokensAlign tier found.")
        token_tier = unalign(align_tier)
        token_tier.set_name("Tokens")
        trs_out.append(token_tier)
    except IOError:
        logging.error("TokensAlign tier not found.")

# ----------------------------------------------------------------------------
# Write

if len(trs_out) > 0:
    logging.info("Write output: {:s}".format(args.o))
    parser.set_filename(args.o)
    parser.write(trs_out)
else:
    logging.info("No tier converted.")
    sys.exit(1)
