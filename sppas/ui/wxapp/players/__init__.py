# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: players & viewers of digital audio/video data.

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

    -------------------------------------------------------------------------

Requires the following dependencies to play audio or video:

* simpleaudio - https://pypi.org/project/simpleaudio/
* opencv - https://opencv.org/

Either the FeatureError or PackageError will be raised if a class
is instantiated, but no error is raised at the time of init/import.

"""

import logging

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasPackageFeatureError

from .penum import PlayerState
from .penum import PlayerType
from .baseplayer import sppasBasePlayer
from .undplayer import sppasUndPlayer

# ---------------------------------------------------------------------------
# Update features & prepare base classes for exceptions: Audio
# ---------------------------------------------------------------------------


class sppasAudioPlayer(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("audioplay")


cfg.set_feature("audioplay", False)
try:
    import simpleaudio
    cfg.set_feature("audioplay", True)
    from .audiosaplayer import sppasAudioPlayer
    logging.info("Audio player is using simpleaudio library.")
except ImportError:
    try:
        import pyaudio
        cfg.set_feature("audioplay", True)
        from .audiopyplayer import sppasAudioPlayer
        logging.info("Audio player is using PyAudio library.")
    except ImportError:
        logging.error("Audio player is disabled.")
        pass

# ---------------------------------------------------------------------------
# Update features & prepare base classes for exceptions: Video
# ---------------------------------------------------------------------------

# Test if opencv library is available. It is the requirement of the
# feature "video".


class sppasVideoPlayerError(object):
    def __init__(self, *args, **kwargs):
        raise sppasEnableFeatureError("video")


try:
    import cv2
    cfg.set_feature("video", True)
except ImportError:
    # Invalidate the feature because the package is not installed
    cfg.set_feature("video", False)
else:
    v = cv2.__version__.split(".")[0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("video", False)


if cfg.feature_installed("video") is True:
    class sppasVideoPlayerError(object):
        def __init__(self, *args, **kwargs):
            raise sppasPackageFeatureError("cv2", "video")

# ---------------------------------------------------------------------------
# Either import classes or define them
# ---------------------------------------------------------------------------


if cfg.feature_installed("video") is True:
    from .videoplayer import sppasVideoPlayer
else:
    class sppasVideoPlayer(sppasVideoPlayerError):
        pass

# ---------------------------------------------------------------------------

# If audioplay and video are not available, the media won't be played but
# the SMMPS can be created in order to use its other functionalities.
from .smmps import sppasMMPS

# ---------------------------------------------------------------------------


__all__ = (
    "PlayerState",
    "PlayerType",
    "sppasBasePlayer",
    "sppasUndPlayer",
    "sppasAudioPlayer",  # play an audio file
    "sppasVideoPlayer",  # play a video file
    "sppasMMPS"          # play a bunch of media synchronously
)
