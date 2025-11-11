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

    scripts.audiopassfilter.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to apply high-pass filter (development version).

"""

import sys
import os.path
from argparse import ArgumentParser
import struct
import math

import audioopy.aio
from audioopy.channel import Channel
from audioopy.audio import AudioPCM

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------
PROGRAM = os.path.abspath(__file__)

parser = ArgumentParser(usage="%s -o output file [options]" % os.path.basename(PROGRAM),
                        description="... a script to apply high-pass filter (development version).")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Audio Input file name')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Audio Output file name')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

audioin = audioopy.aio.open(args.i)
SAMPLE_RATE = audioin.get_framerate()

# ----------------------------------------------------------------------------

# IIR filter coefficients
freq = 2000 # Hz
r = 0.98
a1 = -2.0 * r * math.cos(freq / (SAMPLE_RATE / 2.0) * math.pi)
a2 = r * r
filter = [a1, a2]
print(filter)

n = audioin.get_nframes()
original = struct.unpack('%dh' % n, audioin.read_frames(n))
original = [s / 2.0**15 for s in original]

result = [0 for i in range(0, len(filter))]
biggest = 1
for sample in original:
        for cpos in range(0, len(filter)):
            sample -= result[len(result) - 1 - cpos] * filter[cpos]
        result.append(sample)
        biggest = max(abs(sample), biggest)

result = [sample / biggest for sample in result]
result = [int(sample * (2.0**15 - 1)) for sample in result]

# ----------------------------------------------------------------------------

audioout = AudioPCM()
channel = Channel(framerate=SAMPLE_RATE,
                       sampwidth=audioin.get_sampwidth(),
                       frames=struct.pack('%dh' % len(result), *result))
audioout.append_channel(channel)
audioopy.aio.save(args.o, audioout)
