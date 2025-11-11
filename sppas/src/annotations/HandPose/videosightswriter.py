# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.HandPose.sightswriter.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Writer for a list of sights in a buffer.

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
import logging

from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.videodata import sppasCoordsVideoWriter

from .imgsightswriter import sppasHandsSightsImageWriter

# ---------------------------------------------------------------------------


class sppasSightsVideoWriter(sppasCoordsVideoWriter):
    """Write a video and optionally sights into files.

    Compared to the base class, here the "coords" are sights!

    """

    def __init__(self, image_writer=None):
        """Create a new instance.

        """
        super(sppasSightsVideoWriter, self).__init__()

        # Override
        self._img_writer = sppasHandsSightsImageWriter()
        if image_writer is not None:
            if isinstance(image_writer, sppasHandsSightsImageWriter) is True:
                self._img_writer = image_writer

    # -----------------------------------------------------------------------

    def write_coords(self, fd, video_buffer, buffer_idx, idx):
        """Override to write the sights into the stream instead of coords.

        - frame number
        - hand_number
        - timestamp
        - success
        - buffer number
        - index in the buffer
        - the nb of sights:
        - the nb x values
        - the nb y values
        - eventually, the nb confidence scores

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param video_buffer: (sppasSightsVideoBuffer)
        :param buffer_idx: (int) Buffer number
        :param idx: (int) An integer to write

        """
        sep = self._img_writer.get_csv_sep()

        # Get the lists stored for the i-th image
        hands = video_buffer.get_sights(idx)
        frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx

        # Write the sights
        if len(hands) == 0:
            # the same as base class
            fd.write("{:d}{:s}".format(frame_idx + 1, sep))
            fd.write("none{:s}".format(sep))
            fd.write("{:.3f}{:s}".format(float(frame_idx) / self._fps, sep))
            fd.write("0{:s}".format(sep))
            fd.write("{:d}{:s}".format(buffer_idx + 1, sep))
            fd.write("{:d}{:s}".format(idx, sep))
            fd.write("\n")

        else:
            for j in range(len(hands)):
                fd.write("{:d}{:s}".format(frame_idx + 1, sep))
                fd.write("{}{:s}".format(j+1, sep))
                fd.write("{:.3f}{:s}".format(float(frame_idx) / self._fps, sep))
                fd.write("1{:s}".format(sep))
                fd.write("{:d}{:s}".format(buffer_idx+1, sep))
                fd.write("{:d}{:s}".format(idx, sep))

                # number of sights
                fd.write("{:d}{:s}".format(len(hands[j]), sep))

                # write all x values
                for x in hands[j].get_x():
                    fd.write("{:d}{:s}".format(x, sep))

                # write all y values
                for y in hands[j].get_y():
                    fd.write("{:d}{:s}".format(y, sep))

                # write all z values
                if hands[j].get_z() is not None:
                    for y in hands[j].get_z():
                        fd.write("{:d}{:s}".format(y, sep))
                fd.write("\n")

    # -----------------------------------------------------------------------

    def write_xra_ann(self, tier, video_buffer, buffer_idx, idx):
        labels = list()
        # Get the list of coordinates stored for the i-th image
        hands = video_buffer.get_sights(idx)
        frame_idx = (buffer_idx * video_buffer.get_buffer_size()) + idx
        # append each coord in a list of labels
        for i in range(len(hands)):
            for j, s in enumerate(hands[i]):
                x, y, z, score = s
                tag = sppasTag((x, y), tag_type="point")
                label = sppasLabel(tag, score)
                label.set_key("{:02d}_sight{:02d}".format(i, j))
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

        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            image = next(iter_images)
            b, _ = video_buffer.get_buffer_range()

            # Get the list of sights stored for the i-th image
            hands = video_buffer.get_sights(i)

            # Create the sppasVideoWriter() if it wasn't already done.
            # An image is required to properly fix the video size.
            if self._tag_video_writer is None:
                self._tag_video_writer, fn = self.create_video_writer(out_name, image, pattern)
                new_files.append(fn)

            # Tag&write the image with circles for sights
            if image is not None:
                img = self._img_writer.tag_image(image, hands)
                self._tag_video_writer.write(img)
            else:
                self._tag_video_writer.write(image)

        return new_files

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

        return new_files
