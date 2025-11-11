# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.SpeechToText.deepspeech.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: STT initially based on DeepSpeech, migrated to its clone Coqui STT.

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

"""

from __future__ import annotations
import sys
import os

from .basestt import BaseSTT

try:
    # import deepspeech
    import stt
    from sppas.core.config import sppasExecProcess

    # -----------------------------------------------------------------------


    class DeepSpeechSTT(BaseSTT):
        """DeepSpeech Automatic Transcription -- based on Coqui STT.

        This class used the DeepSpeech engine for Speech-To-Text tasks when
        no orthographic transcription is available. It is replaced by its
        clones version: Coqui STT.

        """

        def __init__(self, model: str | None = None, language: str | None = None, **kwargs):
            """Initialize the STT system.

            :param model: (str) The model identifier.
            :param language: (str) The ISO-639-1 or ISO-639-3 language (e.g., "fra", "eng").
            :param **kwargs: Arbitrary keyword arguments for loading the model

            """
            self.__scorer = None
            super().__init__(model, language, **kwargs)
            self._available = True

        # -------------------------------------------------------------------

        def _load_model(self, model: str, **kwargs):
            """Load the models required by the DeepSpeech system.

            :param model: (str) Directory containing DeepSpeech model files.
            :raises: OSError: If no valid model file is found in the specified directory.
            :raises: FileNotFoundError: If the specified model directory is not found.

            """
            if os.path.isdir(model) is False:
                raise FileNotFoundError(f"Missing the specified model directory: {model}.")

            # Search for model and scorer files in the specified directory
            model_file = None
            scorer_file = None
            for filename in os.listdir(model):
                if filename.endswith("-models.pbmm"):
                    model_file = os.path.join(model, filename)
                elif filename.endswith("-models.scorer"):
                    scorer_file = os.path.join(model, filename)

            if model_file is None:
                raise OSError(f"No model file found in directory: {model}")

            self._model = model_file
            self.__scorer = scorer_file

        # -------------------------------------------------------------------

        def _stt(self, audio_file: str, *args, **kwargs) -> str:
            """Perform speech-to-text transcription using DeepSpeech.

            :param audio_file: (str) Path to an audio file.
            :return: (str) The transcribed text.
            :raises: OSError: If the DeepSpeech executable is not found.
            :raises: RuntimeError: If the DeepSpeech failed to transcribe.
            :raises: FileNotFoundError: If the audio file is not found.

            """
            # Locate the DeepSpeech executable
            python_dir = os.path.dirname(sys.executable)
            deepspeech_executable = os.path.join(python_dir, "deepspeech")
            if not os.path.isfile(deepspeech_executable):
                raise OSError(f"DeepSpeech executable not found in: {python_dir}")

            # Prepare the DeepSpeech command
            command = [
                deepspeech_executable,
                "--audio", audio_file,
                "--model", self._model,
            ]
            if self.__scorer:
                command.extend(["--scorer", self.__scorer])

            # Execute the command
            process = sppasExecProcess()
            process.run(" ".join(command))
            if process.error():
                raise RuntimeError(f"DeepSpeech failed with error: {process.error()}")

            return process.out()

except ImportError:

    class DeepSpeechSTT(BaseSTT):
        """DeepSpeech Automatic Transcription is not available."""

        def __init__(self, model: str):
            super().__init__()
