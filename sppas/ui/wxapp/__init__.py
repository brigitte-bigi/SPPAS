# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  SPPAS UI source code based on WX widgets.

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

GUI Shortcuts
================

Main
----------

- alt+F4 Exit SPPAS
- ctrl+w Exit SPPAS
- ctrl+q Close SPPAS
- alt+f Switch view to page "Files"
- alt+up Switch view to the next page
- alt+down Switch view to the previous page


Edit page
----------

Main toolbar:

- ctrl+O Open the checked files
- ctrl+s Save all modified files
- ctrl+w Close all files
- ctrl+f Open the Search dialog

Search:

- ctrl+g Search forward
- ctrl+G Search backward
- ctrl+h Hide dialog
- ctrl+w Close dialog

Timeline:

- alt+-> Select next annotation
- alt+<- select previous annotation
- ctrl+a Zoom all
- ctrl+i Zoom In
- ctrl+o Zoom out
- ctrl+-> Scroll to right
- ctrl+<- Scroll to left
- shift+-> Play the next 3 frames of videos
- shift+<- Play the previous 3 frames of videos

"""

from sppas.core.config import cfg
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasPackageFeatureError
from sppas.core.coreutils import sppasPackageUpdateFeatureError

# Check if installation and feature configuration are matching...
try:
    import wx
    if cfg.feature_installed("wxpython") is False:
        # WxPython wasn't installed by the SPPAS setup.
        cfg.set_feature("wxpython", True)
except ImportError:
    if cfg.feature_installed("wxpython") is True:
        # Invalidate the feature because the package is not installed!
        cfg.set_feature("wxpython", False)

        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasPackageFeatureError("wx", "wxpython")
    else:
        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasEnableFeatureError("wxpython")

# The feature "wxpython" is enabled. Check the version!
if cfg.feature_installed("wxpython") is True:
    v = wx.version().split()[0][0]
    if v != '4':
        # Invalidate the feature because the package is not up-to-date
        cfg.set_feature("wxpython", False)

        class sppasWxError(object):
            def __init__(self, *args, **kwargs):
                raise sppasPackageUpdateFeatureError("wx", "wxpython")

# ---------------------------------------------------------------------------
# Either import classes or define them in cases wxpython is valid or not.
# ---------------------------------------------------------------------------


if cfg.feature_installed("wxpython") is True:
    from .install_app import sppasInstallApp
    from .main_app import sppasApp

else:

    class sppasInstallApp(sppasWxError):
        pass


    class sppasApp(sppasWxError):
        pass


__all__ = (
    'sppasInstallApp',
    'sppasApp'
)
