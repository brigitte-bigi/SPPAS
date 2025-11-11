# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.app_textcued.text2cue.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Generate the sequence of cues from a text.

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

from __future__ import annotations
import os

from sppas.core.config import paths
from sppas.core.config import symbols
from sppas.src.annotations.Align.aligners.aligner import aligners
from sppas.src.resources import sppasDictRepl
from sppas.src.resources import sppasVocabulary
from sppas.src.resources import sppasDictPron
from sppas.src.resources import sppasMapping
from sppas.src.annotations.TextNorm.normalize import TextNormalizer
from sppas.src.annotations.Phon.phonetize import sppasDictPhonetizer
from sppas.src.annotations.Align.aligners import BasicAligner
from sppas.src.annotations.CuedSpeech import CuedSpeechKeys

# ----------------------------------------------------------------------------


class TextToCues(object):
    """Generates cued keys of a text.

        1- Text Normalization
        2- Phonetization
        3- Alignment
        4- Cued Speech

    """

    def __init__(self, lang: str = "und"):
        """Create a new Text2Cues instance.

        :param lang: (str) Language of the text (iso639-1)

        """
        self.__lang = lang.lower()

    # ---------------------------------------------------------------------------
    # WORKERS
    # ---------------------------------------------------------------------------

    def normalizer(self, text: str) -> list:
        """Return the result of "Text Normalization" on the given text.

        :param text: (str) Input text to be normalized
        :return: (list) List of tokens

        """
        # Vocabulary of the given language
        vocab_file = os.path.join(paths.resources, 'vocab', self.__lang.lower() + '.vocab')
        vocab = sppasVocabulary(vocab_file)
        # The normalizer
        normalizer = TextNormalizer(vocab, self.__lang)

        # List of systematic replacements
        replace_file = os.path.join(paths.resources, "repl", self.__lang + ".repl")
        if os.path.exists(replace_file) is True:
            repl = sppasDictRepl(replace_file, nodump=True)
            normalizer.set_repl(repl)

        # List of punctuations -- for removing
        punct_file = os.path.join(paths.resources, "vocab", "Punctuations.txt")
        if os.path.exists(punct_file):
            punct = sppasVocabulary(punct_file, nodump=True)
            normalizer.set_punct(punct)

        # Numbers to letters conversion
        number_filename = os.path.join(paths.resources, 'num', self.__lang.lower() + '_num.repl')
        if os.path.exists(number_filename) is True:
            numbers = sppasDictRepl(number_filename, nodump=True)
            normalizer.set_num(numbers)

        # Custom options
        normalizer.set_delim("_")   # default is '_'

        # Text Normalization of the input text. The result is a list.
        return normalizer.normalize(text)

    # ---------------------------------------------------------------------------

    def phonetizer(self, text: str) -> list:
        """Return the result of "Phonetization" on the given normalized text.

        :param text: (str) Normalized text to be phonetized
        :return: (list) List of tuple(token, phones, status)

        """
        pdict_file = os.path.join(paths.resources, 'dict', self.__lang.lower() + '.dict')
        pdict = sppasDictPron(pdict_file, nodump=False)

        # A mapping table: sampa -> IPA for example: map_table = sppasMapping(file)
        mapping = sppasMapping()
        # The phonetizer
        phonetizer = sppasDictPhonetizer(pdict, mapping)
        # Custom options: number of phonetization variants
        phonetizer.set_unk_variants(4)
        # Phonetization of the given input normalized text
        results = list()
        for line in text.split("#"):
            # the result is a list of tuple(token, phones, status)
            # status (int): annots.ok or annots.warning or annots.error
            results.extend(phonetizer.get_phon_tokens(line.split(' '), phonunk=True))

        return results

    # ---------------------------------------------------------------------------

    def aligner(self, text: str) -> list:
        """Choose the phonetization variant.

        :param text: (str) Phonetized text.
        :return: (list) List of (begin, end, phoneme)

        """
        text = text.strip()
        if len(text) == 0:
            return list()

        aligner = BasicAligner()
        aligner.set_phones(text)
        # Get selected pronunciation and pseudo time-alignment values
        aligned = aligner.run_basic()

        # The aligned result is a list of tuple(begin, end, phone) with
        # faked time values
        return aligned

    # ---------------------------------------------------------------------------

    def cuer(self, aligned_phonemes: list) -> list:
        """Return the result of "CuedSpeech" on the given phonetized text.

        :param aligned_phonemes: (list) Time-aligned phonemes.
        :return: (list) List of keys

        """
        rule_file = os.path.join(paths.resources, 'cuedspeech', "cueConfig-" + self.__lang + '.txt')
        cs = CuedSpeechKeys(rule_file)
        stops = list(symbols.phone.keys())
        stops.append('#')
        stops.append('*')
        stops.append('@@')
        stops.append('+')
        stops.append('sil')
        stops.append('sp')
        stops.append('gb')
        stops.append('lg')
        stops.append('fp')
        stops.append('dummy')

        results = list()
        phonemes = list()
        # the aligned result is a list of tuple(begin, end, phone)
        for phon in aligned_phonemes:
            p = phon[2]
            if p in stops and len(phonemes) > 0:
                sgmts = cs.syllabify(phonemes)
                phons = cs.phonetize_syllables(phonemes, sgmts)
                keys = cs.keys_phonetized(phons)
                results.append((keys, phons))
                phonemes = list()
            else:
                phonemes.append(p)

        # last segment
        if len(phonemes) > 0:
            sgmts = cs.syllabify(phonemes)
            phons = cs.phonetize_syllables(phonemes, sgmts)
            keys = cs.keys_phonetized(phons)
            results.append((keys, phons))

        return results

    # ---------------------------------------------------------------------------

    def text_to_cues(self, text: str):
        """Perform the full process of text cueing.

        :param text: (str) Input text to be cued
        :return: (str) Sequence of keys

        """
        normalized_result = self.normalizer(text)
        normalized_text = TextToCues.format_normalized(normalized_result)

        phon_lang = self.__lang
        if phon_lang == "fra":
            self.__lang = "fre"
        phonetized_result = self.phonetizer(normalized_text)
        phonetized_text = TextToCues.format_phonetized(phonetized_result)
        self.__lang = phon_lang

        aligned_result = self.aligner(phonetized_text)
        return self.cuer(aligned_result)

    # ---------------------------------------------------------------------------
    # RESULTS FORMATTERS
    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_normalized(result) -> str:
        """Convert the normalized result into a human-readable string.

        :return: (str) Sequence of tokens

        """
        serialized = " ".join(result)
        return serialized.replace("'", "%27")

    # -----------------------------------------------------------------------

    @staticmethod
    def format_normalized(result) -> str:
        """Convert the annotation result into an input for the phonetization.

        :return: (str) Sequence of tokens

        """
        serialized = " ".join(result)
        return serialized.replace("'", "%27")

    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_phonetized(result) -> str:
        """Convert the phonetized result into a string.

        The Phonetization result is a list of tuple(token, phones, status).

        :return: (str) Sequence of phonemes

        """
        text = " ".join([p[1] for p in result])
        return "".join(text.strip())

    # -----------------------------------------------------------------------

    @staticmethod
    def format_phonetized(result) -> str:
        """Convert the annotation result into an input for the cuedspeech.

        :return: (str) Sequence of tokens

        """
        formatted_result = list()
        for r in result:
            formatted_result.append((r[0].replace("'", "%27"), r[1]))
        return str(formatted_result)

    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_aligned(result) -> str:
        """Convert the aligned result into a human-readable string.

        :return: (str) Sequence of phonemes

        """
        formatted_result = list()
        for r in result:
            formatted_result.append(r[2].replace("'", "%27"))
        return str(formatted_result)

    # ---------------------------------------------------------------------------

    @staticmethod
    def format_aligned(result) -> str:
        """Convert the aligned result into an input for the cuedspeech.

        :return: (str) Sequence of phonemes

        """
        formatted_result = list()
        for r in result:
            formatted_result.append(r[2].replace("'", "%27"))
        return str(formatted_result)

    # ---------------------------------------------------------------------------

    @staticmethod
    def serialize_cued(result) -> str:
        """Convert the annotation result into a string.

        :param result: list(tuple(keys,phones)
        :return: (str) a string sequence of keys

        """
        s = list()
        for r in result:
            s.append(r[0])
        return " ".join(s)

    # -----------------------------------------------------------------------

    @staticmethod
    def format_cued(result) -> str:
        """Convert the annotation result into an input for the result.

        :param result: list[tuple(keys,phones)]
        :return: (str)

        """
        formatted_result = list()
        for r in result:
            formatted_result.append((r[0].replace("'", "%27"), r[1]))
        return str(formatted_result)
