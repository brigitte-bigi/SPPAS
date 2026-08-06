# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.VowelFilter.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Filtering of the erroneous formant values of a corpus.

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

    ---------------------------------------------------------------------

This package is filtering the erroneous formant values of a set of files,
with the Mahalanobis distance of the tokens to the mean values of their
vowel class, as proposed by:

    | M. Lancien, J. Stuart-Smith, M. Adda-Decker (2023).
    | Using Mahalanobis distance to filter erroneous vowel features in
    | less-resourced languages: application to Quebec French.
    | In Proceedings of the 20th International Congress of Phonetic
    | Sciences, Prague, Czech Republic.

No required other package.

"""

from .vowel_classifier import VowelClassifier
from .vowel_profiles import VowelProfiles
from .vowel_filter import VowelFilterEstimator
from .sppasvowelfilter import sppasVowelFilter

__all__ = (
    "VowelClassifier",
    "VowelProfiles",
    "VowelFilterEstimator",
    "sppasVowelFilter"
)
