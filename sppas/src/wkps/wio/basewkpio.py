# -*- coding: utf-8 -*-
"""
:filename: sppas.src.wkps.wio.basewkpio.py
:author:   Laurent Vouriot, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Base class for any reader and writer of a workspace.

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

from sppas.core.coreutils import sppasTypeError

from ..workspace import sppasWorkspace

# ---------------------------------------------------------------------------


class sppasBaseWkpIO(sppasWorkspace):
    """Base class for any reader-writer of a workspace.

    """

    def __init__(self, name=None):
        """Initialize a new workspace reader-writer instance.

        :param name: (str) A workspace name

        """
        super(sppasBaseWkpIO, self).__init__(name)

        self.default_extension = None
        self.software = "und"

    # -----------------------------------------------------------------------

    @staticmethod
    def detect(filename):
        """Check whether a file is of an appropriate format or not."""
        return False

    # -----------------------------------------------------------------------

    def set(self, wkp):
        """Set the current workspace with the content of another one.

        :param wkp: (sppasWorkspace)

        """
        if isinstance(wkp, sppasWorkspace) is False:
            raise sppasTypeError(type(wkp), "sppasWorkspace")

        self._id = wkp.get_id()
        for reference in wkp.get_refs():
            self.add_ref(reference)
        for filepath in wkp.get_paths():
            self.add(filepath)

    # -----------------------------------------------------------------------
    # Read/Write
    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a file and fill the workspace.

        :param filename: (str)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a workspace into a file.

        :param filename: (str)

        """
        raise NotImplementedError
