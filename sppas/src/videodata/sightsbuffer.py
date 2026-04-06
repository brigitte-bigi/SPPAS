# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.HandPose.sightsbuffer.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Video buffer to manage the sights of objects of a video.

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

    ---------------------------------------------------------------------

"""


from sppas.core.coreutils import sppasTypeError

from sppas.src.imgdata.sights import sppasSights

from .videobuffer import sppasVideoReaderBuffer

# ---------------------------------------------------------------------------


class sppasSightsVideoBuffer(sppasVideoReaderBuffer):
    """A video buffer with lists of sights.

    """

    def __init__(self,
                 video=None,
                 size=-1):
        """Create a new instance.

        :param video: (str) The video filename
        :param size: (int) Number of images of the buffer or -1 for auto

        """
        super(sppasSightsVideoBuffer, self).__init__(video, size=size)

        # The list of list of sppasSights instances()
        self.__sights = list()
        self.__init_sights()

    # -----------------------------------------------------------------------

    def __init_sights(self):
        # The list of list of sights
        self.__sights = list()
        for i in range(self.get_buffer_size()):
            self.__sights.append(list())

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Reset all the info related to the buffer content."""
        sppasVideoReaderBuffer.reset(self)
        self.__init_sights()

    # -----------------------------------------------------------------------

    def next(self):
        """Override. Fill in the buffer with the next images & reset sights.

        """
        ret = sppasVideoReaderBuffer.next(self)
        self.__init_sights()
        return ret

    # -----------------------------------------------------------------------

    def get_sights(self, buffer_index=None):
        """Return the sights of all objects of a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :return: (list of sppasSights)

        """
        if buffer_index is not None:
            buffer_index = self.check_buffer_index(buffer_index)
            return self.__sights[buffer_index]
        else:
            if len(self.__sights) != self.__len__():
                raise ValueError("sppasSights were not properly associated to images of the buffer")
            return self.__sights

    # -----------------------------------------------------------------------

    def set_sights(self, buffer_index, sights):
        """Set the sights to a given image index.

        The number of sights does not need to match the number of coords.

        :param buffer_index: (int) Index of the image in the buffer
        :param sights: (list of sppasSights) Set the list of sights

        """
        if isinstance(sights, (list, tuple)) is True:
            # Check if all sights items are correct
            checked = list()
            for c in sights:
                if c is None:
                    c = sppasSights()
                else:
                    if isinstance(c, sppasSights) is False:
                        raise sppasTypeError(c, "sppasSights")
                checked.append(c)

            # Set sights and identifiers
            self.__sights[buffer_index] = checked

        else:
            raise sppasTypeError(type(sights), "(list, tuple)")

    # -----------------------------------------------------------------------

    def get_sight(self, buffer_index, obj_idx):
        """Return the sights of an object of a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :param obj_idx: (int) Index of the object
        :return: (sppasSights)

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if 0 <= obj_idx < len(self.__sights[buffer_index]):
            return self.__sights[buffer_index][obj_idx]

        raise ValueError("Invalid index value to get sights.")

    # -----------------------------------------------------------------------

    def append_sight(self, buffer_index, sight):
        """Set the sights to a given object of a given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :param sight: (sppasSights) the given sight object

        """
        buffer_index = self.check_buffer_index(buffer_index)

        if isinstance(sight, sppasSights):
            self.__sights[buffer_index].append(sight)
        else:
            raise sppasTypeError(sight, "sppasSights")
