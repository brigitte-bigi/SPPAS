# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.SpeechToText.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SpeechToText based on Whisper and HuggingFace

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

This package requires stt feature, for whisper, torch and transformers dependencies.

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError

# no specific need of any external library
from .basestt import BaseSTT

# ---------------------------------------------------------------------------


if cfg.feature_installed("stt") is False:

    class WhisperSTT:
        """OpenAI Whisper-based Automatic Transcription is not available."""

        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("stt")

    class WhisperSTTonIPUs:
        """OpenAI Whisper-based Automatic Transcription is not available."""

        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("stt")


    class HuggingFaceSTT:
        """OpenAI HuggingFace-based Automatic Transcription is not available."""

        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("stt")

    class sppasSpeechToText:
        """SPPAS integration of the automatic SpeechToText annotation."""

        def __init__(self, *args, **kwargs):
            raise sppasEnableFeatureError("stt")


else:
    from .whisper import WhisperSTT
    from .huggingface import HuggingFaceSTT
    from .transcribe_ipus import WhisperSTTonIPUs
    from .sppasstt import sppasSpeechToText

# ---------------------------------------------------------------------------

__all__ = (
    "BaseSTT",
    "WhisperSTT",
    "HuggingFaceSTT",
    "WhisperSTTonIPUs",
    "sppasSpeechToText"
)
