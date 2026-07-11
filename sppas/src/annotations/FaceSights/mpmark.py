# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.mpmark.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  MediaPipe Tasks detector of the face mesh in an image.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

The MediaPipe Face Landmarker estimates 478 3D face landmarks: the 468
landmarks of the face mesh, plus 10 landmarks for the irises. Only the
468 mesh landmarks are used here, so the results are the same as the ones
of the previous "Face Mesh" solution. The z-axis is ignored.

The MediaPipe Tasks API externalizes its models: the face landmarker is
instantiated from a ".task" model file of the resources, exactly like the
OpenCV face-markers are instantiated from their ".yaml", ".xml" or ".dat"
model files.

"""

import logging
import numpy
import os

from sppas.core.config import cfg
from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasIOError
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.src.imgdata import sppasSights

from .basemark import BaseFaceMark

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python import vision as mp_vision
    cfg.set_feature("mediapipe", True)
except (ModuleNotFoundError, ImportError):
    cfg.set_feature("mediapipe", False)

# ---------------------------------------------------------------------------


class MediaPipeFaceMesh(BaseFaceMark):
    """Estimate the face mesh with MediaPipe Tasks.

    The number of sights of the mesh is 468. The z-axis is ignored.

    """

    def __init__(self, model):
        """Create a new MediaPipeFaceMesh instance.

        :param model: (str) Filename of the ".task" model file.
        :raises: sppasEnableFeatureError: mediapipe is not installed.
        :raises: IOError: The model file does not exist.
        :raises: sppasError: The detector failed to be instantiated.

        """
        if cfg.feature_installed("mediapipe") is False:
            raise sppasEnableFeatureError("mediapipe")
        super(MediaPipeFaceMesh, self).__init__()
        if os.path.exists(model) is False:
            raise sppasIOError(model)

        self._set_detector(model)
        # Store the mesh result of the detector (or None)
        self.__mesh_mode = False
        self.__mesh = None

    # -----------------------------------------------------------------------

    def enable_mesh(self, value=True):
        """Enable the mesh mode.

        :param value: (bool) True to store all the 468 detected values

        """
        self.__mesh_mode = bool(value)

    # -----------------------------------------------------------------------

    def get_mesh(self):
        """Return all the 468 sight values or None."""
        if self.__mesh is None:
            return None
        return self.__mesh.copy()

    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Initialize the detector with the given model file.

        :param model: (str) Filename of the ".task" model file.
        :raises: sppasError: The detector failed to be instantiated.

        """
        try:
            base_options = mp_tasks.BaseOptions(model_asset_path=model)
            options = mp_vision.FaceLandmarkerOptions(
                base_options=base_options,
                num_faces=1,
                min_face_detection_confidence=0.01)
            self._detector = mp_vision.FaceLandmarker.create_from_options(options)
        except Exception as e:
            logging.error("MediaPipe face landmarker failed to be "
                          "instantiated from model {:s}.".format(str(model)))
            raise sppasError(str(e))

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate current list of sight values."""
        self._sights.reset()
        self.__mesh = None

    # -----------------------------------------------------------------------

    def _detect(self, image, coords):
        """Detect sights on an image with the coords of the face.

        The resulting sppasSights() is internally stored.
        Get access with an iterator or getters.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.
        :param coords: Ignored.
        :return: (bool) True if sights were estimated properly

        """
        # MediaPipe requires a plain contiguous uint8 numpy.ndarray,
        # not a subclass like sppasImage.
        rgb = numpy.ascontiguousarray(image.ito_rgb(), dtype=numpy.uint8)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        try:
            results = self._detector.detect(mp_image)
        except Exception as e:
            logging.error("Error when detecting face sights: {}".format(str(e)))
            return False

        # Get results and convert to sights
        if len(results.face_landmarks) == 0:
            return False

        w, h = image.size()
        self.__mesh = sppasSights(nb=468)
        # Only one face should be detected. The 10 landmarks of the
        # irises, appended after the 468 ones of the mesh, are ignored.
        face = results.face_landmarks[0]
        for i in range(min(len(face), 468)):
            # the X- and Y- coordinates are normalized screen coordinates,
            # while the Z coordinate is relative and is scaled as the X
            # coordinate under the weak perspective projection camera model:
            # https://en.wikipedia.org/wiki/3D_projection#Weak_perspective_projection.
            mark = face[i]
            x_coord = max(0, int(mark.x * float(w)))
            y_coord = max(0, int(mark.y * float(h)))
            self.__mesh.set_sight(i, x_coord, y_coord)

        # we have the mesh but we're interested in the landmarks
        self._sights = self._mesh_to_sights()
        if self.__mesh_mode is False:
            self.__mesh = None
        return True

    # -----------------------------------------------------------------------

    def _mesh_to_sights(self):
        """Return the sights to represent a face in 2D.

        The indexes on the face are matching the regular ones of Face Landmark.

        :return: (Sights) selected 68 sight values

        """
        sights = sppasSights(nb=68)
        if self.__mesh is None:
            return sights
        x = self.__mesh.get_x()
        y = self.__mesh.get_y()
        sights.set_sight(0, x[127], y[127])
        sights.set_sight(1, x[234], y[234])
        sights.set_sight(2, x[93], y[93])
        sights.set_sight(3, x[132], y[132])
        sights.set_sight(4, x[58], y[58])
        sights.set_sight(5, x[172], y[172])
        sights.set_sight(6, x[150], y[150])
        sights.set_sight(7, x[176], y[176])
        sights.set_sight(8, x[152], y[152])
        sights.set_sight(9, x[400], y[400])
        sights.set_sight(10, x[379], y[379])
        sights.set_sight(11, x[397], y[397])
        sights.set_sight(12, x[288], y[288])
        sights.set_sight(13, x[361], y[361])
        sights.set_sight(14, x[323], y[323])
        sights.set_sight(15, x[454], y[454])
        sights.set_sight(16, x[356], y[356])

        sights.set_sight(17, x[70], y[70])
        sights.set_sight(18, x[63], y[63])
        sights.set_sight(19, x[105], y[105])
        sights.set_sight(20, x[66], y[66])
        sights.set_sight(21, x[107], y[107])
        sights.set_sight(22, x[336], y[336])
        sights.set_sight(23, x[296], y[296])
        sights.set_sight(24, x[334], y[334])
        sights.set_sight(25, x[293], y[293])
        sights.set_sight(26, x[300], y[300])

        sights.set_sight(27, x[8], y[8])
        sights.set_sight(28, x[168], y[6] + (abs(y[6] - y[168]) // 2))
        sights.set_sight(29, x[195], y[195])
        sights.set_sight(30, x[4], y[4])
        sights.set_sight(31, x[64], y[64])
        sights.set_sight(32, x[99], y[99])
        sights.set_sight(33, x[2], y[2])
        sights.set_sight(34, x[328], y[328])
        sights.set_sight(35, x[294], y[294])

        sights.set_sight(36, x[130], y[130])
        sights.set_sight(37, x[29], y[29])
        sights.set_sight(38, x[28], y[28])
        sights.set_sight(39, x[243], y[243])
        sights.set_sight(40, x[22], y[22])
        sights.set_sight(41, x[24], y[24])
        sights.set_sight(42, x[463], y[463])
        sights.set_sight(43, x[258], y[258])
        sights.set_sight(44, x[259], y[259])
        sights.set_sight(45, x[359], y[359])
        sights.set_sight(46, x[254], y[254])
        sights.set_sight(47, x[252], y[252])

        sights.set_sight(48, x[61], y[61])
        sights.set_sight(49, x[39], y[39])
        sights.set_sight(50, x[37], y[37])
        sights.set_sight(51, x[0], y[0])
        sights.set_sight(52, x[267], y[267])
        sights.set_sight(53, x[269], y[269])
        sights.set_sight(54, x[291], y[291])
        sights.set_sight(55, x[321], y[321])
        sights.set_sight(56, x[314], y[314])
        sights.set_sight(57, x[17], y[17])
        sights.set_sight(58, x[84], y[84])
        sights.set_sight(59, x[91], y[91])   # ((x[181] - x[91])//2), y[181])
        sights.set_sight(60, x[78], y[78])

        sights.set_sight(61, x[38], y[38])
        sights.set_sight(62, x[12], y[12])
        sights.set_sight(63, x[268], y[268])
        sights.set_sight(64, x[308], y[308])
        sights.set_sight(65, x[316], y[316])
        sights.set_sight(66, x[15], y[15])
        sights.set_sight(67, x[86], y[86])

        return sights
