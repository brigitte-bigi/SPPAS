"""
:filename: sppas.src.annotations.Align.aligners.aligner.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Aligners manager.

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

"""

from .basicalign import BasicAligner
from .juliusalign import JuliusAligner
from .hvitealign import HviteAligner

# ---------------------------------------------------------------------------

# List of supported aligners.
aligners = (BasicAligner, JuliusAligner, HviteAligner)

# ---------------------------------------------------------------------------


class sppasAligners(object):
    """Manager of the aligners implemented in the package.

    """

    def __init__(self):
        """Create a sppasAligners to manage the aligners supported by SPPAS."""
        self._aligners = dict()
        for a in aligners:
            self._aligners[a().name()] = a

    # ---------------------------------------------------------------------------

    def get(self):
        """Return a dictionary of aligners (key=name, value=instance)."""
        return self._aligners

    # ---------------------------------------------------------------------------

    @staticmethod
    def default_aligner_name():
        """Return the name of the default aligner."""
        return BasicAligner().name()

    # ---------------------------------------------------------------------------

    def names(self):
        """Return the list of aligner names."""
        return tuple(self._aligners.keys())

    # ---------------------------------------------------------------------------

    def classes(self, aligner_name=None):
        """Return the list of aligner classes.

        :param aligner_name: (str) A specific aligner
        :returns: BasicAligner, or a list if no aligner name is given

        """
        if aligner_name is not None:
            self.check(aligner_name)
            return self._aligners[aligner_name]

        return tuple(self._aligners.values())

    # ---------------------------------------------------------------------------

    def extensions(self, aligner_name=None):
        """Return the list of supported extensions of each aligner.

        :param aligner_name: (str) A specific aligner
        :returns: list of str, or a dict of list if no aligner name is given

        """
        if aligner_name is not None:
            sppasAligners.check(aligner_name)
            return self._aligners[aligner_name].extensions()

        ext = dict()
        for a in self._aligners:
            ext[a] = self._aligners[a]().extensions()
        return ext

    # ---------------------------------------------------------------------------

    def default_extension(self, aligner_name=None):
        """Return the default extension of each aligner.

        :param aligner_name: (str) A specific aligner
        :returns: str, or a dict of str if no aligner name is given

        """
        if aligner_name is not None:
            self.check()
            return self._aligners[aligner_name].outext()

        ext = dict()
        for a in self._aligners:
            ext[a] = self._aligners[a]().outext()
        return ext

    # ---------------------------------------------------------------------------

    def check(self, aligner_name):
        """Check whether the aligner name is known or not.

        :param aligner_name: (str) Name of the aligner.
        :returns: formatted alignername

        """
        a = aligner_name.lower().strip()
        if a not in self._aligners.keys():
            raise KeyError('Unknown aligner name {:s}.'.format(a))

        return a

    # ---------------------------------------------------------------------------

    def instantiate(self, model_dir=None, aligner_name="basic"):
        """Instantiate an aligner to the appropriate system from its name.

        If an error occurred, the basic aligner is returned.

        :param model_dir: (str) Directory of the acoustic model
        :param aligner_name: (str) Name of the aligner
        :returns: an Aligner instance.

        """
        a = self.check(aligner_name)
        return self._aligners[a](model_dir)
