# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.imgsightswriter.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Image writer for sights of hands.

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

import mimetypes
import os
import codecs
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
from sppas.src.imgdata import sppasSights
from sppas.src.imgdata import sppasCoordsImageWriter

# ---------------------------------------------------------------------------


class sppasHandsSightsImageWriter(sppasCoordsImageWriter):
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
        super(sppasHandsSightsImageWriter, self).__init__()

    # -----------------------------------------------------------------------

    def write_csv_coords(self, coords, out_csv_name, img_name=""):
        """Write or append a list of coordinates/sights in a CSV file.

        - index of the coords in the image
        - confidence
        - x, y, w, h
        - image name

        :param coords: (sppasCoords) The coordinates of objects
        :param out_csv_name: (str) The filename of the CSV file to write
        :param img_name: (str) The filename of the image

        """
        mode = "w"
        if os.path.exists(out_csv_name) is True:
            mode = "a+"

        with codecs.open(out_csv_name, mode, encoding="utf-8") as f:
            for i, c1 in enumerate(coords):
                if isinstance(c1, (list, tuple)) is False:
                    f.write("{:d}{:s}{:d}{:s}".format(i + 1, self._csv_separator, i + 1, self._csv_separator))
                    self.write_coords(f, c1)
                    if len(img_name) > 0:
                        f.write("{:s}{:s}".format(img_name, self._csv_separator))
                    f.write("\n")

                else:
                    for j, c2 in enumerate(c1):
                        f.write("{:d}{:s}{:d}{:s}".format(i + 1, self._csv_separator, j + 1, self._csv_separator))
                        self.write_coords(f, c2, self._csv_separator)
                        if len(img_name) > 0:
                            f.write("{:s}{:s}".format(img_name, self._csv_separator))
                        f.write("\n")

    # -----------------------------------------------------------------------

    def write_coords(self, fd, coords, sep=";", write_success=True):
        """Write sights of all hands in the given stream.

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param coords: (sppasSights) sppasSights to write.
        :param sep: (char) CSV separator
        :param write_success: (bool) Write 0 or 1 in the 1st column

        """
        if coords is None:
            # write un-success
            if write_success is True:
                fd.write("0{:s}".format(sep, sep))
            return 0

        if isinstance(coords, sppasCoords):
            if write_success is True:
                fd.write("1{:s}".format(sep))
            fd.write("{:f}{:s}".format(coords.get_confidence(), sep))
            fd.write("{:d}{:s}".format(coords.x, sep))
            fd.write("{:d}{:s}".format(coords.y, sep))
            fd.write("{:d}{:s}".format(coords.w, sep))
            fd.write("{:d}{:s}".format(coords.h, sep))

        elif isinstance(coords, sppasSights) and len(coords) > 0:
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

            # write all z values
            if coords.get_z() is not None:
                for y in coords.get_z():
                    fd.write("{:d}{:s}".format(y, sep))

        else:
            # write success
            if write_success is True:
                fd.write("0{:s}".format(sep))
            return 0

        return 1

    # -----------------------------------------------------------------------

    def tag_coords(self, img, coords, pen_width, colors=list()):
        """Override. Tag image for the given coords or sights.

        :param img: (sppasImage) The image to write
        :param coords: (list of sppasCoords OR list(list of sppasCoords)) The coordinates of objects
        :param colors: List of (r,g,b) Tuple with RGB int values
        :return: (sppasImage)

        """
        for i, c in enumerate(coords):
            if c is None:
                continue
            if isinstance(c, (list, tuple)) is False:
                c = [c]

            # Either use the i-th default color or the i-th given one
            if len(colors) != len(c):
                # Get the i-th color
                n = len(self._colors['r'])
                r = self._colors['r'][i % n]
                g = self._colors['g'][i % n]
                b = self._colors['b'][i % n]
                rgb = (r, g, b)
            else:
                rgb = colors[i]

            if isinstance(c[0], sppasCoords):
                # Draw the square and the confidence inside the square if the coord is not a point
                img = self.__tag_coords(img, c, pen_width, rgb)
            else:
                # Draw a circle for each sight
                img = self.__tag_sights(img, c, rgb)

        return img

    # -----------------------------------------------------------------------

    def __tag_coords(self, img, coords_list, pen_width, color):
        """Really tag the coords...

        Each coord has a different color.

        """
        for i, c in enumerate(coords_list):
            img = img.isurround([c], color=color, thickness=pen_width, score=True)

        return img

    # -----------------------------------------------------------------------

    def __tag_sights(self, img, sights_list, rgb):
        """Really tag the sights...

        Each hand has a different color.

        """
        if img.channel == 4:
            r, g, b = rgb
            color = (r, g, b, 250)
            gray = (128, 128, 128, 250)
        else:
            color = rgb
            gray = (128, 128, 128)
        for hand_idx in range(len(sights_list)):
            coords = list()
            for s in sights_list[hand_idx]:
                x, y, z, c = s
                coords.append(sppasCoords(x, y, confidence=c))

            thickness = 4
            if len(coords) == 21:
                # This is a hand
                thickness = self.__eval_thickness_from_sights(sights_list[hand_idx], percent=10)
                img = self.__draw_lines_hand(img, coords, gray, thickness)
            elif len(coords) == 33:
                # This is a body pose
                thickness = self.__eval_thickness_from_sights(sights_list[hand_idx], percent=40)
                img = self.__draw_lines_pose(img, coords, gray, thickness)

            for c in coords:
                img = cv2.circle(img, (c.x, c.y), 1, color=gray, thickness=thickness+3)
                img = cv2.circle(img, (c.x, c.y), 1, color=color, thickness=thickness-2)

        return sppasImage(input_array=img)

    # -----------------------------------------------------------------------

    def __draw_lines_hand(self, img, sights, color, thickness):
        # draw fingers
        pts = list()
        for i in range(1, 5):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        for i in range(5, 9):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        for i in range(9, 13):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        for i in range(13, 17):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        for i in range(17, 21):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))

        # hand contour
        pts = list()
        pts.append([sights[0].x, sights[0].y])
        pts.append([sights[1].x, sights[1].y])
        pts.append([sights[5].x, sights[5].y])
        pts.append([sights[9].x, sights[9].y])
        pts.append([sights[13].x, sights[13].y])
        pts.append([sights[17].x, sights[17].y])
        img = self.__draw_polyline(img, pts, is_closed=True, color=color, thickness=max(2, thickness // 4))

        return img

    # -----------------------------------------------------------------------

    def __draw_lines_pose(self, img, sights, color, thickness):
        # lips
        pts = list()
        pts.append([sights[9].x, sights[9].y])
        pts.append([sights[10].x, sights[10].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        # right arm + hand
        pts = list()
        for i in range(12, 20, 2):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        pts.append([sights[22].x, sights[22].y])
        pts.append([sights[16].x, sights[16].y])
        pts.append([sights[20].x, sights[20].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        # left arm + hand
        pts = list()
        for i in range(11, 19, 2):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        pts = list()
        pts.append([sights[21].x, sights[21].y])
        pts.append([sights[15].x, sights[15].y])
        pts.append([sights[19].x, sights[19].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        # body contour
        pts = list()
        pts.append([sights[11].x, sights[11].y])
        pts.append([sights[23].x, sights[23].y])
        pts.append([sights[24].x, sights[24].y])
        pts.append([sights[12].x, sights[12].y])
        img = self.__draw_polyline(img, pts, is_closed=True, color=color, thickness=max(2, thickness // 4))
        # right leg
        pts = list()
        for i in range(24, 32, 2):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))
        # left leg
        pts = list()
        for i in range(23, 31, 2):
            pts.append([sights[i].x, sights[i].y])
        img = self.__draw_polyline(img, pts, color=color, thickness=max(2, thickness // 4))

        return img

    # -----------------------------------------------------------------------

    def __eval_thickness_from_sights(self, sights, percent=10):
        all_x = sights.get_x()
        all_y = sights.get_y()
        min_x = min(all_x)
        min_y = min(all_y)
        max_x = max(all_x)
        max_y = max(all_y)
        w = max_x - min_x
        h = max_y - min_y
        value = min(w // percent, h // percent)

        return min(50, max(4, value))

    # -----------------------------------------------------------------------

    def __draw_polyline(self, image, pts, is_closed=False, color=(128, 128, 128), thickness=2):
        pts = numpy.array(pts, numpy.int32)
        pts = pts.reshape((-1, 1, 2))
        return cv2.polylines(image, [pts], is_closed, color, thickness)

    # -----------------------------------------------------------------------

    def write_xra_coords(self, coords, out_xra_name, img_name=""):
        """Write or append sights in an XRA file.

        :param coords: (sppasSights) The sights of objects
        :param out_xra_name: (str) The filename of the XRA file to write
        :param img_name: (str) The filename of the image

        """
        if coords is None:
            return
        if isinstance(coords, (list, tuple)) is False:
            raise TypeError("expected a list")

        tiername = "ImgSights"
        if self._xra_tiername is not None:
            tiername = self._xra_tiername

        if os.path.exists(out_xra_name):
            trs = sppasXRA("ImageCoordinates")
            trs.read(out_xra_name)
            media = trs.get_media_list()[0]
        else:
            m = mimetypes.guess_type(img_name)
            if m[0] is None:
                fn, fe = os.path.splitext(img_name)
                mime_type = "image/" + fe[1:]
            else:
                mime_type = m[0]
            media = sppasMedia(img_name, mime_type=mime_type)
            trs = sppasXRA("ImageCoordinates")

        # test data structure
        is_list_of_list = False
        for idx in range(len(coords)):
            all_sights = coords[idx]
            if isinstance(all_sights, (list, tuple)) is False:
                is_list_of_list = False
        if is_list_of_list is False:
            coords = [coords]

        for idx in range(len(coords)):
            loc = sppasPoint(1)
            tier = trs.find(tiername + str(idx))
            if tier is not None:
                last_point = tier.get_last_point()
                loc = sppasPoint(last_point.get_midpoint() + 1)
            else:
                tier = sppasTier(tiername + str(idx))
                tier.set_media(media)
                trs.append(tier)

            # Create the annotation representing the given list
            labels = self.__create_labels(coords[idx])
            ann = tier.create_annotation(sppasLocation(loc), labels)
            ann.set_meta("image_name", img_name)

        # Override the XRA file
        trs.write(out_xra_name)

    # -----------------------------------------------------------------------

    def __create_labels(self, c):
        """Create labels from coords or list of coords."""
        if len(c) == 0:
            return list()

        labels = list()
        for i, sights in enumerate(c):
            if isinstance(sights, sppasCoords):
                tag = sppasTag((sights.x, sights.y, sights.w, sights.h), tag_type="rect")
                label = sppasLabel(tag, sights.get_confidence())
                label.set_key("{:d}_coords".format(i))
                labels.append(label)

            elif isinstance(sights, sppasSights):
                for j, s in enumerate(sights):
                    if s is None:
                        continue
                    # Create the sppasTag() with (x,y) values
                    tag = sppasTag((s[0], s[1]), tag_type="point")
                    # Create the sppasLabel() with the sppasTag() and its score
                    label = sppasLabel(tag)
                    label.set_key("{:d}_sight{:02d}".format(i, j))
                    # Append to the list of labels of this annotation
                    labels.append(label)

            elif isinstance(sights, list):
                for j, s in enumerate(sights):

                    if isinstance(s, sppasCoords):
                        tag = sppasTag((s.x, s.y, s.w, s.h), tag_type="rect")
                        label = sppasLabel(tag, s.get_confidence())
                        label.set_key("{:d}_{:d}_coords".format(i, j))
                        labels.append(label)

                    elif isinstance(s, sppasSights):
                        for k, sk in enumerate(s):
                            if sk is None:
                                continue
                            # Create the sppasTag() with (x,y) values
                            tag = sppasTag((sk[0], sk[1]), tag_type="point")
                            # Create the sppasLabel() with the sppasTag() and its score
                            label = sppasLabel(tag)
                            label.set_key("{:d}_{:d}_sight{:02d}".format(i, k, j))
                            # Append to the list of labels of this annotation
                            labels.append(label)

                    else:
                        raise TypeError("Expected coords or sights. Got {:s} instead."
                                        "".format(type(sights)))

            else:
                raise TypeError("Expected coords or sights. Got {:s} instead."
                                "".format(type(sights)))

        return labels
