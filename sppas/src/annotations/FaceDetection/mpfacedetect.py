# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceDetection.mpfacedetect.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  MediaPipe Tasks detector of faces in an image.

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

The MediaPipe Tasks API externalizes its models: the face detector is
instantiated from a ".tflite" model file of the resources, exactly like
the OpenCV detectors are instantiated from their ".xml", ".caffemodel",
".pb" or ".onnx" model files.

"""

import logging
import numpy

from sppas.core.config import cfg
from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import BaseObjectsDetector

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python import vision as mp_vision
    cfg.set_feature("mediapipe", True)
except (ModuleNotFoundError, ImportError):
    cfg.set_feature("mediapipe", False)

# ---------------------------------------------------------------------------


class MediaPipeFaceDetector(BaseObjectsDetector):
    """Detect faces in an image with MediaPipe Tasks.

    The MediaPipe Face Detector processes an RGB image and returns a list
    of the detected face location data. Its model is an externalized
    ".tflite" file, so this detector is loaded, enabled and used exactly
    like the OpenCV-based ones.

    """

    def __init__(self):
        """Create a new MediaPipeFaceDetector instance.

        :raises: sppasEnableFeatureError: mediapipe is not installed.

        """
        if cfg.feature_installed("mediapipe") is False:
            raise sppasEnableFeatureError("mediapipe")
        super(MediaPipeFaceDetector, self).__init__()
        self._extension = ".tflite"
        self.__model = None

    # -----------------------------------------------------------------------

    def set_min_score(self, value):
        """Override. Set the minimum score of a detected object to consider it.

        The detector filters the detected faces with this score at
        detection time, so it is re-instantiated if already loaded.

        :param value: (float) Value ranging [0., 1.]
        :raises: ValueError: Invalid given value.
        :raises: sppasError: The detector failed to be re-instantiated.

        """
        BaseObjectsDetector.set_min_score(self, value)
        if self._detector is not None:
            self._set_detector(self.__model)

    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Override. Initialize the detector with the given model file.

        :param model: (str) Filename of the ".tflite" model file.
        :raises: sppasError: The detector failed to be instantiated.

        """
        try:
            base_options = mp_tasks.BaseOptions(model_asset_path=model)
            options = mp_vision.FaceDetectorOptions(
                base_options=base_options,
                min_detection_confidence=self.get_min_score())
            self._detector = mp_vision.FaceDetector.create_from_options(options)
        except Exception as e:
            logging.error("MediaPipe face detection system failed to be "
                          "instantiated from model {:s}.".format(str(model)))
            raise sppasError(str(e))
        self.__model = model

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Override. Determine the coordinates of the detected objects.

        :param image: (sppasImage or numpy.ndarray) BGR/BGRA image.
        :return: (bool) True if at least one face was detected.

        """
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_array=image)

        # MediaPipe requires a plain contiguous uint8 numpy.ndarray,
        # not a subclass like sppasImage.
        rgb = numpy.ascontiguousarray(image.ito_rgb(), dtype=numpy.uint8)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        try:
            results = self._detector.detect(mp_image)
        except Exception as e:
            logging.error("MediaPipe face detection system failed to process "
                          "detection on the given image: {:s}".format(str(e)))
            return False

        if len(results.detections) == 0:
            return False
        self._coords = MediaPipeFaceDetector.mp_results_to_coords(results)

        return len(self._coords) > 0

    # -----------------------------------------------------------------------

    @staticmethod
    def mp_results_to_coords(results):
        """Convert the given results into a list of coordinates.

        The face coordinates are adjusted in order to be consistent with
        the other face detection systems.

        :param results: (FaceDetectorResult) Result of the MediaPipe face detector.
        :return: (list) List of sppasCoords of the detected objects.

        """
        coords = list()
        for face in results.detections:
            # Compared to the other detectors, MediaPipe scores are lower.
            # They are "boosted" for consistency reasons.
            score = min(1., 1.2 * face.categories[0].score)

            # Compared to the other detectors, the bounding box is very
            # large around the face. It is lowered for consistency reasons.
            box = face.bounding_box
            x_coord = max(0, int(box.origin_x))
            y_coord = max(0, int(box.origin_y))
            w_coord = int(float(box.width) * 0.7)
            h_coord = int(float(box.height) * 0.8)
            x_coord += int(0.2 * float(w_coord))

            coord = sppasCoords(x_coord, y_coord, w_coord, h_coord)
            coord.set_confidence(score)
            coords.append(coord)
        return coords
