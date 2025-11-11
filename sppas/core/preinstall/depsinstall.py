# -*- coding : UTF-8 -*-
"""
:filename: sppas.preinstall.depsinstall.py
:author: Brigitte Bigi
:contributor: Florian Hocquet
:contact: contact@sppas.org
:summary: Manage the installer of SPPAS dependencies.

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

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

import sys
import logging

from sppas.core.config import sppasExecProcess
from sppas.core.coreutils.exceptions import sppasSystemOSError

from .installer import DebianInstaller
from .installer import DnfInstaller
from .installer import WindowsInstaller
from .installer import MacOsInstaller

# ---------------------------------------------------------------------------


class sppasGuessInstaller(object):

    UNIX_SYSTEM_REQUIREMENTS = {
        "debian": (DebianInstaller, ["dpkg", "apt"]),
        "darwin": (MacOsInstaller, ["brew"]),
        "fedora": (DnfInstaller, ["dnf"])
        # no other installer is supported yet.
    }

    # ------------------------------------------------------------------------

    @staticmethod
    def guess(system):
        """Return the installer class matching the given system.

        The given system name is the returned string of `sys.platform`.
        List of returned values depending on the given input:

        - system="win32" (Microsoft Windows) returns `WindowsInstaller`
        - system="darwin" (MacOS Apple) returns `MacOsInstaller`
        - system="linux" returns either `DebianInstaller` if "dpkg" and "apt"
          commands are installed, or `MacOsInstaller` if "brew" command is
          installed or None.

        :param system: (str) Name of the operating system.
        :return: (Installer | None)

        """
        if system.lower() == "win32":
            return WindowsInstaller

        if system in list(sppasGuessInstaller.UNIX_SYSTEM_REQUIREMENTS.keys()):
            return sppasGuessInstaller.UNIX_SYSTEM_REQUIREMENTS[system][0]
        else:
            # Guess the OS
            for system in list(sppasGuessInstaller.UNIX_SYSTEM_REQUIREMENTS.keys()):
                installer, requirements = sppasGuessInstaller.UNIX_SYSTEM_REQUIREMENTS[system]
                # Test all required commands
                if all([sppasExecProcess().test_command(r) for r in requirements]):
                    # All required commands are available. This installer can
                    # be used for the given system.
                    return installer

        return None

# ---------------------------------------------------------------------------


class sppasInstallerDeps(object):
    """Main class to manage the installation of external features.

    sppasInstallerDeps is a wrapper of an Installer Object.

    It allows to:

      - launch the installation process
      - get information, which are important for the users, about the pre-installation
      - configure parameters to get a personalized installation

    :example:
    >>> installer = sppasInstallerDeps()

    See if a feature is available or not:
    >>> installer.available("feature_id")
    >>> True

    Customize what is enabled or not:
    >>> installer.enable("feature_id")
    >>> False
    >>> installer.enable("feature_id", True)
    >>> True

    Launch the installation process:
    >>> errors = installer.install("feature_id")
    >>> assert len(errors) == 0
    >>> assert installer.available("feature_id") is True

    """

    def __init__(self, progress=None):
        """Instantiate the appropriate installer depending on the OS.

        :param progress: (ProcessProgressTerminal|None) The installation progress
        :raises: OSError: Not supported OS for the automatic installer

        """
        # Find which installer should be used for the OS
        system = sys.platform
        logging.info("Operating system: {}".format(system))
        system_installer = sppasGuessInstaller.guess(system)
        if system_installer is None:
            raise sppasSystemOSError("system")

        # Instantiate the installer for the system
        self.__installer = system_installer()
        logging.info("System installer: {}".format(self.__installer.__class__.__name__))

        # Set a progress system to the installer -- if given
        if progress is not None:
            self.__installer.set_progress(progress)

    # ------------------------------------------------------------------------

    def set_progress(self, progress=None):
        self.__installer.set_progress(progress)

    # ------------------------------------------------------------------------

    def features_ids(self, feat_type=None):
        """Return the list of feature identifiers.

        :param feat_type: (str) Only return features of the given type.
        :return: (list)

        """
        return self.__installer.get_fids(feat_type)

    # ------------------------------------------------------------------------

    def feature_type(self, feat_id):
        """Return the feature type: deps, lang, annot.

        :param feat_id: (str) Identifier of a feature
        :return: (str) or None

        """
        return self.__installer.feature_type(feat_id)

    # ------------------------------------------------------------------------

    def brief(self, feat_id):
        """Return the brief description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.brief(feat_id)

    # ------------------------------------------------------------------------

    def description(self, feat_id):
        """Return the description of the feature.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.description(feat_id)

    # ------------------------------------------------------------------------

    def available(self, feat_id):
        """Return True if the feature is available.

        :param feat_id: (str) Identifier of a feature

        """
        return self.__installer.available(feat_id)

    # ------------------------------------------------------------------------

    def enable(self, fid, value=None):
        """Return True if the feature is enabled and/or set it.

        :param fid: (str) Identifier of a feature
        :param value: (bool | None) Enable of disable the feature.

        """
        if value is None:
            return self.__installer.enable(fid)

        return self.__installer.enable(fid, value)

    # ------------------------------------------------------------------------

    def install(self, feat_type=None):
        """Launch the installation process.

        :return: errors: (str) errors happening during installation.

        """
        errors = self.__installer.install(feat_type)
        return errors
