# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.config.trash.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  The application trash for backup files.

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

import os
import time
import logging
import shutil

from sppas.core.config.settings import paths

# ---------------------------------------------------------------------------


class sppasTrash(object):
    """Utility manager of the Trash of SPPAS.

    """

    def __init__(self):
        """Create a sppasTrash instance.

        Create the trash directory if not already existing.

        """
        self._trash_dir = paths.trash
        if os.path.exists(self._trash_dir) is False:
            os.mkdir(self._trash_dir)

    # -----------------------------------------------------------------------

    def is_empty(self):
        """Return True if the trash is empty."""
        return len(os.listdir(self._trash_dir)) == 0

    # -----------------------------------------------------------------------

    def do_empty(self):
        """Empty the trash, i.e. definitely delete all files."""
        for f in os.listdir(self._trash_dir):
            full_name = os.path.join(self._trash_dir, f)
            if os.path.isdir(full_name):
                shutil.rmtree(full_name)
            if os.path.isfile(full_name):
                os.remove(full_name)

    # -----------------------------------------------------------------------

    def put_file_into(self, filename):
        """Put a file into the trash.

        :param filename: (str)
        :returns: Full name of the file in the trash
        :raises: PermissionError

        """
        fn, fe = os.path.splitext(os.path.basename(filename))
        now = time.strftime("-%a-%d-%b-%Y_%H%M%S_0000", time.localtime())
        if os.path.exists(filename):
            trashname = os.path.join(self._trash_dir, fn+now+fe)
            try:
                shutil.move(filename, trashname)
            except PermissionError as e:
                logging.error("Can't put {} into the trash: {}"
                              "".format(filename, str(e)))
                raise

        else:
            return ""

        return trashname

    # -----------------------------------------------------------------------

    def put_folder_into(self, folder):
        """Put a folder into the trash.

        :param folder: (str)

        """
        now = time.strftime("-%a-%d-%b-%Y_%H%M%S_0000", time.localtime())
        shutil.move(folder, os.path.join(self._trash_dir, now))
