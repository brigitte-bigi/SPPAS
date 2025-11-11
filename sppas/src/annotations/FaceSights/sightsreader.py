# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.sightsreader.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Load sights.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

import os
import codecs
import logging

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasXRA
from sppas.src.anndata import sppasFuzzyPoint
from sppas.src.imgdata import sppasSights

from .kidsightswriter import sppasKidsSightsVideoWriter

# ---------------------------------------------------------------------------


class sppasSightsVideoReader(object):
    """Read&create list of ids and sights from a CSV file or XRA.

    The CSV file must have the following columns:

        - 0: frame number
        - 1: the face_id
        - 2: timestamp
        - 3: success
        - 4: buffer number
        - 5: index in the buffer
        - 6: average confidence score
        - 7: n                  -- number of sights
        - x_1 .. x_n
        - y_1 .. y_n
        - optionally score_1 .. score_n

    *** FOR XRA: 68 SIGHTS ARE EXPECTED for each KID! no more... ***

    """

    def __init__(self, input_file, csv_separator=";"):
        """Set the list of ids & sights defined in the given file.

        :param input_file: (str) ids&sights from a sppasSightsVideoWriter
        :param csv_separator: (char) Columns separator in the CSV file

        """
        self.sights = list()
        self.ids = list()
        self.midpoints = list()
        self.radius = list()

        fn, fe = os.path.splitext(input_file)
        if fe.lower() == ".csv":
            self.__load_from_csv(input_file, csv_separator)
        elif fe.lower() == ".xra":
            self.__load_from_xra(input_file)
        else:
            raise Exception("Unrecognized extension, expected .xra or .csv."
                            "Got {} instead.".format(fe))

    # -----------------------------------------------------------------------

    def __load_from_csv(self, input_file, separator):
        with codecs.open(input_file, "r") as csv:
            lines = csv.readlines()

        if len(lines) > 0:
            frame = -1
            for line in lines:
                columns = line.split(separator)

                # this is a new image, not a new face in the previous image
                if int(columns[0]) != frame:
                    new_frame = int(columns[0])
                    while frame < new_frame:
                        # in case of holes
                        self.sights.append(list())
                        self.ids.append(list())
                        #  we can't expect the time values because we don't have metadata
                        self.midpoints.append(None)
                        self.radius.append(None)
                        frame += 1
                        logging.warning("Missing sights at frame {:d}".format(frame))
                    # The midpoint of the new image, but no radius.
                    self.midpoints[-1] = float(columns[2])

                # columns[3] is 0=failed, 1=success -- sights found or not
                if int(columns[3]) == 1:
                    # identifier (the face number by default)
                    name = columns[1]
                    self.ids[len(self.ids) - 1].append(name)

                    # sights
                    # columns[11] is the average score of sights or "none"
                    if len(columns) > 7:
                        # columns[7] is the number of sight values
                        nb = int(columns[7])
                        s = sppasSights(nb)
                        # extract all (x, y, score) -- z ignored if exists
                        z = None
                        for i in range(8, 8+nb):
                            x = int(columns[i])
                            y = int(columns[i+nb])
                            if len(columns) > (8+(2*nb)):
                                score = float(columns[i+(2*nb)])
                            else:
                                score = None
                            s.set_sight(i-8, x, y, z, score)

                        self.sights[len(self.sights) - 1].append(s)
                    else:
                        self.sights[len(self.sights) - 1].append(None)

    # -----------------------------------------------------------------------

    def __load_from_xra(self, input_file):
        trs = sppasXRA("VideoSights")
        trs.read(input_file)
        if len(trs) == 1:
            tier = trs[0]
        else:
            tier = trs.find(sppasKidsSightsVideoWriter().get_xra_tiername())
        if tier is None:
            raise Exception("No valid tier in XRA: not found. Cant load sights.")

        media = tier.get_media()
        if media is None:
            raise Exception("Invalid tier in XRA: no media. Cant load sights.")
        fps = media.get_meta("fps", None)
        if fps is None:
            raise Exception("Invalid media: no fps metadata. Cant load sights.")
        fps = float(fps)

        image_idx = 0
        for ann in tier:
            loc = ann.get_location().get_highest_localization()
            start_time = loc.get_midpoint() - loc.get_radius()

            # get the frame index, i.e. starts from 0.
            frame_idx = ann.get_meta("frame_index", None)
            if frame_idx is None:
                frame_idx = round(start_time * fps)
            else:
                frame_idx = int(frame_idx)

            # in case there are holes (no annotation for an image)
            for i in range(image_idx, frame_idx):
                self.ids.append(list())
                self.sights.append(list())
                # Append the midpoint time value of each image in the hole.
                # Use the radius of the current ann which is supposed the same for all images
                self.midpoints.append(loc.get_radius() + (image_idx * (1. / fps)))
                self.radius.append(loc.get_radius())
                logging.warning("Missing sights at index {:d} - midpoint={}".format(i, self.midpoints[-1]))

            # append the midpoint and radius time value of this annotation
            self.midpoints.append(loc.get_midpoint())
            self.radius.append(loc.get_radius())

            # fill in the list of sights at the current image index
            prev_kid = ""
            six = 0
            s = sppasSights(nb=68)
            if len(ann.get_labels()) == 0:
                # no sights estimated in this annotation
                self.sights.append(list())
                self.ids.append(list())
            else:
                for i, label in enumerate(ann.get_labels()):
                    label_key = label.get_key()
                    if label_key is None:
                        # this happens when loading the result of face detection
                        # but it should not with the result of person face identity.
                        kid = str(i)
                    else:
                        # The label key contains the kid and the sight index
                        kid = label_key.split("_")[0]
                    if kid != prev_kid:
                        self.sights.append(list())
                        self.ids.append(list())
                        prev_kid = kid
                        s = sppasSights(nb=68)
                        self.sights[-1].append(s)
                        self.ids[-1].append(kid)
                        six = 0

                    tag = label.get_best()
                    score = label.get_score(tag)
                    fuzzy_point = tag.get_typed_content()
                    if isinstance(fuzzy_point, sppasFuzzyPoint) is False:
                        raise sppasTypeError(type(fuzzy_point), "sppasFuzzyPoint")
                    x, y = fuzzy_point.get_midpoint()
                    s.set_sight(six, x, y, None, score)
                    six += 1

            image_idx = frame_idx + 1
