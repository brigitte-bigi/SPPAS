# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.HandPose.videohandpose.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Automatic detection of the sights of hands/body of a video.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

import logging

from sppas.core.coreutils import sppasError
from sppas.src.videodata import sppasSightsVideoBuffer

from .mphanddetect import MediaPipeHandPoseDetector

# ---------------------------------------------------------------------------


class HandPoseMode(object):
    """All detection mode of Hand&Pose detection.

    :Example:

        >>>with HandPoseMode() as s:
        >>>    print(s.BOTH)

    This class is a solution to mimic an 'Enum' but is compatible with both
    Python 2.7 and Python 3+.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            POSE=1,
            HAND=2,
            BOTH=3
        )

    # -----------------------------------------------------------------------

    def __contains__(self, item):
        return item in self.__dict__.values()

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------


class VideoHandPoseDetector(object):
    """Estimate the hand&pose sights of a video.

    Three detection modes are available:

        1. Pose only. Detect the 33 sights of the body of a human. Each hand
        is represented by 5 sights.

        2. Hands only. Detect the 21 sights of all hands.

        3. Detect pose first then detect the 2 hands in the ROIs defined by
        the result of the pose detection. If no hand is detected, it has the
        5 sights of the pose detection result, but if a hand is detected, it
        has the 21 expected sights. This solution ensure there will be 2 and
        only 2 detected hands in each image of the video: the right one and
        the left one. The saved results are **hand sights** only.

    """

    def __init__(self, img_hands):
        """Create a new instance.

        :param img_hands: (MediaPipeHandDetector) Image detection system

        """
        # The hand's detection system
        if isinstance(img_hands, MediaPipeHandPoseDetector) is False:
            raise sppasError("A hands detection system was expected.")

        self._video_buffer = sppasSightsVideoBuffer()
        self.__hdi = img_hands
        self.__all_hands = list()
        self.__mode = HandPoseMode().BOTH

    # -----------------------------------------------------------------------

    def get_mode(self):
        """Return the detection mode: hands only, pose only or hand&pose."""
        return self.__mode

    # -----------------------------------------------------------------------

    def set_mode(self, value):
        """Set the detection mode.

        :param value: (HandPoseMode) detection mode: 0, 1 or 2.

        """
        value = int(value)
        with HandPoseMode() as m:
            if value not in m:
                raise ValueError("Expected a mode.")
        self.__mode = value

    # -----------------------------------------------------------------------
    # Automatic detection of the face sights in a video
    # -----------------------------------------------------------------------

    def video_hand_sights(self, video, video_writer=None, output=None):
        """Browse the video, detect hands then detect sights and write results.

        :param video: (str) Video filename
        :param video_writer: ()
        :param output: (str) The output name for the folder and/or the video

        :return: (list) The list of filenames or none

        """
        # Open the video stream
        self._video_buffer.open(video)
        self._video_buffer.seek_buffer(0)
        if video_writer is not None:
            video_writer.set_fps(self._video_buffer.get_framerate())

        # Browse the video using the buffer of images
        self.__all_hands = list()
        result_files = list()
        read_next = True
        nb = 0
        i = 0

        while read_next is True:
            # fill-in the buffer with 'size'-images of the video
            logging.info("Read buffer number {:d}".format(nb+1))
            read_next = self._video_buffer.next()

            # Detect hand sights on all the images of the current buffer
            self._detect_buffer()

            # save the current results: file names
            if output is not None and video_writer is not None:
                new_files = video_writer.write(self._video_buffer, output)
                result_files.extend(new_files)

            nb += 1
            i += len(self._video_buffer)

        # Release the video stream
        self._video_buffer.close()
        self._video_buffer.reset()

        if output is not None and video_writer is not None:
            return result_files

        return self.__all_hands

    # -----------------------------------------------------------------------

    def _detect_buffer(self):
        """Determine the sights of all the detected faces of all images.

        :raise: sppasError if no model was loaded or no faces.

        """
        # No buffer is in-use.
        if len(self._video_buffer) == 0:
            logging.warning("Nothing to detect: no images in the buffer.")
            return

        # Find the sights of all hands in each image.
        for i, image in enumerate(self._video_buffer):
            if image is None:
                continue
            # Detect hands only, pose only, both.
            with HandPoseMode() as m:
                if self.__mode == m.HAND:
                    self.__hdi.detect_hands(image)
                elif self.__mode == m.POSE:
                    self.__hdi.detect_pose(image)
                else:
                    self.__hdi.detect(image)

            # Fill-in the buffer of the current image with the detection
            hands = list()
            for hand in self.__hdi:
                # Save results into the list of sights of such image
                self._video_buffer.append_sight(i, hand)
                hands.append(hand)
            self.__all_hands.append(hands)
