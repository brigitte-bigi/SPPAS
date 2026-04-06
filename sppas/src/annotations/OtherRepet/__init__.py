# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.OtherRepet.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Other-Repetitions detection.

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

This package is the implementation of the following reference:

    | Brigitte Bigi, Roxane Bertrand, Mathilde Guardiola (2014).
    | Automatic detection of other-repetition occurrences:
    | application to French conversational speech,
    | 9th International conference on Language Resources and
    | Evaluation (LREC), Reykjavik (Iceland), pp. 2648-2652.
    | ISBN: 978-2-9517408-8-4.

"""

from .rules import OtherRules
from .sppasrepet import sppasOtherRepet

__all__ = (
    "OtherRules",
    'sppasOtherRepet'
)
