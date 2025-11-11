# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whowtag.handsets.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Data structure to load and store all hands.

.. _This file is part of SPPAS: <https://sppas.org/>
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
import os
import logging

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasValueError
from sppas.core.coreutils import sppasIOError
from sppas.src.resources import sppasHandResource
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasImageSightsReader

from ..whatkey.phonestokeys import CuedSpeechKeys

from .handproperties import sppasHandProperties
from .handfilters import sppasHandFilters

# -----------------------------------------------------------------------


class sppasHandsSet:
    """Data structure to load and store all hands.

    """

    def __init__(self, cue_rules: CuedSpeechKeys = CuedSpeechKeys()):
        """Store an image of a hand for each given consonant.

        :param cue_rules: (CuedSpeechKeys) Cued speech rules
                          Optional parameter, new instance of CuedSpeechKeys class by default
        :raises: sppasTypeError: If the parameter is not an instance of CuedSpeechKeys

        """
        if isinstance(cue_rules, CuedSpeechKeys) is False:
            raise sppasTypeError(cue_rules, "CuedSpeechKeys")

        # The rules to cue. Includes the list of supported positions and shapes.
        self.__cued = cue_rules

        # The property of each hand shape of the hands set.
        # key is a shape_code, value is a sppasHandProperties
        self.__hands_properties = dict()

        # Filters that can be applied on the hand images
        self.__hands_filter = sppasHandFilters()

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechKeys):
        """Set the CuedSpeechKeys used to tag the video.

        :param cue_rules: (CuedSpeechKeys) The instance of the cuedSpeechKeys to set

        """
        self.__cued = cue_rules

    # -----------------------------------------------------------------------

    def image(self, shape_code: str):
        """Return a deep copy of the hand image matching with the given code.

        Return None if no image associated with the given code.

        :param shape_code: (str) Hand shape vowel code
        :return: (sppasImage or None) The hand image corresponding to the code, or None if the code is wrong

        """
        if shape_code in self.__hands_properties.keys():
            return self.__hands_properties[shape_code].image().copy()
        else:
            return None

    # -----------------------------------------------------------------------

    def target_coords(self, shape_code: str):
        """Return target coords of the hand image matching with the given code.

        Return None if no image associated with the given code.

        :param shape_code: (str) Hand shape vowel code
        :return: ((int, int) or None) The target coords of the hand image, or None if the code is wrong

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].target_coords()
        else:
            return None

    # -----------------------------------------------------------------------

    def get_sight(self, shape_code: str, index: int):
        """Return a sight of a hand with the given shape code and index.

        Return None if no image associated with the given code.

        :param shape_code: (str) Hand shape vowel code
        :param index: (int) The index of the sight that we want
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (tuple[int, int] or None) The coords of the sight, or None if the code is wrong

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].get_sight(index)
        else:
            return None

    # -----------------------------------------------------------------------

    def angle(self, shape_code: str) -> int:
        """Return the angle of the hand image matching with the given code.

        Return 0 if no image associated with the given code.

        :param shape_code: (str) Hand shape vowel code
        :return: (int) The angle of the hand image, Or 0 if the code is wrong

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].angle()
        return 0

    # -----------------------------------------------------------------------

    def angle_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Return the angle of the given sight compared to S0-S9 axis.

        :param shape_code: (str) Hand shape vowel code
        :param sight_index: (int) The index of the sight
        :return: (int) the computed angle
        :raises: IntervalRangeException: If the index is negative or out of bounds

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].get_angle_with_s0(sight_index)
        return 0

    # -----------------------------------------------------------------------

    def distance(self, shape_code: str) -> int:
        """Return the distance of the hand image matching with the given code.

        Return 0 if no image associated with the given code.

        :param shape_code: (str) Shape code name
        :return: (int) The distance of the current hand, or 0 if the code is wrong

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].distance()
        return 0

    # -----------------------------------------------------------------------

    def distance_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Get the distance between s0 and a sight of the hand.

        :param shape_code: (str) Shape code name
        :param sight_index: (int) The index of the sight
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (int) the computed distance

        """
        if shape_code in self.__hands_properties:
            return self.__hands_properties[shape_code].get_distance_with_s0(sight_index)
        return 0

    # -----------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------

    def load(self, prefix: str) -> int:
        """Load the hand images matching with the given prefix.

        :param prefix: (str) Prefix in hand image filenames
        :raises: sppasIOError: If the files with the given prefix and pattern are not found
        :return: (int) The number of hands loaded

        """
        hands_sets_manager = sppasHandResource()
        hands_sets_manager.load_hand_set(prefix)

        # load hands set and add them of this instance
        self.__load_hand_pictures(hands_sets_manager.get_hand_images(prefix),
                                  hands_sets_manager.get_hands_sights(prefix))

        return len(self.__hands_properties)

    # -----------------------------------------------------------------------

    def apply_hands_filter(self, filter_name: str) -> None:
        """Apply a filter on all hands images loaded.

        :param filter_name: (str) The name of the filter to apply
        :raises: sppasValueError: Unknown filter name

        """
        if hasattr(self.__hands_filter, filter_name):
            for key, item in self.__hands_properties.items():
                item.set_image(getattr(self.__hands_filter, filter_name)(item, key))

        # Unknown filter name
        else:
            raise sppasValueError("filter_name", filter_name)

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def __load_hand_pictures(self, hands_images: list, hands_sights: list) -> None:
        """Return the dictionary of pictures filepath for the hand shapes.

        The number of images and sights should be the same and equal to the
        number of shapes for the given language.

        Notice that it is supposed that the loaded images are ranked
        in the same order as the shapes, i.e., shape "0" is
        represented in the first image, etc.

        :param hands_images: (list) Prefix in hand image filenames
        :param hands_sights: (list) Pattern in hand image filenames

        :raises: sppasError: If the number of images is different of sights
        :raises: sppasIOError: If a file to read is not found
        :raises: sppasError: If invalid number of images or sights.
        :return: (dict[str, SppasHandProperties]) The pictures filepath dictionary

        """
        _shapes = self.__cued.get_consonants_codes()
        if len(_shapes) != len(hands_images):
            raise sppasError("Invalid number of hand images. "
                             f"Expected {len(_shapes)}. Got {len(hands_images)} instead.")
        if len(_shapes) != len(hands_sights):
            raise sppasError("Invalid number of hand sights. "
                             f"Expected {len(_shapes)}. Got {len(hands_sights)} instead.")

        # Foreach hand shape
        for i, paths in enumerate(zip(hands_images, hands_sights)):
            # "paths" is a tuple (image_path, sights_path)

            # Load image of the hand
            if os.path.exists(paths[0]) is False:
                logging.warning(f"Can't find hand picture file {paths[0]}.")
                break

            hand_img = sppasImage(filename=paths[0])

            # load annotation file
            if os.path.exists(paths[1]) is False:
                logging.warning(f"Can't find hand sights file {paths[1]}.")
                break

            # try to parse the annotation file
            try:
                data = sppasImageSightsReader(paths[1])
                if len(data.sights) != 1:
                    raise sppasError(f"Invalid file sights {paths[1]}. ({len(data.sights)} != 1)")

                current_sights = data.sights[0]

                # If there isn't an expected number of sights
                # if len(current_sights) not in sppasHandProperties.NUMBER_OF_SIGHTS:
                #     raise sppasError(f"Invalid number of sights in file {paths[1]}. "
                #                      f"Expected one of {str(sppasHandProperties.NUMBER_OF_SIGHTS)}. "
                #                      f"Got {str(len(current_sights))} instead.")

                # If s0 or s9 is missing of the file with sights.
                # Actually, only the 2 sights are required; the target is optional
                if current_sights.get_sight(0) is None or current_sights.get_sight(9) is None:
                    raise sppasIOError(paths[1])

                # get target index value depending on the current shape code
                target_index = self.__cued.get_shape_target(_shapes[i])

                # add to dictionary the hand shape and its values
                self.__hands_properties[_shapes[i]] = sppasHandProperties(hand_img, current_sights, target_index)

            except sppasIOError as e:
                logging.error(f"Error while reading hand sights: {e}")

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of hand shapes loaded."""
        return len(self.__hands_properties)
