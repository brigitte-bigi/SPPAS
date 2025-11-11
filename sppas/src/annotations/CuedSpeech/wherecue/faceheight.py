"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.faceheight.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Estimate the height of a face from its sights.

.. _This file is part of SPPAS: <https://sppas.org/>
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
from collections import deque

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasPoint
from sppas.src.calculus import fmean
from sppas.src.calculus.geometry.distances import euclidian
from sppas.src.imgdata import sppasSights

# ---------------------------------------------------------------------------


class sppasFaceHeight:
    """Estimate a smoothed height of the face from its 2D sights.

    """

    @staticmethod
    def eval_height(face_sights):
        """Estimate the size coefficient of the given face using facial landmarks.

        This method computes a face size coefficient based on three facial sights:
        points 19 and 24 (which define a segment across the face), and point 8
        (typically the chin).

        It calculates the midpoint between points 19 and 24, then returns the
        Euclidean distance from this midpoint to point 8. This value is useful
        for normalizing hand size relative to face size in images.

        :param face_sights: (sppasSights) The facial landmarks (68 points expected).
        :return: (float) A coefficient representing the size of the given face.
        :raises: sppasTypeError: Invalid given face sights argument
        :raises: sppasError: Invalid number of given face sights

        """
        if isinstance(face_sights, sppasSights) is False:
            raise sppasTypeError(type(face_sights), "sppasSights")
        if len(face_sights) != 68:
            raise sppasError("Invalid number of sights. Expected 68. "
                             f"Got {len(face_sights)} instead")

        # coords of a point between face sight 19 and 24
        _dx = abs(face_sights.x(19) - face_sights.x(24))
        _dy = abs(face_sights.y(19) - face_sights.y(24))
        _x = float(face_sights.x(19)) + _dx / 2.
        _y = float(face_sights.y(19)) + _dy / 2.

        # distance from this point to face sight 8
        return euclidian((_x, _y), (face_sights.x(8), face_sights.y(8)))

# ---------------------------------------------------------------------------


class sppasFaceHeightGenerator:
    """Estimate a smoothed height of the face from its 2D sights.

    """

    def __init__(self, data_sights: list):
        """Create an instance of the size predictor.

        :param data_sights: list of sppasSights

        """
        self.__data_sights = data_sights

    # -----------------------------------------------------------------------

    def face_height(self, fps: int = 60) -> sppasTier:
        """Return a list of smoothed sizes estimated from the sights.

        :param fps: (int) Framerate of the video. Used to smooth values.
        :return: (sppasTier) tier with name 'CS-FaceHeight'

        """
        # The tier to be returned
        tier = sppasTier("CS-FaceHeight")
        distances = deque(maxlen=fps)

        for midpoint, radius, sights in self.__data_sights:

            # Estimate the observed face size and smooth with the previous ones
            dist = sppasFaceHeight.eval_height(sights)
            smoothed_dist = self.__append_and_smooth(distances, dist)

            # Save the distance into an annotation
            tag = sppasTag(smoothed_dist, tag_type="int")
            label = sppasLabel(tag)
            loc = sppasLocation(sppasPoint(midpoint, radius))
            tier.create_annotation(loc, label)

        return tier

    # -----------------------------------------------------------------------
    # Private
    # ----------------------------------------------------------------------

    @staticmethod
    def __append_and_smooth(deck: deque, value: int):
        """Append into the queue and return the smoothed value.

        """
        # Append the real value into the queue
        deck.append(value)
        # Estimate the smoothed value: average of values in the queue
        if len(deck) > 1:
            return int(fmean(deck))
        return value
