"""
:filename: sppas.src.annotations.FaceSights.opencvmark.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  OpenCV face landmark in an image.

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

OpenCV's facial landmark API is called Facemark. It has three different
implementations of landmark detection based on three different papers:

    - FacemarkKazemi: This implementation is based on a paper titled
    "One Millisecond Face Alignment with an Ensemble of Regression Trees"
     by V.Kazemi and J. Sullivan published in CVPR 2014.
    - FacemarkAAM: This implementation uses an Active Appearance Model
    and is based on an the paper titled "Optimization problems for fast
    AAM fitting in-the-wild" by G. Tzimiropoulos and M. Pantic, published
    in ICCV 2013.
    - FacemarkLBF: This implementation is based a paper titled "Face
    alignment at 3000 fps via regressing local binary features" by
    S. Ren published in CVPR 2014.

"""

import os
import logging
import cv2
import numpy

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasIOError
from sppas.core.coreutils import IOExtensionError

from .basemark import BaseFaceMark

# ---------------------------------------------------------------------------


class OpenCVFaceMark(BaseFaceMark):
    """SPPAS wrapper of any OpenCV Face Mark recognizer.

    https://docs.opencv.org/trunk/db/dd8/classcv_1_1face_1_1Facemark.html

    """

    def __init__(self, model):
        """Initialize the face detection and recognizer from model files.

        :param model: (str) Filename of a recognizer model (Kazemi, LBF, AAM).
        :raise: IOError, IOExtensionError, Exception

        """
        super(OpenCVFaceMark, self).__init__()
        if os.path.exists(model) is False:
            raise sppasIOError(model)

        fn, fe = os.path.splitext(model)
        fe = fe.lower()

        # Face landmark recognizer
        if fe == ".yaml":
            fm = cv2.face.createFacemarkLBF()
        elif fe == ".xml":
            fm = cv2.face.createFacemarkAAM()
        elif fe == ".dat":
            fm = cv2.face.createFacemarkKazemi()
        else:
            raise IOExtensionError(model)

        try:
            fm.loadModel(model)
            # We should check that the model is based on the detection of 68 sights
            # but there's nothing in cv2 to do that... so we should add an image
            # and perform a detection.
            self._detector = fm
        except cv2.error as e:
            logging.error("Loading the model {} failed.".format(model))
            raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detect(self, image, coords):
        """Detect sights on an image with the coords of the face.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.
        :param coords: (sppasCoords) Coordinates of the face in the image
        :return: (bool) True if sights were estimated properly

        """
        # The face-markers requires the face coordinates in a numpy array
        rects = numpy.array([[coords.x, coords.y, coords.w, coords.h]], dtype=numpy.int32)
        try:
            # Detect facial landmarks from the image with the face-marker
            marked, landmarks = self._detector.fit(image, rects)
            # Get the 68 lists of numpy arrays with (x,y) values
            points = landmarks[0][0]
            if marked is True and len(points) == len(self._sights):
                # Convert the list of numpy arrays into a list of tuples
                for i in range(len(points)):
                    x, y = points[i]
                    self._sights.set_sight(i, round(x), round(y))
                return True
        except cv2.error as e:
            logging.error("Landmark detection failed with error: "
                          "{}".format(str(e)))

        return False
