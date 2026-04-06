#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.bin.facedetection.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Run the automatic detection(s) of faces in an image or a video..

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

import logging
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import lgs
from sppas.src.annotations import sppasFaceDetection
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasFiles
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.wkps import sppasWkpRW

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["facedetect.json"])
    ann_step_idx = parameters.activate_annotation("facedetect")
    if ann_step_idx == -1:
        print("The automatic annotation can't be enabled.")
        sys.exit(1)
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
        help='Input image filename.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output base name.')

    group_io.add_argument(
        "-r",
        metavar="model",
        action='append',
        help='Model base name (as many .pb or .caffemodel or .xml models as wishes)')

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
        "-e",
        metavar=".ext",
        default=parameters.get_output_extension("IMAGE"),
        choices=sppasFiles.get_outformat_extensions("IMAGE"),
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("IMAGE"))))

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
        raise SystemExit(1)

    if args.i and not args.r:
        print("argparse.py: error: option -r is required with option -i")
        raise SystemExit(1)

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
        if a not in ('W', 'i', 'o', 'r', 'e', 'I', 'quiet', 'log'):
            if args.i and a.startswith("model:"):
                # Manual mode. Disable all models.
                parameters.set_option_value(ann_step_idx, a, False)
            else:
                parameters.set_option_value(ann_step_idx, a, arguments[a])

    if args.i:
        # Manual mode. Input filename, output basename and model are user-defined.
        ann = sppasFaceDetection(log=None)

        # Perform the annotation on a single file
        # ---------------------------------------
        ann.load_resources(model1=args.r[0], *args.r[1:])
        ann.fix_options(parameters.get_options(ann_step_idx))
        for name in ann.get_recognizer_names():
            ann.set_enable_model(name, True)

        # All instantiated detectors are enabled by default.
        logging.debug("Number of enabled recognizers: {:d} / {:d}"
                      "".format(ann.get_nb_enabled_recognizers(), ann.get_nb_recognizers()))
        logging.debug("   {}".format(ann.get_enabled_recognizer_names()))

        if args.o:
            ann.run([args.i], output=args.o)
        else:
            coords = ann.run([args.i])
            for c in coords:
                print(c)

    elif args.I or args.W:

        # Fix input files
        if args.W:
            wp = sppasWkpRW(args.W)
            wkp = wp.read()
            parameters.set_workspace(wkp)
        if args.I:
            for f in args.I:
                parameters.add_to_workspace(os.path.abspath(f))
                logging.info("File {:s} added to the workspace.".format(f))

        process = sppasAnnotationsManager()

        # Fix the output file extension and others
        parameters.set_report_filename(args.log)
        parameters.set_output_extension(args.e, "IMAGE")

        # Perform the annotation
        process.annotate(parameters)
