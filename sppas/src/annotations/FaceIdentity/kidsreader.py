# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceIdentity.kidsreader.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Read coords and identifiers from a CSV or an XRA file.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

import codecs
import os

from sppas.src.anndata import sppasXRA
from sppas.src.imgdata import sppasCoords
from sppas.src.videodata import sppasCoordsVideoWriter

# ---------------------------------------------------------------------------


class sppasKidsVideoReader(object):
    """Read&create list of coords and ids from a CSV file.

    The CSV file must have the following columns:

        - frame number
        - identifier -- str
        - timestamp
        - confidence
        - success
        - buffer number
        - index in the buffer
        - x, y, w, h

    """

    def __init__(self, input_file, csv_separator=";"):
        """Set the list of coords & ids defined in the given file.

        :param input_file: (str) coords&identifiers from a sppasKidsVideoWriter
        :param csv_separator: (char) Columns separator in the CSV file

        """
        self.coords = list()
        self.ids = list()

        fn, fe = os.path.splitext(input_file)
        if fe.lower() == ".csv":
            self.__load_from_csv(input_file, csv_separator)
        elif fe.lower() == ".xra":
            self.__load_from_xra(input_file)
        else:
            raise Exception("Unrecognized extension, expected .csv or .xra."
                            "Got {} instead.".format(fe))

    # -----------------------------------------------------------------------

    def __load_from_csv(self, input_file, separator):
        with codecs.open(input_file, "r") as csv:
            lines = csv.readlines()

        if len(lines) > 0:
            for line in lines:
                columns = line.split(separator)

                # 1st coord = new image
                if int(columns[1]) in (0, 1):
                    self.coords.append(list())
                    self.ids.append(list())

                # columns[4] is 0=failed, 1=success -- face found or not
                if int(columns[4]) == 1 and len(columns) > 8:
                    # identifier (the face number by default)
                    name = columns[1]
                    self.ids[len(self.ids) - 1].append(name)
                    # coordinates
                    coord = sppasCoords(int(columns[5]), int(columns[6]),
                                        int(columns[7]), int(columns[8]),
                                        float(columns[3]))
                    self.coords[len(self.coords) - 1].append(coord)

    # -----------------------------------------------------------------------

    def __load_from_xra(self, input_file):
        trs = sppasXRA("VideoCoordinates")
        trs.read(input_file)
        if len(trs) == 1:
            tier = trs[0]
        else:
            tier = trs.find(sppasCoordsVideoWriter().get_xra_tiername())
        if tier is None:
            raise Exception("No valid tier in XRA: not found. Cant load coordinates.")

        media = tier.get_media()
        if media is None:
            raise Exception("Invalid tier in XRA: no media. Cant load coordinates.")
        fps = media.get_meta("fps", None)
        if fps is None:
            raise Exception("Invalid media: no fps metadata. Cant load coordinates.")
        fps = float(fps)

        image_idx = 0
        for ann in tier:
            # get the frame index, i.e. starts from 0.
            frame_idx = ann.get_meta("frame_index", None)
            if frame_idx is None:
                loc = ann.get_location().get_highest_localization()
                start_time = loc.get_midpoint() - loc.get_radius()
                frame_idx = round(start_time * fps)
            else:
                frame_idx = int(frame_idx)

            for i in range(image_idx, frame_idx+1):
                self.coords.append(list())
                self.ids.append(list())

            # fill in the list of coords at the current image index
            for i, label in enumerate(ann.get_labels()):
                label_key = label.get_key()
                if label_key is None:
                    # this happens when loading the result of face detection
                    # but it should not with the result of person face identity.
                    label_key = str(i)
                for tag, score in label:
                    fuzzy_rect = tag.get_typed_content()
                    x, y, w, h = fuzzy_rect.get_midpoint()
                    coord = sppasCoords(x, y, w, h, score)
                    self.coords[frame_idx].append(coord)
                    self.ids[frame_idx].append(label_key)

            image_idx = frame_idx + 1
