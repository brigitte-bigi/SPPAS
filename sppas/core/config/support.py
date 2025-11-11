# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.config.support.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Support of SPPAS. Currently under development.

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
import shutil
import logging
from urllib.request import urlopen

from .settings import paths
from .settings import sg

# ---------------------------------------------------------------------------


class sppasPostInstall:
    """Check directories and create if not existing.

    """

    @staticmethod
    def sppas_directories():
        """Create the required directories in the SPPAS package.

        :raise: sppasPermissionError

        """
        logging.debug("Check directories and create them if not existing:")

        # Test if we have the rights to write into the SPPAS directory
        sppas_parent_dir = os.path.dirname(paths.basedir)
        try:
            os.mkdir(os.path.join(sppas_parent_dir, "sppas_test"))
            shutil.rmtree(os.path.join(sppas_parent_dir, "sppas_test"))
            logging.debug(" - Write access to SPPAS package directory is granted.")
        except OSError as e:
            # Check for write access
            logging.critical("Write access denied to {:s}. SPPAS package should be "
                             "installed elsewhere.".format(sppas_parent_dir))
            logging.error(str(e))

        if os.path.exists(paths.logs) is False:
            os.mkdir(paths.logs)
            logging.info(" - The directory {:s} to store logs is created.".format(paths.logs))
        else:
            logging.debug(" - The logs folder is OK.")

        if os.path.exists(paths.wkps) is False:
            os.mkdir(paths.wkps)
            logging.info("The directory {:s} to store workspaces is created.".format(paths.wkps))
        else:
            logging.debug(" - The workspaces folder is OK.")

        if os.path.exists(paths.trash) is False:
            os.mkdir(paths.trash)
            logging.info("The Trash directory {:s} is created.".format(paths.trash))
        else:
            logging.debug(" - The trash folder is OK.")

    # -----------------------------------------------------------------------

    @staticmethod
    def sppas_dependencies():
        """Enable or disable features depending on dependencies."""
        pass

# ---------------------------------------------------------------------------


class sppasUpdate:
    """Check if an update of SPPAS is available.

    This class is not implemented yet.

    """

    @staticmethod
    def check_update():
        current = sg.__version__

        # Perhaps I should create a text file with the version number
        url = sg.__url__ + '/download.html'
        response = urlopen(url)
        data = str(response.read())

        # Extract last version from this page

        # Compare to current version

        return False
