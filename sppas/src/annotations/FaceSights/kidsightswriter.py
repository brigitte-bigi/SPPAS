# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.kidsightswriter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Writer for the 68 sights of faces of a video.

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

import os
import logging

from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.videodata import sppasCoordsVideoWriter
from sppas.src.imgdata import sppasCoords

from .imgsightswriter import sppasFaceSightsImageWriter

# ---------------------------------------------------------------------------


class sppasKidsSightsVideoWriter(sppasCoordsVideoWriter):
    """Write a video and optionally coords/sights into files.

    """

    def __init__(self, image_writer=None):
        """Create a new instance.

        """
        super(sppasKidsSightsVideoWriter, self).__init__()

        # Override
        self._img_writer = sppasFaceSightsImageWriter()
        if image_writer is not None:
            if isinstance(image_writer, sppasFaceSightsImageWriter) is True:
                self._img_writer = image_writer

        # new member: associate a color to a person
        self.__person_colors = dict()

    # -----------------------------------------------------------------------

    def write_coords(self, fd, video_buffer, buffer_idx, idx):
        """Override to write the sights AND ids into the stream.

        - frame number
        - face_id
        - timestamp (of the middle of the frame)
        - success
        - buffer number
        - index in the buffer
        - the nb of sights: 68
        - the 68 x values
        - the 68 y values
        - eventually, the 68 confidence scores

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param video_buffer: (sppasCoordsVideoBuffer)
        :param buffer_idx: (int) Buffer number
        :param idx: (int) An integer to write

        """
        sep = self._img_writer.get_csv_sep()

        # Get the lists stored for the i-th image
        sights = video_buffer.get_sights(idx)
        ids = video_buffer.get_ids(idx)
        frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx
        radius = 0.5 / self._fps

        # Write the sights
        if len(ids) == 0:
            # the same as base class
            fd.write("{:d}{:s}".format(frame_idx + 1, sep))
            fd.write("none{:s}".format(sep))
            fd.write("{:.3f}{:s}".format(radius + (float(frame_idx) / self._fps), sep))
            fd.write("0{:s}".format(sep))
            fd.write("{:d}{:s}".format(buffer_idx + 1, sep))
            fd.write("{:d}{:s}".format(idx, sep))
            fd.write("\n")

        else:
            for j in range(len(ids)):
                fd.write("{:d}{:s}".format(frame_idx + 1, sep))
                fd.write("{}{:s}".format(ids[j], sep))
                fd.write("{:.3f}{:s}".format(radius + (float(frame_idx) / self._fps), sep))
                fd.write("1{:s}".format(sep))
                fd.write("{:d}{:s}".format(buffer_idx+1, sep))
                fd.write("{:d}{:s}".format(idx, sep))
                if j < len(sights):
                    self._img_writer.write_coords(fd, sights[j], write_success=False)
                fd.write("\n")

    # -----------------------------------------------------------------------

    def write_xra_ann(self, tier, video_buffer, buffer_idx, idx):
        labels = list()
        # Get the list of coordinates stored for the i-th image
        sights = video_buffer.get_sights(idx)
        ids = video_buffer.get_ids(idx)
        frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx
        # append each coord in a list of labels
        for i in range(len(ids)):
            if sights[i] is None:
                continue
            for j, s in enumerate(sights[i]):
                x, y, z, score = s
                tag = sppasTag((x, y), tag_type="point")
                label = sppasLabel(tag, score)
                label.set_key(ids[i] + "_sight{:02d}".format(j))
                labels.append(label)
        # create a localization from the frame_idx
        radius = 0.5 / float(self._fps)
        mid_time = (float(frame_idx) / float(self._fps)) + radius
        frame_point = sppasPoint(mid_time, radius)
        # Add the annotation, even if there's no labels:
        # allows a full match between frames and annotations indexes.
        ann = tier.create_annotation(sppasLocation(frame_point), labels)
        ann.set_meta("frame_index", str(frame_idx))
        return ann

    # -----------------------------------------------------------------------

    def write_video(self, video_buffer, out_name, pattern):
        """Save the result in video format.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The filename of the output video file
        :param pattern: (str) Pattern to add to cropped video filename(s)
        :return: list of newly created video file names

        """
        new_files = list()
        if self._img_writer.options.tag is False:
            logging.info("Tag option is not enabled. Nothing to do.")
            return new_files

        all_colors = self._img_writer.get_colors()
        iter_images = video_buffer.__iter__()
        image = None
        for i in range(video_buffer.__len__()):
            tmp = image
            image = next(iter_images)
            if image is None:
                # Replace a "None" image by the previous one
                image = tmp
            b, _ = video_buffer.get_buffer_range()

            # Get the list of sights stored for the i-th image
            sights = video_buffer.get_sights(i)
            coords = video_buffer.get_coordinates(i)
            person_ids = video_buffer.get_ids(i)

            # Create the sppasVideoWriter() if it wasn't already done.
            # An image is required to properly fix the video size.
            if self._tag_video_writer is None:
                self._tag_video_writer, fn = self.create_video_writer(out_name, image, pattern)
                new_files.append(fn)

            # fix the colors of these coords and sights
            colors = list()
            for person_id in person_ids:
                if person_id not in self.__person_colors:
                    # get a new color
                    idx = len(self.__person_colors)
                    n = len(all_colors['r'])
                    # Get the idx-th color
                    r = all_colors['r'][idx % n]
                    g = all_colors['g'][idx % n]
                    b = all_colors['b'][idx % n]
                    rgb = (r, g, b)
                    self.__person_colors[person_id] = rgb
                # append the color for this person
                colors.append(self.__person_colors[person_id])

            # Tag&write the image with squares at the coords,
            # with circled for sights and a rectangle with the name
            if image is not None:
                img = self._img_writer.tag_image(image, coords, colors)
                for x, s in enumerate(sights):
                    img = self._img_writer.tag_image(img, s, [colors[x]])
                self._text_image(img, coords, person_ids, colors)
                self._tag_video_writer.write(img)

        return new_files

    # -----------------------------------------------------------------------

    def _text_image(self, img, coords, texts, colors):
        """Put texts at top of given coords with given colors."""
        for coord, text, color in zip(coords, texts, colors):
            c = sppasCoords(coord.x, coord.y, coord.w, coord.h // 5)
            img.surround_coord(c, color, -4, text)

    # -----------------------------------------------------------------------

    def _tag_and_crop(self, video_buffer, image, idx, img_name, folder, pattern):

        new_files = list()
        # Get the list of coordinates stored for the i-th image
        coords = video_buffer.get_coordinates(idx)
        sights = video_buffer.get_sights(idx)

        # Draw the sights on a copy of the original image
        img = self._img_writer.tag_image(image, sights)

        # Tag and write the image
        if self._img_writer.options.tag is True:
            # Save the image
            out_iname = os.path.join(folder, img_name + self._image_ext)
            img.write(out_iname)
            new_files.append(out_iname)

        # Crop the image and write cropped parts
        if self._img_writer.options.crop is True:
            # Browse through the coords to crop the image
            for j, c in enumerate(coords):

                # Create the image filename
                iname = img_name + "_" + str(j) + pattern + self._image_ext
                out_iname = os.path.join(folder, iname)

                # Crop the given image to the coordinates and
                # resize only if the option width or height is enabled
                img_crop = self._img_writer.crop_and_size_image(img, c)

                # Add the image to the folder
                img_crop.write(out_iname)
                new_files.append(out_iname)

        return new_files
