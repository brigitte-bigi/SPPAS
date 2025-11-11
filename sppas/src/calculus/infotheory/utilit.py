# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.infotheory.utilit.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Utilities for the information theory package.

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

"""

import math

MAX_NGRAM = 8

# ----------------------------------------------------------------------------


def log2(x):
    """Estimate log in base 2.

    :param x: (int, float) value
    :returns: (float)
    """
    x = float(x)
    return math.log(x)/math.log(2)

# ----------------------------------------------------------------------------


def find_ngrams(symbols, ngram):
    """Return a list of n-grams from a list of symbols.

    :param symbols: (list)
    :param ngram: (int) n value for the ngrams
    :returns: list of tuples

    Example:

        >>>symbols=[0,1,0,1,1,1,0]
        >>>print(find_ngrams(symbols, 2))
        >>>[(0, 1), (1, 0), (0, 1), (1, 1), (1, 1), (1, 0)]

    """
    return zip(*[symbols[i:] for i in range(ngram)])

# ----------------------------------------------------------------------------


def symbols_to_items(symbols, ngram):
    """Convert a list of symbols into a dictionary of items.

    Example:

        >>>symbols=[0, 1, 0, 1, 1, 1, 0]
        >>>print symbols_to_items(symbols,2)
        >>>{(0, 1): 2, (1, 0): 2, (1, 1): 2}

    :returns: dictionary with key=tuple of symbols, value=number of occurrences

    """
    nsymbols = find_ngrams(symbols, ngram)

    exr = dict()
    for each in nsymbols:
        v = 1 + exr.get(each, 0)
        exr[each] = v

    return exr
