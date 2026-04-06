# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.imgfacemark.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Automatic detection of the 68 sights on the image of a face.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

The fundamental concept is that any person will have 68 particular points
on the face (called sights).

"""

import logging

from sppas.core.config import cfg
from sppas.src.imgdata import sppasCoords

from .basemark import BaseFaceMark
from .basemark import BasicFaceMark
from .opencvmark import OpenCVFaceMark

if cfg.feature_installed("mediapipe"):
    from .mpmark import MediaPipeFaceMesh
else:
    class MediaPipeFaceMesh(object):
        def __init__(self, *args, **kwargs):
            logging.warning("Mediapipe Face Mesh is disabled. "
                            "It requires mediapipe feature to be installed.")

        def detect_sights(self, *args, **kwargs):
            return False

# ---------------------------------------------------------------------------


class ImageFaceLandmark(BaseFaceMark):
    """Estimate the 68 sights on one face of an image with several detectors.

    """

    def __init__(self):
        """Create a new ImageFaceLandmark instance.

        """
        super(ImageFaceLandmark, self).__init__()
        # The basic "empirical" predictor
        self.__basic = None
        # The MediaPipe predictor
        self.__mediapipe = MediaPipeFaceMesh()
        # The OpenCV landmark recognizers
        self.__markers = list()

    # -----------------------------------------------------------------------

    def get_nb_recognizers(self) -> int:
        """Return the number of initialized landmark recognizers."""
        nb = 2
        if self.__basic is None:
            nb = 1
        return nb + len(self.__markers)

    # -----------------------------------------------------------------------

    def add_model(self, filename: str) -> None:
        """Append an OpenCV recognizer into the list and load the model.

        :param filename: (str) A recognizer model (Kazemi, LBF, AAM).
        :raise: IOError, IOExtensionError, Exception

        """
        predictor = OpenCVFaceMark(filename)
        self.__markers.append(predictor)

    # -----------------------------------------------------------------------

    def enable_empirical_predictor(self, value: str = True) -> None:
        """Enable the basic predictor with empirically fixed sights.

        :param value: (bool) True to enable

        """
        if bool(value) is True:
            self.__basic = BasicFaceMark()
        else:
            self.__basic = None

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def _detect(self, image, coords=None):
        """Detect sights on an image with the coords of the face.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.
        :param coords: (sppasCoords) Coordinates of the face in the image or None for the full image

        """
        # Estimate all the 68 points by each instantiated face-marker
        success, all_points = self.__detect_with_markers(image, coords)

        if success is True:
            # Interpolate all the points and store into our landmarks
            for i in range(len(self._sights)):
                x, y, score = self.__points_to_coords(image, coords, all_points[i])
                self._sights.set_sight(i, x, y, None, score)

        return success

    # ------------------------------------------------------------------------

    def __points_to_coords(self, image, coords, points):
        """Convert a list of estimated points into coordinates of a sight.

        The confidence score of each sight depends on the area covered by the
        points. The image and the coords are used only to estimate the score.

        :param image: (numpy.ndarray) The image.
        :param coords: (sppasCoords) Coordinates of the face in the image.
        :param points: (list of (x,y) values) A sight detected by each method
        :return: Estimated (x,y,c) values

        """
        # 1. Fix the score -- the larger the area the worse
        # Get width and height of the face
        if coords is not None:
            img = image.icrop(coords)
        else:
            img = image.copy()

        h, w = img.shape[:2]
        # The area of the face
        face_area = h * w

        # Get the area of points detected by each method
        min_x = min(result[0] for result in points)
        min_y = min(result[1] for result in points)
        max_x = max(result[0] for result in points)
        max_y = max(result[1] for result in points)
        points_area = (max_x - min_x) * (max_y - min_y)

        # Estimate the score with an area ratio
        if face_area > 0.:
            ratio = float(points_area) / float(face_area)
        else:
            ratio = 1.
        coeff = max(1., min(5., 100. * ratio))
        score = min(1., max(0., 1. - (coeff * ratio)))

        # 2.  Fix (x,y) in the middle
        # Give more weight to MediaPipe result (the 1st in the list)
        # ... but which is the better weight?
        avg_points = [p for p in points]
        for i in range(4):
            avg_points.append(points[0])
        sum_x = sum(result[0] for result in avg_points)
        sum_y = sum(result[1] for result in avg_points)
        x = round(float(sum_x) / float(len(avg_points)))
        y = round(float(sum_y) / float(len(avg_points)))

        return x, y, score

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __detect_with_markers(self, image, coords):
        """Estimate all the 68 points by each instantiated face-marker.

        The returned result is a list of 68 lists of tuples with (x,y) values
        because it's the data structure OpenCV is returning when invoking
        the method 'fit()' of each recognizer.

        """
        # Store results in a dict with:
        #   Key = index of the sight, so the key is ranging (0;68)
        #   Value = list of results; a result is a tuple (x, y)
        all_points = {i:list() for i in range(len(self._sights))}

        # MediaPipe predicted sights
        if coords is not None:
            c = coords.portrait()
        else:
            # No coords. Estimation is on the whole image.
            w, h = image.get_size()
            c = sppasCoords(0, 0, w, h)
        success = self.__mediapipe.detect_sights(image.icrop(c))
        if success is True:
            for i, sight in enumerate(self.__mediapipe):
                (x, y, z, s) = sight
                all_points[i].append((x + c.x, y + c.y))

        # OpenCV predictors
        # https://docs.opencv.org/trunk/db/dd8/classcv_1_1face_1_1Facemark.html
        for cv_marker in self.__markers:
            s = cv_marker.detect_sights(image, coords)
            if s is True:
                success = True
                # Convert the list of sights into a list of tuples
                for i, sight in enumerate(cv_marker):
                    (x, y, z, s) = sight
                    all_points[i].append((x, y))

        # Empirically fixed sights, they can be used to smooth...
        if self.__basic is not None:
            self.__basic.detect_sights(image, coords)
            for i, sight in enumerate(self.__basic):
                (x, y, z, s) = sight
                all_points[i].append((x, y))

        return success, all_points
