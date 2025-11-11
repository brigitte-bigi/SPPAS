"""
:filename: sppas.ui.swapp.app_setup.fieldsets.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Create and manage the fieldset' nodes of the setup app.

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

    -------------------------------------------------------------------------

"""

from whakerpy.htmlmaker import HTMLNode

from .fieldsetwelcome import SetupHomeFieldset
from .fieldsetlicense import SetupLicenseFieldset
from .fieldsetfeature import SetupDepsFieldset
from .fieldsetfeature import SetupLangFieldset
from .fieldsetfeature import SetupAnnotFieldset
from .fieldsetfeature import SetupSpinOffFieldset
from .fieldsetinstall import SetupInstallFieldset

# ---------------------------------------------------------------------------


class SetupFieldsets(object):
    """Create all fieldset node instances for the Setup HTML tree.

    """

    def __init__(self, installer):
        """Create a SetupFieldsMaker instance.

        """
        self._installer = installer

        self.__fields = list()
        self.__fields.append(SetupHomeFieldset(None))
        self.__fields.append(SetupLicenseFieldset(None))
        self.__fields.append(SetupDepsFieldset(None, self._installer, "deps"))
        self.__fields.append(SetupLangFieldset(None, self._installer, "lang"))
        self.__fields.append(SetupAnnotFieldset(None, self._installer, "annot"))
        self.__fields.append(SetupSpinOffFieldset(None, self._installer, "spin"))
        self.__fields.append(SetupInstallFieldset(None))

        self.__keys = tuple([f.identifier for f in self.__fields])

    # -----------------------------------------------------------------------

    def get_index(self, field) -> int:
        """Return the index of the given field.

        :param field: (HTMLNode)
        :raises: ValueError: if field is unknown

        """
        return self.__fields.index(field)

    # -----------------------------------------------------------------------

    def get_index_from_name(self, field_name) -> int:
        """Return the index of the given field from its identifier.

        :raises: ValueError: if field_name is unknown

        """
        return self.__keys.index(field_name)

    # -----------------------------------------------------------------------

    def next_field(self, current):
        """Return the next field.

        :return: (HTMLNode) a fieldset

        """
        if isinstance(current, HTMLNode) is False:
            raise TypeError
        if current.identifier not in self.__keys:
            raise KeyError

        # Get the index of the given field and offset it by +1
        next_index = min(self.__keys.index(current.identifier) + 1, len(self.__keys)-1)

        # Return the previous key's value, or the current if no prev
        return self.__fields[next_index]

    # -----------------------------------------------------------------------

    def prev_field(self, current):
        """Return the previous field.

        :return: (HTMLNode) a fieldset

        """
        if isinstance(current, HTMLNode) is False:
            raise TypeError
        if current.identifier not in self.__keys:
            raise KeyError

        # Get the index of the given field and offset it by -1
        prev_index = max(0, self.__keys.index(current.identifier) - 1)

        # return the next key's value, or the current if no next
        return self.__fields[prev_index]

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __contains__(self, field):
        return field in self.__fields

    def __iter__(self):
        for f in self.__fields:
            yield f

    def __getitem__(self, i):
        return self.__fields[i]

    def __len__(self):
        return len(self.__keys)

    def __index__(self, field):
        return self.__fields.index(field)
