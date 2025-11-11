#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017-2024  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# audioseg.py
# ---------------------------------------------------------------------------

import sys
import os
from argparse import ArgumentParser

from audioopy import AudioPCM
import audioopy.aio

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM))))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS directory not found.")
    sys.exit(1)
sys.path.append(SPPAS)

from sppas.core.coreutils import sppasUnicode
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import serialize_labels
from sppas.src.annotations import sppasFiles
from sppas.src.videodata import sppasVideoReader
from sppas.src.videodata import sppasVideoWriter

# ----------------------------------------------------------------------------


def adjust_on_video(fps, value, start=True):
    """Adjust the value on the closer frame boundary.

    :param fps: (float) Frames per seconds of the video
    :param value: (float) Time value in seconds
    :param start: (bool) return the begin time of the frame interval
    :return: (float)

    Example: if fps=60 and the given value is in range [0.150;0.167] then
    the value is in image index 9 (i.e. the 10th one). The returned value
    will be 0.150 if begin is True or 0.167 if begin is False.

    """
    # Get the index of the frame in which the value is occurring
    frame_idx = int(value * fps)
    # Return the start or end time of the frame interval
    if start is True:
        return float(frame_idx) / fps
    return float(frame_idx + 1) / fps


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file".format(os.path.basename(PROGRAM)),
                        description="... a program to "
                                    "segment an audio file into tracks.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input audio file name.')

parser.add_argument("-t",
                    metavar="tier",
                    required=False,
                    default="IPUs",
                    help="Name of the tier indicating the tracks. (default: IPUs)")

parser.add_argument("-p",
                    metavar="pattern",
                    required=False,
                    default="",
                    help="Pattern of the annotated file with the tier. (default: )")

parser.add_argument("-v",
                    metavar="pattern",
                    required=False,
                    default="",
                    help="Pattern of the video file. (default: )")

parser.add_argument("-P",
                    metavar="pattern",
                    required=False,
                    default="",
                    help="Pattern of the output. (default: )")

parser.add_argument("-e",
                    metavar="ext",
                    required=False,
                    default=".xra",
                    help='File extension for the tracks. (default: .xra)')

parser.add_argument("--shift_start",
                    type=float,
                    default=0.,
                    help="Systematically move at left the boundary of the beginning of a track (default: 0. seconds)")

parser.add_argument("--shift_end",
                    type=float,
                    default=0.,
                    help="Systematically move at right the boundary of the end of a track (default: 0. seconds)")

