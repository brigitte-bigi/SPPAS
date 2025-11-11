# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.RMS.irms.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Estimator of RMS values on intervals.

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

from audioopy.channel import Channel
from audioopy.channelvolume import ChannelVolume

# ---------------------------------------------------------------------------


class IntervalsRMS(object):
    """Estimate RMS on intervals of a channel.

    """

    def __init__(self, channel=None):
        """Create a sppasIntervalsRMS instance.

        :param channel: (Channel) the input channel

        """
        self.__win_len = 0.010

        self._channel = None
        self.__volumes = None
        if channel is not None:
            self.set_channel(channel)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_channel(self, channel):
        """Set a channel, then reset all previous results.

        :param channel: (Channel)

        """
        if isinstance(channel, Channel) is False:
            raise TypeError('Expected a Channel, got {:s} instead'
                            ''.format(str(type(channel))))

        self._channel = channel
        self.__volumes = None

    # -----------------------------------------------------------------------

    def estimate(self, begin, end):
        """Estimate RMS values of the given interval.

        rms = sqrt(sum(S_i^2)/n)

        :param begin: (float) Start value, in seconds
        :param end: (float) End value, in seconds

        """
        begin = float(begin)
        end = float(end)
        if (end - begin) < self.__win_len:
            raise Exception('Invalid interval [{:f};{:f}]'.format(begin, end))

        # Create a channel with only the frames of the interval [begin, end]
        from_pos = int(begin * float(self._channel.get_framerate()))
        to_pos = int(end * float(self._channel.get_framerate()))
        fragment = self._channel.extract_fragment(from_pos, to_pos)

        # Estimates the RMS values
        self.__volumes = ChannelVolume(fragment, self.__win_len)

    # -----------------------------------------------------------------------

    def get_rms(self):
        """Return the global rms value or 0."""
        if self.__volumes is None:
            return 0
        return self.__volumes.volume()

    # -----------------------------------------------------------------------

    def get_values(self):
        """Return the list of estimated rms values."""
        if self.__volumes is None:
            return list()
        return self.__volumes.volumes()

    # -----------------------------------------------------------------------

    def get_mean(self):
        """Return the mean rms value or 0."""
        if self.__volumes is None:
            return 0.
        return self.__volumes.mean()

    # -----------------------------------------------------------------------

    def get_min(self):
        """Return the min rms value or 0."""
        if self.__volumes is None:
            return 0.
        return self.__volumes.min()

    # -----------------------------------------------------------------------

    def get_max(self):
        """Return the max rms value or 0."""
        if self.__volumes is None:
            return 0.
        return self.__volumes.max()

    # -----------------------------------------------------------------------

    def get_stdev(self):
        """Return the max rms value or 0."""
        if self.__volumes is None:
            return 0.
        return self.__volumes.stdev()
