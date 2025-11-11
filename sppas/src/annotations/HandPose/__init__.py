"""
:filename: sppas.src.annotations.HandPose.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Hand & Pose detection automatic annotations of SPPAS.

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

    -------------------------------------------------------------------------

SPPAS is a wrapper for MediaPipe Hand detection and Mediapipe Pose detection.
It also proposes a custom solution in order to detect right-left hands of a
single person.


"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError

# ---------------------------------------------------------------------------

if cfg.feature_installed("video") is False:

    class sppasHandPose(object):
        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("video")


    class MediaPipeHandPoseDetector(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")


    class sppasHandsSightsImageWriter(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")

else:
    from .imgsightswriter import sppasHandsSightsImageWriter

    if cfg.feature_installed("mediapipe") is False:

        class sppasHandPose(object):
            def __init__(self, *args, **kwargs):
                raise sppasEnableFeatureError("mediapipe")


        class MediaPipeHandPoseDetector(object):
            def __init__(self):
                raise sppasEnableFeatureError("mediapipe")

    else:
        # Import the classes in case mediapipe is installed so that
        # the automatic detections can work.
        from .sppashandpose import sppasHandPose

# ---------------------------------------------------------------------------


__all__ = (
    "sppasHandPose",
    "MediaPipeHandPoseDetector",
    "sppasHandsSightsImageWriter"
)
