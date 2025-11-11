# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_videocued.__init__.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: The init file of the app_videocued package

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

"""

import sys

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasPythonFeatureError

# ---------------------------------------------------------------------------


# Define classes in case the video feature is not enabled
if cfg.feature_installed("video") is False:

    class AutoCuedResponseRecipe:
        def __init__(self):
            raise sppasEnableFeatureError("video")
    class VideoCuedResponseRecipe:
        def __init__(self):
            raise sppasEnableFeatureError("video")
    class VideoCuedWebData:
        def __init__(self):
            raise sppasEnableFeatureError("video")

# Define classes in case the cuedspeech feature is not enabled
elif cfg.feature_installed("cuedspeech") is False:
    class AutoCuedResponseRecipe:
        def __init__(self):
            raise sppasEnableFeatureError("cuedspeech")
    class VideoCuedWebData:
        def __init__(self):
            raise sppasEnableFeatureError("cuedspeech")
    class VideoCuedResponseRecipe:
        def __init__(self):
            raise sppasEnableFeatureError("cuedspeech")

# Define classes in case the version of python is inferior to 3.9
elif sys.version_info < (3, 9):
    class AutoCuedResponseRecipe:
        def __init__(self):
            raise sppasPythonFeatureError("app_videocued", "3.9+")
    class VideoCuedResponseRecipe:
        def __init__(self):
            raise sppasPythonFeatureError("app_videocued", "3.9+")
    class VideoCuedWebData:
        def __init__(self):
            raise sppasPythonFeatureError("app_videocued", "3.9+")

else:
    from .videocuedmaker import VideoCuedResponseRecipe
    from .app_videocued import VideoCuedWebData

# ---------------------------------------------------------------------------


__all__ = (
    "VideoCuedResponseRecipe",
    "VideoCuedWebData"
)
