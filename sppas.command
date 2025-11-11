#!/bin/bash
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Filename: sppas.command
# Author:   Brigitte Bigi
# Contact:  contact@sppas.org
# Summary:  Launch the GUI of SPPAS for MacOS/Linux.
# ---------------------------------------------------------------------------
#            ######   ########   ########      ###      ######
#           ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
#           ##        ##     ##  ##     ##   ##   ##   ##            annotation
#            ######   ########   ########   ##     ##   ######        and
#                 ##  ##         ##         #########        ##        analysis
#           ##    ##  ##         ##         ##     ##  ##    ##         of speech
#            ######   ##         ##         ##     ##   ######
#
#           https://sppas.org/
#
# ---------------------------------------------------------------------------
#                   Copyright (C) 2011-2023  Brigitte Bigi, CNRS
#            Laboratoire Parole et Langage, Aix-en-Provence, France
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with SPPAS. If not, see <https://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------


# ===========================================================================
# Fix global & environment variables
# ===========================================================================

PROGRAM_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
export PYTHONIOENCODING=UTF-8
export SPPAS=$PROGRAM_DIR

# Python virtual environment path
PYENV="$PROGRAM_DIR/.sppaspyenv~"
PYTHON="$PYENV/bin/python"


# ===========================================================================
# FUNCTIONS
# ===========================================================================

command_exists () {
    type "$1" &> /dev/null ;
}


# ===========================================================================
# MAIN
# ===========================================================================
cd $SPPAS

# Write useful information
unamestr=`uname | cut -f1 -d'_'`;
echo "This program starts with: ";
echo "  - System:  $unamestr";
echo "  - Display:  $DISPLAY";
echo "  - Location: $PROGRAM_DIR";
echo "  - Command: $PYTHON";

if command_exists "$PYTHON"; then
    echo -e "  - Python: version ";
    "$PYTHON" --version;

    # Get the name of the system
    if [ "$unamestr" == "CYGWIN" ]; then
        if [ -z $DISPLAY ]; then
           echo "[ ERROR ] Unable to access the X Display.";
           echo "Did you enabled XWin server?";
           exit 1;
        fi
    fi

    echo "SPPAS Graphical User Interface...";
    $PYTHON -m sppas;
    exit $?;

else
    echo "[ ERROR ] Python virtual environment for SPPAS does not exist.";
    echo "          ... did you forget to read the installation instructions?";
    exit 1;
fi
