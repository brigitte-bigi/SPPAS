"""
:filename: sppas.ui.swapp.app_setup.fieldsetfeature.py
:author: Brigitte Bigi, Florian Lopitaux
:contact: contact@sppas.org
:summary: Create a "Feature" fieldset node of the setup app.

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

from sppas.core.coreutils import msg
from sppas.core.coreutils import info

from .basefieldsetfeaturetype import SetupFeatureTypeFieldset

# ---------------------------------------------------------------------------


DEPS_FEATURES = info(514, "install")
LANG_FEATURES = info(515, "install")
ANNOT_FEATURES = info(516, "install")
SPIN_FEATURES = info(517, "install")

# ---------------------------------------------------------------------------


class SetupDepsFieldset(SetupFeatureTypeFieldset):
    """List of features of type 'deps'.

    """

    def __init__(self, parent, installer, feature_type):
        super(SetupDepsFieldset, self).__init__(parent, "fieldset_deps", installer, "deps", DEPS_FEATURES)
        self._msg = msg("Tools", "install")

# ---------------------------------------------------------------------------


class SetupLangFieldset(SetupFeatureTypeFieldset):
    """List of features of type 'lang'.

    """

    def __init__(self, parent, installer, feature_type):
        super(SetupLangFieldset, self).__init__(parent, "fieldset_lang", installer, "lang", LANG_FEATURES)
        self._msg = msg("Langs", "install")

# ---------------------------------------------------------------------------


class SetupAnnotFieldset(SetupFeatureTypeFieldset):
    """List of features of type 'annot'.

    """

    def __init__(self, parent, installer, feature_type):
        super(SetupAnnotFieldset, self).__init__(parent, "fieldset_annot", installer, "annot", ANNOT_FEATURES)
        self._msg = msg("Models", "install")

# ---------------------------------------------------------------------------


class SetupSpinOffFieldset(SetupFeatureTypeFieldset):
    """List of features of type 'spin'.

    """

    def __init__(self, parent, installer, feature_type):
        super(SetupSpinOffFieldset, self).__init__(parent, "fieldset_spinoff", installer, "spin", SPIN_FEATURES)
        self._msg = msg("Extras", "install")





