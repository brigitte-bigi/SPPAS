# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.windows.datactrls.videodatavalues.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Data class for video.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

DEFAULT_FRAME_WIDTH = 200
DEFAULT_FRAME_HEIGHT = 100

# ---------------------------------------------------------------------------


class VideoDataValues(object):
    """Data structure to store video data values."""

    # TODO: turn members into private and implement properties, getters and setters to check values

    def __init__(self):
        self.framerate = -1.
        self.duration = 0.
        self.width = DEFAULT_FRAME_WIDTH
        self.height = DEFAULT_FRAME_HEIGHT
        # About what we need to draw if we have a period of time
        self.__fperiod = (0, 0)

    # -----------------------------------------------------------------------

    def set_video_data(self,
                       framerate: float = None,
                       duration: float = None,
                       width: int = None,
                       height: int = None) -> None:
        """Set all or any of the data we need about the video."""
        if framerate is not None:
            self.framerate = float(framerate)
        if duration is not None:
            self.duration = float(duration)
        if width is not None:
            self.width = int(width)
        if height is not None:
            self.height = int(height)

    # -----------------------------------------------------------------------

    def get_start_period(self) -> float:
        return float(self.__fperiod[0]) / self.framerate

    # -----------------------------------------------------------------------

    def get_end_period(self) -> float:
        return float(self.__fperiod[1]) / self.framerate

    # -----------------------------------------------------------------------

    def get_period(self) -> (float, float):
        """Return time period (float, float)."""
        return self.get_start_period(), self.get_end_period()

    # -----------------------------------------------------------------------

    def set_period(self, start_time, end_time) -> None:
        """Set a period of time.

        :param start_time: (int, float) the period start time in seconds
        :param end_time: (int, float) the period end time in seconds

        """
        # Convert the time (in seconds) into a position in the frames
        start_pos = self.time_to_pos(start_time)
        end_pos = self.time_to_pos(end_time)
        self.__fperiod = (start_pos, end_pos)

    # -----------------------------------------------------------------------

    def time_to_pos(self, time_value) -> int:
        return int(time_value * self.framerate)

    # -----------------------------------------------------------------------

    def pos_to_time(self, pos_value) -> float:
        return float(pos_value) / self.framerate
