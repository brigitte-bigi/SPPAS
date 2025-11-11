"""
:filename: sppas.src.annotations.SpeechToText.basestt.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Speech-to-text.

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
import os
import logging

from sppas.core.coreutils import ISO639
from sppas.core.coreutils import LanguageNotFoundError


class BaseSTT(object):
    """Base class for any automated speech-to-text (STT) system.

    Provides the structure for loading a model and transcribing audio files.
    To use a STT system, simply implement the `BaseSTT` interface in a subclass.

    The audio file to be transcribed is preferably mono, 16KHz, 16bits.

    """

    def __init__(self, model: str | None = None, language: str | None = None, **kwargs):
        """Initialize the STT system.

        If provided, the model will be loaded automatically.

        :param model: (str|None) A model name, file path, or directory path.
        :param language: (str) The ISO-639-1 or ISO-639-3 language (e.g., "fra", "eng").
        :param **kwargs: Arbitrary keyword arguments for loading the model

        """
        if isinstance(language, str) is True and len(language) > 2:
            try:
                language = ISO639.get_language_info(language).iso639_1_code
            except LanguageNotFoundError as e:
                logging.error(e)
        else:
            language = None
        logging.debug(f"STT language set to '{language}'")
        self._language = language
        self._available = False
        self._model = None
        if model is not None:
            try:
                self._load_model(model, **kwargs)
            except Exception as e:
                logging.error(f"{self.__class__.__name__} was unable to load model "
                              f"{model}: {str(e)}")

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return STT name."""
        return self.__class__.__name__.replace("STT", "")

    name = property(get_name, None, None)

    # -----------------------------------------------------------------------

    def get_available(self) -> bool:
        """Return availability of the STT system."""
        return self._available

    available = property(get_available, None, None)

    # -----------------------------------------------------------------------

    def get_enabled(self) -> bool:
        """Return True if the STT system is enabled."""
        return self._model is not None

    enabled = property(get_enabled, None, None)

    # -----------------------------------------------------------------------

    def get_language(self) -> str:
        """Return ISO-639-1 language code."""
        return self._language

    language = property(get_language, None, None)

    # -----------------------------------------------------------------------

    def transcribe(self, audio_file: str, *args, **kwargs) -> str:
        """Transcribe the given audio file into text.

        :param audio_file: (str) The path to the audio file.
        :raises: FileNotFoundError: If the audio file is not found.
        :return: (str) The transcribed text.

        """
        if self._available is False:
            raise NotImplementedError("STT system is not available.")

        if os.path.isfile(audio_file) is False:
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        corrected_audio = self.__audio_checker(audio_file)

        return self._stt(audio_file, *args, **kwargs)

    # -----------------------------------------------------------------------
    # To be overridden
    # -----------------------------------------------------------------------

    def _load_model(self, model: str, **kwargs) -> None:
        """To be overridden. Load the model to be used by the STT system.

        :param model: (str) The model name, file path, or directory path.
        :raises: OSError: If the specified model cannot be found.
        :raises: NotImplementedError: If this method is not implemented in a subclass.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def _stt(self, audio_file: str, *args, **kwargs) -> str:
        """Transcribe the given audio file into text.

        :param audio_file: (str) The path to the audio file.
        :raises: NotImplementedError: If this method is not implemented in a subclass.
        :raises: FileNotFoundError: If the audio file is not found.
        :return: (str) The transcribed text.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __audio_checker(audio_file: str) -> str:
        """Return the filename of a mono, 16bits, 16kHz audio file.

        If not possible, return the closest solution.

        :param audio_file: (str) The path to the audio file.
        :return: (str) The filename of a mono, 16bits, 16kHz audio file.

        """
        return audio_file
