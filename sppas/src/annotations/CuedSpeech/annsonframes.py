# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.annsonframes.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Annotation of a tier are aligned to frames of a video.

.. _This file is part of AutoCuedSpeech: <https://auto-cuedspeech.org/>
.. _Originally developed in SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from __future__ import annotations
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasInterval

# ---------------------------------------------------------------------------


class sppasAnnsOnFrames:
    """Move points to match with the framerate of the media

    """

    def __init__(self, fps=60.):
        self.__fps = float(fps)

    # -----------------------------------------------------------------------
    # Getter & Setter
    # -----------------------------------------------------------------------

    def get_fps(self):
        """Return framerate (float)."""
        return self.__fps

    # -----------------------------------------------------------------------

    def set_fps(self, value: float):
        """Set a new framerate.

        :param value: (float) A framerate.

        """
        try:
            value = float(value)
        except:
            raise TypeError("Expected a float.")
        if value < 0.:
            raise ValueError("Invalid framerate. ")
        self.__fps = value

    # -----------------------------------------------------------------------

    fps = property(get_fps, set_fps)

    # -----------------------------------------------------------------------
    # Worker
    # -----------------------------------------------------------------------

    def adjust_boundaries(self, tier: sppasTier) -> None:
        """Move boundaries to frames of a video.

        :param tier: (sppasTier) Tier to be adjusted.

        """
        for ann in tier:
            begin_point = ann.get_lowest_localization()
            end_point = ann.get_highest_localization()
            new_begin = self.adjust_point_boundary(begin_point)
            new_end = self.adjust_point_boundary(end_point)
            ann.set_best_localization(sppasInterval(new_begin, new_end))

    # -----------------------------------------------------------------------

    def adjust_point_boundary(self, point: sppasPoint) -> sppasPoint:
        """Move a point to a frame of a video.

        Put the midpoint either between 2 frames or at the middle of a frame.
        Set the radius to fully cover 0, 1 or 2 frames.

        :param point: (sppasPoint) New point with adjusted midpoint and radius.

        """
        frame_duration = 1. / self.__fps
        half_frame = frame_duration / 2.
        quart_frame = frame_duration / 4.

        nframes = int(point.get_midpoint() / frame_duration)
        s = nframes * frame_duration
        m = s + (frame_duration / 2.)
        radius = point.get_radius()

        if s <= point.get_midpoint() < s + quart_frame:
            midpoint = s
            if radius is None or (radius is not None and radius < quart_frame):
                radius = 0.
            else:
                radius = frame_duration

        elif s + quart_frame <= point.get_midpoint() < m + quart_frame:
            midpoint = m
            if radius is None or (radius is not None and radius < frame_duration):
                radius = half_frame
            else:
                radius = 1.5 * frame_duration

        else:
            midpoint = s + frame_duration
            if radius is None or (radius is not None and radius < quart_frame):
                radius = 0.
            else:
                radius = frame_duration

        return sppasPoint(midpoint, radius)
