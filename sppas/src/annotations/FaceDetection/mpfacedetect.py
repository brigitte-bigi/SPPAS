"""
:filename: sppas.src.annotations.FaceDetection.mpfacedetect.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  MediaPipe detector of faces in an image.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from __future__ import annotations
import logging
import mediapipe as mp
import numpy
from typing import NamedTuple

from sppas.core.coreutils import sppasError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import BaseObjectsDetector

# ---------------------------------------------------------------------------


class MediaPipeFaceDetector(BaseObjectsDetector):
    """SPPAS wrapper of MediaPipe Face Detection.

    MediaPipe Face Detection processes an RGB image and returns a list of the
    detected face location data.

    """

    def __init__(self):
        """Create a MediaPipe Face Detection instance.

        """
        super(MediaPipeFaceDetector, self).__init__()
        self._extension = ""
        self.__model_selector = 0

    # -----------------------------------------------------------------------

    def load_model(self, model=None, *args) -> None:
        """Override. Instantiate a detector.

        :param model: Unused.
        :param args: Unused.

        """
        self._set_detector()

    # -----------------------------------------------------------------------

    def set_min_score(self, value: float) -> None:
        """Override. Set the minimum score of a detected object to consider it.

        It means that any detected object with a score lesser than the given
        one will be ignored. The score of detected objects are supposed to
        range between 0. and 1.

        :param value: (float) Value ranging [0., 1.]
        :raises: ValueError: invalid given value.
        :raises: sppasError: can not instantiate mediapipe face detection model.

        """
        BaseObjectsDetector.set_min_score(self, value)
        if self._detector is not None:
            self._set_detector()

    # -----------------------------------------------------------------------

    def get_model_selector(self):
        """Return 0 for short distance model or 1 for long-distance model."""
        return self.__model_selector

    # -----------------------------------------------------------------------

    def set_model_selector(self, value: int = 0) -> None:
        """Set mediapipe model: 0 for short-distance.

        :param value: (int) 0 to select a short-range model that works
            best for faces within 2 meters from the camera, and 1 for a
            full-range model best for faces within 5 meters.

        """
        value = int(value)
        if value != 0:
            value = 1
        self.__model_selector = value

    # -----------------------------------------------------------------------

    def _set_detector(self, model: str | None = None) -> None:
        """Override. Initialize the detector.

        MediaPipe has its internal model so the given model is not used.

        :param model: (str | None) Un-used.
        :raises: sppasError: can not instantiate mediapipe face detection model.

        """
        try:
            # Arguments of a mp.solutions.face_detection.FaceDetection:
            #   - min_detection_confidence: Minimum confidence value ([0.0, 1.0])
            #     for face detection to be considered successful.
            #   - model_selection: 0 to select a short-range model that works
            #     best for faces within 2 meters from the camera, and 1 for a
            #     full-range model best for faces within 5 meters.
            self._detector = mp.solutions.face_detection.FaceDetection(
                min_detection_confidence=self.get_min_score(),
                model_selection=0
               )
        except Exception as e:
            logging.error("MediaPipe face detection system failed to be instantiated.")
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detection(self, image: sppasImage | numpy.ndarray) -> bool:
        """Override. Determine the coordinates of the detected objects.

        :param image: (sppasImage or numpy.ndarray) BGR/BGRA image
        :return: (bool) True if faces were detected and False otherwise

        """
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_aray=image)

        w, h = image.size()
        rgb = image.ito_rgb()
        try:
            # Processes an RGB image and returns a list of the detected face
            # location data.
            results = self._detector.process(rgb)
            # It raises:
            #  - RuntimeError: If the underlying graph throws any error.
            #  - ValueError: If the input image is not three channel RGB.
            # It returns a NamedTuple object with a "detections" field that
            # contains a list of the detected face location data.
        except ValueError as e:
            logging.error("MediaPipe face detection system failed to process detection "
                          "on the given image: {:s}".format(str(e)))
            return False
        except RuntimeError as e:
            logging.error("MediaPipe face detection system failed to process detection "
                          "due to the following error: {:s}".format(str(e)))
            return False

        # Convert detections into a list of sppasCoords
        if not results.detections:
            return False
        self._coords = MediaPipeFaceDetector.mp_results_to_coords(results, w, h)

        return len(self._coords) > 0

    # -----------------------------------------------------------------------

    @staticmethod
    def mp_results_to_coords(results: NamedTuple, w: int, h: int) -> list:
        """Fill-in the coords from the given results.

        The face coordinates are adjusted in order to be consistent with
        the other face detection systems.

        :param results: (NamedTuple) Result from MediaPipe face detection system.
        :param w: (int) Image width
        :param h: (int) Image height
        :return: (list) List of sppasCoords of the detected objects.

        """
        coords = list()
        for face in results.detections:
            # Compared to the other detectors, Media Pipe scores are lowers.
            # We have to "boost" them for consistency reasons.
            score = min(1., 1.2*face.score[0])

            # The format of the face is a relative bounding box, ie
            # it's a box with a relative size of the image.
            # Compared to the other detectors, this box is very large around
            # the face.
            # We have to lower it also for consistency reasons.
            relative_roi = face.location_data.relative_bounding_box
            x_coord = max(0, int(relative_roi.xmin * float(w)))
            y_coord = max(0, int(relative_roi.ymin * float(h)))
            w_coord = int(relative_roi.width * float(w) * 0.7)
            h_coord = int(relative_roi.height * float(h) * 0.8)
            x_coord += int(0.2 * float(w_coord))

            # OK, the customization of results is done. Coords can be stored.
            coord = sppasCoords(x_coord, y_coord, w_coord, h_coord)
            coord.set_confidence(score)
            coords.append(coord)
        return coords
