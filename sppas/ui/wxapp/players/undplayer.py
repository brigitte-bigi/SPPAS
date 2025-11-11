# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.players.undplayer.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A player that doesn't play anything.

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

from sppas.ui.wxapp.players import sppasBasePlayer
from sppas.ui.wxapp.players import PlayerType

# ---------------------------------------------------------------------------


class sppasUndPlayer(sppasBasePlayer):
    """A media player that simply store a filename and its duration.

    """

    def __init__(self, owner):
        super(sppasUndPlayer, self).__init__(owner)
        self._duration = 0.

    # -----------------------------------------------------------------------

    def load(self, filename):
        """Store the filename.

        :param filename: (str) Name of a file
        :return: (bool) True

        """
        self._filename = filename
        self._mt = PlayerType().unsupported
        return True

    # -----------------------------------------------------------------------

    def get_duration(self):
        return self._duration

    # -----------------------------------------------------------------------

    def set_duration(self, value):
        """Set the duration of the file."""
        self._duration = value

    # -----------------------------------------------------------------------

    def stop(self):
        """Stop to play.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def pause(self):
        """Pause to play the audio.

        :return: (bool) False

        """
        return False

    # -----------------------------------------------------------------------

    def play(self):
        """Start to play the audio stream.

        :return: (bool) False

        """
        return False
