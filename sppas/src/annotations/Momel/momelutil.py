"""
:filename: sppas.src.annotations.Align.tracksio.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  utilities for momel

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
from random import randrange


def quicksortcib(ciblist):
    """Implement quicksort (ie "partition-exchange" sort).
        that makes on average, O(n log n) comparisons to sort n items.
        This solution benefits from "list comprehensions", which keeps
        the syntax concise and easy to read.
        Quicksort dedicated to a list of Targets.
    """
    # an empty list is already sorted, so just return it
    if len(ciblist) == 0:
        return ciblist

    # Select a random pivot value and remove it from the list
    pivot = ciblist.pop(randrange(len(ciblist)))
    # Filter all items less than the pivot and quicksort them
    lesser = quicksortcib([l for l in ciblist if l.get_x() < pivot.get_x()])
    # Filter all items greater than the pivot and quicksort them
    greater = quicksortcib([l for l in ciblist if l.get_x() >= pivot.get_x()])
    # Return the sorted results
    return lesser + [pivot] + greater
