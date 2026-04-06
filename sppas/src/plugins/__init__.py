"""
:filename: sppas.src.plugins.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for plugins of SPPAS.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

*****************************************************************************
plugins: access and manage external programs.
*****************************************************************************

This package includes classes to manage external program to plug into SPPAS.

:Example:

>>> # Create a plugin manager (it will explore the installed plugins).
>>> manager = sppasPluginsManager()
>>> # Install a plugin
>>> plugin_id = manager.install(plugin_zip_filename,
>>>                             plugin_destination_folder_name)
>>> # Get a plugin
>>> p = manager.get_plugin(plugin_id)
>>> # Apply a plugin on a list of files
>>> message = manager.run_plugin(plugin_id, [some_filename1, some_filename2])
>>> print(message)
>>> # Delete an installed plugin
>>> manager.delete(plugin_id)

Requires the following other packages:

* config
* utils
* structs

"""

from .manager import sppasPluginsManager
from .plugin import sppasPluginParam

__all__ = (
    "sppasPluginsManager",
    "sppasPluginParam"
)
