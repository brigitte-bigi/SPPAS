# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.Formants.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Automatic detection of F1/F2 formants.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

This package requires 'formants' feature, for parselmouth, numpy and
scipy dependencies.

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError

# ---------------------------------------------------------------------------


if cfg.feature_installed("formants") is False:
    # Define classes in case parselmouth/numpy/scipy are not installed.

    class FormantsEstimator(object):
        def __init__(self):
            raise sppasEnableFeatureError("formants")

    class sppasFormants():
        def __init__(self, log=None):
            raise sppasEnableFeatureError("formants")

else:
    # Import the classes in case dependencies are all installed so that
    # the automatic detections can work.
    from .formants import FormantsEstimator
    from .sppasformants import sppasFormants

# ---------------------------------------------------------------------------

__all__ = (
    "FormantsEstimator",
    "sppasFormants"
)
