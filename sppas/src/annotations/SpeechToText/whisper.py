"""
:filename: sppas.src.annotations.SpeechToText.whisper.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: STT based on Whisper.

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

import torch
import whisper

from sppas.core.coreutils import ISO639
from sppas.core.coreutils import LanguageNotFoundError

from .basestt import BaseSTT

# Disable Whisper verbosity
logging.getLogger("torch").setLevel(logging.CRITICAL)
logging.getLogger("openai-whisper").disabled = True
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------


def detect_device() -> str:
    """Detect the best device for inference (GPU or CPU).

    :return: (str) The detected device ("cuda", "mps", or "cpu").

    """
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        try:
            # Quick test to ensure MPS works
            torch.randn(1, device="mps")
            return "mps"
        except:
            logging.warning("MPS backend is available but not functional. Falling back to CPU.")
            return "cpu"
    else:
        return "cpu"

# -----------------------------------------------------------------------


class WhisperSTT(BaseSTT):
    """OpenAI Whisper-based Automatic Transcription.

    Whisper is used for Speech-To-Text tasks when no orthographic transcription
    is provided with the audio file.

    Whisper can be installed with:
    > pip install -U openai-whisper

    Whisper uses PyTorch as its back-end. By default, when installing Whisper,
    PyTorch is installed with CPU-only support.

    To enable GPU support in PyTorch, you must install it separately, tailored
    to your hardware:

    - For NVIDIA GPUs (CUDA support), install PyTorch with the appropriate CUDA
     version for your GPU:
    > pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

    - For Apple Silicon (Mx processors), install PyTorch with Metal Performance
     Shaders (MPS) support:
    > pip install torch torchvision torchaudio

    """

    def __init__(self, model: str | None = None, language: str = "eng", **kwargs):
        """Initialize the Whisper STT system with the specified model.

        :param model: (str) The Whisper model name (e.g., "tiny", "base", "small", "medium", "large").
        :param language: (str) The ISO-639-1 or ISO-639-3 language (e.g., "fra", "eng").
        :param **kwargs: Arbitrary keyword arguments for loading the model

        """
        self.__device = detect_device()
        super().__init__(model, language, **kwargs)
        self._available = True

        # Define supported languages as a set of ISO-639-1 codes
        # Last update: 2024, December
        self._supported_languages = {
            "af", "sq", "am", "ar", "hy", "bn", "bs", "ca", "hr", "cs", "da", "nl", "en", "eo", "et", "tl",
            "fi", "fr", "de", "el", "gu", "he", "hi", "hu", "is", "id", "it", "ja", "jv", "km", "kn", "ko", "la",
            "lv", "lt", "ml", "mr", "ne", "pl", "pt", "pa", "ro", "ru", "sr", "si", "sk", "sl", "es", "su", "sw",
            "ta", "te", "th", "tr", "uk", "vi", "cy", "xh", "zh"
        }
        if self._language is not None and self._language not in self._supported_languages:
            # An unsupported language was given. Disable the STT.
            self._model = None
            logging.error(f"Language {self._language} is not supported by Whisper.")

    # -------------------------------------------------------------------

    def get_supported_languages(self) -> frozenset:
        """Return an immutable frozenset of supported languages."""
        return frozenset(self._supported_languages)

    # -------------------------------------------------------------------

    def is_language_supported(self, language: str) -> bool:
        """Check if the given language is supported by Whisper.

        :param language: (str) The ISO-639-1 language (e.g., "fra", "eng").
        :return: (bool) Whether the given language is supported by Whisper.

        """
        if len(language) > 2:
            try:
                language = ISO639.get_language_info(language).iso639_1_code
            except LanguageNotFoundError as e:
                logging.error(e)
        return language in self._supported_languages

    # -------------------------------------------------------------------

    def _load_model(self, model: str, **kwargs):
        """Load the model to be used by the Whisper system.

        :param model: (str) The Whisper model name (e.g., "tiny", "base", "small", "medium", "large").
        :raises: OSError: If the specified model cannot be loaded.

        """
        try:
            logging.info(f"Loading Whisper model '{model}' on device '{self.__device}'...")
            self._model = whisper.load_model(model, device=self.__device, **kwargs)
        except NotImplementedError as e:
            if self.__device != "cpu":
                logging.info(f"Backend '{self.__device}' is not fully supported. Falling back to CPU.")
                self.__device = "cpu"
                try:
                    self._model = whisper.load_model(model, device=self.__device)
                except Exception as e:
                    raise OSError(f"Failed to load Whisper model '{model}': {str(e)}")
            else:
                raise e
        except Exception as e:
            raise OSError(f"Failed to load Whisper model '{model}': {str(e)}")

    # -------------------------------------------------------------------

    def _stt(self, audio_file: str, *args, **kwargs) -> str:
        """Perform speech-to-text transcription using Whisper.

        Additional kwargs for Whisper:
        - language (str): Specify the language (e.g., "en", "fr").
        - task (str): Either "transcribe" (default) or "translate".
        - temperature (float): Sampling temperature (default: 0.0).
        - fp16 (bool): Use FP16 for faster GPU inference (default: True).

        :param audio_file: (str) Path to an audio file.
        :param kwargs: Additional keyword arguments for the Whisper model (UNUSED).
        :return: (str) The transcribed text.
        :raises: RuntimeError: If transcription fails.
        :raises: OSError: If the specified model was not loaded.

        """
        if self._model is None:
            raise OSError("Whisper model is not loaded.")

        try:
            if self._language is not None:
                result = self._model.transcribe(audio_file, language=self._language, temperature=0.5)
            else:
                result = self._model.transcribe(audio_file, temperature=0.5)
            return result.get("text", "")
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe audio with Hugging Face pipeline: {e}")
