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
import json
import urllib.request
from importlib.metadata import version, PackageNotFoundError
from urllib.error import URLError

from .config import paths
from .config import cfg
from .config import vocab_defaults
from .preinstall import Features
from .preinstall import DepsFeatureChecker

# ---------------------------------------------------------------------------


class sppasSupportDirectories:
    """Check directories and create if not existing.

    """

    @staticmethod
    def check():
        """Create the required directories in the SPPAS package.

        :raises: sppasPermissionError

        """
        logging.debug("Check directories and create them if not existing:")

        # Test if we have the rights to write into the SPPAS directory
        sppas_parent_dir = os.path.dirname(paths.basedir)
        try:
            os.mkdir(os.path.join(sppas_parent_dir, "sppas_test"))
            shutil.rmtree(os.path.join(sppas_parent_dir, "sppas_test"))
            if os.path.exists(paths.basedir) is False:
                os.makedirs(paths.basedir, exist_ok=True)
                logging.info(" - The directory {:s} to store SPPAS is created.".format(paths.basedir))
            logging.debug(" - Write access to SPPAS package directory is granted.")
        except OSError as e:
            # Check for write access
            logging.critical("Write access denied to {:s}. SPPAS package should be "
                             "installed elsewhere.".format(sppas_parent_dir))
            logging.error(str(e))

        if os.path.exists(paths.resources) is False:
            os.makedirs(paths.resources, exist_ok=True)
            os.mkdir(os.path.join(paths.resources, "cuedspeech"))
            os.mkdir(os.path.join(paths.resources, "dict"))
            os.mkdir(os.path.join(paths.resources, "faces"))
            os.mkdir(os.path.join(paths.resources, "models"))
            os.mkdir(os.path.join(paths.resources, "num"))
            os.mkdir(os.path.join(paths.resources, "repl"))
            os.mkdir(os.path.join(paths.resources, "samples"))
            os.mkdir(os.path.join(paths.resources, "syll"))
            os.mkdir(os.path.join(paths.resources, "vocab"))
            logging.info(f" - The directory {paths.resources} to store resources is created.")
        else:
            logging.debug(f" - The resources folder {paths.resources} is OK.")

        # Create the default fallback vocab files if they are missing
        vocab_dir = os.path.join(paths.resources, "vocab")
        os.makedirs(vocab_dir, exist_ok=True)
        for filename, content in vocab_defaults.files.items():
            vocab_file = os.path.join(vocab_dir, filename)
            if os.path.exists(vocab_file) is False:
                with open(vocab_file, "w", encoding="utf-8") as fp:
                    fp.write(content)
                logging.info(f" - The default vocab file {vocab_file} is created.")

        if os.path.exists(paths.logs) is False:
            os.makedirs(paths.logs, exist_ok=True)
            logging.info(f" - The directory {paths.logs} to store logs is created.")
        else:
            logging.debug(f" - The logs folder {paths.logs} is OK.")

        if os.path.exists(paths.wkps) is False:
            os.makedirs(paths.wkps, exist_ok=True)
            logging.info(f"The directory {paths.wkps} to store workspaces is created.")
        else:
            logging.debug(f" - The workspaces folder {paths.wkps} is OK.")

        if os.path.exists(paths.trash) is False:
            os.makedirs(paths.trash, exist_ok=True)
            logging.info(f"The directory {paths.trash} to store trashed files is created.")
        else:
            logging.debug(f" - The trash folder {paths.trash} is OK.")

# ---------------------------------------------------------------------------


class sppasSupportDependencies:
    """Check dependencies and update 'cfg' with available features.

    """

    @staticmethod
    def check():
        """Enable or disable features depending on available dependencies.

        """
        # Check if the required dependencies can be imported
        # --------------------------------------------------
        # Hack to avoid ImportError: DLL load failed while importing _framework_bindings.
        # This error occurs specifically if mediapipe is imported AFTER wxPython.
        # Since DepsFeatureChecker() checks both 'wxpython' and 'mediapipe' features,
        # we explicitly import mediapipe BEFORE running DepsFeatureChecker.
        # The order matters because 'wxpython' is listed before 'mediapipe' in features.ini.
        try:
            import mediapipe
        except:
            pass

        msg = DepsFeatureChecker().check(do_report=True)
        logging.debug("Checked required dependencies report:")
        logging.debug("\n".join(msg))

        # Check if enabled features can really be imported -- update if not.
        # ------------------------------------------------

        # Use Features to check if all python dependencies are correctly assigned to 'cfg'
        features = Features(req="", cmdos="")
        features.check_deps(test_all=True)

        # Update enabled features in config
        for fid in features.get_ids("deps"):
            cfg.set_feature(fid, features.enable(fid))
            state = "OK" if features.enable(fid) else "DISABLED"
            logging.debug(f"{fid:15}: {state}")

# ---------------------------------------------------------------------------


class sppasSupportUpdate:
    """Check if an update of SPPAS is available.

    """

    PYPI_URL = 'https://pypi.org/pypi/sppas/json'

    # -----------------------------------------------------------------------

    @staticmethod
    def check():
        cfg.update_info = sppasSupportUpdate.get_update_infos()
        if cfg.update_info.get('update'):
            logging.info("SPPAS core package can been updated.")
        else:
            logging.info("SPPAS core package is up-to-date.")

    # -----------------------------------------------------------------------

    @staticmethod
    def get_update_infos():
        """Return update information for the installed 'sppas' package.

        Returns a dictionary with the following (key: value) pairs:
            - installed: installed version or None
            - latest: latest version on PyPI or None
            - update: True if a newer version is available
            - error: error message or empty string

        :return: (dict) Update information.

        """
        try:
            installed = version('sppas')
        except PackageNotFoundError:
            return {
                'installed': None,
                'latest': None,
                'update': False,
                'error': 'Package "sppas" is not installed in the current Python environment.'
            }

        try:
            with urllib.request.urlopen(sppasSupportUpdate.PYPI_URL, timeout=5) as response:
                data = json.load(response)
            latest = data['info']['version']
        except (URLError, OSError, ValueError, KeyError) as e:
            return {
                'installed': installed,
                'latest': None,
                'update': False,
                'error': str(e)
            }

        def _vtuple(v):
            return tuple(int(x) for x in v.split('.') if x.isdigit())
        installed = version('sppas')
        latest = data['info']['version']

        update = _vtuple(latest) > _vtuple(installed)
        return {
            'installed': installed,
            'latest': latest,
            'update': update,
            'error': ''
        }
