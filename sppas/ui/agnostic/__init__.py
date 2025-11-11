"""
:package: sppas.ui.agnostic
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Components and utilities shared across all SPPAS user interfaces.

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

This package contains classes and functions that are interface-agnostic,
i.e., usable by any user interface (web, terminal, or graphical).
It includes features such as native file choosers or common logic that
must remain independent of any specific UI framework (e.g., wxPython or HTML).

It ensures consistency, code reuse, and interface independence across the SPPAS ecosystem.

"""

from .filechooser import FileChooserMixin

__all__ = ('FileChooserMixin', )
