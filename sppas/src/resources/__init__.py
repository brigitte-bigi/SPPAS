# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.resources.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Resource models of SPPAS.

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

*****************************************************************************
resources: access and manage linguistic resources
*****************************************************************************

This package includes classes to manage the data of linguistic types like
lexicons, pronunciation dictionaries, patterns, etc.

Requires the following other packages:

* config

"""

from .dictpron import sppasDictPron
from .dictrepl import sppasDictRepl
from .mapping import sppasMapping
from .wordstrain import sppasWordStrain
from .patterns import sppasPatterns
from .unigram import sppasUnigram
from .vocab import sppasVocabulary
from .dumpfile import sppasDumpFile
from .hand import sppasHandResource

__all__ = (
    "sppasMapping",
    "sppasDictRepl",
    "sppasDictPron",
    "sppasWordStrain",
    "sppasPatterns",
    "sppasUnigram",
    "sppasVocabulary",
    "sppasDumpFile",
    "sppasHandResource"
)
