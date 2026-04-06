# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.videofacemark.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Automatic detection of the 68 sights on faces of a video.

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

import logging

from sppas.core.coreutils import sppasError
from sppas.src.calculus import tansey_linear_regression
from sppas.src.calculus import linear_fct

from ..FaceIdentity import sppasKidsVideoReader

from .sightsbuffer import sppasKidsSightsVideoBuffer
from .imgfacemark import ImageFaceLandmark

# ---------------------------------------------------------------------------


class VideoFaceLandmark(object):
    """Estimate the 68 face sights on all faces of a video.

    If faces were previously detected, this result can be loaded from a CSV
    or XRA file but if not, a FD system must be declared when initializing
    this class.

    """

    def __init__(self, face_landmark, face_detection=None):
        """Create a new instance.

        :param face_landmark: (ImageFaceLandmark) FL image system
        :param face_detection: (ImageFaceDetection) FD image system

        """
        # The face detection system
        if isinstance(face_landmark, ImageFaceLandmark) is False:
            raise sppasError("A face detection system was expected.")

        self._video_buffer = sppasKidsSightsVideoBuffer()
        self.__fl = face_landmark
        self.__fd = face_detection
        self.__all_faces = list()

    # -----------------------------------------------------------------------
    # Automatic detection of the face sights in a video
    # -----------------------------------------------------------------------

    def video_face_sights(self, video, faces_filename=None, video_writer=None, output=None):
        """Browse the video, get faces then detect sights and write results.

        :param video: (str) Video filename
        :param faces_filename: (str) Filename with the coords of all faces
        :param video_writer: ()
        :param output: (str) The output name for the folder and/or the video

        :return: (list) The coordinates of all detected sights on all images

        """
        # The detection system isn't ready
        if self.__fl.get_nb_recognizers() == 0:
            raise sppasError("A landmark recognizer must be initialized first")

        # Open the video stream
        self._video_buffer.open(video)
        self._video_buffer.set_buffer_size(self._video_buffer.get_framerate())
        self._video_buffer.seek_buffer(0)
        if video_writer is not None:
            video_writer.set_fps(self._video_buffer.get_framerate())

        # Get coordinates of the faces -- if previously estimated
        coords_buffer = None
        ids_buffer = None
        if faces_filename is not None:
            # br = sppasCoordsVideoReader(faces_filename)
            br = sppasKidsVideoReader(faces_filename)
            coords_buffer = br.coords
            nframes = self._video_buffer.get_nframes()
            if len(coords_buffer) != nframes:
                logging.error("The given {:d} coordinates doesn't match the"
                              " number of frames of the video {:d}"
                              "".format(len(coords_buffer), nframes))
                coords_buffer = None
            else:
                ids_buffer = br.ids

        if coords_buffer is None and self.__fd is None:
            # Release the video stream
            self._video_buffer.close()
            self._video_buffer.reset()
            raise sppasError("Face sights estimation requires faces or a "
                             "face detection system. None of them was declared.")

        # Browse the video using the buffer of images
        self.__all_faces = list()
        result_files = list()
        read_next = True
        nb = 0
        i = 0
        previous_buffer = sppasKidsSightsVideoBuffer(size=self._video_buffer.get_buffer_size()//4)
        prev_start = self._video_buffer.get_buffer_size() - previous_buffer.get_buffer_size()
        prev_end = self._video_buffer.get_buffer_size()
        while read_next is True:
            if nb % 10 == 0:
                logging.info("Read buffer number {:d}".format(nb+1))

            # fill-in the buffer with 'size'-images of the video
            read_next = self._video_buffer.next()

            # Detect face sights on all the images of the current buffer
            if coords_buffer is not None:
                coords_i = coords_buffer[i:i+len(self._video_buffer)]
                ids_i = ids_buffer[i:i+len(self._video_buffer)]
                # get face coordinates from the CSV/XRA file
                self._detect_buffer(coords_i, ids_i)
            else:
                # estimate face coordinates from the FD system
                self._detect_buffer()

            # Smooth the sights to provide shaking
            self.__smooth_buffer(previous_buffer)

            # save the current results: file names
            if output is not None and video_writer is not None:
                new_files = video_writer.write(self._video_buffer, output)
                result_files.extend(new_files)

            nb += 1
            i += len(self._video_buffer)

            # Fill-in the previous buffer with the last detected sights of the
            # current buffer
            p = 0
            for img_idx in range(prev_start, prev_end):
                previous_buffer.set_coordinates(p, self._video_buffer.get_coordinates(img_idx).copy())
                previous_buffer.set_ids(p, self._video_buffer.get_ids(img_idx).copy())
                previous_buffer.set_sights(p, self._video_buffer.get_sights(img_idx).copy())
                p = p + 1

        # Release the video stream
        self._video_buffer.close()
        self._video_buffer.reset()

        return result_files

    # -----------------------------------------------------------------------

    def _detect_buffer(self, coords=None, ids=None):
        """Determine the sights of all the detected faces of all images.

        :raise: sppasError if no model was loaded or no faces.

        """
        # No buffer is in-use.
        if len(self._video_buffer) == 0:
            logging.warning("Nothing to detect: no images in the buffer.")
            return

        # Find the sights of faces/ids in each image.
        for i, image in enumerate(self._video_buffer):
            if coords is None:
                self.__fd.detect(image)
                faces = [c.copy() for c in self.__fd]
                faces_ids = [str(i) for i in range(len(faces))]
            else:
                faces = coords[i]
                if ids is None:
                    faces_ids = [str(i) for i in range(len(faces))]
                else:
                    faces_ids = ids[i]

            self._video_buffer.set_coordinates(i, faces)
            self._video_buffer.set_ids(i, faces_ids)

            # Perform detection on all faces in the current image
            if len(faces) > 0:
                for f, face_coord in enumerate(faces):
                    success = self.__fl.detect_sights(image, face_coord)
                    # Save results into the list of sights of such image
                    if success is True:
                        self._video_buffer.set_sight(i, f, self.__fl.get_sights())

            if self.__fd is not None:
                self.__fd.invalidate()
            self.__fl.invalidate()

    # -----------------------------------------------------------------------

    def __smooth_buffer(self, previous_buffer):
        """Smooth the sights through the images."""
        # Update the list of all known face identifiers
        for ids in self._video_buffer.get_ids():
            for face_id in ids:
                if face_id not in self.__all_faces:
                    self.__all_faces.append(face_id)

        # Browse all faces identifiers, get all sights and smooth each one.
        for face_id in self.__all_faces:
            # Get the (commonly 68) sights of the given face for each image
            all_sights = list()
            all_previous_sights = list()
            one_sight = list()
            # Get all the sights of the previous buffer
            for img_idx in range(previous_buffer.get_buffer_size()):
                # Get the index of the face in this image
                img_faces = previous_buffer.get_ids(img_idx)
                if face_id in img_faces:
                    face_idx = self.__all_faces.index(face_id)
                    # get the sights of the face at image i
                    sights = previous_buffer.get_sight(img_idx, face_idx)
                    all_previous_sights.append(sights)
                else:
                    all_previous_sights.append(list())
            # Get all the sights of the current buffer
            for img_idx in range(len(self._video_buffer)):
                # Get the index of the face in this image
                img_faces = self._video_buffer.get_ids(img_idx)
                if face_id in img_faces:
                    face_idx = self.__all_faces.index(face_id)
                    # get the sights of the face at image i
                    sights = self._video_buffer.get_sight(img_idx, face_idx)
                    if sights is not None:
                        one_sight = sights
                    all_sights.append(sights)
                else:
                    all_sights.append(list())

            # smooth each (x,y,z) of each sight of the current buffer
            for sight_idx in range(len(one_sight)):
                px = list()
                py = list()
                pz = list()
                # Add the sights of the previous buffer to estimate the linear interpolation
                for pimg_idx in range(previous_buffer.get_buffer_size()):
                    if len(all_previous_sights[pimg_idx]) > 0:
                        px.append(all_previous_sights[pimg_idx].x(sight_idx))
                        py.append(all_previous_sights[pimg_idx].y(sight_idx))
                        z = all_previous_sights[pimg_idx].z(sight_idx)
                        if z is not None:
                            pz.append(z)

                for img_idx in range(len(self._video_buffer)):
                    if face_id in self._video_buffer.get_ids(img_idx):
                        # Add the sights of the current image to estimate the linear interpolation
                        if all_sights[img_idx] is not None and len(all_sights[img_idx]) > 0:
                            px.append(all_sights[img_idx].x(sight_idx))
                            py.append(all_sights[img_idx].y(sight_idx))
                            z = all_sights[img_idx].z(sight_idx)
                            if z is not None:
                                pz.append(z)
                            if len(px) >= previous_buffer.get_buffer_size():
                                px.pop(0)
                                py.pop(0)
                                if z is not None:
                                    pz.pop(0)

                            # Estimate the new sight
                            if len(px) > 2:
                                ppx = list()
                                ppy = list()
                                for pi in range(len(px)):
                                    ppx.append((pi, px[pi]))
                                    ppy.append((pi, py[pi]))
                                bx, ax = tansey_linear_regression(ppx)
                                by, ay = tansey_linear_regression(ppy)
                                x = max(0, int(linear_fct(len(ppx) - 1, ax, bx)))
                                y = max(0, int(linear_fct(len(ppx) - 1, ay, by)))
                                if len(pz) > 2:
                                    ppz = list()
                                    for pi in range(len(pz)):
                                        ppz.append((pi, pz[pi]))
                                    bz, az = tansey_linear_regression(ppz)
                                    z = max(0, int(linear_fct(len(ppz) - 1, az, bz)))
                                else:
                                    z = all_sights[img_idx].z(sight_idx)
                                # Set the new value to the stored sights
                                # logging.debug(" OLD: {}".format(all_sights[img_idx].get_sight(sight_idx)))
                                all_sights[img_idx].set_sight(sight_idx, x, y, z, all_sights[img_idx].score(sight_idx))
                                # logging.debug(" => NEW: {}".format(all_sights[img_idx].get_sight(sight_idx)))
