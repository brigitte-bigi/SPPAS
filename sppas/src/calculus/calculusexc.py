"""
:filename: sppas.src.calculus.calculusexc.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Exceptions for the package calculus.

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

from sppas.core.coreutils import error

# -----------------------------------------------------------------------


class VectorsError(Exception):
    """:ERROR 3010:.

    Both vectors p and q must have the same length and
    must contain probabilities.

    """

    def __init__(self):
        self.parameter = error(3010) + (error(3010, "calculus"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ProbabilityError(Exception):
    """:ERROR 3015:.

    Value must range between 0 and 1. Got {:f}.

    """

    def __init__(self, value=None):
        if value is not None:
            value = float(value)
            self.parameter = error(3015) + \
                             (error(3015, "calculus")).format(value=value)
        else:
            self.parameter = error(3015) + \
                             (error(3015, "calculus")).replace("{value}", "")

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class SumProbabilityError(Exception):
    """:ERROR 3016:.

    Probabilities must sum to 1. Got {:f}.

    """

    def __init__(self, value=None):
        if value is not None:
            value = float(value)
            self.parameter = error(3016) + \
                             (error(3016, "calculus")).format(value=value)
        else:
            self.parameter = error(3016) + \
                             (error(3016, "calculus")).replace("{value}", "")

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EuclidianDistanceError(ValueError):
    """:ERROR 3025:.

    Error while estimating Euclidian distances of rows and columns.

    """

    def __init__(self):
        self.parameter = error(3025) + (error(3025, "calculus"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class EmptyError(Exception):
    """:ERROR 3030:.

    The given data must be defined or must not be empty.

    """

    def __init__(self):
        self.parameter = error(3030) + (error(3030, "calculus"))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class InsideIntervalError(ValueError):
    """:ERROR 3040:.

     Value {value} is out of range: expected value in range
     [{min_value},{max_value}].

     """

    def __init__(self, value, min_value, max_value):
        min_value = int(min_value)
        max_value = int(max_value)
        value = int(value)
        self.parameter = error(3040) + \
                         (error(3040, "calculus")).format(
                             value=value,
                             min_value=min_value,
                             max_value=max_value)

    def __str__(self):
        return repr(self.parameter)
