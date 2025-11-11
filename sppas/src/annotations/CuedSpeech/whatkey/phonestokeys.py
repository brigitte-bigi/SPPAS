# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.phonestokeys.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Apply Cued Speech rules to a sequence of phonemes.

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
from sppas.core.config import separators

from .keysrules import CuedSpeechCueingRules

# ----------------------------------------------------------------------------


class CuedSpeechKeys(CuedSpeechCueingRules):
    """Cued Speech keys generation from a sequence of phonemes.

    :Example:

        >>> # Define the input: a list of phonemes
        >>> phonemes = ["#", "s", "p", "a", "s"]
        >>> # Create the instance
        >>> self.lfpc = CuedSpeechKeys(FRA_KEYS)
        >>> # Apply the rules to get result in various formats
        >>> sgmts = self.lfpc.syllabify(phonemes)
        >>> [(1, 1), (2, 3), (4, 4)]
        >>> phons = self.lfpc.phonetize_syllables(phonemes, sgmts)
        >>> "s-vnil.p-a.s-vnil"
        >>> keys = self.lfpc.keys_phonetized(phons)
        >>> "3-s.1-s.3-s"

    """

    def __init__(self, keyrules_filename:str | None = None):
        """Create a new instance.

        Load keys from a text file, depending on the language and phonemes
        encoding. See documentation for details about this file.

        :param keyrules_filename: (str) Name of the file with the list of keys.

        """
        super(CuedSpeechKeys, self).__init__(keyrules_filename)

    # -----------------------------------------------------------------------

    def syllabify(self, phonemes: list) -> list:
        """Return the key boundaries of a sequence of phonemes.

        Perform the segmentation of the sequence of phonemes into the
        syllables-structure of the Cued Speech coding scheme.
        A syllable structure is CV, or V or C.

        >>> phonemes = ['b', 'O~', 'Z', 'u', 'R']
        >>> CuedSpeechKeys("fra-config-file").syllabify(phonemes)
        >>> [ (0, 1), (2, 3), (4, 4) ]

        :param phonemes: (list of str) List of phonemes
        :returns: list of tuples (begin index, end index)

        """
        # Convert a list of phonemes into a list of key classes.
        classes = [self.get_class(p) for p in phonemes]
        syll = list()

        i = 0
        while i < len(phonemes):
            c = classes[i]
            # Syllables are made of phonemes exclusively, i.e. 'C','V','W' classes.
            if c in ("W", "V", "C"):
                if c in ("V", "W") or i + 1 == len(phonemes):
                    # Either the current phoneme is a vowel
                    # or it's the last in the list.
                    syll.append((i, i))         # V (or C if last phoneme)
                else:
                    # The current phoneme is a consonant.
                    # See the next one to decide what is the segmentation.
                    c_next = classes[i+1]
                    if c_next in ("V", "W"):
                        # The next phoneme is a vowel.
                        syll.append((i, i+1))    # CV
                        i += 1
                    else:
                        # Both cases:
                        #  - the next phoneme is a consonant
                        #  - the next phoneme is neither a vowel nor a consonant.
                        syll.append((i, i))      # C
            i += 1

        return syll

    # -----------------------------------------------------------------------
    # Output formatting
    # -----------------------------------------------------------------------

    def phonetize_syllables(self, phonemes: list, syllables: list) -> str:
        """Return the phonetized sequence of syllables.

        The output string is using the X-SAMPA standard to indicate the
        phonemes and syllables segmentation.

        :example:
        >>> phonemes = ['b', 'O~', 'Z', 'u', 'R']
        >>> lpc_keys = CuedSpeechKeys("fra-config-file")
        >>> syllables = lpc_keys.syllabify(phonemes)
        >>> [ (0, 1), (2, 3), (4, 4) ]
        >>> lpc_keys.phonetize_syllables(phonemes, syllables)
        >>> "b-O~.Z-u.R-vnone"

        :param phonemes: (list) List of phonemes
        :param syllables: list of tuples (begin index, end index)
        :return: (str) String representing the syllables segmentation

        """
        str_syll = list()
        for (begin, end) in syllables:
            if begin == end:
                p = phonemes[begin]
                if self.get_class(p) in ("V", "W"):
                    str_syll.append("cnil" + separators.phonemes + p)
                else:
                    str_syll.append(p + separators.phonemes + "vnil")
            else:
                str_syll.append(separators.phonemes.join(phonemes[begin:end+1]))

        return separators.syllables.join(str_syll)

    # -----------------------------------------------------------------------

    def keys_phonetized(self, phonetized_syllables: str) -> str:
        """Return the keys of a phonetized syllable as C-V sequences.

        The input string is using the X-SAMPA standard to indicate the
        phonemes and syllables segmentation.

        >>> phonetized_syllable = "e.p-a.R"
        >>> lpc_keys = CuedSpeechKeys("fra-config-file")
        >>> lpc_keys.keys_phonetized(phonetized_syllable)
        >>> "0-t.1-s.3-s"

        :param phonetized_syllables: (str) String representing the keys segments
        :return: (str)

        """
        key_codes = list()
        for syll in phonetized_syllables.split(separators.syllables):
            try:
                phones = syll.split(separators.phonemes)
                if len(phones) == 2:
                    if self.get_class(phones[1]) == "W":
                        (c1, v1), (c2, v2) = self.syll_to_key(syll)
                        key_codes.append(c1 + separators.phonemes + v1)
                        key_codes.append(c2 + separators.phonemes + v2)
                    else:
                        consonant, vowel = self.syll_to_key(syll)
                        key_codes.append(consonant + separators.phonemes + vowel)
                else:
                    logging.error("Syllables must have two phonemes. Ignored: %s", syll)
            except ValueError as e:
                logging.warning(str(e))
                key_codes.append(separators.phonemes)

        return separators.syllables.join(key_codes)
