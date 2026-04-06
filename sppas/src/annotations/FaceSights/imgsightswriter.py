# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.imgsightswriter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Image writer for sights of a face.

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

    ---------------------------------------------------------------------

"""

import mimetypes
import os
import codecs
import logging
import cv2
import numpy

from sppas.src.anndata import sppasXRA
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasCoordsImageWriter
from sppas.src.imgdata import sppasSights

# ---------------------------------------------------------------------------


class sppasImageFaceSightsReader(object):
    """Read&create sights from a CSV file.

    Unused and never tested.
    z-axis mustn't be in the csv file.

    """

    def __init__(self, csv_file):
        """Set the list of sights defined in the given file.

        :param csv_file: sights from a sppasSightsImageWriter

        """
        self.sights = list()
        with codecs.open(csv_file, "r") as csv:
            lines = csv.readlines()

        if len(lines) > 0:
            for line in lines:
                content = line.split(";")
                # column to indicate a success: 1 if yes
                if content[2] == "1":
                    # number of sight values
                    nb = int(content[3])
                    s = sppasSights(nb)
                    # extract all (x, y, score)
                    for i in range(3, 3+nb):
                        x = content[i]
                        y = content[i+nb]
                        if len(content) > (3+(2*nb)):
                            score = content[i+(2*nb)]
                        else:
                            score = None
                        s.set_sight(i, x, y, score)

                    self.sights.append(s)

# ---------------------------------------------------------------------------


class sppasFaceSightsImageWriter(sppasCoordsImageWriter):
    """Write an image and optionally sppasSights into files.

    z-axis is ignored.

    """

    def __init__(self):
        """Create a new sppasSightsImageWriter instance.

        Write the given image in the given filename.
        Parts of the image can be extracted in separate image files.
        Output images can be resized.
        sppasSights can be drawn in any of such output images.

        """
        super(sppasFaceSightsImageWriter, self).__init__()

    # -----------------------------------------------------------------------

    def write_coords(self, fd, coords, sep=";", write_success=True):
        """Write sights in the given stream.

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param coords: (sppasSights) sppasSights to write in other columns.
        :param sep: (char) CSV separator
        :param write_success: (bool) Write 0 or 1 in the 1st column

        """
        if coords is None:
            # write un-success
            fd.write("none{:s}0{:s}".format(sep, sep))
            return 0

        # write the average score, if we have one
        avg_score = coords.get_mean_score()
        if avg_score is None:
            fd.write("none{:s}".format(sep))
        else:
            fd.write("{:f}{:s}".format(avg_score, sep))

        # then write success, then coords
        if len(coords) > 0:
            # write success -- like in OpenFace2 CSV results
            if write_success is True:
                fd.write("1{:s}".format(sep))

            # number of sights
            fd.write("{:d}{:s}".format(len(coords), sep))

            # write all x values
            for x in coords.get_x():
                fd.write("{:d}{:s}".format(x, sep))

            # write all y values
            for y in coords.get_y():
                fd.write("{:d}{:s}".format(y, sep))

            # write confidence scores if they exist
            scores = coords.get_score()
            if scores is not None:
                for s in scores:
                    if s is None:
                        fd.write("none{:s}".format(sep))
                    else:
                        fd.write("{:f}{:s}".format(s, sep))

        else:
            # write success
            if write_success is True:
                fd.write("0{:s}".format(sep))
            return 0

        return 1

    # -----------------------------------------------------------------------

    def tag_image(self, image, coords, colors=list()):
        """Tag the image at the given coords.

        :param image: (sppasImage) The image to write
        :param coords: (list of tuples) The list of nb sights of objects
        :param colors: list of (r,g,b) List of tuple with RGB int values
        :return: a copy of the image with colored squares at the given coords

        """
        if image is None:
            return None
        if coords is None:
            return image
        for i, s in enumerate(reversed(coords)):
            if isinstance(s, sppasSights) is False:
                if isinstance(s, sppasCoords) is True:
                    img = sppasCoordsImageWriter.tag_image(self, image, coords, colors)
                    return img
                if isinstance(s, tuple) is False and len(s) != 4:
                    logging.error("A list of sights was expected.")
                    coords.remove(s)

        # Make a copy of the image to tag it without changing the given one
        img = sppasImage(input_array=image.copy())
        # Add colors if we need more
        if len(colors) > 0:
            rgb = colors[0]
        else:
            if len(self._colors['r']) < 2:
                nb = max(10, len(coords) - len(self._colors['r']) + 1)
                new_colors = sppasCoordsImageWriter.gen_colors(nb)
                self._colors.update(new_colors)
            r = self._colors['r'][0]
            g = self._colors['g'][0]
            b = self._colors['b'][0]
            rgb = (r, g, b)

        if isinstance(coords, (list, tuple)) is True:
            for s in coords:
                img = self.__tag_sights(img, s, color=rgb)
            return img
        return self.__tag_sights(img, coords, color=rgb)

    # -----------------------------------------------------------------------

    def __tag_sights(self, img, sights, color):
        """Really tag the sights..."""
        coords = list()
        for s in sights:
            x, y, z, c = s
            coords.append(sppasCoords(x, y, confidence=c))

        if len(coords) == 68:
            pts = list()
            for i in range(0, 17):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts)
            pts = list()
            for i in range(17, 22):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts)
            pts = list()
            for i in range(22, 27):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts)
            pts = list()
            for i in range(27, 31):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts)
            pts = list()
            for i in range(31, 36):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts)
            pts = list()
            for i in range(36, 42):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts, True)
            pts = list()
            for i in range(42, 48):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts, True)
            pts = list()
            for i in range(48, 60):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts, True)
            pts = list()
            for i in range(60, 68):
                pts.append([coords[i].x, coords[i].y])
            img = self.__draw_polyline(img, pts, True)

        for c in coords:
            img = cv2.circle(img, (c.x, c.y), 1, color, 2)

        return img

    # -----------------------------------------------------------------------

    def __draw_polyline(self, image, pts, is_closed=False):
        pts = numpy.array(pts, numpy.int32)
        pts = pts.reshape((-1, 1, 2))
        color = (240, 240, 240)
        thickness = 1
        return cv2.polylines(image, [pts], is_closed, color, thickness)

    # -----------------------------------------------------------------------

    def write_xra_coords(self, coords, out_xra_name, img_name=""):
        """Write or append sights in an XRA file.

        :param coords: (sppasSights or list of sights) The sights of objects
        :param out_xra_name: (str) The filename of the XRA file to write
        :param img_name: (str) The filename of the image

        """
        if coords is None:
            return
        for i, s in enumerate(reversed(coords)):
            if isinstance(s, sppasSights) is False:
                if isinstance(s, sppasCoords) is True:
                    sppasCoordsImageWriter.write_xra_coords(self, coords, out_xra_name)
                    return
                if isinstance(s, tuple) is False and len(s) != 4:
                    logging.error("Sights or a list of sights was expected.")
                    coords.remove(s)

        tiername = "ImgSights"
        if self._xra_tiername is not None:
            tiername = self._xra_tiername

        loc = sppasPoint(1)
        if os.path.exists(out_xra_name):
            trs = sppasXRA("ImageSights")
            trs.read(out_xra_name)
            tier = trs.find(tiername)
            if tier is None:
                raise Exception("Invalid tier in XRA. Can't add sights.")
            last_point = tier.get_last_point()
            loc = sppasPoint(last_point.get_midpoint() + 1)
        else:
            m = mimetypes.guess_type(img_name)
            if m[0] is None:
                fn, fe = os.path.splitext(img_name)
                mime_type = "image/" + fe[1:]
            else:
                mime_type = m[0]
            media = sppasMedia(img_name, mime_type=mime_type)
            tier = sppasTier(tiername)
            tier.set_media(media)
            trs = sppasXRA("ImageSights")
            trs.append(tier)

        if isinstance(coords, (list, tuple)) is True:
            if len(coords) > 1:
                raise NotImplementedError("Saving sights of more than one face in an image is not supported yet.")
            if len(coords) == 1:
                coords = coords[0]

        # Create the annotation representing the given sights
        labels = self.__sight_labels(coords)
        ann = tier.create_annotation(sppasLocation(loc), labels)
        ann.set_meta("image_name", img_name)

        # Override the XRA file
        trs.write(out_xra_name)

    # -----------------------------------------------------------------------

    @staticmethod
    def __sight_labels(sight):
        labels = list()
        for i, c in enumerate(sight):
            if c is None:
                continue
            # Create the sppasTag() with (x,y) values
            tag = sppasTag((c[0], c[1]), tag_type="point")
            # Create the sppasLabel() with the sppasTag() and its score
            label = sppasLabel(tag, c[2])
            label.set_key("sight{:2d}".format(i))
            # Append to the list of labels of this annotation
            labels.append(label)
        return labels
