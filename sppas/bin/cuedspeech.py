#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.bin.cuedspeech.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Run the automatic generation of Cued Speech key codes annotation.

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

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import (
    sg, separators, lgs, symbols)
from sppas.core.coreutils import sppasPythonFeatureError
from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.annotations import sppasCuedSpeech
from sppas.src.annotations.CuedSpeech import CuedSpeechKeys
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasFiles
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.wkps import sppasWkpRW

# ---------------------------------------------------------------------------


def is_float(element):
    """Return True if element is or can be a float."""
    #If you expect None to be passed:
    if element is None:
        return False
    # Already a float
    if isinstance(element, float):
        return True
    # Can be converted to float
    try:
        float(element)
        return True
    except ValueError:
        return False

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    try:
        ann = sppasCuedSpeech(log=None)
    except sppasPythonFeatureError as e:
        print(str(e))
        sys.exit(-1)

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["cuedspeech.json"])
    ann_step_idx = parameters.activate_annotation("cuedspeech")
    if ann_step_idx == -1:
        print("This annotation can't be enabled.")
        sys.exit(-1)
    ann_options = parameters.get_options(ann_step_idx)

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description=
        parameters.get_step_name(ann_step_idx) + ": " +
        parameters.get_step_descr(ann_step_idx),
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    parser.add_argument(
        "--log",
        metavar="file",
        help="Filename of the Procedure Outcome Report (default: None)")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files (manual)')

    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input time-aligned phonemes filename.')

    group_io.add_argument(
        "-v",
        metavar="file",
        help='Input video filename.')

    group_io.add_argument(
        "-s",
        metavar="file",
        help='Input sights of the face detection filename.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output filename with Cued Speech key codes.')

    group_wkp = parser.add_argument_group('Files (auto)')

    group_wkp.add_argument(
        "-W",
        metavar="wkp",
        help='Workspace filename')

    group_wkp.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input filename or folder (append).')

    group_wkp.add_argument(
        "-r",
        metavar="rules",
        help='File with Cued Speech keys description')

    group_wkp.add_argument(
        "-l",
        metavar="lang",
        choices=parameters.get_langlist(ann_step_idx),
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(parameters.get_langlist(ann_step_idx))))

    group_wkp.add_argument(
        "-e",
        metavar=".ext",
        default=parameters.get_output_extension("ANNOT"),
        choices=sppasFiles.get_outformat_extensions("ANNOT_ANNOT"),
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("ANNOT_ANNOT"))))

    # Add arguments from the options of the annotation
    # ------------------------------------------------

    group_opt = parser.add_argument_group('Options')

    for opt in ann_options:
        group_opt.add_argument(
            "--" + opt.get_key(),
            type=opt.type_mappings[opt.get_type()],
            default=opt.get_value(),
            help=opt.get_text() + " (default: {:s})"
                                  "".format(opt.get_untypedvalue()))

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Mutual exclusion of inputs
    # --------------------------

    if args.i and args.W:
        parser.print_usage()
        print("{:s}: error: argument -W: not allowed with argument -i"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

    if args.i and args.I:
        parser.print_usage()
        print("{:s}: error: argument -I: not allowed with argument -i"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

    # -----------------------------------------------------------------------
    # The automatic annotation is here:
    # -----------------------------------------------------------------------

    # Redirect all messages to logging
    # --------------------------------

    if args.quiet:
        lgs.set_log_level(30)

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('W', 'i', 'v', 's', 'o', 'r', 'I', 'l', 'e', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        if not args.r:
            print("argparse.py: error: option -r is required with option -i")
            sys.exit(1)

        ann.load_resources(args.r, lang="")
        ann.fix_options(parameters.get_options(ann_step_idx))

        files = [args.i]
        if args.v:
            files.append(args.v)
        if args.s:
            files.append(args.s)

        if args.o:
            ann.run(files, output=args.o)
        else:
            trs = ann.run(files)

            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    print("{} {} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        serialize_labels(a.get_labels(), " ")))


    elif args.W or args.I:

        if not args.l:
            print("argparse.py: error: option -l is required with option -I or -W")
            sys.exit(1)

        # Fix input files
        # ---------------

        if args.W:
            wp = sppasWkpRW(args.W)
            wkp = wp.read()
            parameters.set_workspace(wkp)

        if args.I:
            for f in args.I:
                parameters.add_to_workspace(os.path.abspath(f))

        # Perform the annotation on a set of files
        # ----------------------------------------

        # Fix the output file extension and others
        parameters.set_lang(args.l)
        parameters.set_output_extension(args.e, "ANNOT")
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)

    else:
        stops = list(symbols.phone.keys())
        stops.append('#')
        stops.append('@@')
        stops.append('+')
        stops.append('gb')
        stops.append('lg')

        if not args.r:
            print("argparse.py: error: option -r is required")
            sys.exit(1)

        phonemes = list()
        cs = CuedSpeechKeys(args.r)
        for line in sys.stdin:
            line = line.strip()
            split_line = line.split(" ")
            if len(split_line) == 3 and is_float(split_line[0]) and is_float(split_line[1]):
                # Time-aligned phonemes
                p = split_line[2]
                if p in stops and len(phonemes) > 0:
                    sgmts = cs.syllabify(phonemes)
                    phons = cs.phonetize_syllables(phonemes, sgmts)
                    keys = cs.keys_phonetized(phons)
                    print(keys)
                    phonemes = list()
                else:
                    phonemes.append(p)

            else:
                # In-line phonetization -- Must not contain variants!
                line = line.replace(" ", separators.phonemes)
                phonemes = line.split(separators.phonemes)
                sgmts = cs.syllabify(phonemes)
                phons = cs.phonetize_syllables(phonemes, sgmts)
                keys = cs.keys_phonetized(phons)
                print(keys)
                phonemes = list()

        if len(phonemes) > 0:
            sgmts = cs.syllabify(phonemes)
            phons = cs.phonetize_syllables(phonemes, sgmts)
            keys = cs.keys_phonetized(phons)
            print(keys)
