# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.ReOccurrences.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Re-Occurrences detection.

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

This annotation is searching for re-occurrences of an annotation of a
speaker in the next N annotations of the interlocutor. It was originally
used on annotation gestures in (M. Karpinski et al. 2018):

    | Maciej Karpinski, Katarzyna Klessa
    | Methods, Tools and Techniques for Multimodal Analysis of
    | Accommodation in Intercultural Communication
    | CMST 24(1) 29–41 (2018), DOI:10.12921/cmst.2018.0000006

"""

from .reoccurrences import ReOccurences
from .sppasreocc import sppasReOcc

__all__ = (
    "ReOccurences",
    "sppasReOcc"
)
