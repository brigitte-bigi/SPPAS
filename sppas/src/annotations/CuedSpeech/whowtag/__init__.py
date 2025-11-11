# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tag a hand on a video for Cued Speech automatic annotation.

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

To cite this work, use one of the following references:

>Brigitte Bigi (2023).
>An analysis of produced versus predicted French Cued Speech keys.
>In 10th Language & Technology Conference: Human Language Technologies
>as a Challenge for Computer Science and Linguistics, Poznań, Poland.

:Abstract:
    Cued Speech is a communication system developed for deaf people to
    complement speechreading at the phonetic level with hands. This
    visual communication mode uses handshapes in different placements
    near the face in combination with the mouth movements of speech
    to make the phonemes of spoken language look different from each other.
    This paper presents an analysis on produced cues in 5 topics of CLeLfPC,
    a large corpus of read speech in French with Cued Speech.
    A phonemes-to-cues automatic system is proposed in order to predict the
    cue to be produced while speaking. This system is part of SPPAS -
    the automatic annotation an analysis of speech, an open source software
    tool. The predicted keys of the automatic system are compared to the
    produced keys of cuers. The number of inserted, deleted and substituted
    keys are analyzed. We observed that most of the differences between
    predicted and produced keys comes from 3 common position’s substitutions
    by some of the cuers.

>
"""

import os.path
import sys

from sppas.core.config import cfg
from sppas.core.config import paths
from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasPythonFeatureError
import sppas.src.videodata

# ---------------------------------------------------------------------------

class sppasHandFilters:
    def __init__(self, *args, **kwargs):
        raise sppasError("The hand filters can't be used.")


if os.path.exists(os.path.join(paths.resources, "cuedspeech")) is False:
    # The feature is enabled but the corresponding resources are missing.
    cfg.set_feature("cuedspeech", False)

if cfg.feature_installed("video") and cfg.feature_installed("cuedspeech"):

    # -----------------------------------------------------------------------
    # Import the classes in case the "video" feature is enabled: opencv&numpy
    # are both installed and the automatic detections can work.
    # -----------------------------------------------------------------------
    if sys.version_info > (3, 6):

        # -----------------------------------------------------------------------
        # Check if we have at least one hands set in the 'resources/cuedspeech' folder to tag a video.
        # -----------------------------------------------------------------------
        from sppas.src.resources import sppasHandResource

        hands_manager = sppasHandResource()
        hands_manager.automatic_loading()

        if len(hands_manager) > 0:
            from .whowtagvideo import CuedSpeechVideoTagger
            from .handfilters import sppasHandFilters

        else:
            # -----------------------------------------------------------------------
            # Define class in case we have no hands set in the 'resources/cuedspeech' folder.
            # -----------------------------------------------------------------------
            class CuedSpeechVideoTagger:
                OPTIONS = {}
                def __init__(self, *args, **kwargs):
                    raise sppasError("The 'resources/cuedspeech' folder doesn't contains any hand-set.")

                @staticmethod
                def get_hands_filters() -> list:
                    return []

            class sppasHandFilters:
                def __init__(self, *args, **kwargs):
                    raise sppasError("The hand filters can't be used.")

                @staticmethod
                def get_filter_names() -> list:
                    return []

    else:
        # -----------------------------------------------------------------------
        # Define class in case python version is inferior to 3.6
        # -----------------------------------------------------------------------

        class CuedSpeechVideoTagger:
            OPTIONS = {}
            def __init__(self, *args, **kwargs):
                raise sppasPythonFeatureError("cuedspeech", "3.6+")

else:
    # -----------------------------------------------------------------------
    # Define class in case opencv&numpy are not installed.
    # -----------------------------------------------------------------------

    class CuedSpeechVideoTagger:
        OPTIONS = {}
        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("cuedspeech")


__all__ = (
    "CuedSpeechVideoTagger"
)
