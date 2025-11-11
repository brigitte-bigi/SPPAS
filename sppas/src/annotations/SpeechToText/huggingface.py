"""
:filename: sppas.src.annotations.SpeechToText.huggingface.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: HuggingFace STT.

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
import logging
import warnings

from transformers import pipeline

from .basestt import BaseSTT
from .whisper import detect_device

# Disable Whisper verbosity
logging.getLogger("torch").setLevel(logging.CRITICAL)
logging.getLogger("openai-whisper").disabled = True
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------


class HuggingFaceSTT(BaseSTT):
    """Speech-to-Text using a fine-tuned Whisper model from Hugging Face.

    """

    def __init__(self, model: str | None = None, language: str | None = None, **kwargs):
        """Initialize the Hugging Face STT system.

        :param model: (str) The Hugging Face model identifier.
        :param language: (str) Ignored. The ISO-639-1 or ISO-639-3 language.
        :param **kwargs: Arbitrary keyword arguments for loading the model

        """
        self.__device = detect_device()
        super().__init__(model, language, **kwargs)
        self._available = True

    # -----------------------------------------------------------------------

    def _load_model(self, model: str, **kwargs):
        """Load the Hugging Face model and set device preferences.

        :param model: (str) The Hugging Face model path.
        :raises: RuntimeError: If the model fails to load.

        """
        try:
            self._pipeline = pipeline(
                "automatic-speech-recognition",
                model=model,
                device=self.__device,
                **kwargs
            )
            # if self._language is not None:
            #     self._pipeline.model.config.forced_decoder_ids = (
            #         self._pipeline.tokenizer.get_decoder_prompt_ids(
            #             language=self._language, task="transcribe"))
            # else:
            self._pipeline.model.config.forced_decoder_ids = (
                self._pipeline.tokenizer.get_decoder_prompt_ids(task="transcribe"))

            self._model = model
        except Exception as e:
            import traceback
            logging.error(traceback.format_exc())
            raise RuntimeError(f"Failed to load Hugging Face model: {e}")

    # -----------------------------------------------------------------------

    def _stt(self, audio_file: str, *args, **kwargs) -> str:
        """Perform speech-to-text transcription using Hugging Face's pipeline.

        :param audio_file: (str) Path to an audio file.
        :return: (str) The transcribed text.
        :raises: RuntimeError: If transcription fails.
        :raises: OSError: If the specified model was not loaded.

        """
        if self._model is None:
            raise OSError("HuggingFace model is not loaded.")

        if not hasattr(self, "_pipeline"):
            raise RuntimeError("HuggingFace pipeline is not initialized.")

        try:
            # Transcribe audio.
            result = self._pipeline(audio_file, **kwargs)
            return result.get("text", "")
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe audio with Hugging Face pipeline: {e}")
