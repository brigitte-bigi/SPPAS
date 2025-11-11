"""
:filename: sppas.src.utils.utilsexc.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Exceptions for utils package.

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


class UtilsDataTypeError(TypeError):
    """:ERROR 7010:.

    Expected a {data_name} of type {expected_type}. Got {data_type} instead.

    """

    def __init__(self, data_name, expected_type, data_type):
        self.parameter = error(7010) + \
                         (error(7010, "utils")).format(
                             data_name=data_name,
                             expected_type=expected_type,
                             data_type=data_type)

    def __str__(self):
        return repr(self.parameter)
