# -*- coding : UTF-8 -*-
"""
:filename: sppas.bin.preinstall.py
:author: Brigitte Bigi
:contributor: Florian Hocquet
:contact: contact@sppas.org
:summary: Launch the installation of external features.

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

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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
import time
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.core.config import cfg
from sppas.core.config import lgs
from sppas.core.coreutils import sppasLogFile
from sppas.core.preinstall import sppasInstallerDeps

from sppas.ui.term.textprogress import ProcessProgressTerminal
from sppas.ui.term.terminalcontroller import TerminalController

# ---------------------------------------------------------------------------

EXIT_DELAY = 2
ERROR_EXIT = 1

# ---------------------------------------------------------------------------


def exit_error(msg="Unknown."):
    """Exit the program with status 1 and an error message.

    :param msg: (str) Message to print on stdout.

    """
    sys.stderr.write("[ ERROR ] {:s}\n".format(msg))
    time.sleep(EXIT_DELAY)
    raise SystemExit(ERROR_EXIT)


# ---------------------------------------------------------------------------


if __name__ == "__main__":

    log_report = sppasLogFile(pattern="install")
    lgs.file_handler(log_report.get_filename())

    # -----------------------------------------------------------------------
    # Fix initial sppasInstallerDeps parameters
    # -----------------------------------------------------------------------
    installer = sppasInstallerDeps()

    # ----------------------------------------------------------------------------
    # Verify and extract args:
    # ----------------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [action]",
        description="User command interface to enable SPPAS features.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__),
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    # Add arguments from the features of features.ini
    # -----------------------------------------------

    group_g = parser.add_argument_group("Overall selections")
    group_ge = group_g.add_mutually_exclusive_group()

    group_ge.add_argument(
        "-a",
        "--all",
        action='store_true',
        help="Install all the available features for this os.")

    group_ge.add_argument(
        "-d",
        "--default",
        action='store_true',
        help="Install all the features that are enabled by default.")

    group_p = parser.add_argument_group("Programs selection:")
    for fid in installer.features_ids("deps"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

    group_p = parser.add_argument_group("Languages selection:")
    for fid in installer.features_ids("lang"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

    group_p = parser.add_argument_group("Annotation data selection:")
    for fid in installer.features_ids("annot"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

    group_p = parser.add_argument_group("Spin-offs selection:")
    for fid in installer.features_ids("spin"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable feature '{name}': '{desc}'".format(
                name=fid,
                desc=installer.description(fid)))

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()
    if args.quiet and len(args) == 1:
        parser.print_usage()
        exit_error("{:s}: error: argument --quiet: not allowed alone."
                   "".format(os.path.basename(PROGRAM)))
    p = None
    if not args.quiet:
        p = ProcessProgressTerminal()
        installer.set_progress(p)

    # Fix user communication way
    # -------------------------------

    sep = "-" * 72
    if not args.quiet:
        try:
            term = TerminalController()
            print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
            print(term.render('${RED} {} - Version {}${NORMAL}'
                              '').format(sg.__name__, sg.__version__))
            print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
            print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
            print(term.render('${GREEN}{:s}${NORMAL}\n').format(sep))

        except:
            print('{:s}\n'.format(sep))
            print('{}   -  Version {}'.format(sg.__name__, sg.__version__))
            print(sg.__copyright__)
            print(sg.__url__ + '\n')
            print('{:s}\n'.format(sep))

    # convert the Namespace into a dictionary
    args_dict = vars(args)
    if args_dict["all"] is True:
        # enable all available features
        for fid in installer.features_ids():
            installer.enable(fid, True)

    elif args_dict["default"] is False:
        # Set the values to enable individually each feature
        for fid in installer.features_ids():
            installer.enable(fid, False)
            if args_dict[fid] is True:
                if installer.available(fid) is True:
                    installer.enable(fid, True)

    # process the installation
    errors = installer.install()

    msg = "See full installation report in file: {}".format(log_report.get_filename())

    if not args.quiet:
        p.close()
        try:
            term = TerminalController()
            print(term.render('\n${GREEN}{:s}${NORMAL}').format(sep))
            print(term.render('${RED}See {}.').format("..."))
            print(term.render('${GREEN}Thank you for using {}.').format(sg.__name__))
            print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        except:
            print('\n{:s}\n'.format(sep))
            print(msg)
            print('{:s}\n'.format(sep))

    if len(errors) > 0:
        msg += "\n".join(errors)
        exit_error(msg)

cfg.save()
sys.exit(0)
