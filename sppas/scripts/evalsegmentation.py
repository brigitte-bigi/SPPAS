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

    scripts.evalsegmentation.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ... a script to evaluate a segmentation vs a reference segmentation.

    It estimates the Unit Boundary Positioning Accuracy and generates an
    R script to draw a boxplot of the evaluation.

"""

import sys
import os
import codecs
import os.path
from argparse import ArgumentParser
import subprocess

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.anndata import sppasTrsRW
from sppas.src.calculus import ubpa
from sppas.src.anndata.aio import extensions as aio_extensions

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

fillers = ["laugh", "noise", "fp"]


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def is_vowel(entry):
    """Return true if the given entry is a vowel.

    :param entry: ((str)

    """
    _vowels = ["a", "e", "i", "o", "u", "y", "M", "Q", "V", "{", "}", "@",
               "1", "2", "3", "6", "7", "8", "9", "&"]
    if len(entry) == 0:
        return False
    if entry in _vowels:
        return True
    for v in _vowels:
        if entry[0] == v or entry[0].lower() == v:
            return True
    return False


def is_consonant(entry):
    """Return true if the given entry is a consonant.

    :param entry: ((str)

    """
    if len(entry) == 0:
        return False
    _consonants = ["b", "b", "c", "d", "f", "g", "h", "j", "k", "l", "m",
                   "n", "p", "q", "r", "s", "t", "v", "w", "x", "z", "?",
                   "4", "5", "<", ">"]
    if entry in _consonants:
        return True
    if is_vowel(entry):
        return False
    for c in _consonants:
        if entry[0] == c or entry[0].lower() == c:
            return True
    return False

# ----------------------------------------------------------------------------
# Functions to manage input annotated files


def get_tier(filename, tier_idx):
    """Return the tier of the given index in an annotated file.

    :param filename: (str) Name of the annotated file
    :param tier_idx: (int) Index of the tier to get
    :returns: sppasTier or None

    """
    try:
        parser = sppasTrsRW(filename)
        trs_input = parser.read(filename)
    except:
        return None
    if tier_idx < 0 or tier_idx >= len(trs_input):
        return None

    return trs_input[tier_idx]

# ----------------------------------------------------------------------------


def get_tiers(ref_filename, hyp_filename, ref_idx=0, hyp_idx=0):
    """Return a reference and an hypothesis tier from annotated files.

    :param ref_filename: Name of the annotated file with the reference
    :param hyp_filename: Name of the annotated file with the hypothesis
    :param ref_idx: (int)
    :param hyp_idx: (int)

    :returns: a tuple with sppasTier or None for both ref and hyp

    """
    ref_tier = get_tier(ref_filename, ref_idx)
    hyp_tier = get_tier(hyp_filename, hyp_idx)

    return ref_tier, hyp_tier

# ---------------------------------------------------------------------------
# Function to draw the evaluation as BoxPlots (using an R script)


def test_R():
    """Test if Rscript is available as a command of the system. """
    try:
        NULL = open(os.devnull, "w")
        subprocess.call(['Rscript'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False
    return True

# ---------------------------------------------------------------------------


def exec_Rscript(filenamed, filenames, filenamee, rscriptname, pdffilename, vector):
    """Perform an the R script to draw boxplots from the given files.
    
    Write the script, then execute it, and delete it.

    :param filenamed: (str) duration
    :param filenames: (str) start
    :param filenamee: (str) end
    :param rscriptname: (str)
    :param pdffilename: PDF file with the result
    :param vector: list of phonemes in the expected order

    """
    level = ""
    for p in vector:
        if "\\" in p:
            p = p.replace("\\", "\\\\")
        level += '"' + p + '"' + ','
    level = level[:-1]

    with codecs.open(rscriptname, "w", "utf8") as fp:
        fp.write("#!/usr/bin/env Rscript \n")
        fp.write("# Title: Boxplot for phoneme alignments evaluation \n")
        fp.write("\n")
        fp.write("args <- commandArgs(trailingOnly = TRUE) \n")
        fp.write("\n")
        fp.write("# Get datasets \n")
        fp.write('dataD <- read.csv("%s",header=TRUE,sep=",") \n' % filenamed)
        fp.write('dataPS <- read.csv("%s",header=TRUE,sep=",") \n' % filenames)
        fp.write('dataPE <- read.csv("%s",header=TRUE,sep=",") \n' % filenamee)
        fp.write("\n")
        fp.write("# Define Output file \n")
        fp.write('pdf(file="%s", paper="a4") \n' % pdffilename)
        fp.write("\n")
        fp.write("# Control plotting style \n")
        fp.write("par(mfrow=c(3,1))    # only one line and one column \n")
        fp.write("par(cex.lab=1.1)     # controls the font size of the axis title \n")
        fp.write("par(cex.axis=0.85)    # controls the font size of the axis labels \n")
        fp.write("par(cex.main=1.3)    # controls the font size of the title \n")
        fp.write("\n")
        fp.write("# Then, plot: \n")

        # I reorder the phonemes in R data
        fp.write("dataD$PhoneD <- factor(dataD$PhoneD, levels=c(" + level + "))\n")
        # Then create the boxplot
        fp.write("boxplot(dataD$DeltaD ~ dataD$PhoneD, \n")
        fp.write('   main="Delta Duration",             # graphic title \n')
        fp.write('   ylab="T(automatic) - T(manual)",   # y axis title \n')
        fp.write('   #range=0,                          # use min and max for the whisker \n')
        fp.write('   outline = FALSE,                   # REMOVE OUTLIERS \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        # fp.write('   ylim=c(-0.2,0.2), \n')
        fp.write('   col="pink") \n')
        fp.write("   abline(0,0) \n")
        fp.write("\n")

        fp.write("dataPS$PhoneS <- factor(dataPS$PhoneS, levels=c(" + level + "))\n")
        fp.write('boxplot(dataPS$DeltaS ~ dataPS$PhoneS, \n')
        fp.write('   main="Delta Start Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE, \n')
        fp.write('   border = "blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col = "pink") \n')
        fp.write('   abline(0,0) \n')
        fp.write("\n")

        fp.write("dataPE$PhoneE <- factor(dataPE$PhoneE, levels=c(" + level + "))\n")
        fp.write('boxplot(dataPE$DeltaE ~ dataPE$PhoneE, \n')
        fp.write('   main="Delta End Position", \n')
        fp.write('   ylab="T(automatic) - T(manual)", \n')
        fp.write('   outline = FALSE,  \n')
        fp.write('   border="blue", \n')
        fp.write('   ylim=c(-0.05,0.05), \n')
        fp.write('   col="pink") \n')
        fp.write('abline(0,0) \n')
        fp.write('graphics.off() \n')
        fp.write("\n")
        fp.close()

    command = "Rscript " + rscriptname
    try:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        retval = p.wait()
        line = p.communicate()
    except OSError as e:
        os.remove(rscriptname)
        return e

    # os.remove(rscriptname)
    if retval != 0:
        return line

    return ""

# ---------------------------------------------------------------------------


def boxplot(deltaposB, deltaposE, deltaposD, extras, out_name, vector, name):
    """Create a PDF file with boxplots of selected phonemes.

    :param vector: the list of phonemes

    """
    filenamed = out_name + "-delta-duration-" + name + ".csv"
    filenames = out_name + "-delta-position-start-" + name + ".csv"
    filenamee = out_name + "-delta-position-end-" + name + ".csv"

    fpb = codecs.open(filenames, "w", 'utf8')
    fpe = codecs.open(filenamee, "w", 'utf8')
    fpd = codecs.open(filenamed, "w", 'utf8')
    fpb.write("PhoneS,DeltaS\n")
    fpe.write("PhoneE,DeltaE\n")
    fpd.write("PhoneD,DeltaD\n")
    for i, extra in enumerate(extras):
        etiquette = extra[0]
        tag = extra[2]
        if etiquette in vector:
            if "\\" in etiquette:
                etiquette = etiquette.replace("\\", "\\\\")

            if tag != 0:
                fpb.write("%s,%f\n" % (etiquette, deltaposB[i]))
            if tag != -1:
                fpe.write("%s,%f\n" % (etiquette, deltaposE[i]))
            fpd.write("%s,%f\n" % (etiquette, delta_durationur[i]))
    fpb.close()
    fpe.close()
    fpd.close()

    message = exec_Rscript(filenamed, filenames, filenamee, out_name+name+".R", out_name+"-delta-"+name+".pdf", vector)

    # os.remove(filenamed)
    # os.remove(filenames)
    # os.remove(filenamee)
    return message


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Verify and extract args:

parser = ArgumentParser(
    usage="%(prog)s -fr ref -fh hyp [options]", 
    description="Compare two segmentation boundaries, "
                "in the scope of evaluating an hypothesis vs a reference.")

parser.add_argument(
    "-fr",
    metavar="file",
    required=True,
    help='Input annotated file/directory name of the reference.')

parser.add_argument(
    "-fh",
    metavar="file",
    required=True,
    help='Input annotated file/directory name of the hypothesis.')

parser.add_argument(
    "-tr",
    metavar="file",
    type=int,
    default=1,
    required=False,
    help='Tier number of the reference (default=1).')

parser.add_argument(
    "-th",
    metavar="file",
    type=int,
    default=1,
    required=False,
    help='Tier number of the hypothesis (default=1).')

parser.add_argument(
    "-d",
    metavar="delta",
    required=False,
    type=float,
    default=0.04,
    help='Delta max value for the UBPA estimation (default=0.02).')

parser.add_argument(
    "-s",
    metavar="step",
    required=False,
    type=float,
    default=0.005,
    help='Delta step value for the UBPA estimation (default=0.005).')

parser.add_argument(
    "-o",
    metavar="path",
    required=False,
    help='Path for the output files.')

parser.add_argument(
    "--quiet",
    action='store_true',
    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Global variables

idxref_tier = args.tr - 1
idxhyp_tier = args.th - 1
files = []      # List of tuples: (ref_filename, hyp_filename)
delta_durationur = []   # Duration of each phoneme
deltaposB = []  # Position of the beginning boundary of each phoneme
deltaposE = []  # Position of the end boundary of each phoneme
deltaposM = []  # Position of the center of each phoneme
extras = []     # List of tuples: (evaluated phoneme, hypothesis file names, a tag)
vowels = list()      # List of evaluated vowels
consonants = list()  # List of evaluated consonants


# ----------------------------------------------------------------------------
# Prepare file names to be analyzed, as a list of tuples (ref,hyp)

out_path = None
if args.o:
    out_path = args.o
    if not os.path.exists(out_path):
        os.mkdir(out_path)

if os.path.isfile(args.fh) and os.path.isfile(args.fr):
    hyp_filename, extension = os.path.splitext(args.fh)
    out_basename = os.path.basename(hyp_filename)
    if out_path is None:
        out_path = os.path.dirname(hyp_filename)
    out_name = os.path.join(out_path, out_basename)

    files.append((os.path.basename(args.fr), os.path.basename(args.fh)))
    ref_directory = os.path.dirname(args.fr)
    hyp_directory = os.path.dirname(args.fh)

elif os.path.isdir(args.fh) and os.path.isdir(args.fr):
    if out_path is None:
        out_path = args.fh
    out_name = os.path.join(out_path, "phones")

    ref_directory = args.fr
    hyp_directory = args.fh

    ref_files = []
    hyp_files = []
    for fr in os.listdir(args.fr):
        if os.path.isfile(os.path.join(ref_directory, fr)):
            ref_files.append(fr)
    for fh in os.listdir(args.fh):
        if os.path.isfile(os.path.join(hyp_directory, fh)):
            hyp_files.append(os.path.basename(fh))

    for fr in ref_files:
        base_fr, ext_fr = os.path.splitext(fr)
        if not ext_fr.lower() in aio_extensions:
            continue
        for fh in hyp_files:
            base_fh, ext_fh = os.path.splitext(fh)
            if not ext_fh.lower() in aio_extensions:
                continue
            if fh.startswith(base_fr):
                files.append((fr, fh))

else:
    print("Both reference and hypothesis must be of the same type: "
          "file or directory.")
    sys.exit(1)

if not args.quiet:
    print("Results will be stored in: {}".format(out_name))

if len(files) == 0:
    print("No matching hyp/ref files. Nothing to do!")
    sys.exit(1)

# ----------------------------------------------------------------------------
# Evaluate the delta from the hypothesis to the reference
# Delta = T(hyp) - T(ref)

if not args.quiet:
    print("Results are evaluated on {:d} files: ".format(len(files)))

for f in files:

    if not args.quiet:
        print("    {:s}".format(os.path.basename(f[1])))

    fr = os.path.join(ref_directory, f[0])
    fh = os.path.join(hyp_directory, f[1])
    ref_tier, hyp_tier = get_tiers(fr, fh, idxref_tier, idxhyp_tier)
    if ref_tier is None or hyp_tier is None:
        print("[ INFO ] No aligned phonemes found in tiers. Nothing to do. ")
        continue
    if len(ref_tier) != len(hyp_tier):
        print("[ ERROR ] Hypothesis: {} -> {} vs Reference: {} -> {} phonemes."
              .format(f[1], len(hyp_tier), f[0], len(ref_tier)))
        continue
    if not args.quiet:
        print("[ OK ] Hypothesis: {} vs Reference: {} -> {} phonemes."
              .format(f[1], f[0], len(ref_tier)))

    # ----------------------------------------------------------------------------
    # Compare boundaries and durations of annotations.

    i = 0
    imax = len(ref_tier)-1

    for ref_ann, hyp_ann in zip(ref_tier, hyp_tier):
        etiquette = serialize_labels(ref_ann.get_labels(), separator="")
        if etiquette == "#":
            continue

        # begin
        rb = ref_ann.get_location().get_best().get_begin().get_midpoint()
        hb = hyp_ann.get_location().get_best().get_begin().get_midpoint()
        delta_start = hb-rb
        # end
        re = ref_ann.get_location().get_best().get_end().get_midpoint()
        he = hyp_ann.get_location().get_best().get_end().get_midpoint()
        delta_end = he-re
        # middle
        rm = rb + (re-rb)/2.
        hm = hb + (he-hb)/2.
        delta_center = hm-rm
        # duration
        rd = ref_ann.get_location().get_best().duration().get_value()
        hd = hyp_ann.get_location().get_best().duration().get_value()
        delta_duration = hd-rd

        tag = 1
        if i == 0:
            tag = 0
        elif i == imax:
            tag = -1

        # Add new values into vectors, to evaluate the accuracy
        deltaposB.append(delta_start)
        deltaposE.append(delta_end)
        deltaposM.append(delta_center)
        delta_durationur.append(delta_duration)
        extras.append((etiquette, fh, tag))

        # Fill in the lists of evaluated consonants and vowels
        if is_vowel(etiquette) is True:
            if etiquette not in vowels:
                vowels.append(etiquette)
        elif is_consonant(etiquette) is True:
            if etiquette not in consonants:
                consonants.append(etiquette)

        i += 1

# ----------------------------------------------------------------------------
# Save delta values into output files

fpb = codecs.open(os.path.join(out_name)+"-delta-position-start.txt", "w", 'utf8')
fpe = codecs.open(os.path.join(out_name)+"-delta-position-end.txt", "w", 'utf8')
fpm = codecs.open(os.path.join(out_name)+"-delta-position-middle.txt", "w", 'utf8')
fpd = codecs.open(os.path.join(out_name)+"-delta-duration.txt",  "w", 'utf8')

fpb.write("Phone Delta Filename\n")
fpe.write("Phone Delta Filename\n")
fpm.write("Phone Delta Filename\n")
fpd.write("Phone Delta Filename\n")

for i, extra in enumerate(extras):
    etiquette = extra[0]
    filename = extra[1]
    tag = extra[2]
    if tag != 0:
        fpb.write("%s %f %s\n" % (etiquette, deltaposB[i], filename))
    if tag != -1:
        fpe.write("%s %f %s\n" % (etiquette, deltaposE[i], filename))
    fpm.write("%s %f %s\n" % (etiquette, deltaposM[i], filename))
    fpd.write("%s %f %s\n" % (etiquette, delta_durationur[i], filename))

fpb.close()
fpe.close()
fpm.close()
fpd.close()

# ----------------------------------------------------------------------------
# Estimates the Unit Boundary Positioning Accuracy

if not args.quiet:
    ubpa(deltaposB, "Start boundary", sys.stdout, delta_max=args.d, step=args.s)

with open(out_name+"-eval-position-start.txt", "w") as fp:
    ubpa(deltaposB, "Start boundary position", fp, delta_max=args.d, step=args.s)
with open(out_name+"-eval-position-end.txt", "w") as fp:
    ubpa(deltaposE, "End boundary position", fp, delta_max=args.d, step=args.s)
with open(out_name+"-eval-position-middle.txt", "w") as fp:
    ubpa(deltaposM, "Middle boundary position", fp, delta_max=args.d, step=args.s)

with open(out_name+"-eval-duration.txt", "w") as fp:
    ubpa(delta_durationur, "Duration", fp, delta_max=args.d, step=args.s)

# ----------------------------------------------------------------------------
# Draw BoxPlots of the accuracy via an R script

if test_R() is False:
    sys.exit(0)

# Sorting list of vowels in case-insensitive manner
vowels = sorted(vowels, key=lambda s: s.casefold())
# Create the PDF file with Box Plots of vowels
message = boxplot(deltaposB, deltaposE, delta_durationur, extras, out_name, vowels, "vowels")
if len(message) > 0 and not args.quiet:
    print("{}".format(message))

# Sorting list of consonants in case-insensitive manner
consonants = sorted(consonants, key=lambda s: s.casefold())
# Create the PDF file with Box Plots os consonants
message = boxplot(deltaposB, deltaposE, delta_durationur, extras, out_name, consonants, "consonants")
if len(message) > 0 and not args.quiet:
    print("{}".format(message))

# Create the PNG file with Box Plots
message = boxplot(deltaposB, deltaposE, delta_durationur, extras, out_name, fillers, "fillers")
if len(message) > 0 and not args.quiet:
    print("{}".format(message))

others = []
known = vowels + consonants + fillers
for extra in extras:
    etiquette = extra[0]
    if not (etiquette in known or etiquette in others):
        others.append(etiquette)

if len(others) > 0:
    message = boxplot(deltaposB, deltaposE, delta_durationur, extras, out_name, others, "others")
    if len(message) > 0 and not args.quiet:
        print("{}".format(message))
