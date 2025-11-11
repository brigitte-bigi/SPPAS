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

    scripts.saplay.py
    ~~~~~~~~~~~~~~~~~~~~

    ... a script to play an audio file.

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import audioopy.aio
try:
    import pyaudio
    PLAYER = 1
except ImportError:
    try:
        import simpleaudio
        PLAYER = 2
    except ImportError:
        PLAYER = 0

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM),
                        description="... SPPAS audio file player.")

parser.add_argument("-w",
                    metavar="file",
                    required=True,
                    help='Input audio file name')

parser.add_argument("-bs",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position in seconds when playing starts.')

parser.add_argument("-es",
                    default=0,
                    metavar="value",
                    type=float,
                    help='The position in seconds when playing stops.')

parser.add_argument("-bf",
                    default=0,
                    metavar="value",
                    type=int,
                    help='The number of frames when playing starts.')

parser.add_argument("-ef",
                    default=0,
                    metavar="value",
                    type=int,
                    help='The number of frames when playing stops.')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if args.bf and args.bs:
    print("bf option and bs option can't both be used at the same time!")
    sys.exit(1)

if args.ef and args.es:
    print("ef option and es option can't both be used at the same time!")
    sys.exit(1)

if PLAYER == 0:
    print("None of the supported audio player backend libraries is installed.")
    sys.exit(1)
print("Player:            {:d} (1=PyAudio, 2=SimpleAudio)".format(PLAYER))

# ----------------------------------------------------------------------------
# Open the sound file and prepare playing infos...
# ----------------------------------------------------------------------------

audio = audioopy.aio.open(args.w)
print("Audio file name:     {:s}".format(args.w))
print("Duration (seconds):  {:f}".format(audio.get_duration()))
fps = audio.get_framerate()
print("Frame rate (Hz):     {:d}".format(fps))
sp = audio.get_sampwidth()
print("Sample width (bits): {:d}".format(sp*8))
nc = audio.get_nchannels()
print("Number of channels:  {:d}".format(nc))

if args.bf:
    begin = args.bf
elif args.bs:
    begin = int(args.bs * audio.get_framerate())
else:
    begin = 0

if args.ef:
    end = args.ef
elif args.es:
    end = int(args.es * audio.get_framerate())
else:
    end = audio.get_nframes()

if end <= begin:
    print("Must start playing before ending!")
    audio.close()
    sys.exit(1)
print("Start playing at:  {:d}".format(begin))
print("Stop playing at:   {:d}".format(end))

# Load all frames. Any computer today can store audio frames in RAM!
audio.seek(begin)
frames = audio.read_frames(end-begin)
audio.close()

# ----------------------------------------------------------------------------
# Create an interface to PortAudio or SimpleAudio, play and close
# ----------------------------------------------------------------------------

if PLAYER == 1:
    # Create a PyAudio instance.
    p = pyaudio.PyAudio()

    # Open a Stream object to write the frames of the audio to.
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(format=p.get_format_from_width(sp), channels=nc, rate=fps, output=True)

    # Play the sound by writing the audio data to the stream
    chunk = fps // 10  # a chunk every 100 ms.
    i = 0
    while i < len(frames):
        stream.write(frames[i:i+chunk])
        i += chunk

    # Close and terminate
    stream.stop_stream()
    stream.close()
    p.terminate()

elif PLAYER == 2:
    # Create a SimpleAudio object, send frames and play
    player = simpleaudio.play_buffer(frames, nc, sp, fps)

    # Wait for playback to finish before exiting
    player.wait_done()
