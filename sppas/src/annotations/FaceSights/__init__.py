# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Automatic detection of 68 face landmarks with opencv Facemark.

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

This package requires 'video' feature, for opencv and numpy dependencies.

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError


if cfg.feature_installed("video") is True:
    # -----------------------------------------------------------------------
    # Import the classes in case the "video" feature is enabled:
    # opencv&numpy are both installed.
    # -----------------------------------------------------------------------

    from .imgfacemark import ImageFaceLandmark
    from .imgsightswriter import sppasFaceSightsImageWriter
    from .sightsbuffer import sppasKidsSightsVideoBuffer
    from .sightsreader import sppasSightsVideoReader
    from .kidsightswriter import sppasKidsSightsVideoWriter
    from .sppasfacesights import sppasFaceSights

else:
    # -----------------------------------------------------------------------
    # Define exception classes in case opencv&numpy are not installed.
    # -----------------------------------------------------------------------

    class ImageFaceLandmark(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")


    class sppasFaceSightsImageWriter(object):
        def __init__(self):
            raise sppasEnableFeatureError("video")


    class sppasKidsSightsVideoBuffer(object):
        def __init__(self, video=None, size=-1):
            raise sppasEnableFeatureError("video")


    class sppasKidsSightsVideoWriter(object):
        def __init__(self, image_writer=None):
            raise sppasEnableFeatureError("video")


    class sppasSightsVideoReader(object):
        def __init__(self, input_file, csv_separator=";"):
            raise sppasEnableFeatureError("video")


    class sppasFaceSights(object):
        def __init__(self, log=None):
            raise sppasEnableFeatureError("video")


__all__ = (
    "sppasFaceSightsImageWriter",
    "ImageFaceLandmark",
    "sppasKidsSightsVideoBuffer",
    "sppasKidsSightsVideoWriter",
    "sppasSightsVideoReader",
    "sppasFaceSights"
)
