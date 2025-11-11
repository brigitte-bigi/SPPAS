# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.structs.basefilters.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Base class for any filter system.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from sppas.core.coreutils import sppasValueError
from sppas.core.coreutils import sppasKeyError

# ---------------------------------------------------------------------------


class sppasBaseFilters(object):
    """Base class for any filter system.

    """

    def __init__(self, obj):
        """Create a sppasBaseFilters instance.

        :param obj: (object) The object to be filtered.

        """
        self.obj = obj

    # -----------------------------------------------------------------------

    @staticmethod
    def test_args(comparator, **kwargs):
        """Raise an exception if any of the args is not correct.

        :param comparator: (sppasBaseComparator)

        """
        names = ["logic_bool", "logic_bool_label"] + \
                comparator.get_function_names()
        for func_name, value in kwargs.items():
            if func_name.startswith("not_"):
                func_name = func_name[4:]

            if func_name not in names:
                raise sppasKeyError("kwargs function name", func_name)

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_logic_bool(**kwargs):
        """Return the value of a logic boolean predicate.

        Expect the "logic_bool" argument.

        :return: (str) "and" or "or". By default, the logical "and" is returned.
        :raise: sppasValueError

        """
        for func_name, value in kwargs.items():
            if func_name == "logic_bool":
                if value not in ['and', 'or']:
                    raise sppasValueError(value, "logic bool")
                return value
        return "and"

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_logic_bool_label(**kwargs):
        """Return the value of a logic boolean predicate.

        Expect the "logic_bool_label" args.

        :return: (str) "all" or "any". By default, "any" is returned.
        :raise: sppasValueError

        """
        for func_name, value in kwargs.items():
            if func_name == "logic_bool_label":
                if value not in ['all', 'any']:
                    raise sppasValueError(value, "logic bool label")
                return value
        return "any"

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_function_values(comparator, **kwargs):
        """Return the list of function names and the expected value.

        :param comparator: (sppasBaseComparator)

        """
        fct_values = list()
        for func_name, value in kwargs.items():
            if func_name in comparator.get_function_names():
                fct_values.append("{:s} = {!s:s}".format(func_name, value))

        return fct_values

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_functions(comparator, **kwargs):
        """Parse the args to get the list of function/value/complement.

        :param comparator: (sppasBaseComparator)

        """
        f_functions = list()
        for func_name, value in kwargs.items():

            logical_not = False
            if func_name.startswith("not_"):
                logical_not = True
                func_name = func_name[4:]

            if func_name in comparator.get_function_names():
                f_functions.append((comparator.get(func_name),
                                    value,
                                    logical_not))

        return f_functions
