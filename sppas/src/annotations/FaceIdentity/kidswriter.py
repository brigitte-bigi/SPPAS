# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceIdentity.kidswriter.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Write coords and identifiers.

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

import os

from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasCoordsImageWriter
from sppas.src.videodata import sppasCoordsVideoWriter

# ---------------------------------------------------------------------------


class sppasKidsVideoWriter(sppasCoordsVideoWriter):
    """Write a video and optionally coords and ids into files.

    """

    def __init__(self, image_writer=None):
        """Create a new instance.

        """
        super(sppasKidsVideoWriter, self).__init__()

        # Override
        self._img_writer = sppasCoordsImageWriter()
        if image_writer is not None:
            if isinstance(image_writer, sppasCoordsImageWriter) is True:
                self._img_writer = image_writer

        # new member: associate a color to a person
        self.__person_colors = dict()

    # -----------------------------------------------------------------------

    def write_coords(self, fd, video_buffer, buffer_idx, idx):
        """Override to write the coords AND ids into the stream.

        - frame number
        - the identifier
        - timestamp
        - confidence
        - success
        - buffer number
        - index in the buffer
         - x, y, w, h,

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param video_buffer: (sppasCoordsVideoBuffer)
        :param buffer_idx: (int) Buffer number
        :param idx: (int) An integer to write

        """
        sep = self._img_writer.get_csv_sep()

        # Get the lists stored for the i-th image
        coords = video_buffer.get_coordinates(idx)
        ids = video_buffer.get_ids(idx)
        # frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx
        begin_idx, end_idx = video_buffer.get_buffer_range()
        frame_idx = begin_idx + idx

        # Write the coords & ids
        if len(coords) == 0:
            # no coords were assigned to this image
            # the same as base class, except for the identifier: none
            fd.write("{:d}{:s}".format(frame_idx + 1, sep))
            fd.write("none{:s}".format(sep))
            fd.write("{:.3f}{:s}".format(float(frame_idx) / self._fps, sep))
            fd.write("none{:s}".format(sep))
            fd.write("0{:s}".format(sep))
            fd.write("0{:s}0{:s}0{:s}0{:s}".format(sep, sep, sep, sep))
            fd.write("{:d}{:s}".format(buffer_idx + 1, sep))
            fd.write("{:d}{:s}".format(idx, sep))
            fd.write("\n")

        else:
            # write each coord & id in a new line
            for j in range(len(coords)):
                fd.write("{:d}{:s}".format(frame_idx + 1, sep))
                if j < len(ids):
                    fd.write("{}{:s}".format(ids[j], sep))
                else:
                    fd.write("{:d}{:s}".format(j + 1, sep))
                fd.write("{:.3f}{:s}".format(float(frame_idx) / self._fps, sep))
                fd.write("{:f}{:s}".format(coords[j].get_confidence(), sep))
                fd.write("1{:s}".format(sep))
                fd.write("{:d}{:s}".format(coords[j].x, sep))
                fd.write("{:d}{:s}".format(coords[j].y, sep))
                fd.write("{:d}{:s}".format(coords[j].w, sep))
                fd.write("{:d}{:s}".format(coords[j].h, sep))
                fd.write("{:d}{:s}".format(buffer_idx+1, sep))
                fd.write("{:d}{:s}".format(idx, sep))
                fd.write("\n")

    # -----------------------------------------------------------------------

    def write_xra_ann(self, tier, video_buffer, buffer_idx, idx):
        labels = list()
        # Get the list of coordinates stored for the i-th image
        coords = video_buffer.get_coordinates(idx)
        ids = video_buffer.get_ids(idx)
        frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx
        # append each coord in a list of labels
        for i, c in enumerate(coords):
            tag = sppasTag((c.x, c.y, c.w, c.h), tag_type="rect")
            label = sppasLabel(tag, c.get_confidence())
            label.set_key(ids[i])
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
        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            image = next(iter_images)

            if self._video is True:
                # Create the sppasVideoWriter() if it wasn't already done.
                # An image is required to properly fix the video size.
                if self._video_writer is None:
                    self._video_writer, fn = self.create_video_writer(out_name, image, "")
                    new_files.append(fn)
                # Write the image, as it
                self._video_writer.write(image)

            if self._img_writer.options.tag is True:

                # Get the list of coords & ids stored for the i-th image
                coords = video_buffer.get_coordinates(i)
                ids = video_buffer.get_ids(i)
                colors = self._get_ids_colors(ids)

                # Create the sppasVideoWriter() if it wasn't already done.
                # An image is required to properly fix the video size.
                if self._tag_video_writer is None:
                    if len(pattern) == 0:
                        pattern = "tag"
                    self._tag_video_writer, fn = self.create_video_writer(out_name, image, pattern)
                    new_files.append(fn)

                # Tag&write the image with squares at the coords,
                # and a rectangle with the id
                if image is not None:
                    img = self._img_writer.tag_image(image, coords, colors)
                    self._text_image(img, coords, ids, colors)
                    self._tag_video_writer.write(img)
                else:
                    self._tag_video_writer.write(image)

        return new_files

    # -----------------------------------------------------------------------

    def _get_ids_colors(self, ids):
        """Return the colors corresponding to the given list of ids."""
        all_colors = self._img_writer.get_colors()
        colors = list()
        for pid in ids:
            if pid not in self.__person_colors:
                # get a new color
                idx = len(self.__person_colors)
                n = len(all_colors['r'])
                # Get the idx-th color
                r = all_colors['r'][idx % n]
                g = all_colors['g'][idx % n]
                b = all_colors['b'][idx % n]
                rgb = (r, g, b)
                self.__person_colors[pid] = rgb
            # append the color for this id
            colors.append(self.__person_colors[pid])

        return colors

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
        ids = video_buffer.get_ids(idx)
        colors = self._get_ids_colors(ids)

        # Draw the coords & ids on a copy of the original image
        img = self._img_writer.tag_image(image, coords)
        self._text_image(img, coords, ids, colors)

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

                # each identifier has its own folder
                id_folder = os.path.join(os.path.dirname(folder), ids[j])
                if os.path.exists(id_folder) is False:
                    os.mkdir(id_folder)

                # Create the image filename, starting by the id
                iname = str(ids[j]) + "_" + img_name + "_" + str(j) + pattern + self._image_ext
                out_iname = os.path.join(id_folder, iname)

                # Crop the given image to the coordinates and
                # resize only if the option width or height is enabled
                img_crop = self._img_writer.crop_and_size_image(image, c)

                # Add the image to the folder
                img_crop.write(out_iname)
                new_files.append(out_iname)

        return new_files
