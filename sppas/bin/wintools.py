"""
:filename: sppas.bin.wintools.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Download and install executables for Windows.

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
if sys.version_info < (3, 9):
    print("The version of Python is too old: "
          "This program requires at least version 3.9.")
    sys.exit(1)
if sys.platform != "win32":
    print(f"This program is dedicated to 'win32' platforms but your is {sys.platform}.")
    sys.exit(1)

import os
import urllib.request as urlreq
import zipfile

PROGRAM = os.path.abspath(__file__)
HERE = os.path.dirname(PROGRAM)
DOWNLOAD = "https://sourceforge.net/projects/sppas/files/wintools.zip/download"

julius_exe = os.path.join(HERE, "julius.exe")
ffmpeg_exe = os.path.join(HERE, "ffmpeg.exe")
praat_exe = os.path.join(HERE, "Praat.exe")
if all(os.path.isfile(p) for p in (julius_exe, ffmpeg_exe, praat_exe)):
    print("All tools for windows are already installed. Nothing to do.")
    sys.stderr.write("All tools for windows are already installed. Nothing to do.")
    sys.exit(0)

# Download the zip file with executable files
# -------------------------------------------------

print(f"Start to download file: {DOWNLOAD}")
zip_path = os.path.join(HERE, "wintools.zip")
urlreq.urlretrieve(DOWNLOAD, zip_path)
if os.path.exists(zip_path) is False:
    print("WinTools zip package can't be downloaded.")
    sys.stderr.write("WinTools zip package can't be downloaded.")
    raise SystemExit(-1)
print(f"Download completed: {zip_path}")

# Extract the executable file
# -------------------------------------------------

with zipfile.ZipFile(zip_path, 'r') as zf:
    zf.extractall(HERE)

if os.path.exists(julius_exe) is False:
    sys.stderr.write("Julius executable not found in zip.")
    raise SystemExit(-1)
if os.path.exists(ffmpeg_exe) is False:
    sys.stderr.write("ffmpeg executable not found in zip.")
    raise SystemExit(-1)
if os.path.exists(praat_exe) is False:
    sys.stderr.write("Praat executable not found in zip.")
    raise SystemExit(-1)

# No need of the zip file anymore
# -------------------------------------------------

os.remove(zip_path)
sys.exit(0)
