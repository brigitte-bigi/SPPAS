# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TGA.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Time-Group Analyzer automatic annotation.

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

TGA: Time Group Analyzer is an online tool for speech annotation mining
written by Dafydd Gibbon, emeritus professor of English and General
Linguistics at Bielefeld University..

TGA software calculates, inter alia, mean, median, rPVI, nPVI, slope and
intercept functions within inter-pausal groups.

For details, read the following reference:
    | Dafydd Gibbon (2013).
    | TGA: a web tool for Time Group Analysis.
    | Tools ans Resources for the Analysis of Speech Prosody,
    | Aix-en-Provence, France, pp. 66-69.

See also: <http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>

"""

from .timegroupanalysis import TimeGroupAnalysis
from .sppastga import sppasTGA

__all__ = (
    "TimeGroupAnalysis",
    "sppasTGA"
)
