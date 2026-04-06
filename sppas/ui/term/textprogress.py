# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.term.textprogress.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  progress bar for a terminal output.

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

import sys

from sppas.core.coreutils import u
from sppas.core.coreutils import b
from sppas.core.coreutils import sppasBaseProgress

from .terminalcontroller import TerminalController

# ----------------------------------------------------------------------------

WIDTH = 74
BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'

# ----------------------------------------------------------------------------


class ProcessProgressTerminal(sppasBaseProgress):
    """A 3-lines progress bar to be used while processing from a terminal.

    It looks like:

                            header
    20% [===========----------------------------------]
                        message text

    The progress self._bar is colored, if the terminal supports color
    output; and adjusts to the width of the terminal.

    The use of a colored terminal controller is temporarily disabled:
    problems with bytes/unicode in Python3 must be solved.

    """

    def __init__(self):
        """Create a ProcessProgressTerminal instance."""
        super(ProcessProgressTerminal, self).__init__()
        try:
            raise NotImplementedError
            self._term = TerminalController()
            if not (self._term.CLEAR_EOL and self._term.UP and self._term.BOL):
                self._term = None
            self._bar = self._term.render(BAR)
        except Exception as e:
            # import traceback
            # print('[WARNING] The progress bar is disabled because this terminal'
            #       ' does not support colors, EOL, UP, etc. Returned error: {}'
            #       ''.format(traceback.format_exc()))
            self._term = None
            self._bar = ""

        self._cleared = True  # We haven't drawn the self._bar yet.

    # ------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Update the progress.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text (default: None)

        """
        if percent is None:
            percent = self._percent
        else:
            percent = int(percent)
        if message is None:
            message = self._text
        else:
            message = u(message)

        if self._term:
            n = int((WIDTH - 10) * percent)
            if self._cleared is True:
                self._cleared = False

                sys.stdout.write(u(self._term.BOL + self._term.CLEAR_EOL +
                                   self._term.UP + self._term.CLEAR_EOL +
                                   self._term.UP + self._term.CLEAR_EOL))

            val = self._bar % (100*percent, b('=')*n, b('-')*(WIDTH-10-n))
            sys.stdout.write(
                str(self._term.BOL + self._term.UP + self._term.CLEAR_EOL) +
                str(val) +
                str(self._term.CLEAR_EOL) +
                str(message.center(WIDTH)))
        else:
            try:
                print("  => {} ({} percents)".format(message, percent))
            except UnicodeError:
                print("  => {} percents".format(percent))

        self._percent = percent
        self._text = message

    # ------------------------------------------------------------------

    def clear(self):
        """Clear."""
        if self._cleared is False:
            sys.stdout.write("\n\n")
            self._cleared = True

    # ------------------------------------------------------------------

    def set_header(self, header):
        """Set a new progress header text.

        :param header: (str) new progress header text.

        """
        if header is None:
            header = ""
        if self._term:
            self._header = self._term.render(HEADER % header.center(WIDTH))
            self._header = u(self._header)
            sys.stdout.write("\n" + self._header + "\n")
            sys.stdout.write("\n")

        else:
            self._header = u("\n         * * *  " + header + "  * * *  ")
            print(self._header)

    # ------------------------------------------------------------------

    def set_new(self):
        """Initialize a new progress line."""
        self.clear()
        self._text = ""
        self._percent = 0
        self._header = ""
