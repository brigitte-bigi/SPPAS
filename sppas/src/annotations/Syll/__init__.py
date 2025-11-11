# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.Syll.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Syllabification rule system.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

The syllabification of phonemes is performed with a rule-based system.
This RBS phoneme-to-syllable segmentation system is based on 2 main
principles:

    - a syllable contains a vowel, and only one.
    - a pause is a syllable boundary.

These two principles focus the problem of the task of finding a syllabic
boundary between two vowels.
As in state-of-the-art systems, phonemes were grouped into classes and
rules established to deal with these classes.

For details, read the following reference:

    | B. Bigi, C. Meunier, I. Nesterenko, R. Bertrand (2010).
    | Automatic detection of syllable boundaries in spontaneous speech.
    | In Language Resource and Evaluation Conference, pp. 3285–3292,
    | La Valetta, Malta.

"""

from .rules import SyllRules
from .syllabify import Syllabifier
from .sppassyll import sppasSyll

__all__ = (
    'SyllRules',
    'Syllabifier',
    'sppasSyll'
)
