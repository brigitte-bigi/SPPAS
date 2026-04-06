# -*- coding: UTF-8 -*-
"""
:filename: sppas.scripts.sppasseg.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Use Praat and Parsel-mouth to estimate formants.

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

"""

import sys
import os
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import lgs
lgs.set_log_level(50)

import audioopy.aio

from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import serialize_labels
from sppas.src.annotations import sppasFiles
from sppas.src.annotations import sppasFindTier

from sppas.src.annotations.Formants.formants import FormantsEstimator

# ---------------------------------------------------------------------------
# Constants -- Default values for formant' estimators options.
# ---------------------------------------------------------------------------

# For a window, the half window duration:
HALF_WIN_DUR = 0.015

# 0 = Auto. else, fix an RMS value:
MIN_RMS_THRESHOLD = 0

ORDER = 12
FLOOR_FREQUENCY = 70.

# For diagnosis about the newly implemented methods
TARGET_PHONES = ['A/', 'e', 'E', 'i', 'o', 'O', 'u', 'y', '@', '2', '9', 'a~', 'o~', 'e~']

# ----------------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------------

# The formant estimators. None of the methods are actually enabled.
estimator = FormantsEstimator()

# Prepare a dictionary to store and compare estimated F1/F2
stats = {phone: {method: [] for method in estimator.get_available_method_names()} for phone in TARGET_PHONES}

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def load_aligned_phones(filename, log_func=None):
    """Locate and load phoneme alignment corresponding to an audio file.

    :param filename: (str) Root name of the file
    :param log_func: Optional logging/debugging function
    :return: tier of aligned phonemes
    :raises: SystemExit: if no annotation found or invalid

    """
    print("Loading phoneme alignment... from {filename}".format(filename=filename))
    phonemes = None
    for ext in sppasFiles.get_informat_extensions("ANNOT"):
        path = filename + "-palign" + ext
        if os.path.exists(path):
            phonemes = path
            break

    if phonemes is None:
        print(f"No annotated data corresponding to the audio file {filename}.")
        sys.exit(1)

    if log_func:
        log_func(f"Annotated file with phonemes was found: {phonemes}.")

    try:
        parser = sppasTrsRW(phonemes)
        trs_input = parser.read()
        tier = sppasFindTier.aligned_phones(trs_input)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    if log_func:
        log_func(f"Annotated file with phonemes is valid.")

    return tier

# ----------------------------------------------------------------------------
# Parse command-line arguments
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file -p file [options]".format(os.path.basename(PROGRAM)),
                        description="Estimate F1/F2 formants for phonemes of a given audio file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help="Input WAV file name.")

parser.add_argument("-p",
                    metavar="file",
                    required=True,
                    help="Input phonemes file name.")

parser.add_argument("-o",
                    metavar="ext",
                    required=False,
                    help='Output file name.')

parser.add_argument("--method",
                    action="append",
                    required=True,
                    choices=estimator.get_available_method_names(),
                    help="Add a formant estimation method (repeatable).")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable output display.")

if len(sys.argv) <= 1:
    sys.argv.append("-h")

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Load time-aligned phonemes and open audio
# ----------------------------------------------------------------------------

filename = os.path.splitext(args.i)[0]
tier_palign = load_aligned_phones(filename, logging.debug)

# ----------------------------------------------------------------------------
# Formant configuration and extraction
# ----------------------------------------------------------------------------

for method in args.method:
    estimator.enable_method(method)

estimator.set_order(ORDER)
estimator.set_win_dur(HALF_WIN_DUR*2.)
estimator.set_rms_threshold(MIN_RMS_THRESHOLD)
estimator.set_floor_frequency(FLOOR_FREQUENCY)
tier_f1, tier_f2 = estimator.estimate(args.i, tier_palign)

# ----------------------------------------------------------------------------
# Write result into an annotated file or on stdout
# ----------------------------------------------------------------------------
if args.o:
    trs = sppasTranscription("Formants")
    trs.append(tier_f1)
    trs.append(tier_f2)
    parser = sppasTrsRW(args.o)
    parser.write(trs)

methods = estimator.get_enabled_method_names()

# Print estimated values on stdout
for f1, f2 in zip(tier_f1, tier_f2):
    begin = f1.get_lowest_localization()
    end = f1.get_highest_localization()
    label_f1 = f1.get_labels()[0]
    label_f2 = f2.get_labels()[0]
    phon = label_f1.get_key()
    n = 0
    for (tag1, score1), (tag2, score2) in zip(label_f1, label_f2):
        t1 = tag1.get_typed_content()
        t2 = tag2.get_typed_content()
        method_name = methods[n]
        n += 1
        # Fill-in stats
        if phon in TARGET_PHONES:
            stats[phon][method_name].append((t1, t2))

    if not args.quiet:
        f1_str = "|".join([f.get_content() for f,s in label_f1])
        f2_str = "|".join([f.get_content() for f,s in label_f2])
        print("{:.3f} {:.3f} {} F1={} F2={}"
              "".format(begin.get_midpoint(), end.get_midpoint(), phon, f1_str, f2_str))

# Print stats
if len(estimator.get_enabled_method_names()) > 1:
    print("\n--- Method evaluation against reference ---\n")

    ref_method = estimator.get_enabled_method_names()[0]
    min_count = 10  # minimum required occurrences per phone

    for phone in TARGET_PHONES:
        phone_data = stats[phone]
        if len(phone_data[ref_method]) < min_count:
            continue  # skip underrepresented phones

        print(f"[{phone}] ({len(phone_data[ref_method])} occurrences)")
        ref_values = phone_data[ref_method]

        for method, values in phone_data.items():
            if len(values) != len(ref_values):
                continue  # skip incomplete comparisons

            # Exclude failed values (f1=0 or f2=0)
            valid_f1 = [f1 for f1, f2 in values if f1 > 0 and f2 > 0]
            valid_f2 = [f2 for f1, f2 in values if f1 > 0 and f2 > 0]
            fail_count = len(values) - len(valid_f1)

            if valid_f1:
                mean_f1 = sum(valid_f1) / len(valid_f1)
                mean_f2 = sum(valid_f2) / len(valid_f2)
            else:
                mean_f1 = mean_f2 = 0.0

            if method != ref_method:
                diff_f1 = [abs(rf1 - tf1) for (rf1, _), (tf1, _) in zip(ref_values, values)
                           if rf1 > 0 and tf1 > 0]
                diff_f2 = [abs(rf2 - tf2) for (_, rf2), (_, tf2) in zip(ref_values, values)
                           if rf2 > 0 and tf2 > 0]

                if diff_f1:
                    delta_f1 = sum(diff_f1) / len(diff_f1)
                    delta_f2 = sum(diff_f2) / len(diff_f2)
                else:
                    delta_f1 = delta_f2 = 0.0
            else:
                delta_f1 = delta_f2 = 0.0

            print(f"  → {method}")
            print(f"     Mean F1: {mean_f1:.1f} Hz")
            print(f"     Mean F2: {mean_f2:.1f} Hz")
            print(f"     ΔF1 vs ref: {delta_f1:.1f} Hz")
            print(f"     ΔF2 vs ref: {delta_f2:.1f} Hz")
            print(f"     Failed estimations: {fail_count}")
        print()
