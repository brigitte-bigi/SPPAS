# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceDetection.imgfacedetect.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Automatic detection of faces in an image.

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

from sppas.core.config import cfg
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageObjectDetection

from .mpfacedetect import MediaPipeFaceDetector

# ---------------------------------------------------------------------------


class ImageFaceDetection(sppasImageObjectDetection):
    """Detect faces in an image.

    Automatic face detection, based on opencv HaarCascadeClassifier and
    Artificial Neural Networks: this class allows to analyze an image in
    order to detect all faces. It stores internally the list of sppasCoords()
    for each detected face.

    Like the base class, this class allows multiple models in order to
    launch multiple detections and to combine results. Moreover, it allows
    to convert the coordinates into the portrait instead of the face.

    SPPAS>=5.1: The MediaPipe Tasks face detector is used exactly like the
    other systems, from its ".tflite" model file in the resources.

    :Example:

        >>> f = ImageFaceDetection()
        >>> f.load_model(filename1, filename2...)
        >>> # Detect all the faces in an image
        >>> image = sppasImage(filename="image path"))
        >>> f.detect(image)
        >>> # Get number of detected faces
        >>> len(f)
        >>> # Browse through all the detected face coordinates:
        >>> for c in f:
        >>>     print(c)
        >>> # Get the detected faces with the highest score
        >>> f.get_best()
        >>> # Get the 2 faces with the highest scores
        >>> f.get_best(2)
        >>> # Get detected faces with a confidence score greater than 0.8
        >>> f.get_confidence(0.8)
        >>> # Convert coordinates to a portrait size (i.e. scale by 2.1)
        >>> f.to_portrait(image)

    """

    # Inheritable registry: the detectors of the base class and the
    # face-dedicated ones. The MediaPipe face detector is added below,
    # only if the mediapipe feature is installed.
    DETECTORS = dict(sppasImageObjectDetection.DETECTORS)

    def __init__(self):
        """Create a new instance."""
        super(ImageFaceDetection, self).__init__()
        self._extension = ""

    # -----------------------------------------------------------------------

    def detect(self, image):
        """Determine the coordinates of all the detected faces.

        :param image: (sppasImage or numpy.ndarray)
        :raises: sppasTypeError: Given parameter is not an image.
        :raises: sppasError: No model 'face' was instantiated.

        """
        # Launch the base method to detect objects, here objects are faces.
        # Can raise sppasTypeError or sppasError.
        sppasImageObjectDetection.detect(self, image)

        # Overlapped faces are much rarer than overlapped objects:
        # re-filter with overlapping portraits.

        # Backup the current coords in a dictionary with key=portrait
        backup_coords = dict()
        for coord in self._coords:
            portrait = coord.portrait(image)
            backup_coords[portrait] = coord

        # Replace the original coords by the portrait
        self._coords = list(backup_coords.keys())

        # Filter the overlapping portraits but do not re-normalize the scores
        # by the number of classifiers.
        self.filter_overlapped(overlap=60., norm_score=False)
        self.sort_by_score()

        # re-assign the normal size
        new_coords = list()
        for portrait_coord in self._coords:
            normal_coord = backup_coords[portrait_coord]
            new_coords.append(normal_coord)

        self._coords = new_coords

    # -----------------------------------------------------------------------

    def to_portrait(self, image=None):
        """Scale coordinates of faces to a portrait size.

        The given image allows to ensure we wont scale larger than what the
        image can do.

        :param image: (sppasImage) The original image.

        """
        if len(self._coords) == 0:
            return False

        portraits = list()
        for coord in self._coords:
            c = coord.portrait(image)
            portraits.append(c)

        # no error occurred, all faces are converted to their portrait
        self._coords = portraits
        return True

# ---------------------------------------------------------------------------
# Register the face-dedicated detector, only if available.
# ---------------------------------------------------------------------------


if cfg.feature_installed("mediapipe") is True:
    ImageFaceDetection.DETECTORS[MediaPipeFaceDetector().get_extension().lower()] = MediaPipeFaceDetector
