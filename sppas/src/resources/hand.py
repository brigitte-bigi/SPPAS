# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.resources.hand.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Manage all hands image and annotation files installed in the resources folder.

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

from __future__ import annotations
import os
import logging
import re

from sppas.core.config import paths
from sppas.core.coreutils import sppasEnableFeatureError
from sppas.core.coreutils import sppasIOError
from sppas.core.coreutils import NegativeValueError
from sppas.core.coreutils import IndexRangeException
from sppas.src.imgdata import image_extensions
from sppas.src.imgdata import sppasImage
from sppas.src.wkps import FileRoot

# ----------------------------------------------------------------------------

NB_SHAPES = 9

# ----------------------------------------------------------------------------


class sppasHandResource:
    """Manage hand files in the resources folder to the cued speech annotation.

    A hands set is composing of 9 hand shapes images and sights annotation file (xra or csv).
    The files are to be in the resources/cuedspeech folder with this specific files name format:
        - {prefix}_{hand_shape_number}{postfix}.png
        - {prefix}_{hand_shape_number}{postfix}.xra || {prefix}_{hand_shape_number}{postfix}.csv

    The prefix and postfix mustn't content number (0-9) character.

    """

    def __init__(self):
        """The constructor of the sppasHandResource class.

        """
        self.__hands = dict()

    # ----------------------------------------------------------------------------
    # Getters
    # ----------------------------------------------------------------------------

    def get_hand_sets_identifiers(self) -> list:
        """Get all hands sets identifiers loaded.

        The identifiers are the prefix of the hands sets when they are loaded.

        :return: (list[str]) All identifiers

        """
        return list(self.__hands.keys())

    # ----------------------------------------------------------------------------

    def get_hand_images(self, identifier: str) -> list | None:
        """Get all hands shapes images path of a hands set linked with the given prefix.

        :param identifier: (str) The identifier (prefix) of the hands set

        :return: (list[str] or None) The path of the hands shapes images
                                     None if no hands set is associated with the given prefix

        """
        if self.__hands.get(identifier) is None:
            return None

        return self.__hands.get(identifier)[0]

    # ----------------------------------------------------------------------------

    def get_shape(self, identifier: str, index: int) -> sppasImage | None:
        """Get hand image path associated with the given prefix and index.

        :param identifier: (str) The identifier (prefix) of the hands set
        :param index: (int) The index of the shape

        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of shapes

        :return: (sppasImage or None) The path of the hand shape
                                      None if no hands set is associated with the given prefix

        """
        if index < 0:
            raise NegativeValueError(index)

        if index > NB_SHAPES:
            raise IndexRangeException(index, 0, NB_SHAPES)

        if self.__hands.get(identifier) is None:
            return None

        return self.__hands.get(identifier)[0][index]

    # ----------------------------------------------------------------------------

    def get_hands_sights(self, identifier: str) -> list | None:
        """Get all hands shapes sights path linked with the given prefix.

        :param identifier: (str) The identifier (prefix) of the hands set

        :return: (list[sppasSights] or None) The path of the hands shapes sights
                                             None if no hands set is associated with the given prefix

        """
        if self.__hands.get(identifier) is None:
            return None

        return self.__hands.get(identifier)[1]

    # ----------------------------------------------------------------------------

    def get_sights(self, identifier: str, index: int) -> sppasImage | None:
        """Get hand image path associated with the given prefix and index.

        :param identifier: (str) The identifier (prefix) of the hands set
        :param index: (int) The index of the shape

        :raises: NegativeValueError: If the index is negative (Impossible for an index !)
        :raises: IndexRangeException: If the index is superior of the number of shapes

        :return: (sppasImage or None) The path of the hand shape
                                      None if no hands set is associated with the given prefix

        """
        if index < 0:
            raise NegativeValueError(index)

        if index > NB_SHAPES:
            raise IndexRangeException(index, 0, NB_SHAPES)

        if self.__hands.get(identifier) is None:
            return None

        return self.__hands.get(identifier)[1][index]

    # ----------------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------------

    def clear_hands_resources(self) -> None:
        """Clear all hands sets loaded."""
        self.__hands.clear()

    # ----------------------------------------------------------------------------

    def automatic_loading(self) -> None:
        """Search and load all hands sets in the resources' folder.

        :raises: sppasEnableFeatureError: If the resources/cuedspeech folder doesn't exist
        :raises: sppasIOError: If a hands set found has a missing file (image or annotation)

        """
        # check if the resources/cuedspeech folder exist
        if os.path.exists(os.path.join(paths.resources, "cuedspeech")) is False:
            raise sppasEnableFeatureError("cuedspeech")

        # get files in the resources/cuedspeech folder
        files = os.listdir(os.path.join(paths.resources, "cuedspeech"))

        for file in files:
            # search file pattern {prefix}_{shape-code}{pattern}.{file-extension}
            if not re.search("^[^0-9]+_[0-8][^0-9]*\\..+$", file):
                continue

            # split the filename with the number (shape code) as separator
            file_root = FileRoot.root(file)
            prefix = file_root[:-2]
            postfix = FileRoot.pattern(file)

            # hands set already append
            if prefix in self.__hands.keys():
                continue

            try:
                self.load_hand_set(prefix, postfix=postfix)
            except sppasIOError as error:
                logging.warning("The hands set '{0}' is missing a file.\nLog Trace: {1}".format(prefix, error))

    # ----------------------------------------------------------------------------

    def load_hand_set(self, prefix: str, postfix: str = "-hands"):
        """Load a hands set from the given prefix and postfix in the resources' folder.

        :param prefix: (str) The prefix (identifier) of the hands set
        :param postfix: (str) The postfix of the hands set

        :raises: sppasIOError: If the image or the annotation files are not found

        """
        image_list = list()
        sights_list = list()

        for i in range(NB_SHAPES):
            # get files path of the current image and sights hand shape
            image_filepath, sights_filepath = self.__check_shape_files(prefix, postfix, i)
            logging.debug(f" - Image file path: {image_filepath}")
            logging.debug(f" - Sights file path: {sights_filepath}")

            # missing shape image or shape annotation
            if len(image_filepath) == 0:
                raise sppasIOError(f"Missing image file {prefix}_{i}{postfix}")
            if len(sights_filepath) == 0:
                raise sppasIOError(f"Missing annotation file {prefix}_{i}{postfix}")

            image_list.append(image_filepath)
            sights_list.append(sights_filepath)

        # set the hands set
        self.__hands[prefix] = image_list, sights_list

    # ----------------------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------------------

    def __check_shape_files(self, prefix: str, postfix: str, index: int) -> tuple:
        """Return the file path of the image and annotation file (or empty string).

        :param prefix: (str) The prefix (identifier) of the hands set
        :param postfix: (str) The postfix of the hands set
        :param index: (int) The index of the shape files

        :return: (tuple[str, str]) The file path of the image and sights annotation
                                  Empty string if the doesn't exist

        """
        img_file_path = ""
        annotation_file_path = ""

        files_name = "{0}_{1}{2}"
        files_path1 = os.path.join(paths.resources, "cuedspeech", files_name.format(prefix, index, ""))
        files_path2 = os.path.join(paths.resources, "cuedspeech", files_name.format(prefix, index, postfix))

        for extension in image_extensions:
            if os.path.exists(files_path1 + extension) is True:
                img_file_path = files_path1 + extension
                break

        if os.path.exists(files_path2 + ".xra") is True:
            annotation_file_path = files_path2 + ".xra"
        elif os.path.exists(files_path2 + ".csv") is True:
            annotation_file_path = files_path2 + ".csv"

        return img_file_path, annotation_file_path

    # ----------------------------------------------------------------------------
    # Overloads Methods
    # ----------------------------------------------------------------------------

    def __len__(self):
        """Return the number of hands sets loaded."""
        return len(self.__hands)
