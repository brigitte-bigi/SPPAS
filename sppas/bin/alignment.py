#!/usr/bin/env python
"""
:filename: sppas.bin.alignment.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Run the alignment automatic annotation

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.core.config import lgs
from sppas.core.coreutils import u

from sppas.src.annotations import sppasAlign
from sppas.src.annotations import sppasParam
from sppas.src.annotations import sppasFiles
from sppas.src.annotations import sppasAnnotationsManager
from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.annotations.Align.aligners import BasicAligner
from sppas.src.wkps import sppasWkpRW

# ---------------------------------------------------------------------------


def get_args_from_cmd(parameters, ann_step_idx):
    """Get args from the command-line interface with ArgumentParser.

    The arguments of the options of the annotation are added to the ones of
    the files, so the parser requires the annotation parameters.

    :param parameters: (sppasParam) Parameters of the annotations
    :param ann_step_idx: (int) Index of the activated annotation
    :return: (Namespace) The parsed arguments

    """
    ann_options = parameters.get_options(ann_step_idx)
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
        help='Input wav file name.')

    group_io.add_argument(
        "-p",
        metavar="file",
        help='Input filename with the phonetization.')

    group_io.add_argument(
        "-t",
        metavar="file",
        help='Input filename with the tokenization.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output filename with estimated alignments.')

    group_io.add_argument(
        "-r",
        metavar="model",
        help='Directory of the acoustic model of the language of the text')

    group_io.add_argument(
        "-R",
        metavar="model",
        help='Directory of the acoustic model of the mother language of the speaker')

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
            help=u(opt.get_text()) + " (default: {:s})"
                                  "".format(opt.get_untypedvalue()))

    # ------------------------------------------------------
    args = parser.parse_args()

    # Mutual exclusion of inputs
    # --------------------------

    if args.i and args.W:
        parser.error("argument -W: not allowed with argument -i")

    if args.i and args.I:
        parser.error("argument -I: not allowed with argument -i")

    if args.R and not args.r:
        parser.error("argument -R: not allowed without argument -r")


    # Required combinations of inputs
    # -------------------------------

    if (args.I or args.W) and not args.l:
        parser.error("option -l is required with option -I")
    if not (args.I or args.W) and (args.i or args.p) and not args.p:
        parser.error("option -p is required with option -i")

    return args

# ---------------------------------------------------------------------------


def alignment():

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["alignment.json"])
    ann_step_idx = parameters.activate_annotation("alignment")

    args = get_args_from_cmd(parameters, ann_step_idx)

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
        if a not in ('W', 'i', 'o', 'p', 't', 'r', 'R', 'I', 'l', 'e', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.I or args.W:

        # Fix input files
        # ---------------

        if args.W:
            wp = sppasWkpRW(args.W)
            wkp = wp.read()
            parameters.set_workspace(wkp)

        if args.I:
            for f in args.I:
                parameters.add_to_workspace(os.path.abspath(f))
                logging.info("File {:s} added to the workspace.".format(f))

        # Perform the annotation on a set of files
        # ----------------------------------------

        # Fix the output file extension and others
        parameters.set_lang(args.l)
        parameters.set_output_extension(args.e, "ANNOT")
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)

    elif args.i or args.p:

        # Perform the annotation on a single file
        # ---------------------------------------

        ann = sppasAlign(log=None)
        if args.r:
            ann.load_resources(args.r, args.R)
        ann.fix_options(parameters.get_options(ann_step_idx))
        ann.print_options()

        if args.o:
            ann.run([args.p, args.i, args.t], args.o)
        else:
            trs = ann.run([args.p, args.i, args.t])
            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    print("{} {} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        serialize_labels(a.get_labels(), " ")))

    else:
        aligner = BasicAligner()
        here = 0.
        for line in sys.stdin:
            aligner.set_phones(line)
            if len(line) > 0:
                # Get selected pronunciation and pseudo time-alignment values
                aligned = aligner.run_basic()
                for (begin, end, phone) in aligned:
                    b = here + float(begin)
                    e = here + float(end)
                    print("{} {} {:s}".format(b, e, phone))
                here = here + (0.01 * aligned[-1][1])

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    alignment()
