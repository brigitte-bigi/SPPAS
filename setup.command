#!/bin/bash
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
# Filename: setup.command
# Author:   Brigitte Bigi
# Contact:  contact@sppas.org
# Summary:  Launch the Setup application of SPPAS for MacOS/Linux.
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
#                   Copyright (C) 2011-2025  Brigitte Bigi, CNRS
#            Laboratoire Parole et Langage, Aix-en-Provence, France
# ---------------------------------------------------------------------------
#                   This banner notice must not be removed
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
# Fix global variables
# ===========================================================================

# Exit status:
STATUS_SUCCESS=0
STATUS_NOPYTHON=1
STATUS_NOPYENV=2
STATUS_FAILED=3

# Program info
PROGRAM_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
export SPPAS=$PROGRAM_DIR

# Python virtual environment path
PYENV="$PROGRAM_DIR/.sppaspyenv~"
export PYTHONIOENCODING=UTF-8

# Python info we'll try to find
PYTHON=""
v="0"

# Colors
BLACK='\e[0;30m'
WHITE='\e[1;37m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
BLUE='\e[0;34m'
DARK_BLUE='\e[1;34m'
GREEN='\e[0;32m'
LIGHT_GREEN='\e[1;32m'
CYAN='\e[0;36m'
LIGHT_CYAN='\e[1;36m'
RED='\e[0;31m'
LIGHT_RED='\e[1;31m'
PURPLE='\e[0;35m'
LIGHT_PURPLE='\e[1;35m'
BROWN='\e[0;33m'
YELLOW='\e[1;33m'
NC='\e[0m' # No Color


# ===========================================================================
# FUNCTIONS
# ===========================================================================

# Test if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}


# Print an error message with a GUI or on stdout if no GUI found
# Parameters:
#   $1: message to print
function fct_error_message()
{
  TITLE_MSG="Cannot start SPPAS Setup"
  if [ -n "$(command -v zenity)" ]; then
      zenity --error --title="$TITLE_MSG" --text="$1" --no-wrap
  elif [ -n "$(command -v kdialog)" ]; then
      kdialog --error "$1" --title "$TITLE_MSG"
  elif [ -n "$(command -v notify-send)" ]; then
      notify-send "ERROR: $TITLE_MSG" "$1"
  elif [ -n "$(command -v xmessage)" ]; then
      xmessage -center "ERROR: $TITLE_MSG: $1"
  else
      printf "ERROR: %s\n%s\n" "$TITLE_MSG" "$1"
  fi
}


# ===========================================================================
# CREATE OR CHECK THE PYTHON VIRTUAL ENVIRONMENT FOR SPPAS
# ===========================================================================

# Get the name of the system
unamestr=`uname | cut -f1 -d'_'`;

if [ -e $PYENV ]; then

    # The virtual environment directory is existing. We expect the python
    # command to be available at the right place!
    echo "Python virtual environment for SPPAS already exists.";
    PYTHON="$PYENV/bin/python";

else

    echo "A python virtual environment for SPPAS will be created."

    # At first, a python -- version 3 -- has to be found.
    # ------------------------

    echo -n "Search for 'python3' command: ";
    for cmd in `which -a python3`;
    do
        v=$($cmd -c "import sys; print(sys.version_info[0])");
        if [[ "$v" == "3" ]]; then
            PYTHON=$cmd;
            break;
        fi;
    done;

    if command_exists "$PYTHON"; then
        echo " ... found.";
    else
        echo "... not found.";
        echo -n "Search for 'python' command: ";
        for cmd in `which -a python`;
        do
            v=$($cmd -c "import sys; print(sys.version_info[0])");
            if [[ "$v" == "3" ]]; then
                PYTHON=$cmd;
                break;
            fi;
        done;
    fi;

    if command_exists "$PYTHON"; then
        echo " ... a valid python command was found.";
    else
        fct_error_message " ... no valid python command found.";
        exit $STATUS_NOPYTHON;
    fi;

    # Then, a python venv is created, and other stuff.
    # ------------------------

    echo "Both 'pip' and 'virtualenv' packages must be updated:";
    $PYTHON -m pip install --upgrade pip --break-system-packages;
    $PYTHON -m pip install --upgrade virtualenv --break-system-packages;

    echo "Please wait while Python virtual environment is being created";
    if [[ "$unamestr" == "Darwin" ]]; then
        $PYTHON -m venv $PYENV;
    else
        $PYTHON -m venv $PYENV --copies;
    fi;
    echo "... done";

    # Finally, redirect PYTHON variable to the python venv version.
    # ------------------------

    PYTHON="$PYENV/bin/python";

fi;


# DO MORE TESTS... (useful particularly for MacOS)
# ===========================================================================

if [ -e $PYENV ]; then
    if [ -e $PYTHON ]; then
        echo;
    else
        fct_error_message "Python command does not exists in virtual environment for SPPAS.";
        exit $STATUS_NOPYTHON;
    fi
else
    fct_error_message "Python virtual environment for SPPAS not found.";
    exit $STATUS_NOPYENV;
fi;


# PYTHON 3 VIRTUAL ENVIRONMENT for SPPAS IS OK. CAN START INSTALLATION SETUP.
# ===========================================================================

echo "This setup configuration: ";
echo "  - Python virtual environment: $PYENV";
echo "  - Command: $PYTHON";
echo "  - System: $unamestr";
echo "  - Display: $DISPLAY";
echo "  - Location: $PROGRAM_DIR";

echo "Required dependencies installation: "
$PYTHON -m pip install whakerpy==1.4 || $PYTHON -m pip install /sppas/dist/whakerpy-1.4-py3-none-any.whl
$PYTHON -m pip install WhakerKit==1.3 || $PYTHON -m pip install /sppas/dist/whakerkit-1.3-py3-none-any.whl
$PYTHON -m pip install AudiooPy==0.5 || $PYTHON -m pip install /sppas/dist/AudiooPy-0.5-py3-none-any.whl

# Check output status
if [ $? -ne 0 ] ; then
    fct_error_message "This setup failed to install automatically the required core feature. See https://sppas.org/installation.html to do it manually."
    exit $STATUS_FAILED
fi

# Execute the SPPAS Web-based Setup application - for SPPAS >= 4.10
echo "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *";
echo "* * *   Closing this windows will kill the application  * * *";
echo "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *";
cd $PROGRAM_DIR
$PYTHON ./sppas/ui/swapp --Setup

# Check output status
if [ $? -ne 0 ] ; then
    fct_error_message "This setup failed to install automatically some of the optional external packages. See https://sppas.org/installation.html to do it manually."
    exit $STATUS_FAILED
fi

exit $STATUS_SUCCESS
