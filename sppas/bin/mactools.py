"""
:filename: sppas.bin.mactools.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Download Homebrew and install executables for macOS.

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

import os
import shutil
import subprocess
import sys

if sys.version_info < (3, 9):
    print("The version of Python is too old: "
          "This program requires at least version 3.9.")
    sys.exit(1)
if sys.platform != "darwin":
    print(f"This program is dedicated to darwin platforms but your is {sys.platform}.")
    sys.exit(1)

# ---------------------------------------------------------------------------


BREW_INSTALL_CMD = (
    'NONINTERACTIVE=1 /bin/bash -c '
    '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
)

BREW_CANDIDATES = (
    "/opt/homebrew/bin/brew",
    "/usr/local/bin/brew",
)

# ---------------------------------------------------------------------------


def _run(command, env=None):
    """Run a shell command and stop on error."""
    print("Run: {}".format(command))
    result = subprocess.run(
        command,
        shell=True,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return result

# ---------------------------------------------------------------------------

def _get_brew_path():
    """Return the absolute path of brew, or None."""
    for candidate in BREW_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("brew")

# ---------------------------------------------------------------------------

def _make_env(brew_path):
    """Return an environment with brew in PATH."""
    env = os.environ.copy()
    brew_dir = os.path.dirname(brew_path)
    current_path = env.get("PATH", "")
    if brew_dir not in current_path.split(os.pathsep):
        env["PATH"] = brew_dir + os.pathsep + current_path if current_path else brew_dir
    return env

# ---------------------------------------------------------------------------

def _is_formula_installed(brew_path, env, formula):
    """Return True if a Homebrew formula is already installed."""
    result = subprocess.run(
        [brew_path, "list", "--formula", formula],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

brew_path = _get_brew_path()
if brew_path is None:
    print("Homebrew is not installed. Start installation.")
    _run(BREW_INSTALL_CMD)
    brew_path = _get_brew_path()

if brew_path is None:
    sys.stderr.write("Homebrew executable was not found after installation.")
    sys.exit(1)

env = _make_env(brew_path)

for formula in ('julius', 'ffmpeg', 'praat'):
    if _is_formula_installed(brew_path, env, formula):
        print("{} is already installed.".format(formula))
    else:
        if formula == 'praat':
            _run('"{}" install --cask praat'.format(brew_path), env=env)
        else:
            _run('"{}" install {}'.format(brew_path, formula), env=env)

for formula in ('julius', 'ffmpeg', 'praat'):
    if _is_formula_installed(brew_path, env, formula) is False:
        sys.stderr.write("{} installation failed.".format(formula))
        sys.exit(1)

sys.exit(0)
