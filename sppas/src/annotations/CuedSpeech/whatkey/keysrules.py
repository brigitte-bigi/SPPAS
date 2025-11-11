# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.keysrules.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Manage a file with cueing rules.

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
import os

from sppas.core.config import symbols
from sppas.core.config import separators
from sppas.core.coreutils import sppasUnicode
from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasIOError

from .whatkeyexc import sppasCuedRulesValueError
from .whatkeyexc import sppasCuedRulesMinValueError
from .whatkeyexc import sppasCuedRulesMaxValueError

# ----------------------------------------------------------------------------


class CuedSpeechCueingRules(object):
    """Rules data structure for a system to predict Cued Speech keys.

    Format of the rules:

    NEUTRAL_CLASS i V
    NEUTRAL_CLASS e V
    NEUTRAL_CLASS aU W
    ...
    NEUTRAL_CLASS p C
    NEUTRAL_CLASS t C
    ...
    PHONKEY i m
    PHONKEY e t
    PHONKEY p 1
    PHONKEY t 5
    ...
    NEUTRAL_CLASS cnil N
    NEUTRAL_CLASS vnil N
    PHONKEY cnil 5
    PHONKEY vnil s
    ...
    SHAPETARGET 0 5
    SHAPETARGET 1 8
    SHAPETARGET 2 12

    :Example:
        >>> rules = CuedSpeechCueingRules()
        >>> result = rules.load(FRA_KEYS)
        >>> assert(result is True)
        >>> rules.get_key("e")
        "t"

    """
    
    # List of all accepted phoneme class identifiers
    PHON_CLASSES = ["N", "C", "V", "W"]

    # A class for a non-phoneme sound or a pause or a silence
    NEUTRAL_CLASS = "N"

    # Default target
    SHAPE_TARGET = 12

    # -----------------------------------------------------------------------

    def __init__(self, filename:str | None = None):
        """Create a new instance.

        :param filename: (str) Name of the file with the rules.

        """
        # key = phoneme or symbol;
        # value = tuple(class, shape or position code)
        self.__phon = dict()
        # key = shape code
        # value = target on the hand
        self.__shptgt = dict()

        if filename is not None:
            self.load(filename)
        else:
            self.reset()

    # ------------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the set of rules.

        """
        self.__phon = dict()
        self.__shptgt = dict()

        for phone in symbols.all:
            self.__phon[phone] = (CuedSpeechCueingRules.NEUTRAL_CLASS, None)

        # neutral position and shape is a system-dependent coding scheme
        # (but not language-dependent)
        self.__phon["vnone"] = (CuedSpeechCueingRules.NEUTRAL_CLASS, "n")
        self.__phon["cnone"] = (CuedSpeechCueingRules.NEUTRAL_CLASS, "0")

        # a missing consonant or vowel is a language-dependent key code
        # but the class has to be added.
        self.__phon["vnil"] = (CuedSpeechCueingRules.NEUTRAL_CLASS, None)
        self.__phon["cnil"] = (CuedSpeechCueingRules.NEUTRAL_CLASS, None)

    # ------------------------------------------------------------------------

    def load(self, filename: str) -> bool:
        """Load the rules from a file.

        Invalidate the already defined set of rules.

        :param filename: (str) Name of the file with the rules.
        :raises: sppasIOError: If the file cannot be opened.
        :raises: sppasError: File is not a regular Cued Speech file.
        :return: (bool) Rules were appended or not

        """
        self.reset()
        
        if os.path.exists(filename) is True and os.path.isfile(filename):
            with open(filename, "r") as f:
                lines = f.readlines()
                f.close()
        else:
            raise sppasIOError(filename)

        added = False
        for line_nb, line in enumerate(lines, 1):
            sp = sppasUnicode(line)
            line = sp.to_strip()
            # Ignore comments
            if line.startswith("#") is True:
                continue

            # Regular rules of all made of 3 columns
            columns = line.split()
            if len(columns) == 3:
                # The string representing the phoneme is the key of the self.__phon dict.
                p = columns[1]
                if p not in self.__phon:
                    # create a new entry in the dictionary of phonemes
                    self.__phon[p] = (None, None)

                # fill-in the value of the phoneme entry in the dict
                tup = self.__phon[p]
                if columns[0] == "PHONCLASS":
                    if columns[2] not in CuedSpeechCueingRules.PHON_CLASSES:
                        raise sppasError("Invalid PHONCLASS. One of {:s} was expected. Got {:s} instead."
                                         "".format(CuedSpeechCueingRules.PHON_CLASSES, columns[2]))
                    # PHONCLASS allows to fill in the phoneme class.
                    if columns[1] not in ("cnone", "vnone"):
                        self.__phon[columns[1]] = (columns[2], tup[1])
                        added = True

                elif columns[0] == "PHONKEY":
                    # PHONKEY allows to fill in the phoneme key
                    if columns[1] not in ("cnone", "vnone"):
                        self.__phon[columns[1]] = (tup[0], columns[2])
                        added = True

                elif columns[0] == "SHAPETARGET":
                    if columns[1] not in self.__shptgt:
                        try:
                            target = int(columns[2])
                            if 0 <= target <= 20:
                                self.__shptgt[columns[1]] = target
                            else:
                                raise sppasError(f"Invalid SHAPETARGET value {target}")
                        except ValueError:
                            # invalid target
                            raise sppasError(f"SHAPETARGET '{columns[2]}' is not an integer for shape {columns[1]}")
                    else:
                        # duplicated entry
                        raise sppasError(f"shape {columns[1]} is already defined.")

        return added

    # ------------------------------------------------------------------------
    # Getters: about the classes
    # ------------------------------------------------------------------------

    def get_class(self, phoneme: str) -> str:
        """Return the class identifier of the phoneme.

        If the phoneme is unknown, the neutral class is returned.

        :param phoneme: (str) A phoneme
        :return: class of the phoneme or neutral class

        """
        tup = self.__phon.get(phoneme, None)
        if tup is None:
            return CuedSpeechCueingRules.NEUTRAL_CLASS
        return tup[0]

    # ------------------------------------------------------------------------
    # Getters about the keys: shape and position
    # ------------------------------------------------------------------------

    def get_vowels_codes(self) -> list:
        """Return the list of key codes of all the positions (vowels).

        """
        vowels_codes = list()
        for phon in self.__phon:
            phon_key = self.get_key(phon)
            if phon_key is not None:
                if self.get_class(phon) == "V":
                    vowels_codes.append(phon_key)
                elif self.get_class(phon) == "W":
                    for key_code in phon_key:
                        vowels_codes.append(key_code)

        # Trick: reverse is true in order to have 'b' of the French LfPC
        # at the last position because it does not exist in English CS.
        # Then, English and French will have the vowels sorted the same...
        return [self.get_neutral_vowel()] + \
               sorted(list(set(vowels_codes)), reverse=True)

    # ------------------------------------------------------------------------

    def get_consonants_codes(self) -> list:
        """Return the list of key codes of all the shapes (consonants).

        """
        cons_codes = list()
        for phon in self.__phon:
            phon_key = self.get_key(phon)
            if self.get_class(phon) == "C" and phon_key is not None:
                cons_codes.append(phon_key)

        return [self.get_neutral_consonant()] + sorted(list(set(cons_codes)))

    # ------------------------------------------------------------------------

    def get_key(self, phoneme: str) -> tuple[str,str] | str | None:
        """Return the key identifier of the phoneme.

        None is returned if the phoneme is unknown or if it is a break.
        If the phoneme is known but no key was defined for this phoneme,
        the "nil" key is returned.

        :param phoneme: (str) A phoneme or a diphthong
        :return: key or tuple(key,key) if diphtong or None if unknown

        """
        if self.get_class(phoneme) == "W":
            return self.get_diphthong_key(phoneme)

        tup = self.__phon.get(phoneme, None)
        if tup is None:
            return None

        # The key like it is defined in the config file
        key = tup[1]

        # If no key was defined for this phoneme, use nil.
        if key is None:
            if tup[0] in ("V", "W"):
                key = self.__phon["vnil"][1]
            elif tup[0] == "C":
                key = self.__phon["cnil"][1]

        return key

    # ------------------------------------------------------------------------

    def get_diphthong_key(self, diphthong: str) -> tuple[str,str] | None:
        """Return the key identifiers of the given diphthong.

        :param diphthong: (str) A diphthong made of 2 phonemes
        :return: tuple(key,key) or None if unknown

        """
        if len(diphthong) == 2:
            tup = self.__phon.get(diphthong[0], None)
            if tup is None:
                return None
            key1 = tup[1]
            tup = self.__phon.get(diphthong[1], None)
            if tup is None:
                return None
            key2 = tup[1]
            return key1, key2

        return None

    # ------------------------------------------------------------------------

    def get_nil_consonant(self) -> str:
        """Return the key code for a missing consonant."""
        return self.__phon['cnil'][1]

    # ------------------------------------------------------------------------

    def get_nil_vowel(self) -> str:
        """Return the key code for a missing vowel."""
        return self.__phon['vnil'][1]

    # ------------------------------------------------------------------------

    def get_neutral_vowel(self) -> str:
        """Return the key code of the neutral position (vowel)."""
        return self.__phon['vnone'][1]

    # ------------------------------------------------------------------------

    def get_neutral_consonant(self) -> str:
        """Return the key code of the neutral shape (consonant)."""
        return self.__phon['cnone'][1]

    # ------------------------------------------------------------------------
    # Getters about the shape targets
    # ------------------------------------------------------------------------

    def get_shape_target(self, shape: str) -> int:
        """Return the target index of the given shape.

        :param shape: (str) Shape code
        :return: (int) target index of the given shape or the default target index

        """
        return self.__shptgt.get(shape, CuedSpeechCueingRules.SHAPE_TARGET)

    # ------------------------------------------------------------------------

    def get_phon_target(self, phoneme: str) -> int:
        """Return the target index of the given phoneme.

        :param phoneme: (str) Shape code
        :return: (int) target index of the given phoneme or the default target index

        """
        _tup = self.__phon.get(phoneme, None)
        if _tup is None:
            return CuedSpeechCueingRules.SHAPE_TARGET
        return self.__shptgt.get(_tup[1], CuedSpeechCueingRules.SHAPE_TARGET)

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def syll_to_key(self, syll: str) -> tuple:
        """Return the key codes matching the given syllable.

        The given entry can be either of the form:
        C-V or C- or C or -V or V.

        :example:
        >>> syll_to_key("-E")
        ('5', 'c')
        >>> syll_to_key("E")
        ('5', 'c')
        >>> syll_to_key("p-")
        ('1', 's')
        >>> syll_to_key("p")
        ('1', 's')
        >>> syll_to_key("p-E")
        ('1', 'c')
        >>> syll_to_key("p-aI")
        (('1', 's'), ('5', 't'))

        :param syll: (str) A syllable like "p-a", or "p-" or "-a" or "p-aI".
        :return: (tuple or None) Key codes
        :raises: sppasCuedRulesValueError: malformed syll
        :raises: sppasCuedRulesMinValueError: not enough phonemes in syll
        :raises: sppasCuedRulesMaxValueError: too many phonemes in syll

        """
        phons = self.__syll_to_phons(syll)
        if self.get_class(phons[0]) not in ("N", "C") or self.get_class(phons[1]) not in ("N", "V", "W"):
            raise sppasCuedRulesValueError(syll)

        key_cons = self.get_key(phons[0])
        key_vowel = self.get_key(phons[1])
        if key_cons is None or key_vowel is None:
            raise sppasCuedRulesValueError(syll)

        if self.get_class(phons[1]) == "W":
            # returns two tuples of key codes
            return (key_cons, key_vowel[0]), (self.get_nil_consonant(), key_vowel[1])

        return key_cons, key_vowel

    # ------------------------------------------------------------------------

    def __syll_to_phons(self, syll: str) -> list[str, str]:
        """Return the phonemes matching the given syllable.

        :return: (tuple) Tuple with (consonant, vowel)
        :raises: sppasCuedRulesValueError: malformed syll
        :raises: sppasCuedRulesMinValueError: not enough phonemes in syll
        :raises: sppasCuedRulesMaxValueError: too many phonemes in syll

        """
        # Check entry length
        if len(syll.strip()) == 0 or syll.strip() == "-":  # at least 1 character
            raise sppasCuedRulesValueError(syll)

        phons = syll.split(separators.phonemes)
        if len(phons) == 0:
            raise sppasCuedRulesMinValueError(syll)
        elif len(phons) == 1:
            if self.get_class(phons[0]) == "V":
                phons.insert(0, "cnil")
            elif self.get_class(phons[0]) == "C":
                phons.append("vnil")
            else:
                phons.insert(0, "unknown")
        elif len(phons) == 2:
            if len(phons[0]) == 0:
                phons[0] = "cnil"
            if len(phons[1]) == 0:
                phons[1] = "vnil"
        else:   # >2
            raise sppasCuedRulesMaxValueError(syll)

        return phons
