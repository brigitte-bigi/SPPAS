#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.bin.plugin.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Main script to work with SPPAS plugins.

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

Examples:

Install a plugin:
>>> ./sppas/bin/plugin.py --install -p sppas/src/plugins/tests/data/soxplugin.zip

Use a plugin on a file:
>>> ./sppas/bin/plugin.py --apply -p soxplugin -i samples/samples-eng/oriana1.wav -o resampled.wav

Remove a plugin:
>>> ./sppas/bin/plugin.py --remove -p soxplugin

An "all-in-one" solution:
>>> ./sppas/bin/plugin.py --install --apply --remove -p sppas/src/plugins/tests/data/soxplugin.zip -i samples/samples-eng/oriana1.wav -o resampled.wav

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.ui.term import TerminalController
from sppas.src.plugins import sppasPluginsManager
from sppas.src.structs import sppasOption

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [actions] [files]",
        description="Plugin command line interface.",
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    # Add arguments for actions
    # -------------------------

    group_act = parser.add_argument_group('Actions')

    group_act.add_argument(
        "--install",
        action='store_true',
        help="Install a new plugin from a plugin package.")

    group_act.add_argument(
        "--remove",
        action='store_true',
        help="Remove an existing plugin.")

    group_act.add_argument(
        "--apply",
        action='store_true',
        help="Apply a plugin on a file.")

    group_act.add_argument(
        "--list",
        action='store_true',
        help="Display the list of plugins. ")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-p",
        metavar="string",
        required=False,
        help="Plugin (either an identifier, or an archive file).")

    group_io.add_argument(
        "-i",
        metavar="string",
        required=False,
        help="Input file to apply a plugin on it.")

    group_io.add_argument(
        "-o",
        metavar="string",
        required=False,
        help="Output file, ie the result of the plugin.")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Plugins is here:
    # -----------------------------------------------------------------------
    sep = "-"*72

    try:
        term = TerminalController()
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
        print(term.render('${RED} {} - Version {}${NORMAL}'
                          '').format(sg.__name__, sg.__version__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__copyright__))
        print(term.render('${BLUE} {} ${NORMAL}').format(sg.__url__))
        print(term.render('${GREEN}{:s}${NORMAL}').format(sep))
    except:
        print('{:s}\n'.format(sep))
        print('{:s}   -  Version {}'.format(sg.__name__, sg.__version__))
        print(sg.__copyright__)
        print(sg.__url__+'\n')
        print('{:s}\n'.format(sep))

    manager = sppasPluginsManager()
    if args.list:
        print("List of plugins: ")
        for plugin_id in manager.get_plugin_ids():
            print("  - identifier: {:s}".format(plugin_id))
            params = manager.get_plugin(plugin_id)
            print("    {:s}".format(params.get_name()))
            print("    {:s}".format(params.get_descr()))
            if not args.p:
                sys.exit(0)

    plugin_id = args.p

    if args.install:

        print("Plugin installation")

        # fix a name for the plugin directory
        plugin_folder = os.path.splitext(os.path.basename(args.p))[0]
        plugin_folder.replace(' ', "_")

        # install the plugin.
        plugin_id = manager.install(args.p, plugin_folder)

    if args.apply:
        if args.i:
            # Get the plugin
            p = manager.get_plugin(plugin_id)

            # Set the output file name (if any)
            if args.o:
                options = p.get_options()
                is_changed = False
                for opt in options:
                    if opt.get_key() == "-o":
                        opt.set_value(args.o)
                        is_changed = True
                if is_changed is False:
                    opt = sppasOption("-o", "str", args.o)
                    options.append(opt)
                p.set_options(options)

            # Run
            message = manager.run_plugin(plugin_id, [args.i])
            print(message)

        else:
            print("Error: argument -i is required with argument --apply")
            sys.exit(1)

    if args.remove:
        manager.delete(plugin_id)

    print('{:s}\n'.format(sep))
