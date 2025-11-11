# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Cued Speech position predictor. Answer the "Where?" question.

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

This is a Proof of Concept.
==========================

This is a package to predict the position (x,y) of points S0 and S9 of the
hand for each image of the video. It requires:

- 68 sights of the face of each image. If missing, a "standard" face
  is used with size 1000x1000px.
-


"""

from .faceheight import sppasFaceHeight
from .position import FaceTwoDim
from .wherecueexc import sppasWhereCuedSightsValueError
from .wherecue import sppasWhereCuePredictor

__all__ = (
    "sppasFaceHeight",
    "sppasWhereCuedSightsValueError",
    "sppasWhereCuePredictor"
)
