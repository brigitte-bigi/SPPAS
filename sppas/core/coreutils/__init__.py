# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.coreutils.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the management of SPPAS core utilities.

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

# Messages need to be imported first: many others need them.
from .messages import error
from .messages import info
from .messages import msg

# Exceptions
from .exceptions import sppasPythonError          # 9999
from .exceptions import sppasPythonFeatureError   # 9990
from .exceptions import sppasError                # 0000
from .exceptions import sppasTypeError            # 0100
from .exceptions import sppasIndexError           # 0200
from .exceptions import sppasValueError           # 0300
from .exceptions import sppasKeyError             # 0400
from .exceptions import sppasOSError              # 0500
from .exceptions import sppasInstallationError    # 0510
from .exceptions import sppasSystemOSError        # 0505
from .exceptions import sppasPermissionError      # 0513
from .exceptions import sppasEnableFeatureError   # 0520
from .exceptions import sppasPackageFeatureError  # 0530
from .exceptions import sppasPackageUpdateFeatureError  # 0540
from .exceptions import sppasIOError              # 0600
from .exceptions import NegativeValueError        # 0310
from .exceptions import RangeBoundsException      # 0320
from .exceptions import IntervalRangeException    # 0330
from .exceptions import IndexRangeException       # 0340
from .exceptions import LanguageNotFoundError     # 0350
from .exceptions import IOExtensionError          # 0610
from .exceptions import NoDirectoryError          # 0620
from .exceptions import sppasOpenError            # 0650
from .exceptions import sppasReadError            # 0655
from .exceptions import sppasWriteError           # 0660
from .exceptions import sppasExtensionReadError   # 0670
from .exceptions import sppasExtensionWriteError  # 0680

# Utility class to manage progress.
# No external requirement.
from .progress import sppasBaseProgress

# The trash to put backup files requires the path settings.
from .trash import sppasTrash

# Strings backward compatibility and string operations.
# Requires the settings and exceptions
from .makeunicode import u
from .makeunicode import b
from .makeunicode import sppasUnicode
from .makeunicode import text_type
from .makeunicode import binary_type
from .makeunicode import basestring

# ISO639 language manager
# Requires exceptions
from .iso639 import ISO639
from .iso639 import LanguageInfo

# Logs in a file.
# It requires settings to print the appropriate headers.
from .reports import sppasLogFile

# ---------------------------------------------------------------------------

__all__ = (
    "info",
    "error",
    "msg",
    "sppasPythonError",
    "sppasError",
    "sppasTypeError",
    "sppasIndexError",
    "sppasValueError",
    "sppasKeyError",
    "sppasOSError",
    "sppasSystemOSError",
    "sppasInstallationError",
    "sppasPermissionError",
    "sppasEnableFeatureError",
    "sppasPackageFeatureError",
    "sppasPythonFeatureError",
    "sppasPackageUpdateFeatureError",
    "sppasIOError",
    "NegativeValueError",
    "RangeBoundsException",
    "IntervalRangeException",
    "IndexRangeException",
    "LanguageNotFoundError",
    "IOExtensionError",
    "NoDirectoryError",
    "sppasOpenError",
    "sppasReadError",
    "sppasWriteError",
    "sppasExtensionReadError",
    "sppasExtensionWriteError",
    "u",
    "b",
    "sppasUnicode",
    "text_type",
    "binary_type",
    "basestring",
    "ISO639",
    "LanguageInfo",
    "sppasLogFile",
    "sppasTrash",
    "sppasBaseProgress"
)
