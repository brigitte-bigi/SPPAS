# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.FaceSights.sightsbuffer.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Video buffer to manage the 68 sights on faces of a video.

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
from sppas.src.videodata import sppasCoordsVideoBuffer

from sppas.src.imgdata.sights import sppasSights

# ---------------------------------------------------------------------------


class sppasKidsSightsVideoBuffer(sppasCoordsVideoBuffer):
    """A video buffer with lists of coordinates, identifiers and sights.

    """

    def __init__(self,
                 video=None,
                 size=-1):
        """Create a new instance.

        :param video: (str) The video filename
        :param size: (int) Number of images of the buffer or -1 for auto

        """
        super(sppasKidsSightsVideoBuffer, self).__init__(video, size=size)

        # The list of list of sppasSights instances() and face identifiers
        # By default, the identifier is the face number
        self.__sights = list()
        self.__ids = list()
        self.__init_sights()

    # -----------------------------------------------------------------------

    def __init_sights(self):
        # The list of list of identifiers
        self.__ids = list()
        # The list of list of sights
        self.__sights = list()
        for i in range(self.get_buffer_size()):
            self.__sights.append(list())
            self.__ids.append(list())

    # -----------------------------------------------------------------------

    def reset(self):
        """Override. Reset all the info related to the buffer content."""
        sppasCoordsVideoBuffer.reset(self)
        self.__init_sights()

    # -----------------------------------------------------------------------

    def next(self):
        """Override. Fill in the buffer with the next images & reset sights.

        """
        ret = sppasCoordsVideoBuffer.next(self)
        self.__init_sights()
        return ret

    # -----------------------------------------------------------------------

    def get_ids(self, buffer_index=None):
        """Return the identifiers of all faces of a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :return: (list of identifiers)

        """
        if buffer_index is not None:
            buffer_index = self.check_buffer_index(buffer_index)
            return self.__ids[buffer_index]
        else:
            return self.__ids

    # -----------------------------------------------------------------------

    def get_sights(self, buffer_index=None):
        """Return the sights of all faces of a given image.

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

    def set_ids(self, buffer_index, ids):
        """Set the face identifiers of a given image index.

        The number of identifiers must match the number of faces.

        :param buffer_index: (int) Index of the image in the buffer
        :param ids: (list of identifiers) A list of face identifiers

        """
        coords_i = self.get_coordinates(buffer_index)
        if isinstance(ids, (list, tuple)) is True:
            if len(coords_i) != len(ids):
                raise ValueError("Expected {:d} identifiers. Got {:d} instead."
                                 "".format(len(coords_i), len(ids)))
            self.__ids[buffer_index] = ids

        else:
            raise sppasTypeError(type(ids), "(list, tuple)")

    # -----------------------------------------------------------------------

    def set_sights(self, buffer_index, sights):
        """Set the sights to a given image index.

        The number of sights must match the number of faces.

        :param buffer_index: (int) Index of the image in the buffer
        :param sights: (list of sppasSights) Set the list of sights

        """
        coords_i = self.get_coordinates(buffer_index)

        if isinstance(sights, (list, tuple)) is True:
            if len(coords_i) != len(sights):
                raise ValueError("Expected {:d} sights. Got {:d} instead."
                                 "".format(len(coords_i), len(sights)))
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

    def get_sight(self, buffer_index, face_index):
        """Return the sights of a face of a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :param face_index: (int) Index of the face
        :return: (sppasSights)

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if 0 <= face_index < len(self.__sights[buffer_index]):
            return self.__sights[buffer_index][face_index]

        raise ValueError("Invalid face index value.")

    # -----------------------------------------------------------------------

    def get_id(self, buffer_index, face_index):
        """Return the identifier of a face of a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :param face_index: (int) Index of the face
        :return: (sppasSights)

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if 0 <= face_index < len(self.__ids[buffer_index]):
            return self.__ids[buffer_index][face_index]

        raise ValueError("Invalid face index value.")

    # -----------------------------------------------------------------------

    def set_sight(self, buffer_index, face_index, sight):
        """Set the sights to a face of a given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :param sight: (sppasSights) the given sight object

        """
        buffer_index = self.check_buffer_index(buffer_index)

        if isinstance(sight, sppasSights):
            if face_index < len(self.__sights[buffer_index]):
                self.__sights[buffer_index][face_index] = sight
            else:
                raise ValueError("face index error")
        else:
            raise sppasTypeError(sight, "sppasSights")

    # -----------------------------------------------------------------------

    def set_id(self, buffer_index, coords_index, identifier):
        """Set the id to coordinate of a given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :param coords_index: (int) Index of the coordinates for this id
        :param identifier: (any) Any relevant information

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if coords_index < len(self.__ids[buffer_index]):
            self.__ids[buffer_index][coords_index] = identifier
        else:
            raise ValueError("Face index error {}".format(coords_index))

    # -----------------------------------------------------------------------

    def set_coordinates(self, buffer_index, coords):
        """Set the coordinates to a given image index.

        Override to invalidate the corresponding sights and identifiers.

        :param buffer_index: (int) Index of the image in the buffer
        :param coords: (list of sppasCoords) Set the list of coords

        """
        sppasCoordsVideoBuffer.set_coordinates(self, buffer_index, coords)
        self.__sights[buffer_index] = [None for i in range(len(coords))]
        self.__ids[buffer_index] = [str(i+1) for i in range(len(coords))]

    # -----------------------------------------------------------------------

    def append_coordinate(self, buffer_index, coord):
        """Override. Append the coordinates to a given image index.

        :param buffer_index: (int) Index of the image in the buffer
        :param coord: (sppasCoords) Append the given coord
        :return: (int) Index of the new coordinate

        """
        sppasCoordsVideoBuffer.append_coordinate(self, buffer_index, coord)
        self.__sights[buffer_index].append(None)
        self.__ids[buffer_index].append(str(len(self.__sights)))
        return len(self.__sights[buffer_index])-1

    # -----------------------------------------------------------------------

    def remove_coordinate(self, buffer_index, coord):
        """Remove the coordinates to a given image index.

        Override to remove the sights and the identifier too.

        :param buffer_index: (int) Index of the image in the buffer
        :param coord: (sppasCoords) Remove the given coord

        """
        face_idx = self.index_coordinate(buffer_index, coord)
        sppasCoordsVideoBuffer.pop_coordinate(self, buffer_index, face_idx)
        self.__sights[buffer_index].pop(face_idx)
        self.__ids[buffer_index].pop(face_idx)

    # -----------------------------------------------------------------------

    def pop_coordinate(self, buffer_index, coord_index):
        """Remove the coordinates to a given image index.

        Override to pop the sights and the identifier too.

        :param buffer_index: (int) Index of the image in the buffer
        :param coord_index: (int) Pop the given coord

        """
        buffer_index = self.check_buffer_index(buffer_index)
        sppasCoordsVideoBuffer.pop_coordinate(self, buffer_index, coord_index)
        self.__sights[buffer_index].pop(coord_index)
        self.__ids[buffer_index].pop(coord_index)

    # -----------------------------------------------------------------------

    def get_id_coordinate(self, buffer_index, identifier):
        """Return the coordinate of a given identifier in a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :param identifier: (int) Identifier to search
        :return: (sppasCoords) Coordinates or None

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if identifier in self.__ids[buffer_index]:
            coord_idx = self.__ids[buffer_index].index(identifier)
            return self.get_coordinate(buffer_index, coord_idx)

        return None

    # -----------------------------------------------------------------------

    def get_id_sight(self, buffer_index, identifier):
        """Return the sights of a given identifier in a given image.

        :param buffer_index: (int) Index of the image in the buffer
        :param identifier: (int) Identifier to search
        :return: (sppasCoords) Coordinates or None

        """
        buffer_index = self.check_buffer_index(buffer_index)
        if identifier in self.__ids[buffer_index]:
            coord_idx = self.__ids[buffer_index].index(identifier)
            return self.get_sight(buffer_index, coord_idx)

        return None
