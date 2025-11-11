"""
:filename: sppas.src.annotations.Align.aligners.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Internal or externals automatic aligners

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

How to get the list of supported aligner names?

>>> a = sppasAligners()
>>> a.default_aligner_name()
>>> a.names()

How to get an instance of a given aligner?

>>> a1 = sppasAligners().instantiate(model_dir, "julius")
>>> a2 = JuliusAligner(model_dir)

"""

from .aligner import sppasAligners
from .basicalign import BasicAligner
from .juliusalign import JuliusAligner
from .hvitealign import HviteAligner

# ---------------------------------------------------------------------------

__all__ = (
    'sppasAligners',
    'JuliusAligner',
    'HviteAligner',
    'BasicAligner'
)
