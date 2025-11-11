# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.Anonym.anonymvideo.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Anonymization of segments of a video.

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

import logging

from sppas.core.coreutils import sppasKeyError
from sppas.src.imgdata import sppasCoords
from sppas.src.videodata import sppasVideoReader
from sppas.src.videodata import sppasVideoWriter

# ----------------------------------------------------------------------------


class sppasVideoAnonymizer():
    """Anonymize segments of a video stream.

    """

    VIDEO_MODE = ["face", "mouth", None]

    def __init__(self, videofile, facedetect):
        """Anonymize segments of a video stream.

        :param videofile: (sppasVideoReaderBuffer)
        :param facedetect: (sppasFaceDetection)

        """
        self._mode = "face"
        self._video = sppasVideoReader()
        self._video.open(videofile)

        self._facedetect = facedetect

    # -----------------------------------------------------------------------

    def set_mode(self, mode="face"):
        """

        """
        if mode not in sppasVideoAnonymizer.VIDEO_MODE:
            raise sppasKeyError("VideoMode", mode)
        self._mode = mode

    # -----------------------------------------------------------------------

    def ianonymize(self, segments, output):
        """Anonymize faces of the video into the given time intervals (in seconds).

        :param segments: (list of tuples) List of (start time, end time) time values

        """
        if self._facedetect is None:
            return

        w, h = self._video.get_size()
        video_writer = sppasVideoWriter()
        video_writer.set_fps(self._video.get_framerate())
        video_writer.set_size(w, h)
        video_writer.open(output)

        prev = 0
        self._video.seek(0)

        for i in range(len(segments)):
            # Segment begin time and segment end time
            sbt, set = segments[i]

            # Turn time values into index of frame
            sbf = int(sbt * self._video.get_framerate())
            sef = int(round(set * self._video.get_framerate(), 0))

            # A non-anonymized segment in the hole
            if sbf > prev:
                for i in range(sbf-prev):
                    frame = self._video.read_frame()
                    video_writer.write(frame)

            logging.debug("  - Anonymized frames: {} {}".format(sbf, sef))
            for i in range(sef-sbf):
                # Where are the faces in this image?
                frame = self._video.read_frame()
                coords = self._facedetect.image_face_detect(frame)
                # Anonymization of each detected face area
                for c in coords:
                    if c is not None:
                        if self._mode == "mouth":
                            # Blur mouth only -- with approx. coords
                            x = c.x + (c.w // 10)   # shift x 10% to the right
                            y = c.y + c.h - (c.h // 3)    # shift y
                            w = int(float(c.w) * 0.8)  # Reduce width by 20%
                            h = int(float(c.h) * 0.35)  # Reduce width by 20%
                            c = sppasCoords(x, y, w, h)
                        mouth_crop = frame.icrop(c)
                        bface = mouth_crop.iblur(value=51, method=None)
                        frame = frame.ipaste(bface, c)

                video_writer.write(frame)

            # prepare next round
            prev = sef

        # end
        if prev < self._video.get_nframes():
            logging.debug("  -> NON-anonymized: {} {}".format(prev, self._video.get_nframes()))
            for i in range(self._video.get_nframes()-prev):
                frame = self._video.read_frame()
                video_writer.write(frame)

        video_writer.close()
