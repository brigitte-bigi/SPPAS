#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.scripts.answer_time.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: estimate the delay of answers in conversation.

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

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

Use cases:
##########


Case 1/
#######

       --------------1---------------------------2-----------------
tier1        #       |             speech        |        #
       ------------------------------------------------------------

       ---------------------------------------------3--------------
tier2                                       #       |    speech
       ------------------------------------------------------------

case1_delay = (time3 - time2)
is a positive value because speaker2 waited speaker1 ends to speak.
Condition: time1 < time3 succeeded


Case 2/
#######

       --------------1---------------------------2-----------------
tier1        #       |             speech        |        #
       ------------------------------------------------------------

       ------------------------------------3-----------------------
tier2                              #       |    speech
       ------------------------------------------------------------

case2_delay = (time3 - time2)
is a negative value because speaker2 started to speak before speaker1
ended its own speech.
Condition: time1 < time3 succeeded

Case 3/
#######

       --------------1---------------------------2-----------------
tier1        #       |             speech        |        #
       ------------------------------------------------------------

       ---------3---------------------------------4--------5-------
tier2      #    |        speech1                  |    #   | speech2
       ------------------------------------------------------------

case3_delay = (time5 - time2)
because speaker2 started before speaker1. It's answer to speaker1
IPU is speech2.
Condition: time1 < time3 failed; time1 < time5 succeeded.


Case 4/
#######

       --------------1---------------------------2-----------------
tier1        #       |             speech        |        #
       ------------------------------------------------------------

       --------------------3 ---------------------4--------5-------
tier2                 #    |        speech1       |    #   | speech2
       ------------------------------------------------------------

case4_delay = (time3 - time2)
is a negative value because speaker2 speak during speaker1 speech!
Condition: time1 < time3 succeeded
====>>>> IN THIS CASE, SHOULD WE CONSIDER speech2 INSTEAD?
(so, what are the conditions to ignore speech1?)

