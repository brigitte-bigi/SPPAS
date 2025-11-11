# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.imgdata.imgsightsreader.py
:author:   Brigitte Bigi, Florian Lopitaux
:contact:  contact@sppas.org
:summary:  Read a CSV or XRA file and load sights of an image.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

    ---------------------------------------------------------------------

"""

import logging
import codecs
import os

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasExtensionReadError
from sppas.core.coreutils import sppasIOError
from sppas.src.anndata import sppasXRA

from .sights import sppasSights
from .coordinates import sppasCoords

# ---------------------------------------------------------------------------


class sppasImageSightsReader:
    """Read&create sights from a CSV/XRA file.

    The CSV file must have the following columns:

        - 1
        - index of the sights in the image;
        - success -- like in OpenFace2 CSV results
        - number of sights
        - all x values
        - all y values
        - all z values -- if not None
        - image name

    """

    def __init__(self, input_file, csv_separator=";"):
        """Set the list of sights defined in the given file.

        :param input_file: (str) Coords from a sppasCoordsImageWriter
        :param csv_separator: (char) Optional parameter, ';' character by default
                                     Columns separator in the CSV file

        :raises sppasTypeError: If one of the two parameters are not a string object
        :raises sppasIOError: If the input file is not found
        :raises sppasExtensionReadError: If the extension of the input file is not 'xra' or 'csv'

        """
        if not isinstance(input_file, str):
            raise sppasTypeError(input_file, "str")

        if not os.path.exists(input_file):
            raise sppasIOError(input_file)

        # List of coordinates, and corresponding image filenames
        self.sights = list()

        _, file_extension = os.path.splitext(input_file)
        if file_extension.lower() == ".csv":
            if not isinstance(csv_separator, str):
                raise sppasTypeError(csv_separator, "str")

            self.__load_from_csv(input_file, csv_separator)

        elif file_extension.lower() == ".xra":
            self.__load_from_xra(input_file)

        else:
            raise sppasExtensionReadError("Unrecognized extension, expected .csv or .xra."
                                          "Got {0} instead.".format(file_extension))

    # -----------------------------------------------------------------------

    def __load_from_csv(self, input_file, separator):
        """Initialize all sights data from the csv file data loaded.

        :param input_file: (str) Coords from a sppasCoordsImageWriter
        :param separator: (char) Columns separator in the CSV file

        :raises sppasTypeError: If the csv has a bad value in this data

        """
        # open and read the csv file
        with codecs.open(input_file, "r") as csv:
            lines = csv.readlines()

        # Browse the (expected only one) line(s) to get sights.
        if len(lines) == 0:
            return

        for line in lines:
            content = line.split(separator)
            # column to indicate a success: 1 if yes
            if content[2] == "1":
                # number of sight values
                nb_sights = sppasCoords.to_dtype(content[3])
                current_sights = sppasSights(nb_sights)

                # extract all (x, y)
                for i in range(3, 3 + nb_sights):
                    x = sppasCoords.to_dtype(content[i-3], unsigned=False)
                    y = sppasCoords.to_dtype(content[i-3 + nb_sights], unsigned=False)

                    current_sights.set_sight(i-3, x, y)

                self.sights.append(current_sights)

    # -----------------------------------------------------------------------

    def __load_from_xra(self, input_file):
        """Initialize all sights data from the xra file data loaded.

        :param input_file: (str) Coords from a sppasCoordsImageWriter

        :raises sppasError: If the annotation file doesn't contain any sights tier.

        """
        # read the annotation file
        transcription = sppasXRA("HandImageSights")
        transcription.read(input_file)

        # Get the tier with the expected type:
        # location is point and labels are fuzzy points
        tier = None

        for current_tier in transcription:
            if current_tier.is_point() is True and current_tier.is_fuzzypoint() is True:
                tier = current_tier
                break

        if tier is None:
            raise sppasError("No valid tier in XRA. Cant load sights.")

        # Browse the (expected only one) annotation(s) to get sights.
        for annotation in tier:
            current_sights = sppasSights(nb=len(annotation.get_labels()))

            for label in annotation.get_labels():
                tag = label.get_best()

                # get score
                score = label.get_score(tag)

                # get coordinates
                fuzzy_point = tag.get_typed_content()
                x, y = fuzzy_point.get_midpoint()

                sight_index = label.get_key()[-2:]

                try:
                    sight_index = int(sight_index)
                    current_sights.set_sight(sight_index, x, y, z=None, score=score)

                # if the name of the key of the sight is incorrect
                except ValueError:
                    logging.error("The key of the sight is incorrect : " + sight_index)

            self.sights.append(current_sights)
