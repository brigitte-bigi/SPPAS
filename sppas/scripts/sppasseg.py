# -*- coding: UTF-8 -*-
"""
:filename: sppas.scripts.sppasseg.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Full automatic process of speech segmentation.

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

Preamble:
=========

The audio file must be MONO, e.g. with only one channel. It can be 16,000Hz
or more but not less. It can be 16bits or 24bits (not tested) but 32bits can
be randomly problematic.

The transcribed file (if given) must be utf-8.

Any filename -- it includes its path, should only be US-ASCII characters
without whitespace: if not, it can randomly cause problems under Windows.

Description:
============

It's a three automatic steps process:

1. Prepare the data:

    - Nothing is done if the ortho. transcription is already time-aligned into
      the IPUs;
    - Fill in IPUs if the ortho. transcription is already available but not
      time-aligned. Notice that it can't work if the recording protocol was
      not very very very strict: it works only if the number of sounding
      segments EXACTLY matches the given number of transcribed segments.
    - Search for IPUs and auto. transcribe with the STT DeepSpeech. It
      requires installing DeepSpeech in the currently used Python and to give
      the path of the models. Get it here (DeepSpeech + English model):
      https://github.com/mozilla/DeepSpeech/releases/
      or here for another language:
      https://discourse.mozilla.org/t/links-to-pretrained-models/62688

      The function "stt" can be modified in order to replace DeepSpeech by
      another STT system. It could also be modified in order to use the API
      of DeepSpeech (much faster) rather than launching a process.

2. Perform Speech Segmentation;

    - no option to configure the annotations. They are all fixed internally!
    - can estimate an intensity coefficient;
    - can predict silent pauses (the ones into the IPUs).

3. Format the output (if asked).

    - can map the phoneme into another set (IPA, Praat, ...) if a mapping
      table is given. It's a file with two columns, both separated by a
      whitespace: 1st is SPPAS phoneme, 2nd is expected phoneme.
    - can create a data structure with all the results and write into a JSON
      file.

Example of use:
==============

    $SPPAS/.sppaspyenv~/bin/python3 $SPPAS/sppas/scripts/sppasseg.py
       -w ./audio_files/some_mono_audio.wav
       -l eng
       --sil
       --rms
       --norm
       -e .TextGrid

"""

import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sg
from sppas.core.config import lgs
lgs.set_log_level(30)
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasTrsRW
from sppas.src.annotations.SpeechSeg.sppasspeechseg import sppasSpeechSeg
from sppas.src.annotations import sppasFiles
from sppas.src.annotations.SpeechToText import WhisperSTTonIPUs

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -i text_file -w audio_file -e lang [options]",
        description="Fully automatic speech segmentation",
        epilog="This program is part of {:s} version {:s}. {:s}.".format(
            sg.__name__, sg.__version__, sg.__copyright__)
    )

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-w",
        required=True,
        metavar="file",
        help='Input audio file name (.wav).')

    group_io.add_argument(
        "-i",
        required=False,
        metavar="file",
        help='Input transcription file name (trs within IPUs or simple txt).')

    group_io.add_argument(
        "-l",
        metavar="lang",
        required=True,
        help='Iso of one of the available languages.')

    group_io.add_argument(
        "-e",
        metavar=".ext",
        default=sppasFiles.get_default_extension("ANNOT"),
        choices=sppasFiles.get_outformat_extensions("ANNOT"),
        help='Output annotation file extension. One of: {:s}'
             ''.format(" ".join(sppasFiles.get_outformat_extensions("ANNOT"))))

    group_io.add_argument(
        "--map",
        metavar="file",
        required=False,
        help='A phoneme mapping table (2 columns with a whitespace separator).')

    parser.add_argument(
        "--sil",
        action='store_true',
        help="Enable the prediction of a short silence after each token")

    parser.add_argument(
        "--rms",
        action='store_true',
        help="Add the intensity in a [0-20] range scale")

    parser.add_argument(
        "--norm",
        action='store_true',
        help="Normalize and print the output on stdout")

    parser.add_argument(
        "--json",
        action='store_true',
        help="Normalize and save the result in a json file")

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable verbosity")

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Redirect all messages to a quiet logging
    # ----------------------------------------
    if not args.quiet:
        lgs.set_log_level(15)
    lgs.stream_handler()

    # ----------------------------------------------------------------------------
    # Annotations are running here
    # ----------------------------------------------------------------------------
    fn, fe = os.path.splitext(args.w)

    # Prepare the data: create an ortho. transcription into IPUs
    # ----------------------------------------------------------------------------
    ipus = WhisperSTTonIPUs(language=args.l)
    tier_ipus = ipus.ipussegments([args.w, args.i])
    media = sppasMedia(os.path.abspath(args.w), mime_type="audio/" + fe)
    tier_ipus.set_media(media)
    trs = sppasTranscription("AutoIPUs")
    trs.append(tier_ipus)

    # Write the resulting transcription into an annotated (intermediate) file
    # Not needed but it can be useful to check this intermediate step.
    output_ipus_file = fn + "-autotrs" + args.e
    parser = sppasTrsRW(output_ipus_file)
    parser.write(trs)

    # And Speech Segmentation is here
    # ----------------------------------------------------------------------------
    # Fix options to the speech segmenter
    seg = sppasSpeechSeg()
    map_table = None
    if args.map:
        map_table = args.map
    seg.load_resources(args.l, map_table)
    if args.sil:
        # predict the silent pauses into IPUs
        seg.set_predict_sil(True)
    else:
        seg.set_predict_sil(False)
    if args.rms:
        # predict the intensity
        seg.set_predict_intensity(True)
    else:
        seg.set_predict_intensity(False)

    if args.norm or args.json:
        seg.set_output_json(True)
    else:
        seg.set_output_json(False)

    # Perform the full speech segmentation process

    # Get directly the transcription object without reading a file
    trs = seg.convert(args.w, tier_ipus)
    # and turn the trs into a dictionary (ready to be written in JSON)
    # (only if output json was enabled).
    if len(trs) > 0:
        output_file = seg.fix_out_file_ext(fn + seg.get_output_pattern() + args.e)
        parser = sppasTrsRW(output_file)
        parser.write(trs)

        if args.json:
            output_file = seg.fix_out_file_json_ext(fn + seg.get_output_pattern() + args.e)
            seg.save_trs(trs, output_file)

        if args.norm:
            result = seg.save_trs(trs, None)
            print(result)

    else:
        print("The annotation failed to produce a result.")