parser.add_argument("--video",
                    action='store_true',
                    help="Create tracks from the video file too.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

# remove the initial "-" in the output pattern
args = parser.parse_args()
if len(args.P) > 0 and args.P[0] == "-":
    args.P = args.P[1:]

# ----------------------------------------------------------------------------
# Load input data

# Open the audio and check it
try:
    audio = audioopy.aio.open(args.i)
except Exception as e:
    print(str(e))
    sys.exit(1)
if audio.get_nchannels() > 1:
    print('audioseg only supports mono audio files.')
    sys.exit(1)

# fix the annotated data filename
pattern = args.p
if pattern.startswith("\\"):
    pattern = pattern[1:]
if len(pattern) > 1 and pattern.startswith("-") is False:
    pattern = "-" + pattern

filename, _ = os.path.splitext(args.i)
ann_file = None
for ext in sppasFiles.get_informat_extensions("ANNOT"):
    ann_file = filename + pattern + ext
    if os.path.exists(ann_file):
        break
    else:
        ann_file = None
if ann_file is None:
    print("[ ERROR ] No annotated data file is matching the audio file {:s} with pattern {:s}."
          "".format(args.i, args.p))
    sys.exit(1)

# Load annotated data
try:
    parser = sppasTrsRW(ann_file)
    trs_input = parser.read()
except Exception as e:
    print(str(e))
    sys.exit(1)

# fix the video filename and open the video
vid_file = None
vid_ext = ".mp4"
if args.video:
    vpattern = args.v
    if vpattern.startswith("\\"):
        vpattern = vpattern[1:]
    if len(vpattern) > 1 and vpattern.startswith("-") is False:
        vpattern = "-" + vpattern
    for ext in sppasFiles.get_informat_extensions("VIDEO"):
        vid_file = filename + vpattern + ext
        if os.path.exists(vid_file):
            vid_ext = ext.lower()
            break
        else:
            vid_file = None
    if vid_file is None:
        print("[WARNING] No video file is matching the audio file {:s}.".format(args.i))
        print("The video option is disabled.")

# Open the video -- create a VideoReader
if vid_file is not None:
    # Create a VideoReader
    vid_reader = sppasVideoReader()
    vid_reader.open(vid_file)
    vid_fps = vid_reader.get_framerate()
    vid_w, vid_h = vid_reader.get_size()

# ----------------------------------------------------------------------------
# Extract the data we'll work on

# Extract the tier
tier = trs_input.find(args.t, case_sensitive=False)
if tier is None:
    print("[ ERROR] A tier with name {:s} wasn't found in file {:s}."
          "".format(args.t, ann_file))
    sys.exit(1)
if not args.quiet:
    print("The tier {:s} of the annotated file {:s} was loaded successfully"
          "".format(tier.get_name(), ann_file))

# Extract the channel
audio.extract_channel(0)
channel = audio.get_channel(0)
audio.rewind()
framerate = channel.get_framerate()
duration = channel.get_duration()

# ----------------------------------------------------------------------------
# Prepare output

tier_name = sppasUnicode(tier.get_name()).to_ascii()

# output directory
if len(args.P) > 0:
    output_dir = "-".join([filename, args.P, tier_name])
else:
    output_dir = filename + "-" + tier_name
if os.path.exists(output_dir):
    print("A directory with name {:s} is already existing.".format(output_dir))
    sys.exit(1)
os.mkdir(output_dir)
if not args.quiet:
    print("The output directory {:s} was created.".format(output_dir))

# ----------------------------------------------------------------------------
# Split the data into tracks

nb = 0
for i, ann in enumerate(tier):

    # is a track? if yes, extract the text content!
    text = serialize_labels(ann.get_labels(), separator="_", empty="", alt=False)
    if len(text) == 0 or ann.get_best_tag().is_silence():
        continue

    # get localization information
    begin = ann.get_lowest_localization().get_midpoint()
    end = ann.get_highest_localization().get_midpoint()

    # add shift value
    begin = max(0., begin - args.shift_start)
    end = min(duration, end + args.shift_end)

    # if video is enabled, we must adjust begin and end values to match
    # the beginning of the first frame and the end of the last frame
    # of the interval to be saved.
    if vid_file is not None:
        begin = adjust_on_video(vid_fps, begin, start=True)
        end = adjust_on_video(vid_fps, end, start=False)

    # fix base name of autio/trs files
    su = sppasUnicode(text)
    su.clear_whitespace()
    text_ascii = su.to_ascii()
    text_ascii = text_ascii[:29]  # to limit the size of the filename...
    if "'" in text_ascii:
        # remove quotes
        text_ascii = text_ascii.replace("'", "_")
    idx = "{:04d}".format(nb + 1)
    if len(args.P) > 0:
        fn = os.path.join(output_dir, idx + "_" + text_ascii + "-" + args.P)
    else:
        fn = os.path.join(output_dir, idx + "_" + text_ascii)
    if not args.quiet:
        print('* track {:s} from {:f} to {:f}'.format(idx, begin, end))

    # create audio output
    extracter = channel.extract_fragment(int(begin*framerate),
                                         int(end*framerate))
    audio_out = AudioPCM()
    audio_out.append_channel(extracter)
    if not args.quiet:
        print("   - audio: " + fn + ".wav" + " of %.3f seconds." % (end-begin))
    audioopy.aio.save(fn + ".wav", audio_out)

    # create text output (copy original label as it!)
    trs_output = sppasTranscription("TrackSegment")
    tracks_tier = trs_output.create_tier(tier_name + "-" + idx)
    tracks_tier.create_annotation(
        sppasLocation(sppasInterval(
            sppasPoint(0.),
            sppasPoint(float(end-begin))
        )),
        [l.copy() for l in ann.get_labels()]
    )
    parser.set_filename(fn + args.e)
    if not args.quiet:
        print("   - text: " + fn + args.e)
    parser.write(trs_output)

    # create video output
    if vid_file is not None:
        # Seek the video at the first frame of the interval
        start_frame = int(begin * vid_fps)
        end_frame = int(end * vid_fps)
        vid_reader.seek(start_frame)
        # Create a video writer
        vw = sppasVideoWriter()
        vw.set_fps(vid_fps)
        vw.set_size(vid_w, vid_h)
        vw.open(fn + vid_ext)
        # Read then write each image of the given interval
        for i in range(start_frame, end_frame):
            img = vid_reader.read()
            vw.write(img)
        vw.close()
        print("   - video: " + fn + vid_ext + " of %d images." % (end_frame - start_frame))

    nb += 1

# just to do things... properly!

if vid_file is not None:
    vid_reader.close()

if nb == 0:
    os.remove(output_dir)
    print("Done. No track extracted!\n")
else:
    if not args.quiet:
        print("Done. {:d} tracks were extracted.\n".format(nb))
