#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
:filename: sppas.scripts.img_tag_sights.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tag given sights on a given image.

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

You detected sights, for example a face or hands, and you want to see
the sights at the given coordinates on your image

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
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImageSightsReader
from sppas.src.imgdata import sppasCoordsImageWriter
from sppas.src.annotations.FaceSights import sppasFaceSightsImageWriter
from sppas.src.annotations.HandPose import sppasHandsSightsImageWriter

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Parse command-line arguments
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -s sights -o image [options]",
        description="Tag an image with the given sights.",
        epilog="This program is part of {:s} version {:s}. {:s}.".format(
            sg.__name__, sg.__version__, sg.__copyright__)
    )

    # Required argument: the annotated files of speakers
    parser.add_argument(
        "-s",
        required=True,
        metavar="file1",
        help='Filename of the sights (face.s, hand.s, etc)')

    parser.add_argument(
        "-o",
        required=True,
        metavar="file2",
        help='Output filename of the tagged image.')

    parser.add_argument(
        "-i",
        required=False,
        metavar="file3",
        help='Filename of the image to tag.')

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
    # Load data files
    # ----------------------------------------------------------------------------

    # Load sights first, in case we have to fix the image size
    _img_sights = sppasImageSightsReader(args.s)

    # Load the given image or create a blank one
    if args.i:
        _img = sppasImage(filename=args.i)
    else:
        # Fix the image size
        _img_w = 0
        _img_h = 0
        for _cur_sight in _img_sights.sights:
            # Search for the max x and max y values in all sights
            x_max = max(_cur_sight.get_x())
            y_max = max(_cur_sight.get_y())
            if x_max > _img_w:
                _img_w = x_max
            if y_max > _img_h:
                _img_h = y_max

        # Create a blank image to draw the target points on
        _img = sppasImage(0).blank_image(
            w=int(_img_w*1.1),
            h=int(_img_h*1.1),
            white=True)

    # Draw the sights
    # ---------------

    # Create drawers
    _face_drawer = sppasFaceSightsImageWriter()
    _hand_drawer = sppasHandsSightsImageWriter()
    _coords_drawer = sppasCoordsImageWriter()

    # Browse and draw sights on the image
    for _cur_sight in _img_sights.sights:
        if len(_cur_sight) == 68:
            _img = _face_drawer.tag_image(_img, [_cur_sight], [(128, 128, 128)])
        elif len(_cur_sight) == 21:
            _img = _hand_drawer.tag_coords(_img, [_cur_sight], [(0, 0, 0)])

    _all_coords = list()
    for _cur_sight in _img_sights.sights:
        if len(_cur_sight) not in (68, 21):
            _cur_coords = [None] * len(_cur_sight)
            for i, _c in enumerate(_cur_sight):
                _cur_coords[i] = sppasCoords(_c[0], _c[1])
            _all_coords.append(_cur_coords)
    if len(_all_coords) > 0:
        _img = _coords_drawer.tag_image(_img, _all_coords)

    # Save image file
    _img.write(args.o)