"""

# Import required Python modules
from __future__ import annotations
import sys
import os.path
import logging
from argparse import ArgumentParser

# Get this program and SPPAS pathes
PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

# Add SPPAS to the list of importable paths
sys.path.append(SPPAS)

# Import SPPAS configuration and annotation modules
from sppas.core.config import lgs       # Logger settings
from sppas.core.config import sg        # General SPPAS info (name, version, etc.)
from sppas.core.coreutils import sppasError
from sppas.src.anndata import sppasTrsRW   # For reading annotation files
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation
from sppas.src.annotations import sppasFindTier
from sppas.src.calculus import fmean
from sppas.src.calculus import lstdev

# ---------------------------------------------------------------------------


def get_transcription(filename: str) -> sppasTier:
    """Return the tier with orthographic transcription.

    :param filename: (str) The filename of the transcription file.
    :return: (sppasTier) The tier with the orthographic transcription.
    :raises: sppasError: No transcription found or transcription is not time-aligned.
    :raises: IOExtensionError: File extension is not supported

    """
    parser = sppasTrsRW(filename)
    trs = parser.read()
    tier = sppasFindTier.transcription(trs)
    if tier is None:
        tier = sppasFindTier.ipus(trs)
        if tier is None:
            raise sppasError(f"No transcription tier found in {filename}")
    if tier.is_point() is True:
        raise sppasError(f"No time-aligned transcription tier found in {filename}")
    return tier

# ---------------------------------------------------------------------------


def is_speech_labelled(ann: sppasAnnotation, laughter: bool = False) -> bool:
    """Return true if the given annotation is speech.

    :param ann: (sppasAnnotation) The annotation to consider.
    :param laughter: (bool) Whether a laughter is considered speech or not.
    :return: (bool) True if the annotation is speech.

    """
    # An empty annotation
    if ann.is_labelled() is False:
        return False

    # Get the first annotation label.
    # In an ortho transcript it should be the only one.
    label = ann.get_labels()[0]

    # Check the tag with best score of this label.
    # In an ortho transcript it should be the only one.
    _speech = label.get_best().is_speech()

    # Consider a laughter as speech (used in a feedback)
    if laughter is True:
        laughter = label.get_best().is_laugh()

    return _speech or laughter

# ---------------------------------------------------------------------------


def ann_delay(ann1: sppasAnnotation, ann2: sppasAnnotation) -> float:
    """Return the delay between two annotations.

    Estimate the time difference between the end of `ann1` and the start of
    `ann2`. The result can be negative if `ann2` starts before `ann1` ends.

    :param ann1: (sppasAnnotation) The first annotation.
    :param ann2: (sppasAnnotation) The second annotation.
    :return: (float) The delay in seconds.

    """
    _loc1 = ann1.get_highest_localization()
    _loc2 = ann2.get_lowest_localization()
    return _loc2.get_midpoint() - _loc1.get_midpoint()

# ---------------------------------------------------------------------------


def estimate_delay(tier1: sppasTier, tier2: sppasTier) -> list:
    """Return the delays between IPUs of two tiers.

    :param tier1: (sppasTier) The first tier.
    :param tier2: (sppasTier) The second tier.
    :return: (list) The delays in seconds.

    """
    _delays = list()

    for _ann1 in tier1:
        # Check if this annotation is speech
        if is_speech_labelled(_ann1) is False:
            continue

        # Get annotation begin/end localization
        # -------------------------------------
        _begin1_loc = _ann1.get_lowest_localization()
        _end1_loc = _ann1.get_highest_localization()
        # We reached the end of tier2. No answer anymore.
        if _end1_loc >= tier2.get_last_point():
            break

        # Get interlocutor answer: find the next IPUs with speech in tier2
        # ------------------------
        # Get annotation in tier2 this point is inside
        _ann2_index = tier2.near(_end1_loc, direction=0)
        logging.debug(f"NEAR result for ann1 end value: {_end1_loc} ==> "
                      f"ann2 idx={_ann2_index}: {tier2[_ann2_index]}")
        _is_speech = False
        if _ann2_index != -1:
            # Search for the closer forward annotation with speech
            while _is_speech is False and _ann2_index < len(tier2):
                _ann2 = tier2[_ann2_index]
                logging.debug(f" ... for ann1 end value: {_end1_loc} ==> "
                              f" tested ann2 idx={_ann2_index}: {tier2[_ann2_index]}")
                _begin2_loc = _ann2.get_lowest_localization()

                # Consider this ann2 only if both:
                # 1. it's speech; and
                # 2. this speech started after ann1 started.
                logging.debug(f" ... is_speech: {is_speech_labelled(_ann2, laughter=True)}")
                logging.debug(f" ... is starting after: {_begin2_loc >= _begin1_loc}")

                if (is_speech_labelled(_ann2, laughter=True) is True
                        and _begin2_loc >= _begin1_loc):
                    _is_speech = True
                # Increment only if there's a next loop
                if _is_speech is False:
                    _ann2_index += 1
                logging.debug(f" ... ... is considered speech: {_is_speech}")

                # Stop searching if _ann2 is very far away...
                if _ann2_index < len(tier2):
                    _d = ann_delay(_ann1, tier2[_ann2_index])
                    if _d > 2.:
                        break

            # Estimate the delay between both speech IPUs
            # --------------------------------------------
            if _is_speech is True:
                _d = ann_delay(_ann1, tier2[_ann2_index])
                logging.debug(f"Delay={_d} between {_end1_loc} and {tier2[_ann2_index]}")
                _delays.append(_d)

        if _is_speech is False:
            logging.debug(f"No answer found for ann {_ann1}")

    return _delays

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Parse command-line arguments
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -s file1 -i file2 [options]",
        description="Estimate answer delay of both speakers in conversation.",
        epilog="This program is part of {:s} version {:s}. {:s}.".format(
            sg.__name__, sg.__version__, sg.__copyright__)
    )

    # Required argument: the annotated files of speakers
    parser.add_argument(
        "-s",
        required=True,
        metavar="file1",
        help='Filename of the orthographic transcription, speaker 1.')

    parser.add_argument(
        "-i",
        required=True,
        metavar="file2",
        help='Filename of the orthographic transcription, speaker 2.')

    # Optional argument: reduce log output
    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable verbosity")

    # If the user runs the script without arguments, show the help
    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    # Parse the arguments
    args = parser.parse_args()

    # ------------------------------------------------------------------------
    # Set up logging based on the verbosity level
    # ------------------------------------------------------------------------

    if not args.quiet:
        lgs.set_log_level(1)  # Normal verbosity
    else:
        lgs.set_log_level(30)  # Warnings only
    lgs.stream_handler()       # Output logs to the terminal

    # ----------------------------------------------------------------------------
    # Load data files and search for the transcription tier
    # ----------------------------------------------------------------------------

    tier1 = get_transcription(args.s)  # Speaker 1
    tier2 = get_transcription(args.i)  # Speaker 2
    spk1 = os.path.basename(args.s).split(".")[0]
    spk2 = os.path.basename(args.i).split(".")[0]

    if tier1 == tier2:
        raise Exception("Given speaker transcriptions are the same ones.")

    # Iterate over IPUs of speaker2 to estimate the average answer delay of speaker1.
    delays1 = estimate_delay(tier2, tier1)
    print(f"{spk1} average answer delay to {spk2}: {round(fmean(delays1), 3)} "
          f"(stdev={round(lstdev(delays1), 3)})")

    # Iterate over IPUs of speaker1 to estimate the average answer delay of speaker2.
    delays2 = estimate_delay(tier1, tier2)
    print(f"{spk2} average answer delay to {spk1}: {round(fmean(delays2), 3)} "
          f"(stdev={round(lstdev(delays2), 3)})")
