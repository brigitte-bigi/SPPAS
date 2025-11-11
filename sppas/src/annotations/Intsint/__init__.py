# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.Intsint.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  INTSINT automatic annotation.

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

INTSINT is an acronym for INternational Transcription System for INTonation.
It was originally developed by Daniel Hirst in his 1987 thesis as a
prosodic equivalent of the International Phonetic Alphabet, and the
INTSINT alphabet was subsequently used in Hirst & Di Cristo (eds) 1998
in just over half of the chapters.

INTSINT codes the intonation of an utterance by means of an alphabet of
8 discrete symbols constituting a surface phonological representation
of the intonation:

    T (Top),
    H (Higher),
    U (Upstepped),
    S (Same),
    M (mid),
    D (Downstepped),
    L (Lower),
    B (Bottom).

These tonal symbols are considered phonological in that they represent
discrete categories and surface since each tonal symbol corresponds to
a directly observable property of the speech signal.

INTSINT is computed from a set of selected F0 anchors. The implementation
into SPPAS corresponds to the most recent version of the algorithm:

    | De Looze, Céline & Hirst, Daniel. (2010).
    | Integrating changes of register into automatic intonation analysis.
    | Proceedings of the Fifth International Conference on Speech Prosody,
    | Chicago

"""

from .intsint import Intsint
from .sppasintsint import sppasIntsint

__all__ = (
    "Intsint",
    "sppasIntsint"
)
