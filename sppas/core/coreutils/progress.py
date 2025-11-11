# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.progress.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Print messages on the logging while processing some task.

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

"""

import logging

# ----------------------------------------------------------------------------


class sppasBaseProgress(object):
    """Base class for a progress bar to be used while processing some task.

    """

    def __init__(self, *args, **kwargs):
        """Create a sppasBaseProgress instance."""
        self._percent = 0
        self._text = ""
        self._header = ""

    # ------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Update the progress.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text  (default: None)

        """
        if percent is not None:
            self._percent = percent
        if message is not None:
            logging.info('  => ' + message)
            self._text = message

    # ------------------------------------------------------------------

    def clear(self):
        """Clear."""
        pass

    # ------------------------------------------------------------------

    def set_fraction(self, percent):
        """Set a new progress value.

        :param percent: (float) new progress value

        """
        self.update(percent=percent)

    # ------------------------------------------------------------------

    def set_text(self, text):
        """Set a new progress message text.

        :param text: (str) new progress text

        """
        self.update(message=text.strip())

    # ------------------------------------------------------------------

    def set_header(self, header):
        """Set a new progress header text.

        :param header: (str) new progress header text.

        """
        if len(header) > 0:
            self._header = "          * * *  " + header + "  * * *  "
        else:
            self._header = ""
        logging.info(self._header)

    # ------------------------------------------------------------------

    def set_new(self):
        """Initialize a new progress line."""
        self.set_header("")
        self.update(percent=0, message="")

    # ------------------------------------------------------------------

    def close(self):
        pass
