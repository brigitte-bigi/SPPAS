# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Cued Speech Hand transitions predictor. Answer the "When?" question.

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

    ---------------------------------------------------------------------

"""

# Each transition predictor
from .transition import BaseWhenTransitionPredictor
from .transition import WhenTransitionPredictorDuchnowski1998
from .transition import WhenTransitionPredictorAttina
from .transition import WhenTransitionPredictorRules
# A manager of predictors
from .transitions import WhenTransitionPredictor
# An interface between the predictor manager and the annotated data
from .whenhandtrans import sppasWhenHandTransitionPredictor

__all__ = (
    "BaseWhenTransitionPredictor",
    "WhenTransitionPredictorDuchnowski1998",
    "WhenTransitionPredictorAttina",
    "WhenTransitionPredictorRules",
    "sppasWhenHandTransitionPredictor"
)
