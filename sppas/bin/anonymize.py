#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.bin.anonymize.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Run the automatic anonymization annotation.

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

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.core.config import lgs
from sppas.core.config import cfg
from sppas.core.coreutils import sppasPythonFeatureError

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.annotations.Anonym import sppasAnonym
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasFiles
from sppas.src.annotations import sppasAnnotationsManager

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    try:
        ann = sppasAnonym(log=None)
    except sppasPythonFeatureError as e:
        print(str(e))
        sys.exit(-1)

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["anonym.json"])
    ann_step_idx = parameters.activate_annotation("anonym")
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
        help="File name for a Procedure Outcome Report (default: None)")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files (manual mode)')
    group_io_manager = parser.add_argument_group('Files (auto mode)')

    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input annotated file name.')

    group_io.add_argument(
        "-v",
        metavar="file",
        help='Input video file name.')

    group_io.add_argument(
        "-w",
        metavar="file",
        help='Input audio file name.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output file name.')

    group_io_manager.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input filename or folder (append).')

    group_io_manager.add_argument(
        "-e",
        metavar=".ext",
        default=parameters.get_output_extension("ANNOT"),
        choices=sppasFiles.get_outformat_extensions("ANNOT_ANNOT"),
        help='Output annotated file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("ANNOT_ANNOT"))))

    group_io_manager.add_argument(
        "-ev",
        metavar=".ext",
        default=parameters.get_output_extension("VIDEO"),
        choices=sppasFiles.get_outformat_extensions("VIDEO"),
        help='Output video file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("VIDEO"))))

    group_io_manager.add_argument(
        "-ew",
        metavar=".ext",
        default=parameters.get_output_extension("AUDIO"),
        choices=sppasFiles.get_outformat_extensions("AUDIO"),
        help='Output video file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("AUDIO"))))

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
        if a not in ('i', 'v', 'w', 'o', 'I', 'e', 'ev', 'ew', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        ann.fix_options(parameters.get_options(ann_step_idx))

        files = [args.i]
        if args.v:
            files.append(args.v)
        if args.w:
            files.append(args.w)

        if args.o:
            ann.run(files, output=args.o)
        else:
            trs, video, audio = ann.run(files)

            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    print("{} {} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        serialize_labels(a.get_labels(), " ")))

    elif args.I:

        # Perform the annotation on a set of files
        # ----------------------------------------

        # Fix input files
        files = list()
        for f in args.I:
            parameters.add_to_workspace(os.path.abspath(f))

        # Fix the output file extension and others
        parameters.set_output_extension(args.e, "ANNOT")
        if cfg.feature_installed("video") is True:
            parameters.set_output_extension(args.ev, "VIDEO")
        parameters.set_output_extension(args.ew, "AUDIO")
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)
