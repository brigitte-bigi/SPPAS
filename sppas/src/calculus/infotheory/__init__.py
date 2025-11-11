# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.infotheory.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for information theory calculus.

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

Information Theory is a scientific fields that started with the Claude
Shannon's 1948 paper: *“A Mathematical  Theory  of  Communication”*
published in the Bell Systems Technical Journal.
There are several major concepts in this paper, including:

1. every communication channel has a speed limit, measured in binary
digits per second,
2. the architecture and design of communication systems,
3. source coding, i.e. the efficiency of the data representation
(remove redundancy in the information to make the message smaller)

"""

from .entropy import sppasEntropy
from .kullbackleibler import sppasKullbackLeibler
from .perplexity import sppasPerplexity
from .utilit import find_ngrams, symbols_to_items

__all__ = [
        "sppasEntropy",
        "sppasKullbackLeibler",
        "sppasPerplexity",
        "find_ngrams",
        "symbols_to_items"
]
