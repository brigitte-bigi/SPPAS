# -*- coding : UTF-8 -*-
"""
:filename: sppas.bin.sppassetup.py
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
SEP = "-" * 72

# ---------------------------------------------------------------------------


def exit_error(msg="Unknown."):
    """Exit the program with status 1 and an error message.

    :param msg: (str) Message to print on stderr.

    """
    sys.stderr.write("[ ERROR ] {:s}\n".format(msg))
    time.sleep(EXIT_DELAY)
    raise SystemExit(ERROR_EXIT)

# ---------------------------------------------------------------------------


def setup_logging() -> sppasLogFile:
    """Initialize the log file for the installation report.

    :return: (sppasLogFile) The log file instance.

    """
    log_report = sppasLogFile(pattern="install")
    lgs.file_handler(log_report.get_filename())
    return log_report

# ---------------------------------------------------------------------------


def print_banner(quiet: bool):
    """Print the SPPAS banner to stdout.

    :param quiet: (bool) If True, nothing is printed.

    """
    if quiet is True:
        return
    try:
        term = TerminalController()
        print(term.render('${GREEN}{:s}${NORMAL}').format(SEP))
        print(term.render('${RED} {} - Version {}${NORMAL}').format(sg.__name__, sg.__version__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
        print(term.render('${GREEN}{:s}${NORMAL}\n').format(SEP))
    except Exception:
        print('{}\n{} - Version {}\n{}\n{}\n{}\n'.format(
            SEP, sg.__name__, sg.__version__, sg.__copyright__, sg.__url__, SEP))

# ---------------------------------------------------------------------------


def enable_features(installer: sppasInstallerDeps, args_dict: dict):
    """Enable features in the installer according to parsed arguments.

    :param installer: (sppasInstallerDeps) The installer instance.
    :param args_dict: (dict) Parsed arguments as a dictionary.

    """
    if args_dict["all"] is True:
        for fid in installer.features_ids():
            installer.enable(fid, True)
    elif args_dict["default"] is False:
        for fid in installer.features_ids():
            installer.enable(fid, False)
            if args_dict.get(fid) is True and installer.available(fid) is True:
                installer.enable(fid, True)

# ---------------------------------------------------------------------------


def print_summary(quiet: bool, log_report: sppasLogFile, errors: list):
    """Print the installation summary and exit with error if any.

    :param quiet: (bool) If True, nothing is printed.
    :param log_report: (sppasLogFile) The log file instance.
    :param errors: (list) List of error messages.

    """
    msg = "See full installation report in file: {}".format(log_report.get_filename())
    if quiet is False:
        try:
            term = TerminalController()
            print(term.render('\n${GREEN}{:s}${NORMAL}').format(SEP))
            print(term.render('${GREEN}Thank you for using {}.').format(sg.__name__))
            print(term.render('${GREEN}{:s}${NORMAL}').format(SEP))
        except Exception:
            print('\n{}\n{}\n{}\n'.format(SEP, msg, SEP))
    if len(errors) > 0:
        exit_error(msg + "\n".join(errors))

# ---------------------------------------------------------------------------


def get_args_from_cmd(installer: sppasInstallerDeps):
    """Get args from the command-line interface with ArgumentParser.

    :param installer: (sppasInstallerDeps) The installer instance.
    :return: (Namespace) Parsed arguments.

    """
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

    group_g = parser.add_argument_group("Overall selections")
    group_ge = group_g.add_mutually_exclusive_group()

    group_ge.add_argument(
        "-a", "--all",
        action='store_true',
        help="Install all the available features for this os.")

    group_ge.add_argument(
        "-d", "--default",
        action='store_true',
        help="Install all the features that are enabled by default.")

    group_p = parser.add_argument_group("Programs selection:")
    for fid in installer.features_ids("deps"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable 'deps' feature '{name}': '{desc}'".format(
                name=fid, desc=installer.description(fid)))

    group_p = parser.add_argument_group("Languages selection:")
    for fid in installer.features_ids("lang"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable 'lang' feature '{name}': '{desc}'".format(
                name=fid, desc=installer.description(fid)))

    group_p = parser.add_argument_group("Annotation data selection:")
    for fid in installer.features_ids("annot"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable 'annot' feature '{name}': '{desc}'".format(
                name=fid, desc=installer.description(fid)))

    group_p = parser.add_argument_group("Spin-offs selection:")
    for fid in installer.features_ids("spin"):
        group_p.add_argument(
            "--" + fid,
            action='store_true',
            help="Enable 'spin' feature '{name}': '{desc}'".format(
                name=fid, desc=installer.description(fid)))

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    return parser.parse_args()

# ---------------------------------------------------------------------------


def sppassetup():
    """Perform SPPAS setup to install external dependencies.

    """
    installer = sppasInstallerDeps()
    args = get_args_from_cmd(installer)
    args_dict = vars(args)

    if args.quiet is True and all(v is False for k, v in args_dict.items() if k != "quiet"):
        exit_error("{:s}: argument --quiet: not allowed alone.".format(os.path.basename(PROGRAM)))

    log_report = setup_logging()

    if args.quiet is False:
        p = ProcessProgressTerminal()
        installer.set_progress(p)

    print_banner(args.quiet)
    enable_features(installer, args_dict)
    errors = installer.install()

    if args.quiet is False:
        p.close()

    print_summary(args.quiet, log_report, errors)
    cfg.save()

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    sppassetup() 
    sys.exit(0)
