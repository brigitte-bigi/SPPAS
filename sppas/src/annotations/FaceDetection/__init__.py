# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceDetection.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Automatic detection of faces with opencv.

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

This package requires video feature, for opencv and numpy dependencies.

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError

# ---------------------------------------------------------------------------


if cfg.feature_installed("video") is False:
    # Define classes in case opencv&numpy&mediapipe are not installed.

    class ImageFaceDetection(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")


    class VideoFaceDetection(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")


    class sppasFaceDetection(object):
        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("video")

else:
    # Import the classes in case opencv&numpy are both installed so that
    # the automatic detections can work.

    from .imgfacedetect import ImageFaceDetection
    from .videofacedetect import VideoFaceDetection
    from .sppasfacedetect import sppasFaceDetection

# ---------------------------------------------------------------------------

__all__ = (
    "ImageFaceDetection",
    "VideoFaceDetection",
    "sppasFaceDetection"
)
