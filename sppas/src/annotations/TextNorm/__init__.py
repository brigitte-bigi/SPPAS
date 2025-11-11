"""
:filename: sppas.src.annotations.TextNorm.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Text Normalization automatic annotation.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

The creation of text corpora requires a sequence of processing steps in
order to constitute, normalize, and then to directly exploit it by a given
application.
This package implements a generic approach for text normalization that can
be applied on a multipurpose multilingual text or transcribed corpus.
It consists in splitting the text normalization problem in a set of minor
sub-problems as language-independent as possible. The portability to a new
language consists of heritage of all language independent methods and
rapid adaptation of other language dependent methods or classes.

For details, read the following reference:

    | Brigitte Bigi (2011).
    | A Multilingual Text Normalization Approach.
    | 2nd Less-Resourced Languages workshop,
    | 5th Language & Technology Conference, Poznan (Poland).

"""

from .orthotranscription import sppasOrthoTranscription
from .splitter import sppasSimpleSplitter
from .tokenize import sppasTokenSegmenter
from .normalize import TextNormalizer
from .tiernorm import TierNormalizer
from .cutparser import TextCutParser
from .sppastextnorm import sppasTextNorm

__all__ = (
    'sppasOrthoTranscription',
    'sppasSimpleSplitter',
    'sppasTokenSegmenter',
    'TextNormalizer',
    'TextCutParser',
    'TierNormalizer',
    'sppasTextNorm',
)
