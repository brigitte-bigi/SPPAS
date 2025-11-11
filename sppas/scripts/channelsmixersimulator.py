#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
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

    scripts.channelsmixersimulator.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to get the maximum value of a mix between mono audio files.

"""

from argparse import ArgumentParser
import os
import sys

import audioopy.aio
from audioopy import ChannelMixer

# ----------------------------------------------------------------------------
PROGRAM = os.path.abspath(__file__)

parser = ArgumentParser(usage="%s -w input files" % os.path.basename(PROGRAM),
                        description="... a script to get the minimum and maximum values"
                                    " of a mix between mono audio files.")

parser.add_argument("-w",
                    metavar="file",
                    nargs='+',
                    required=True,
                    help='Audio Input file names')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

mixer = ChannelMixer()

for inputFile in args.w:
    audio = audioopy.aio.open(inputFile)
    idx = audio.extract_channel(0)
    mixer.append_channel(audio.get_channel(idx))

print(mixer.get_minmax())
