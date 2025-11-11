# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.videodata.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Package for the management of video files.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

*****************************************************************************
videodata: management of video files
*****************************************************************************

Requires the following other internal packages:

* config
* utils
* imgdata

Requires the following other external libraries:

* opencv
* numpy

If the video feature is not enabled, the sppasEnableFeatureError() is raised
when a class is instantiated.

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasPackageFeatureError
from sppas.core.coreutils import sppasPackageUpdateFeatureError

# ---------------------------------------------------------------------------


class sppasVideodataError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")

# ---------------------------------------------------------------------------
# The feature "video" is enabled: cv2 is installed.
# Check version.
if cfg.feature_installed("video") is True:
    import cv2
    v = cv2.__version__.split(".")[0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("video", False)

    class sppasVideoDataError(object):
        def __init__(self, *args, **kwargs):
            if v != '4':
                raise sppasPackageUpdateFeatureError("cv2", "video")
            else:
                raise sppasPackageFeatureError("cv2", "video")


# ---------------------------------------------------------------------------


if cfg.feature_installed("video") is True:
    from .video import sppasVideoReader
    from .video import sppasVideoWriter
    from .videobuffer import sppasVideoReaderBuffer
    from .videobuffer import sppasBufferVideoWriter
    from .coordsbuffer import sppasCoordsVideoBuffer
    from .coordsbuffer import sppasCoordsVideoWriter
    from .coordsbuffer import sppasCoordsVideoReader
    from .sightsbuffer import sppasSightsVideoBuffer
    from .videoutils import sppasImageVideoWriter
    video_extensions = sppasVideoWriter.get_extensions()

else:

    # Define classes in case opencv&numpy are not installed.
    video_extensions = tuple()


    class sppasVideoWriter(sppasVideodataError):
        MAX_FPS = 0
        FOURCC = dict()
        RESOLUTIONS = dict()


    class sppasImageVideoWriter(sppasVideoWriter):
        pass


    class sppasVideoReader(sppasVideodataError):
        pass


    class sppasVideoReaderBuffer(sppasVideodataError):
        DEFAULT_BUFFER_SIZE = 0
        DEFAULT_BUFFER_OVERLAP = 0
        MAX_MEMORY_SIZE = 0
        pass


    class sppasBufferVideoWriter(sppasVideodataError):
        pass


    class sppasCoordsVideoBuffer(sppasVideodataError):
        pass


    class sppasCoordsVideoWriter(sppasVideoWriter):
        pass


    class sppasCoordsVideoReader(sppasVideoWriter):
        pass


    class sppasSightsVideoBuffer(sppasVideodataError):
        pass


# ---------------------------------------------------------------------------


__all__ = (
    "sppasVideoReader",
    "sppasVideoWriter",
    "sppasImageVideoWriter",
    "sppasVideoReaderBuffer",
    "sppasBufferVideoWriter",
    "sppasCoordsVideoBuffer",
    "sppasCoordsVideoWriter",
    "sppasCoordsVideoReader",
    "sppasSightsVideoBuffer",
    "video_extensions",
)
