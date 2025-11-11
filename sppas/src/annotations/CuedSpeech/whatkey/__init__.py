"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Cued Speech keys predictor. Answer the "What?" question.

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

from .whatkeyexc import sppasCuedRulesValueError
from .whatkeyexc import sppasCuedRulesMinValueError
from .whatkeyexc import sppasCuedRulesMaxValueError
from .keysrules import CuedSpeechCueingRules
from .phonestokeys import CuedSpeechKeys
from .whatkey import sppasWhatKeyPredictor


__all__ = (
    "sppasCuedRulesValueError",
    "sppasCuedRulesMinValueError",
    "sppasCuedRulesMaxValueError",
    "CuedSpeechCueingRules",
    "CuedSpeechKeys",
    "sppasWhatKeyPredictor"
)
