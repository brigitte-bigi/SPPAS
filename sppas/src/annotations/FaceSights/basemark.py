"""
:filename: sppas.src.annotations.FaceSights.basemark.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class for auto detection of face mark or face mesh.

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

import numpy

from sppas.core.coreutils import sppasTypeError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasSights

# ---------------------------------------------------------------------------


class BaseFaceMark(object):
    """SPPAS base class for Face Landmark or Face Mesh.

    """

    def __init__(self):
        # The face Landmark detector
        self._detector = None

        # The nb sights detected on the face
        self._sights = sppasSights(nb=68)

    # -----------------------------------------------------------------------

    def get_sights(self):
        """Return a copy of the sights.

        :return: (Sights)

        """
        return self._sights.copy()

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate current list of sight coordinates."""
        self._sights.reset()

    # -----------------------------------------------------------------------
    # Getters of specific points
    # -----------------------------------------------------------------------

    def get_chin(self):
        """Return coordinates of the right side of the face.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [0-16].

        """
        if len(self._sights) == 68:
            return self._sights[:17]
        return list()

    # -----------------------------------------------------------------------

    def get_left_eyebrow(self):
        """Return coordinates of the left brow.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [18-22].

        """
        if len(self._sights) == 68:
            return self._sights[17:22]
        return list()

    # -----------------------------------------------------------------------

    def get_right_eyebrow(self):
        """Return coordinates of the right brow.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [23-27].

        """
        if len(self._sights) == 68:
            return self._sights[22:27]
        return list()

    # -----------------------------------------------------------------------

    def get_nose(self):
        """Return coordinates of the nose.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [28-36].

        """
        if len(self._sights) == 68:
            return self._sights[27:36]
        return list()

    # -----------------------------------------------------------------------

    def get_left_eye(self):
        """Return coordinates of the left eye.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [37-42].

        """
        if len(self._sights) == 68:
            return self._sights[36:42]
        return list()

    # -----------------------------------------------------------------------

    def get_right_eye(self):
        """Return coordinates of the right eye.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [43-48].

        """
        if len(self._sights) == 68:
            return self._sights[42-48]
        return list()

    # -----------------------------------------------------------------------

    def get_lips(self):
        """Return coordinates of the mouth.

        If the list of marked points has the 68-standard number of points that
        make up an "Active Shape Model", return points [49-68].

        """
        if len(self._sights) == 68:
            return self._sights[48:]
        return list()

    # -----------------------------------------------------------------------
    # Automatic detection of the landmark points
    # -----------------------------------------------------------------------

    def detect_sights(self, image, coords=None):
        """Detect sights on an image with the coords of the face.

        sppasSights are internally stored. Get access with an iterator or getters.

        :param image: (sppasImage or numpy.ndarray or None) The image to be processed.
        :param coords: (sppasCoords) Coordinates of a detected face, or None.
        :raises: sppasTypeError: Invalid image type.

        """
        if image is None:
            return False

        # Convert image to sppasImage if necessary
        if isinstance(image, numpy.ndarray) is True:
            image = sppasImage(input_array=image)
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")

        # Delete previous results
        self.invalidate()

        # Make predictions on the given image on the face at given coords.
        success = self._detect(image, coords)
        return success

    # -----------------------------------------------------------------------

    def _detect(self, image, coords):
        """Detect landmarks on the given image.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    @staticmethod
    def to_dtype(value, dtype=int):
        """Convert a value to dtype or raise the appropriate exception.

        :param value: (any type)
        :param dtype: (type) Expected type of the value
        :returns: Value of the given type
        :raises: TypeError

        """
        try:
            value = dtype(value)
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        return value

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of landmarks."""
        return len(self._sights)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(len(self._sights)):
            yield self._sights[i]

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self._sights[i]

    # ----------------------------------------------------------------------

    def __contains__(self, other):
        """Return true if value in sights -- score is ignored.

        :param other: a list/tuple of (x,y,score)

        """
        return other in self._sights

    # -----------------------------------------------------------------------

    def __str__(self):
        """Return coords separated by CR."""
        return "\n".join([str(coords) for coords in self._sights])

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

# ---------------------------------------------------------------------------


