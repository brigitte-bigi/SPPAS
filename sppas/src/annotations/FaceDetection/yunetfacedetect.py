# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceDetection.yunetfacedetect.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  OpenCV YuNet detector of faces in an image.

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

YuNet is a light-weight and fast face detection model, released under the
MIT license. An ONNX model file describes the network but not its input
pre-processing nor its output decoding, so the generic ONNX detector of
imgdata can not be used: the dedicated cv2.FaceDetectorYN API embeds the
decoding of the network outputs (anchors and strides).

"""

import logging
import cv2

from sppas.core.coreutils import sppasError
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import BaseObjectsDetector

# ---------------------------------------------------------------------------


class YuNetFaceDetector(BaseObjectsDetector):
    """Detect faces in an image with the OpenCV YuNet detector.

    The detector is instantiated from its ".onnx" model file, loaded,
    enabled and used exactly like the other face detection systems.
    The detection score threshold and the non-maximum suppression are
    embedded in the cv2.FaceDetectorYN API.

    """

    def __init__(self):
        """Create a new YuNetFaceDetector instance."""
        super(YuNetFaceDetector, self).__init__()
        self._extension = ".onnx"

    # -----------------------------------------------------------------------

    def _set_detector(self, model):
        """Override. Initialize the detector with the given model file.

        The input size given at creation is a placeholder: it is fixed
        for each image at detection time.

        :param model: (str) Filename of the ".onnx" YuNet model file.
        :raises: sppasError: The detector failed to be instantiated.

        """
        try:
            self._detector = cv2.FaceDetectorYN.create(
                model, "", (320, 320),
                score_threshold=self.get_min_score())
        except cv2.error as e:
            logging.error("YuNet face detection system failed to be "
                          "instantiated from model {:s}.".format(str(model)))
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detection(self, image):
        """Override. Determine the coordinates of the detected objects.

        :param image: (sppasImage or numpy.ndarray) BGR image.
        :return: (bool) True if at least one face was detected.

        """
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_array=image)

        w, h = image.size()
        self._detector.setInputSize((w, h))
        try:
            retval, faces = self._detector.detect(image)
        except cv2.error as e:
            logging.error("YuNet face detection system failed to process "
                          "detection on the given image: {:s}".format(str(e)))
            return False

        if faces is None:
            return False

        # Each row of the results is made of 15 values: the (x, y, w, h)
        # of the face box, then the (x, y) of 5 landmarks, then the score.
        for face in faces:
            x_coord = max(0, int(face[0]))
            y_coord = max(0, int(face[1]))
            w_coord = int(face[2])
            h_coord = int(face[3])
            # Compared to the other detectors, YuNet scores are high,
            # even for the false positives (about 0.5, while the true
            # faces are at 0.9 or more). Squaring the scores keeps the
            # true faces high and lowers the false positives, so the
            # scores are consistent with the other detection systems.
            score = float(face[14])
            score = min(1., score * score)

            coord = sppasCoords(x_coord, y_coord, w_coord, h_coord)
            coord.set_confidence(score)
            self._coords.append(coord)

        return len(self._coords) > 0
