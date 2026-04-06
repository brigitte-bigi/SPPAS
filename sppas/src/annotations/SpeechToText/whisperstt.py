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
import logging
import warnings
import os

import torch
import whisper
from whisper.tokenizer import LANGUAGES

from sppas.core.coreutils import ISO639
from sppas.core.coreutils import LanguageNotFoundError

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


class WhisperSTT:
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

    def __init__(self,
                 model: str | None = None,
                 language: str = "und",
                 prompt: str | None = None):
        """Initialize the Whisper STT system with the specified model.

        :param model: (str) The Whisper model name (e.g., "tiny", "base", "small", "medium", "large").
        :param language: (str) The ISO-639-1 or ISO-639-3 language (e.g., "fra", "eng").
        :param prompt: Initial prompt, a prefix text to bias transcription.

        """
        self.__device = detect_device()

        self._prompt = None
        self.set_prompt(prompt)

        if language is not None and type(language) is not str:
            raise TypeError("Expected language type is 'str', or None.")
        self._language = language

        if model is not None and type(model) is not str:
            raise TypeError("Expected model type is 'str', or None.")
        self._model = None

        # Define supported languages as a set of ISO-639-1 codes
        # Last update: 2024, December
        self._supported_languages = set(LANGUAGES.keys())

        # Language
        # --------

        if isinstance(language, str):
            lang = language.strip().lower()
            if lang in {"", "und", "auto"}:
                self._language = None
            elif len(lang) == 2:
                self._language = lang
            else:
                try:
                    info = ISO639.get_language_info(lang)
                    self._language = info.iso639_1_code or None
                except LanguageNotFoundError as exc:
                    logging.error(exc)
                    self._language = None
        else:
            self._language = None
        logging.debug(f"STT language set to '{self._language}'")

        # Model
        # --------

        if self._language is not None and self._language not in self._supported_languages:
            # An unsupported language was given.
            logging.warning(
                f"Language '{self._language}' is not supported by Whisper; "
                f"falling back to auto-detect."
            )
            self._language = None

        if model is not None:
            try:
                self._load_model(model)
            except Exception as e:
                logging.error(f"{self.__class__.__name__} was unable to load model "
                              f"{model}: {str(e)}")

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

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return STT name."""
        return self.__class__.__name__.replace("STT", "")

    name = property(get_name, None, None)

    # -----------------------------------------------------------------------

    def get_enabled(self) -> bool:
        """Return True if the STT system is enabled."""
        return self._model is not None

    enabled = property(get_enabled, None, None)

    # -----------------------------------------------------------------------

    def get_language(self) -> str:
        """Return ISO-639-1 language code."""
        if self._language is None:
            return "und"
        return self._language

    language = property(get_language, None, None)

    # -----------------------------------------------------------------------

    def set_prompt(self, new_prompt: str | None):
        """Assign a prompt to Whisper.

        :param new_prompt: Initial prompt, a prefix text to bias transcription.
        :raises: TypeError: Invalid prompt type

        """
        if new_prompt is not None:
            if type(new_prompt) is not str:
                raise TypeError("Expected prompt type is 'str' or None.")
            if len(new_prompt.strip()) == 0:
                self._prompt = None
            else:
                self._prompt = new_prompt
        else:
            self._prompt = None

    # -----------------------------------------------------------------------

    def transcribe(self, audio_file: str, *args, **kwargs) -> str:
        """Transcribe the given audio file into text.

        Additional kwargs for Whisper:
        - task (str): Either "transcribe" (default) or "translate".
        - fp16 (bool): Use FP16 for faster GPU inference (default: True).

        :param audio_file: (str) Path to an audio file.
        :param kwargs: Additional keyword arguments for the Whisper model (CURRENTLY UNUSED).
        :raises: RuntimeError: If transcription failed.
        :raises: OSError: If the specified model was not loaded.
        :raises: FileNotFoundError: If the audio file is not found.
        :return: (str) The transcribed text.

        """
        if os.path.isfile(audio_file) is False:
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        if self._model is None:
            raise OSError("Whisper model is not loaded.")

        try:
            if self._prompt is None:
                p = ""
            else:
                p = self._prompt.strip()

            if self._language is not None:
                result = self._model.transcribe(audio_file, initial_prompt=p, language=self._language, temperature=0.5)
            else:
                result = self._model.transcribe(audio_file, initial_prompt=p, temperature=0.5)

            return result.get("text", "")
        except Exception as e:
            raise RuntimeError(f"Whisper failed to transcribe audio: {e}")

    # -------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------

    def _load_model(self, model: str):
        """Load the model to be used by the Whisper system.

        :param model: (str) The Whisper model name (e.g., "tiny", "base", ...).
        :raises: OSError: If the specified model cannot be loaded.

        """
        try:
            logging.info(f"Loading Whisper model '{model}' on device '{self.__device}'...")
            self._model = whisper.load_model(model, device=self.__device)
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
