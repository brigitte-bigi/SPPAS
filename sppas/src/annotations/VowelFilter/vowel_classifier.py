# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.VowelFilter.vowel_classifier.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Class name of the vowels to be filtered.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasPoint

# ---------------------------------------------------------------------------


class VowelClassifier:
    """Assign a class name to the vowels of a tier of formant values.

    A vowel class gathers the tokens sharing the same expected acoustic
    values. By default, a class is a phoneme. Given a tier with time-aligned
    syllables, a class is a phoneme and its position in the syllable: the
    acoustic values of a vowel closing its syllable are not the expected
    ones of the same vowel followed by a coda.

    :example:
    >>> classifier = VowelClassifier()
    >>> classifier.get_class(ann)
    'a'
    >>> classifier = VowelClassifier(syll_tier)
    >>> classifier.get_class(ann)
    'aC'

    """

    # Symbol appended to the phoneme when the vowel closes its syllable
    OPEN_SYMBOL = "#"

    # Symbol appended to the phoneme when a coda follows the vowel
    CODA_SYMBOL = "C"

    # -----------------------------------------------------------------------

    def __init__(self, syll_tier: sppasTier = None):
        """Create a VowelClassifier instance.

        :param syll_tier: (sppasTier) Tier with time-aligned syllables, or None
        :raises: TypeError: The given tier is not with intervals

        """
        if syll_tier is not None:
            if isinstance(syll_tier, sppasTier) is False:
                raise TypeError("Expected a sppasTier of syllables. "
                                "Got {:s} instead.".format(str(type(syll_tier))))
            if syll_tier.is_interval() is False:
                raise TypeError("Expected a tier of syllables with intervals.")

        self.__syll_tier = syll_tier

    # -----------------------------------------------------------------------

    def get_class(self, ann: sppasAnnotation) -> str:
        """Return the class name of the given annotation of formant values.

        The phoneme of an annotation of formant values is the key of its
        label. An empty class name is returned if the label has no key,
        i.e. if the annotation is not the one of an identified phoneme.

        :param ann: (sppasAnnotation) Annotation with formant values
        :return: (str) Name of the class of the vowel

        """
        _labels = ann.get_labels()
        if len(_labels) == 0:
            return ""

        _phoneme = _labels[0].get_key()
        if _phoneme is None:
            return ""

        if self.__syll_tier is None:
            return _phoneme

        return _phoneme + self.__coda_symbol(ann)

    # -----------------------------------------------------------------------

    def __coda_symbol(self, ann: sppasAnnotation) -> str:
        """Return the symbol of the position of the vowel in its syllable.

        No symbol is returned if the vowel is not inside a syllable: its
        position is unknown, so it can't be compared to the other vowels.

        :param ann: (sppasAnnotation) Annotation with formant values
        :return: (str) Symbol of the position, or an empty string

        """
        _begin = ann.get_lowest_localization().get_midpoint()
        _end = ann.get_highest_localization().get_midpoint()

        _index = self.__syll_tier.mindex(sppasPoint((_begin + _end) / 2.), bound=0)
        if _index == -1:
            return ""

        _syllable = self.__syll_tier[_index]
        if _syllable.get_highest_localization().get_midpoint() <= _end:
            return VowelClassifier.OPEN_SYMBOL

        return VowelClassifier.CODA_SYMBOL
