# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ######   ########   ########      ###      ######
        ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
        ##        ##     ##  ##     ##   ##   ##   ##            annotation
         ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
        ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

        https://sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <https://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    ui.tips.py
    ~~~~~~~~~~

"""

import os.path
import codecs
import random
import logging

from sppas.core.config import sg
from sppas.core.config import paths
from sppas.core.coreutils import sppasUnicode
from sppas.core.coreutils import b

# ---------------------------------------------------------------------------


class sppasTips(object):
    """Manage a set of tips.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi, CNRS

    Tips is a set of short help messages that a software tool can display
    when it's starting. Some users find them useful...

    Tips are stored into a file with name TIPS_FILE. This file format is
    with one tip a line.

    >>> t = sppasTips()
    >>> print(t.get_message())

    """

    def __init__(self):
        """Create a sppasTips instance.

        Load the list of message tips of the software.

        """
        self._current = 0
        self._tips = list()
        self.load_tips()

    # -----------------------------------------------------------------------

    def load_tips(self, filename=None):
        """Load message tips from a file.

        Update the existing tips of the list (if any).

        :param filename: (str) Name of the file to get message tips.

        """
        if filename is None:
            filename = os.path.join(paths.etc, "tips.txt")

        try:
            with codecs.open(filename, 'r', sg.__encoding__) as f:
                for line in f.readlines():
                    self.add_message(line)
        except Exception as e:
            logging.info('Error while reading tips: {:s}'.format(str(e)))

        if len(self._tips) == 0:
            self._tips = ["Welcome!"]

    # -----------------------------------------------------------------------

    def save_tips(self, filename=None):
        """Save tips in a file.

        :param filename: (str) Name of the file to store message tips.

        """
        if filename is None:
            filename = os.path.join(paths.etc, "tips.txt")

        with codecs.open(filename, 'w', sg.__encoding__) as f:
            for message in self._tips:
                f.write("{:s}\n".format(b(message)))

    # -----------------------------------------------------------------------

    def add_message(self, message):
        """Add a new message tips in the list of tips.

        :param message: (str) A help message.

        """
        su = sppasUnicode(message)
        u_message = su.to_strip()
        if len(u_message) > 0:
            self._tips.append(u_message)

    # -----------------------------------------------------------------------

    def get_message(self):
        """Return a random tips message.

        :returns: unicode

        """
        if len(self._tips) == 1:
            self._current = 0
            return self._tips[0]

        if len(self._tips) == 2:
            self._current = (self._current+1) % 2
            return self._tips[self._current]

        p_round = 0
        new = self._current
        while new == self._current and p_round < 3:
            new = random.randint(0, len(self._tips) - 1)
            p_round += 1

        self._current = new
        return self._tips[self._current]

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of tips."""
        return len(self._tips)