class BasicFaceMark(BaseFaceMark):
    """Absolute sights of a face.

    """

    def __init__(self):
        """Initialize the basic predictor.

        """
        super(BasicFaceMark, self).__init__()

    # ------------------------------------------------------------------------

    def _detect(self, img, coords):
        """Fix sights empirically on an image with the coords of the face.

        sppasSights are internally stored. Get access with an iterator or getters.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.
        :param coords: Coordinates of the face in the image.
        :return: (bool) True

        """
        self._sights = BasicFaceMark.basic_sights(img, coords)
        return True

    # ------------------------------------------------------------------------

    @staticmethod
    def basic_sights(image, coords):
        """Return empirically fixed sights which does not require any model.

        All sights were estimated by supposing that:
            1. it's a frontal face
            2. coords are properly surrounding the face

        :param image: (numpy.ndarray) The image to be processed.
        :param coords: (sppasCoords) Coordinates of the face in the image.
        :return: (sppasSights) Estimated sights.

        """
        basic_sights = sppasSights(nb=68)
        img = image.icrop(coords)
        h, w = img.shape[:2]
        sx = w // 20
        sy = h // 20
        x = w // 2
        y = h // 2

        # chin -- face contour
        basic_sights.set_sight(0, 1, y - (2*sy))
        basic_sights.set_sight(1, sx // 3, y)
        basic_sights.set_sight(2, sx // 2, y + (2*sy))
        basic_sights.set_sight(3, sx, y + (4*sy))
        basic_sights.set_sight(4, 2*sx, y + (6*sy))
        basic_sights.set_sight(5, 4*sx, y + (8*sy))
        basic_sights.set_sight(6, 6*sx, h - sy)
        basic_sights.set_sight(7, 8*sx, h - (sy//2))
        basic_sights.set_sight(8, x, h)
        basic_sights.set_sight(9, x + (2*sx), h - (sy//2))
        basic_sights.set_sight(10, x + (4*sx), h - sy)
        basic_sights.set_sight(11, x + (6*sx), y + (8*sy))
        basic_sights.set_sight(12, x + (8*sx), y + (6*sy))
        basic_sights.set_sight(13, w - sx, y + (4*sy))
        basic_sights.set_sight(14, w - (sx // 2), y + (2*sy))
        basic_sights.set_sight(15, w - (sx // 3), y)
        basic_sights.set_sight(16, w - 1, y - (2*sy))

        # brows
        basic_sights.set_sight(17, 2*sx, 6*sy)
        basic_sights.set_sight(18, (3*sx) + (sx//2), (5*sy) + (sy//2))
        basic_sights.set_sight(19, 5*sx, 5*sy)
        basic_sights.set_sight(20, (6*sx) + (sx//2), (5*sy) + (sy//2))
        basic_sights.set_sight(21, 8*sx, 6*sy)
        basic_sights.set_sight(22, x + 2*sx, 6*sy)
        basic_sights.set_sight(23, x + (3*sx) + (sx//2), (5*sy) + (sy//2))
        basic_sights.set_sight(24, x + 5*sx, 5*sy)
        basic_sights.set_sight(25, x + (6*sx) + (sx//2), (5*sy) + (sy//2))
        basic_sights.set_sight(26, x + (8*sx), 6*sy)

        # nose
        basic_sights.set_sight(27, x, y - (2*sy) - (sy//2))
        basic_sights.set_sight(28, x, y - sy - (sy//2))
        basic_sights.set_sight(29, x, y - (sy//2))
        basic_sights.set_sight(30, x, y + (sy//2))
        basic_sights.set_sight(31, x - (3*sx), y + (2*sy) - (sy//2))
        basic_sights.set_sight(32, x - (2*sx), y + (2*sy) - (sy//3))
        basic_sights.set_sight(33, x, y + (2*sy))
        basic_sights.set_sight(34, x + (2*sx), y + (2*sy) - (sy//3))
        basic_sights.set_sight(35, x + (3*sx), y + (2*sy) - (sy//2))

        # eyes
        basic_sights.set_sight(36, x - (6*sx), 7*sy + (sy//2))
        basic_sights.set_sight(37, x - (5*sx) - (sx//4), 7*sy)
        basic_sights.set_sight(38, x - (4*sx), 7*sy)
        basic_sights.set_sight(39, x - (3*sx), 7*sy + (sy//2))
        basic_sights.set_sight(40, x - (4*sx), 8*sy)
        basic_sights.set_sight(41, x - (5*sx), 8*sy)
        basic_sights.set_sight(42, x + (3*sx), 7*sy + (sy//2))
        basic_sights.set_sight(43, x + (4*sx), 7*sy)
        basic_sights.set_sight(44, x + (5*sx), 7*sy)
        basic_sights.set_sight(45, x + (6*sx), 7*sy + (sy//2))
        basic_sights.set_sight(46, x + (5*sx), 8*sy)
        basic_sights.set_sight(47, x + (4*sx), 8*sy)

        # mouth
        basic_sights.set_sight(48, x - (4*sx), y + (4*sy) + (sy//2))
        basic_sights.set_sight(49, x - (2*sx) - (sx//2), y + (4*sy))
        basic_sights.set_sight(50, x - sx, y + (4*sy) - (sy//3))
        basic_sights.set_sight(51, x, y + (4*sy) - (sy//4))
        basic_sights.set_sight(52, x + sx, y + (4*sy) - (sy//3))
        basic_sights.set_sight(53, x + (2*sx) + (sx//2), y + (4*sy))
        basic_sights.set_sight(54, x + (4*sx), y + (4*sy) + (sy//2))
        basic_sights.set_sight(55, x + (2*sx) + (sx//2), y + (5*sy) + (sy//4))
        basic_sights.set_sight(56, x + sx, y + (6*sy) - (sy//4))
        basic_sights.set_sight(57, x, y + (6*sy))
        basic_sights.set_sight(58, x - sx, y + (6*sy) - (sy//4))
        basic_sights.set_sight(59, x - (2*sx) - (sx//2), y + (5*sy) + (sy//4))
        basic_sights.set_sight(60, x - (2*sx) - (sx//2), y + (4*sy) + (sy//2))
        basic_sights.set_sight(61, x - sx, y + (4*sy) + (sy//4))
        basic_sights.set_sight(62, x, y + (4*sy) + (sy//2))
        basic_sights.set_sight(63, x + sx, y + (4*sy) + (sy//4))
        basic_sights.set_sight(64, x + (2*sx) + (sx//2), y + (4*sy) + (sy//2))
        basic_sights.set_sight(65, x + sx, y + (5*sy))
        basic_sights.set_sight(66, x, y + (5*sy) + (sy//4))
        basic_sights.set_sight(67, x - sx, y + (5*sy))

        # adjust to the image coords and not the face ones
        for i, s in enumerate(basic_sights):
            x, y, z, score = s
            x += coords.x
            y += coords.y
            basic_sights.set_sight(i, x, y)

        return basic_sights
