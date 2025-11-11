# -*- coding: utf-8 -*-
"""
:filename: sppas.src.wkps.wio.wkpreadwrite.py
:author:   Laurent Vouriot, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A reader/writer of any supported workspace file format.

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

import os
from collections import OrderedDict

from sppas.core.coreutils import IOExtensionError
from sppas.core.coreutils import u
from sppas.src.anndata.anndataexc import AioEncodingError

from .wjson import sppasWJSON
from .wannotationpro import sppasWANT

# ----------------------------------------------------------------------------


class sppasWkpRW(object):
    """A reader/writer of any supported workspace file format.

    """

    WORKSPACE_TYPES = OrderedDict()
    WORKSPACE_TYPES[sppasWJSON().default_extension.lower()] = sppasWJSON
    WORKSPACE_TYPES[sppasWANT().default_extension.lower()] = sppasWANT

    # ------------------------------------------------------------------------

    def __init__(self, filename):
        """Create a workspace reader/writer.

        :param filename: (str)

        """
        self.__filename = u(filename)

    # ------------------------------------------------------------------------

    @staticmethod
    def default_extension():
        """Return the default extension to read/write workspaces."""
        return sppasWJSON().default_extension

    # ------------------------------------------------------------------------

    @staticmethod
    def extensions():
        """Return the list of supported extensions in lower case."""
        return list(sppasWkpRW.WORKSPACE_TYPES.keys())

    # ------------------------------------------------------------------------

    def read(self):
        """Read a workspace from a file.

        :returns: (sppasWkpRW)

        """
        try:
            wkp = sppasWkpRW.create_wkp_from_extension(self.__filename)
            wkp.read(self.__filename)
        except Exception:
            raise

        return wkp

    # ------------------------------------------------------------------------

    @staticmethod
    def create_wkp_from_extension(filename):
        """Return a workspace according to a filename.

        :param filename: (str)
        :returns: sppasBaseWkpIO()

        """
        extension = os.path.splitext(filename)[1][1:]
        extension = extension.lower()

        if extension in sppasWkpRW.extensions():
            return sppasWkpRW.WORKSPACE_TYPES[extension]()

        raise IOExtensionError(filename)

    # ------------------------------------------------------------------------

    def write(self, wkp):
        """Write a workspace into a file.

        :param wkp: (sppasWorkspace) Data to be saved

        """
        wkp_rw = sppasWkpRW.create_wkp_from_extension(self.__filename)
        wkp_rw.set(wkp)

        try:
            wkp_rw.write(self.__filename)
        except UnicodeDecodeError as e:
            raise AioEncodingError(self.__filename, str(e))
        except Exception:
            raise

        return wkp_rw

# ---------------------------------------------------------------------------


class WkpFormatProperty(object):
    """Represent one format and its properties.

    """

    def __init__(self, extension):
        """Create a WkpFormatProperty instance.

        :param extension: (str) File name extension.

        """
        self._extension = extension
        if extension.startswith(".") is False:
            self._extension = "." + extension
        self._instance = sppasWkpRW.WORKSPACE_TYPES[extension.lower()]()
        self._software = self._instance.software

        try:
            self._instance.read("")
        except NotImplementedError:
            self._reader = False
        except Exception:
            self._reader = True
        try:
            self._instance.write("")
        except NotImplementedError:
            self._writer = False
        except Exception:
            self._writer = True

    # -----------------------------------------------------------------------

    def get_extension(self):
        """Return the extension, including the initial dot."""
        return self._extension

    def get_software(self):
        """Return the name of the software matching the extension."""
        return self._software

    def get_reader(self):
        """Return True if SPPAS can read files of the extension."""
        return self._reader

    def get_writer(self):
        """Return True if SPPAS can write files of the extension."""
        return self._writer

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'WkpFormatProperty() of extension {!s:s}' \
               ''.format(self._extension)
