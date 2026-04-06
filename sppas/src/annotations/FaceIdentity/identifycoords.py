# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceIdentity.identifycoords.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Cluster and identify the sets of coords of a video.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    -------------------------------------------------------------------------

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

    -------------------------------------------------------------------------

"""

import logging
import collections
import os

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import IntervalRangeException
from sppas.src.calculus import symbols_to_items
from sppas.src.calculus import tansey_linear_regression
from sppas.src.calculus import linear_fct
from sppas.src.calculus import fmean
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasCoordsCompare
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImagesSimilarity
from sppas.src.videodata import sppasCoordsVideoReader
from sppas.src.videodata import sppasVideoWriter

from .kidsbuffer import sppasKidsVideoBuffer
from .kidswriter import sppasKidsVideoWriter

# ---------------------------------------------------------------------------

MSG_ERROR_MISMATCH = "The given {:d} coordinates in coords file doesn't match " \
                     "the number of frames of the video {:d}"

# ---------------------------------------------------------------------------


class VideoCoordsIdentification(object):
    """Set an identity to the coordinates detected in a video.

    Glossary: KID = Known Identity.

    System 1st pass: Create the set of known identities

        * 1st pass - Step 1: fix a set of candidates

    -> if the confidence of the face coordinates has a high enough value, the
       face is supposed relevant to be a candidate: minconf > 0.9
    -> the face is a new candidate if its coordinates are not matching another
       already known candidate. score_compare_coords > 0.4
    -> the image of the face is stored into the set of reference images if
       the candidate has not enough images already and if the score > 0.6.

        * 1st pass - Step 2: filter the set of candidates

    -> estimate a distance between the candidates and remove the duplicated
       ones. The distance is comparing the stored coords of a reference face
       and a stored reference image. Two candidates are considered the same if
       dist_coords > 0.1 OR dist_images > 0.8.

    System 2nd pass: assign each face coordinate an identity or remove it.

    -> Train a face recognizer from the selected known identities
    -> Assign an identity to all face coordinates: compare coords with the known
       ones but if none of them is matching, use the recognizer to identify the face.
       It results in an identity assignment to each detected face or not if
       the face is not matching a kid.
    -> Remove un-relevant isolated detected coords and fill in holes of
       relevant missing ones.
    -> Use rules to remove un-relevant detected face kids (rare and/or scattered)
    -> Remove the un-identified coords in each image of the buffer

    System 3rd pass: Smooth coordinates and save into files

    """

    NUMBER_OF_FACE_KID_IMAGES = 20

    # Threshold values
    MIN_FACE_DETECTION_CONFIDENCE = 0.9
    MIN_MATCHING_COMPARE_COORDS = 0.4
    MIN_ADDREF_COMPARE_COORDS = 0.6
    MIN_DISTANCE_KIDS_COORDS = 0.1
    MIN_DISTANCE_KIDS_IMAGES = 0.8

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a new instance.

        """
        # Video stream with a buffer of images and the lists of coordinates
        self._video_buffer = sppasKidsVideoBuffer()

        # Kids data & similarity measures: identifier, images, coords...
        self.__kidsim = sppasImagesSimilarity()

        # Number of images in the ImagesFIFO() to train the recognition system
        self.__nb_fr_img = VideoCoordsIdentification.NUMBER_OF_FACE_KID_IMAGES

        # Threshold values
        self.__min_face_score = VideoCoordsIdentification.MIN_FACE_DETECTION_CONFIDENCE
        self.__min_coords = VideoCoordsIdentification.MIN_MATCHING_COMPARE_COORDS
        self.__min_ref_coords = VideoCoordsIdentification.MIN_ADDREF_COMPARE_COORDS
        self.__min_dist_coords = VideoCoordsIdentification.MIN_DISTANCE_KIDS_COORDS
        self.__min_dist_imgs = VideoCoordsIdentification.MIN_DISTANCE_KIDS_IMAGES
        
        # Export a video file for each identified person
        self._out_ident = True   # export portrait of each identified person
        self._selfi = True       # selfie instead of portrait
        self._shift = 0          # use -x to shift left and +x to shift right

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_out_ident(self, value):
        """Export a video of the portrait and csv/xra file for each identified person."""
        self._out_ident = bool(value)

    def set_out_selfi(self, value):
        """Export a selfie video instead of a portrait of each identified person."""
        self._selfi = bool(value)

    def set_out_shift(self, value):
        """Export a shifted selfie or portrait video of each identified person.

        :param value: (int) Negative to shift left, 0 to center, Positive to shift right

        """
        value = int(value)
        if -100 < value < 100:
            self._shift = value
        else:
            raise sppasError("Cant shift more than 100%")

    # -----------------------------------------------------------------------

    def set_nb_images_recognizer(self, value):
        """Number of images to store to train a recognizer of a kid.

        Default value is 20. Value must range (0; 100).

        :param value: (int) Number of image to represent a kid

        """
        value = int(value)
        if value < 0 or value > 100:
            raise IntervalRangeException(value, 0, 100)
        self.__nb_fr_img = value

    # -----------------------------------------------------------------------

    def set_face_min_confidence(self, value):
        """Fix the minimum confidence score to propose a coord as candidate.

        Default value is 0.9. Value must range (0.; 1.).

        :param value: (float) threshold for the confidence score of coords

        """
        value = float(value)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_face_score = value

    # -----------------------------------------------------------------------

    def set_compare_coords_min_threshold(self, value):
        """Fix the minimum comparison score to select a coord as candidate.

        :param value: (float) threshold for the comparison score of coords

        """
        value = float(value)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_coords = value

    # -----------------------------------------------------------------------

    def set_compare_coords_ref_min_threshold(self, value):
        """Fix the minimum comparison score to add a coord as reference.

        :param value: (float) threshold for the comparison score of coords

        """
        value = float(value)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_ref_coords = value

    # -----------------------------------------------------------------------

    def set_coords_min_dist(self, value):
        """Fix the minimum distance of coords between 2 candidate kids.

        :param value: (float) threshold for the distance of coords

        """
        value = float(value)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_dist_coords = value

    # -----------------------------------------------------------------------

    def set_images_min_dist(self, value):
        """Fix the minimum distance of images between 2 candidate kids.

        :param value: (float) threshold for the distance of images

        """
        value = float(value)
        if value < 0. or value > 1.:
            raise IntervalRangeException(value, 0., 1.)
        self.__min_dist_imgs = value

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate the list of all known identifiers."""
        self.__kidsim = sppasImagesSimilarity()

    # -----------------------------------------------------------------------
    # Assign an identity to detected coordinates
    # -----------------------------------------------------------------------

    def video_identity(self, video, coords_filename, video_writer=None, output=None, pattern="-ident"):
        """Browse the video, get coords then cluster, identify and write results.

        :param video: (str) Video filename
        :param coords_filename: (str) Filename with the coords (CSV or XRA)
        :param video_writer: (sppasKidsVideoWriter)
        :param output: (str) The output name for the folder
        :param pattern: (str) Optional output pattern

        :return: (list)

        """
        self.invalidate()
        # Open the video stream
        self._video_buffer.open(video)
        if video_writer is not None:
            video_writer.set_fps(self._video_buffer.get_framerate())

        # Load the coordinates from the CSV or XRA file
        br = sppasCoordsVideoReader(coords_filename)
        coords = br.coords
        nframes = self._video_buffer.get_nframes()
        if len(coords) != nframes:
            # Release the video stream
            self._video_buffer.close()
            self._video_buffer.reset()
            raise sppasError(MSG_ERROR_MISMATCH.format(len(coords), nframes))

        # Cluster coords into kids and remove duplicated kids
        self.__first_pass_clustering(coords)
        if output is not None:
            # write the stored images of each kid in the output folder
            self.__kidsim.write(output)

        # Associate each coord to a kid or remove it if no kid matches
        self.__kidsim.train_recognizer()
        coords, idents = self.__second_pass_identification(coords)

        # Smooth coordinates and save into files
        # result is the list of created file names
        result = self.__third_pass_smoothing(coords, idents, video_writer, output, pattern)

        # Release the video stream
        self._video_buffer.close()
        self._video_buffer.reset()

        if output is not None and video_writer is not None:
            return result

        return self.__kidsim.get_known_identifiers()

    # -----------------------------------------------------------------------

    def __first_pass_clustering(self, coords):
        """Create the kids in the whole video.

        :param coords: (list of list of sppasCoords)

        """
        logging.info("System 1st pass: Create the set of known identities.")

        # Browse the images of the buffers to fix a list of candidates
        read_next = True
        i = 0
        nb = 0
        self._video_buffer.seek_buffer(0)
        while read_next is True:
            # fill-in the buffer with 'size'-images of the video
            logging.info(" ... buffer number {:d}".format(nb+1))
            read_next = self._video_buffer.next()

            # fill-in the buffer with coords
            for buf_idx, image in enumerate(self._video_buffer):
                all_idx_coords = coords[i+buf_idx]
                self._video_buffer.set_coordinates(buf_idx, all_idx_coords)

            # cluster the coords to set the identities
            self.__cluster_buffer()

            nb += 1
            i += len(self._video_buffer)
        logging.info(" ... {:d} identity candidates were found.".format(len(self.__kidsim)))

        # Estimate distances among candidates in order to cluster them
        self.__filter_distance_kids()

        # Check if there are enough relevant images of each kid
        # We must have enough images to train a recognizer at the next step
        remove_ids = list()
        for kid in self.__kidsim:
            nb = self.__kidsim.get_nb_images(kid)
            if (nb*3) < VideoCoordsIdentification.NUMBER_OF_FACE_KID_IMAGES:
                remove_ids.append(kid)
                logging.info(" ... identity {:s} is removed because it doesn't "
                             "have enough reference images: {:d}.".format(kid, nb))
        for pid in remove_ids:
            self.__kidsim.remove_identifier(pid)

        logging.info(" ... Know identities are: {:s}".format(str([kid for kid in self.__kidsim])))

    # -----------------------------------------------------------------------

    def __filter_distance_kids(self):
        """Verify if all kids are different ones and remove duplicated.
        
        """
        # the list of already estimated distances (do not eval it twice!)
        dist = list()
        # the list of ids to be removed because they are duplicated
        remove_ids = list()
        # compare all kids, two by two
        for pid1 in self.__kidsim:
            for pid2 in self.__kidsim:
                # Do not compare the same pid twice
                if pid1 == pid2 or (pid1, pid2) in dist or (pid2, pid1) in dist:
                    continue
                # Do not compare the already compared ones
                if (pid1, pid2) in dist or (pid2, pid1) in dist:
                    continue
                # Do not compare if one pid is already removed
                if pid1 in remove_ids or pid2 in remove_ids:
                    continue

                # we'll compare 2 different kids not already compared
                dist.append((pid1, pid2))
                # then... search for similarities between the 2 kids
                score_coords = self.__kidsim.compare_kids_coords(pid1, pid2)
                score_refs = self.__kidsim.compare_kids_images(pid1, pid2)

                # The coordinates are overlapping or the images are close enough
                if score_coords > self.__min_dist_coords or score_refs > self.__min_dist_imgs:
                    # keep the one with the higher number of images
                    nb1 = self.__kidsim.get_nb_images(pid1)
                    nb2 = self.__kidsim.get_nb_images(pid2)
                    if nb1 >= nb2 and pid2 not in remove_ids:
                        remove_ids.append(pid2)
                        logging.info(" ... identity {:s} is removed because "
                                     "duplicated with {:s}. Scores = {} and {}."
                                     "".format(pid2, pid1, score_coords, score_refs))
                    if nb2 > nb1 and pid1 not in remove_ids:
                        remove_ids.append(pid1)
                        logging.info(" ... identity {:s} is removed because "
                                     "duplicated with {:s}. Scores = {} and {}"
                                     "".format(pid1, pid2, score_coords, score_refs))
                else:
                    logging.debug(" ... identity {:s} is different to {:s}. Scores = {} and {}"
                                  "".format(pid1, pid2, score_coords, score_refs))

        for pid in remove_ids:
            self.__kidsim.remove_identifier(pid)

    # -----------------------------------------------------------------------

    def __second_pass_identification(self, coords):
        """Set an identity to the coords in the whole video.

        :param coords: (list of list of sppasCoords)
        :param video_writer: (sppasKidsVideoWriter)
        :param output: (str) The output name for the folder

        """
        logging.info("System 2nd pass: assign each coordinate an identity or remove it.")

        # Browse the video using the buffer of images
        read_next = True
        idents = list()
        revised_coords = list()
        i = 0
        nb = 0
        self._video_buffer.seek_buffer(0)
        while read_next is True:
            # fill-in the buffer with 'size'-images of the video
            logging.info(" ... buffer number {:d}".format(nb+1))
            read_next = self._video_buffer.next()

            # fill-in the buffer with coords
            for buf_idx, image in enumerate(self._video_buffer):
                self._video_buffer.set_coordinates(buf_idx, coords[i + buf_idx])

            # set identity to coords of the buffer
            self.__identify_buffer()
            for buf_idx, image in enumerate(self._video_buffer):
                all_coords = self._video_buffer.get_coordinates(buf_idx)
                all_ids = self._video_buffer.get_ids(buf_idx)
                idents.append(all_ids)
                revised_coords.append(all_coords)

            nb += 1
            i += len(self._video_buffer)

        assert len(coords) == len(revised_coords)
        return revised_coords, idents

    # -----------------------------------------------------------------------

    def __third_pass_smoothing(self, coords, idents, video_writer, output, pattern):
        """Smooth and save coords of the persons in the whole video."""
        logging.info("System 3rd pass: Smooth and save the identified persons")

        read_next = True    # reached the end of the video or not
        i = 0               # index of the first image of each buffer
        nb = 0              # buffer number
        result = list()

        self._video_buffer.seek_buffer(0)
        self._video_buffer.set_buffer_size(3 * int(self._video_buffer.get_framerate()))
        kids_video_writers, kids_video_buffers = self.create_kids_writers_buffers(video_writer)

        previous_buffer = sppasKidsVideoBuffer(size=self._video_buffer.get_buffer_size()-1)
        prev_start = self._video_buffer.get_buffer_size() - previous_buffer.get_buffer_size()
        prev_end = self._video_buffer.get_buffer_size()
        copied_buffer = sppasKidsVideoBuffer(size=self._video_buffer.get_buffer_size())

        while read_next is True:
            # fill-in the buffer with 'size'-images of the video
            if nb % 10 == 0:
                logging.info(" ... buffer number {:d}".format(nb + 1))

            # fill-in the buffer with images, coords and ids
            read_next = self._video_buffer.next()
            for buf_idx, image in enumerate(self._video_buffer):
                self._video_buffer.set_coordinates(buf_idx, coords[i + buf_idx])
                self._video_buffer.set_ids(buf_idx, idents[i + buf_idx])

            # Create a copy of the buffer with the detected kids.
            # The images are not required.
            for img_idx in range(self._video_buffer.get_buffer_size()):
                copied_buffer.set_coordinates(img_idx, self._video_buffer.get_coordinates(img_idx).copy())
                copied_buffer.set_ids(img_idx, self._video_buffer.get_ids(img_idx).copy())

            # Smooth face kid coordinates of the buffer
            self.__smooth_buffer(previous_buffer)

            # save the current results: created file names
            if output is not None:
                if video_writer is not None:
                    # Write each kid individually: a few holes will be filled in
                    if self._out_ident is True:
                        for kid in self.__kidsim:
                            new_files = self.__export_kid(output, pattern, kid, kids_video_buffers[kid], kids_video_writers[kid])
                            result.extend(new_files)
                    # Write all-in-ones
                    new_files = video_writer.write(self._video_buffer, output, pattern)
                    result.extend(new_files)

            nb += 1
            i += len(self._video_buffer)

            # Fill-in the previous buffer with the detected kids.
            # The images are not required.
            p = 0
            for img_idx in range(prev_start, prev_end):
                previous_buffer.set_coordinates(p, copied_buffer.get_coordinates(img_idx).copy())
                previous_buffer.set_ids(p, copied_buffer.get_ids(img_idx).copy())
                p = p + 1

        # really write the XRA files (if xra option enabled)
        for kid in self.__kidsim:
            kids_video_writers[kid].close()
        return result

    # -----------------------------------------------------------------------

    def __coords_to_portrait(self, coords, image):
        """Return a list of coordinates to their portrait size."""
        portraits = list()
        # Adjust coordinates of each face
        for coord in coords:

            # Estimate the coordinates in the portrait/selfie size
            if self._selfi is True:
                c = coord.portrait(image, scale=(4.6, 5.))
            else:
                c = coord.portrait(image)

            # Shift at left or right
            if self._shift != 0:
                shift_value = c.x * self._shift // 100
                c.shift(x_value=shift_value, y_value=0, image=image)

            portraits.append(c)
        return portraits

    # -----------------------------------------------------------------------

    def __cluster_buffer(self):
        """Search for kids among the given coords: system 1st pass.
        
        """
        self.__kidsim.set_score_level(self.__min_coords)

        # Browse the buffer to search for new identifiers.
        for i in range(len(self._video_buffer)):
            image = self._video_buffer[i]
            coords_i = self._video_buffer.get_coordinates(i)

            for f, c in enumerate(coords_i):
                # The coord has a high enough confidence -- so supposed relevant 
                if c.get_confidence() > self.__min_face_score:
                    # Already an identified kid or a new one?
                    # Try to identify the kid with the coordinates
                    identity_c, score_c = self.__kidsim.identify(image=None, coords=c)
                    if identity_c is None:
                        # The coords are not matching a kid. So, this is probably a new one.
                        kid = self.__create_kid(i, f)
                    else:
                        # The coords are matching a kid.
                        if score_c > self.__min_ref_coords and self.__kidsim.get_nb_images(identity_c) < self.__nb_fr_img:
                            cropped_img = image.icrop(c)
                            self.__kidsim.add_image(identity_c, cropped_img, reference=False)
                        # update coords to follow when the kid is moving
                        self.__kidsim.set_cur_coords(identity_c, c)

    # -----------------------------------------------------------------------

    def __identify_buffer(self):
        """Set an identifier to coords and apply filters: system 2nd pass.

        """
        # Assign an identity to coordinates
        self._set_identity_by_similarity()

        # Remove un-relevant isolates detected coords and
        # fill in holes of relevant missing ones
        for kid in self.__kidsim:
            self._dissociate_or_fill_isolated(kid)

        # Use rules to remove un-relevant detected kids
        self._dissociate_rare_and_scattered()

        # Remove the un-identified coords in each image of the buffer
        for i in range(len(self._video_buffer)):
            # Get detected identifiers in this image
            all_ids = self._video_buffer.get_ids(i)
            c = len(all_ids) - 1
            for kid in reversed(all_ids):
                if kid.startswith("unk"):
                    self._video_buffer.pop_coordinate(i, c)
                c -= 1

    # -----------------------------------------------------------------------

    def __smooth_buffer(self, previous_buffer):
        """Smooth the coords of detected persons.

        :param previous_buffer: (sppasKidsVideoBuffer) The previous buffer

        """
        for kid_id in self.__kidsim:
            # create the list of points with all known coordinates of the kid in the previous buffer
            px = list()
            py = list()
            pw = list()
            ph = list()
            for pimg_idx in range(previous_buffer.get_buffer_size()):
                all_coords = previous_buffer.get_coordinates(pimg_idx)
                all_ids = previous_buffer.get_ids(pimg_idx)
                if kid_id in all_ids:
                    kid_idx = all_ids.index(kid_id)
                    c = all_coords[kid_idx]
                    if c is not None:
                        px.append(c.x)
                        py.append(c.y)
                        pw.append(c.w)
                        ph.append(c.h)

            # linear regression to fix the equation of the line representing
            # as close as possible the (x,y) coords of the kid.
            # Set the new coords to the kid
            for img_idx in range(len(self._video_buffer)):
                all_coords = self._video_buffer.get_coordinates(img_idx)
                all_ids = self._video_buffer.get_ids(img_idx)
                if kid_id in all_ids:
                    kid_idx = all_ids.index(kid_id)
                    c = all_coords[kid_idx]
                    if c is not None:
                        px.append(c.x)
                        py.append(c.y)
                        pw.append(c.w)
                        ph.append(c.h)
                        if len(px) > previous_buffer.get_buffer_size():
                            px.pop(0)
                            py.pop(0)
                            pw.pop(0)
                            ph.pop(0)

                if len(px) > 2:
                    ppx = list()
                    ppy = list()
                    for pi in range(len(px)):
                        ppx.append((pi, px[pi]))
                        ppy.append((pi, py[pi]))
                    bx, ax = tansey_linear_regression(ppx)
                    by, ay = tansey_linear_regression(ppy)
                    idx = len(px) - 1
                    x = int(linear_fct(idx, ax, bx))
                    y = int(linear_fct(idx, ay, by))
                    w = fmean(pw)
                    h = fmean(ph)

                    if kid_id in all_ids:
                        kid_idx = all_ids.index(kid_id)
                        c = all_coords[kid_idx]
                        if c is not None:
                            c.x = max(0, x)
                            c.y = max(0, y)
                            c.w = max(0, w)
                            c.h = max(0, h)

                    else:
                        # The kid does not have coordinates for this image, so
                        # the linearly estimated one are set.
                        c = sppasCoords(max(0, x), max(0, y), max(0, w), max(0, h), 0.)
                        ci = self._video_buffer.append_coordinate(img_idx, c)
                        self._video_buffer.set_id(img_idx, ci, kid_id)
                        logging.debug("Added coords {} for {} at {}".format(c, kid_id, img_idx))

    # -----------------------------------------------------------------------

    def __export_kid(self, output, pattern, kid, kid_buffer, kid_writer):
        """Export the buffer into video/csv of each kid.

        Fill in some holes of the kid.

        """
        w = kid_writer.get_output_width()
        h = kid_writer.get_output_height()

        kid_buffer.reset_with_start_idx(self._video_buffer.get_buffer_range()[0])
        kid_last_coords = None
        kid_last_portrait = None
        # Fill in the kids buffer with the cropped images
        for img_idx in range(len(self._video_buffer)):
            image = self._video_buffer[img_idx]
            all_coords = self._video_buffer.get_coordinates(img_idx)
            portraits = self.__coords_to_portrait(all_coords, image)
            all_ids = self._video_buffer.get_ids(img_idx)
            # set the coords/portrait of the kid in this image
            if kid in all_ids:
                kid_idx = all_ids.index(kid)
                kid_last_portrait = portraits[kid_idx]
                kid_last_coords = all_coords[kid_idx].copy()
            elif kid_last_portrait is not None:
                # The kid is not detected in this image.
                # we'll back-up on its last detected coordinates...
                logging.debug("Added coords {} for id {}".format(kid_last_portrait, kid))
                cidx = self._video_buffer.append_coordinate(img_idx, kid_last_coords)
                self._video_buffer.set_id(img_idx, cidx, kid)
                kid_last_coords.set_confidence(0.)

            # extract the image portrait and the coordinates
            if kid_last_portrait is None:
                # The kid is not detected and was not already detected
                kid_buffer.append(sppasImage(0).blank_image(w, h))
                kid_buffer.set_coordinates(img_idx, [])
                kid_buffer.set_ids(img_idx, [])
            else:
                try:
                    kid_img, kid_img_coords = self.__transpose_to_portrait(image, kid_last_coords, kid_last_portrait, w, h)
                except:
                    kid_img = sppasImage(0).blank_image(w, h)
                    kid_img_coords = kid_last_coords
                kid_buffer.append(kid_img)
                kid_buffer.set_coordinates(img_idx, [kid_img_coords])
                kid_buffer.set_ids(img_idx, [kid])

        # Save to video/csv/img files
        pathname = os.path.dirname(output)
        filename = os.path.basename(output) + pattern + kid
        new_files = kid_writer.write(kid_buffer, os.path.join(pathname, filename))

        return new_files

    # -----------------------------------------------------------------------

    def __transpose_to_portrait(self, image, face_coords, portrait_coords, w, h):
        """Return the image portrait and the adjusted coordinates.

        face_coords are the coordinates of the face in the image
        portrait_coords are the coordinates of the portrait in the image

        """
        max_x = image.width
        max_y = image.height
        # step 1. Crop the portrait in the original image
        cropped = image.icrop(portrait_coords)
        # set the face coords in the portrait, no longer in the image
        face_coords.x = max(0, face_coords.x - portrait_coords.x)
        face_coords.y = max(0, face_coords.y - portrait_coords.y)

        # step 2. Extend the image to either w or h in order to keep the aspect ratio
        aspect_ratio = int(100. * float(cropped.width) / float(cropped.height)) / 100.
        res_aspect_ratio = int(100. * float(w) / float(h)) / 100.
        res_w = w
        res_h = h
        if aspect_ratio > res_aspect_ratio:
            coeff = float(w) / float(cropped.width)
            res_h = int(coeff * float(cropped.height))
        else:
            coeff = float(h) / float(cropped.height)
            res_w = int(coeff * float(cropped.width))
        extended = cropped.iresize(res_w, res_h)
        rx = res_w / cropped.width
        ry = res_h / cropped.height
        face_coords.x = min(max_x, int(face_coords.x * rx))
        face_coords.y = min(max_y, int(face_coords.y * ry))
        face_coords.w = min(max_x - face_coords.x, int(face_coords.w * rx))
        face_coords.h = min(max_y - face_coords.y, int(face_coords.h * ry))

        # step3. Center the image in a blank image of size (w, h)
        mask = extended.blank_image(w, h)
        try:
            # Fix the position of the extended image into the mask
            x_pos = (w - extended.width) // 2
            y_pos = (h - extended.height) // 2
            # Replace (BGR) values of the mask by the ones of the image
            mask[y_pos:y_pos + extended.height, x_pos:x_pos + extended.width, :] = extended[:extended.height, :extended.width, :]
            face_coords.x = face_coords.x + x_pos
            face_coords.y = face_coords.y + y_pos
        except ValueError as e:
            logging.error("Can't extract portrait: {:s}".format(str(e)))

        return sppasImage(input_array=mask), face_coords

    # -----------------------------------------------------------------------

    def create_kids_writers_buffers(self, video_writer):
        """Create as many kids writers&buffers as the number of persons.

        The resolution of the kid output video should be an option.
        By default, it is fixed to "SD" (704*528).

        """
        kids_video_writers = dict()
        kids_video_buffers = dict()
        if video_writer is not None:
            w = video_writer.get_output_width()
            h = video_writer.get_output_height()
            if w == 0:
                w = sppasVideoWriter.RESOLUTIONS["SD"][0]
            if h == 0:
                h = sppasVideoWriter.RESOLUTIONS["SD"][1]
            for kid_id in self.__kidsim:
                writer = sppasKidsVideoWriter()
                writer.set_fps(video_writer.get_fps())
                writer.set_image_extension(video_writer.get_image_extension())
                writer.set_video_extension(video_writer.get_video_extension())
                export_csv = video_writer.get_csv_output()
                writer.set_options(csv=export_csv, xra=not export_csv, folder=False, tag=False, crop=False, width=w, height=h)
                writer.set_video_output(True)
                kids_video_writers[kid_id] = writer
                kids_video_buffers[kid_id] = sppasKidsVideoBuffer(size=self._video_buffer.get_buffer_size())
        return kids_video_writers, kids_video_buffers

    # -----------------------------------------------------------------------

    def _dissociate_or_fill_isolated(self, kid):
        """Remove the coordinates of a kid in an isolated image.

        When a kid is detected at an image i-1 but not at both
        image i and image i-2, cancel its link to the coordinates.

        A kid can't appear furtively nor disappear!!!

        """
        here = [False, False, False]

        # For each image of the buffer
        for i in range(len(self._video_buffer)):
            # Get detected identifiers in this image
            all_ids = self._video_buffer.get_ids(i)
            if kid in all_ids:
                # the kid is detected at i and i-2 but wasn't at i-1
                here[2] = True
                if i > 1 and here[0] is True and here[1] is False:
                    # check if there wasn't a detection/identification problem
                    coord_prev = self._video_buffer.get_id_coordinate(i-2, kid)
                    coord_cur = self._video_buffer.get_id_coordinate(i, kid)
                    cc = sppasCoordsCompare(coord_prev, coord_cur)
                    # at i-2 and at i, it's seems it's really the same kid
                    if cc.compare_coords() > 0.5:
                        # add the kid at i-1
                        c = coord_prev.intermediate(coord_cur)
                        nc_idx = self._video_buffer.append_coordinate(i-1, c)
                        # and obviously add the id in the buffer
                        self._video_buffer.set_id(i-1, nc_idx, kid)

            else:
                # the kid is not detected at i, and it wasn't at
                # i-2 but it was at i-1.
                if here[0] is False and here[1] is True:
                    self.__dissociate_kid_coord(i-1, kid)
                    here[1] = False

            # shift for next image
            here[0] = here[1]
            here[1] = here[2]
            here[2] = False

    # -----------------------------------------------------------------------

    def _reduce_population(self, nb_kids):
        """Remove data of the most rarely detected kids in the buffer.

        :param nb_kids: (int) Max number of kids to be detected

        """
        # check if there is something to do
        how_many = len(self.__kidsim) - nb_kids
        if how_many <= 0:
            return 0

        # Estimate the number of times each kid is detected in this buffer
        count_coords = collections.Counter(self._count_buffer_kids())

        # Get the kids we observed the most frequently
        frequents = collections.Counter(dict(count_coords.most_common(nb_kids)))
        # and deduce the identifiers we observed the most rarely
        rare_ids = tuple(x for x in count_coords - frequents)

        # Dissociate the un-relevant kids
        for i in range(len(self._video_buffer)):
            for kid in rare_ids:
                self.__dissociate_kid_coord(i, kid)

    # -----------------------------------------------------------------------

    def _dissociate_rare_and_scattered(self, percent=15., n=4):
        """Remove coords of kids appearing/disappearing like blinking.

        Consider to remove the kid only if the detected coords are
        occurring less than given percent of the buffer images

        :param percent: (float) Percentage threshold.
        :param n: n-gram used to know if data are scattered or not

        """
        # Estimate the number of times each kid is detected
        count_coords = self._count_buffer_kids()

        # A kid is rare if it's coords are detected in less than '%' images
        rare_ids = list()
        for kid in count_coords:
            freq_pid = 100. * float(count_coords[kid]) / float(len(self._video_buffer))
            if freq_pid < percent:
                rare_ids.append(kid)

        # Remove these rare kids ONLY if their coords are not continuous
        for kid in rare_ids:
            # Are they continuous or scattered?
            scattered = False
            # Estimate the N-grams of detected/non detected states
            states = [False]*len(self._video_buffer)
            for i in range(len(self._video_buffer)):
                if kid in self._video_buffer.get_ids(i):
                    states[i] = True
            true_ngram = tuple([True]*n)
            ngrams = symbols_to_items(states, n)
            # Estimate the ratio of sequences of 'n' true states
            if true_ngram in ngrams:
                ngrams_of_kid = ngrams[true_ngram]
                # the nb of possible sequences of kid->...->kid is nb_images-n-1
                ratio = float(ngrams_of_kid) / float(len(self._video_buffer) - n - 1)
                if ratio < 0.25:
                    scattered = True
            else:
                scattered = True

            # the kid is rare and its coords are scattered
            if scattered is True:
                for i in range(len(self._video_buffer)):
                    self.__dissociate_kid_coord(i, kid)

    # -----------------------------------------------------------------------

    def _count_buffer_kids(self):
        """Estimate the number of images in which each kid is detected.

        :return: (dict) key=kid, value=number of images

        """
        count_coords = dict()
        for kid in self.__kidsim:
            count_coords[kid] = 0

        for i in range(len(self._video_buffer)):
            for kid in self._video_buffer.get_ids(i):
                # if this kid was not already dissociated
                if kid in self.__kidsim:
                    count_coords[kid] += 1

        return count_coords

    # -----------------------------------------------------------------------

    def _set_identity_by_similarity(self):
        """Set a kid to each coord of the buffer with image similarities.

        """
        self.__kidsim.set_score_level(self.__min_coords)
        for i in range(len(self._video_buffer)):
            image = self._video_buffer[i]
            coords_i = self._video_buffer.get_coordinates(i)

            # for each of the coordinates, assign a kid
            identified = list()
            # logging.debug("{:d} => {:d} faces".format(i, len(coords_i)))
            for f, c in enumerate(coords_i):
                # Use similarity to identify which kid is matching the coords
                # or if none of them.
                identity = None
                score = 0.
                # Priority is given to coords similarity.
                # Coords are not matching enough. Rescue with the image similarities.
                img = image.icrop(c)
                # in case of invalid coords, the image is shape (0, 0, 3)
                if img.width * img.height > 0:
                    identity, score = self.__kidsim.identify(image=img, coords=None)
                    # logging.debug("    {} => id={}, score={} with recognizer"
                    #               "".format(c, identity, score))
                    if identity is None:
                        identity, score = self.__kidsim.identify(image=None, coords=c)
                    #    logging.debug("     {} => id={}, score={} with coords"
                    #                  "".format(c, identity, score))

                # The similarity measure identified a kid
                if identity is not None:
                    # Verify if this kid was not already assigned to a previous coord of this image.
                    for j in range(len(identified)):
                        identitj, scorj = identified[j]
                        # a kid is identified at 2 different coords: f and j
                        if identity == identitj:
                            # keep only the best score, invalidate the other one
                            if scorj < score:
                                identified[j] = (None, 0.)
                            else:
                                identity = None
                                score = 0.
                                break

                # Store the information for next coords
                identified.append((identity, score))
                # logging.debug(" - img {} identified id={}, score={} at coords {}."
                #               "".format(i, identity, score, c))

            # So, now that we know who is where... we can store the information
            for f, c in enumerate(coords_i):
                identity, score = identified[f]
                if identity is None:
                    # Either the similarity does NOT identified a kid, or,
                    # a kid was identified then invalidated
                    self._video_buffer.set_id(i, f, "unknown")
                else:
                    # Yep! the coords are matching a kid
                    self._video_buffer.set_id(i, f, identity)
                    self.__kidsim.set_cur_coords(identity, c)

    # -----------------------------------------------------------------------

    def __create_kid(self, image_index, coords_index):
        """Create and add a new kid.
        
        """
        coords_i = self._video_buffer.get_coordinates(image_index)

        image = self._video_buffer[image_index]
        img_kid = image.icrop(coords_i[coords_index])
        kid = self.__kidsim.create_identifier()
        self.__kidsim.add_image(kid, img_kid, reference=True)
        self.__kidsim.set_ref_coords(kid, coords_i[coords_index])

        # set the kid to the buffer
        self._video_buffer.set_id(image_index, coords_index, kid)

        return kid

    # -----------------------------------------------------------------------

    def __dissociate_kid_coord(self, buffer_index, kid):
        """Dissociate the kid to its assigned coord at given image.

        """
        if buffer_index < 0:
            return

        all_ids = self._video_buffer.get_ids(buffer_index)
        if kid in all_ids:
            idx = all_ids.index(kid)
            # fix and set the default identifier at this index
            identifier = "unk_{:03d}".format(idx+1)
            self._video_buffer.set_id(buffer_index, idx, identifier)
