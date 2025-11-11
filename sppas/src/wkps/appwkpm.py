# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.wkps.appwkpm.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  The application workspaces manager.

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

from sppas.src.wkps.sppasWkps import sppasWkps

# ---------------------------------------------------------------------------


class sppasWkpsManager(object):
    """Manager of the data of the currently enabled workspace.

    Among the list of available workspaces in the software, this class allows
    to manage this list and to enable any of them.

    """

    def __init__(self, wkp_index=0):
        # Load the list of available workspaces in SPPAS.
        self.__wkps = sppasWkps()
        # Ensure at least one workspace is available. Add a Blank one if needed.
        if len(self.__wkps) == 0:
            self.__wkps.new("Blank")

        # The data (a workspace) this page is working on
        self.data = None
        self.__current = self.load_data(wkp_index)

    # -----------------------------------------------------------------------
    # Public methods to access the data
    # -----------------------------------------------------------------------

    def load_data(self, index=None):
        """Set the data saved of the current workspace.

        If the file of the workspace does not exist, return an empty
        instance of sppasWorkspace.

        :param index: (int) Index of the workspace to get data
        :returns: (int) Index of the loaded workspace
        :raises: IndexError

        """
        if index is None:
            index = self.__current
        self.data = self.__wkps.load_data(index)
        return index

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the number of workspaces.

        :returns: (int)

        """
        return len(self.__wkps)

    # -----------------------------------------------------------------------

    def get_wkp_name(self, index=None):
        """Return the name of the current workspace.

        :param index: (int) Index of the workspace to get name
        :returns: (str)

        """
        if index is None:
            index = self.__current
        return self.__wkps[index]

    # -----------------------------------------------------------------------

    def get_wkp_index(self, name):
        """Return the index of the given workspace name.

        :param name: (str) Workspace name
        :returns: (int)
        :raises: (ValueError)

        """
        return self.__wkps.index(name)

    # -----------------------------------------------------------------------

    def get_wkp_current_index(self):
        """Return the index of the current workspace.

        :returns: (int)

        """
        return self.__current

    # -----------------------------------------------------------------------

    def switch_to(self, index):
        """Set the current workspace at the given index.

        :param index: (int) Index of the workspace to switch on

        """
        # check if the given index is a valid one - raise if not!
        wkp_name = self.__wkps[index]

        # assign the new workspace
        self.__current = index
        self.load_data()

    # -----------------------------------------------------------------------

    def pin(self, new_name):
        """Append a new empty workspace and set it the current one.

        :param new_name: (str) Name of the new workspace.

        """
        new_name = self.__wkps.new(new_name)
        index = self.__wkps.index(new_name)
        self.switch_to(index)

    # -----------------------------------------------------------------------

    def import_from(self, filename):
        """Append a new imported workspace.

        A ".wjson" extension is expected.

        :param filename: (str) Name of the file to import.

        """
        try:
            with open(filename, 'r'):
                pass
        except IOError:
            raise  # TODO: raise a sppasIOError (to get translation!)
        wkp_name = self.__wkps.import_from_file(filename)

    # -----------------------------------------------------------------------

    def export_to(self, filename):
        """Save the current workspace into an external file.

        A ".wjson" extension is expected but not verified.

        :param filename: (str) Name of the exported file.

        """
        self.__wkps.export_to_file(self.__current, filename)

    # -----------------------------------------------------------------------

    def rename(self, new_name):
        """Set a new name to the current workspace.

        :param new_name: (str) New name to assign to the workspace.

        """
        # rename the workspace
        u_name = self.__wkps.rename(self.__current, new_name)

    # -----------------------------------------------------------------------

    def save(self, data, index=None):
        """Save the given data to the active workspace or to the given one.

        :param data: (sppasWorkspace)
        :param index: (int) Save data to the workspace with this index
        :raises: IndexError, IOError

        """
        if index is None:
            index = self.__current

        self.__wkps.save_data(data, index)

    # -----------------------------------------------------------------------

    def remove(self, index):
        """Remove a workspace of the list and delete the corresponding file.

        :param index: (int)

        """
        if index == self.__current:
            # TODO: custom error sppasWkpIndexError (mainly to get translation)
            raise IndexError("The currently displayed workspace can't be removed")

        if index == 0:
            # TODO: custom error sppasWkpIndexError (mainly to get translation)
            raise IndexError("The 'Blank' workspace can't be removed")

        # Delete of the list
        self.__wkps.delete(index)
