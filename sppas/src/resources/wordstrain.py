# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.resources.wordstrain.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A very simplified but multilingual lemmatizer.

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

import codecs

from sppas.core.config import sg

from .dictrepl import sppasDictRepl
from .resourcesexc import FileUnicodeError

# ---------------------------------------------------------------------------


class sppasWordStrain(sppasDictRepl):
    """Sort of basic lemmatization.

    """

    def __init__(self, filename=None):
        """Create a WordStain instance.

        :param filename: (str) 2 or 3 columns file with word/freq/wordstrain

        """
        super(sppasWordStrain, self).__init__(dict_filename=None, nodump=True)
        self.load(filename)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Load word substitutions from a file.

        Replace the existing substitutions.

        :param filename: (str) 2 or 3 columns file with word/freq/replacement

        """
        if filename is None:
            return

        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            try:
                line = fd.readline()
            except UnicodeDecodeError:
                raise FileUnicodeError(filename=filename)
            fd.close()

        content = line.split()
        if len(content) < 3:
            self.load_from_ascii(filename)
        else:
            self.__load_with_freq(filename)

    # -----------------------------------------------------------------------

    def __load_with_freq(self, filename):
        """Load a replacement dictionary from a 3-columns ascii file.

        :param filename: (str) Replacement dictionary file name

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fd:
            try:
                lines = fd.readlines()
            except UnicodeDecodeError:
                raise FileUnicodeError(filename=filename)
            fd.close()

        self.__filename = filename
        frequency = {}
        for line in lines:
            line = " ".join(line.split())
            if len(line) == 0:
                continue

            tab_line = line.split()
            if len(tab_line) < 2:
                continue

            # To add (or modify) the entry in the dict:
            # Search for a previous token in the dictionary...
            key = tab_line[0].lower()
            freq = int(tab_line[1])
            value = sppasDictRepl.REPLACE_SEPARATOR.join(tab_line[2:])

            # does such entry already exists?
            if key in frequency:
                # does the new one is more frequent?
                if freq > frequency[key]:
                    # replace the old one by the new one
                    frequency[key] = freq
                    self.pop(key)
                    self.add(key, value)
            else:
                # add the new entry
                frequency[key] = freq
                self.add(key, value)
