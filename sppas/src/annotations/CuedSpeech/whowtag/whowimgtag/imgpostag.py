# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whowtag.whowimgtag.imgpostag.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Tag an image with the vowels positions.

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
import numpy

from sppas.core.coreutils import sppasTypeError
from sppas.src.imgdata import sppasImage
from sppas.src.anndata import sppasFuzzyPoint
from sppas.src.annotations.CuedSpeech.whatkey.phonestokeys import CuedSpeechKeys

# ---------------------------------------------------------------------------


class sppasImageVowelPosTagger:
    """Tag the image of vowel positions with colored circles.

    """

    def __init__(self, cue_rules: CuedSpeechKeys = CuedSpeechKeys()):
        """The constructor of the SppasImageVowelsTagger class.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes
        :raises: sppasTypeError: If the parameter are not an instance of CuedSpeechKeys class

        """
        if not isinstance(cue_rules, CuedSpeechKeys):
            raise sppasTypeError(cue_rules, "CuedSpeechKeys")

        self.__cued = cue_rules

        # The colors for the vowels
        self.__colors = dict()
        #self.__colors['b'] = [128, 255,   0,   0, 205, 200]
        #self.__colors['g'] = [128, 128, 175, 128,   0,   0]
        #self.__colors['r'] = [128,   0,   0, 255,   0, 100]
        self.__colors['b'] = [128, 0, 200, 0, 180, 100, 50, 100]
        self.__colors['g'] = [128, 120, 100, 80, 0, 0, 170, 220]
        self.__colors['r'] = [128, 0, 0, 160, 80, 180, 50, 100]

        # Add the name of the vowel inside the circle
        self.__vowel_name_option = False
        self.__thickness = 2

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechKeys):
        """Set the CuedSpeechKeys used to tag the video.

        :param cue_rules: (CuedSpeechKeys) The instance of the cuedSpeechKeys to set

        """
        self.__cued = cue_rules

    # -----------------------------------------------------------------------

    def get_vowel_text(self, vowel_index: int) -> str:
        """Return the text code for the given vowel index.

        :param vowel_index: (int) The vowel rank
        :return: (str) The text code associated with the given index, or empty string if the index is wrong

        """
        # Vowels key codes
        vowels_code = self.__cued.get_vowels_codes()

        # Code of the i-th vowel
        if 0 <= vowel_index < len(vowels_code):
            return vowels_code[vowel_index]

        return ""

    # -----------------------------------------------------------------------

    def get_vowel_color(self, color_index: int) -> tuple:
        """Return the color for the given vowel index.

        :param color_index: (int) The vowel rank
        :return: (tuple) The bgr color of the vowel associated with the given index
                 If we have a wrong index the method return (128, 128, 128) bgr color by default

        """
        bgr_color = (128, 128, 128)

        if 0 <= color_index < len(self.__colors['r']):
            r = self.__colors['r'][color_index]
            g = self.__colors['g'][color_index]
            b = self.__colors['b'][color_index]

            bgr_color = (b, g, r)

        return bgr_color

    # -----------------------------------------------------------------------

    def enable_vowel_name(self, value: bool = True) -> None:
        """Set the option to tag the name of each vowel in its circle.

        :param value: (bool) Boolean value representing if the option "tag name" is activated or not
                      Optional parameter, value = True by default

        """
        self.__vowel_name_option = value

    # -----------------------------------------------------------------------

    def set_thickness(self, value: int = 1) -> None:
        """Set the thickness of the pen to draw the text into vowel circles.

        :param value: (int) The thickness value
                      Optional parameter, value = 1 by default

        """
        if value < 1:
            value = 1

        self.__thickness = value

    # -----------------------------------------------------------------------
    # Image tagging
    # -----------------------------------------------------------------------

    def slap_on(self, image: numpy.ndarray, fuzzy_points: list) -> sppasImage:
        """Tag the given vowels to the image.

        :param image: (sppasImage or numpy.ndarray) The image to draw vowel positions on
        :param fuzzy_points: (list[sppasFuzzyPoint]) The coordinates of vowels
        :raises: sppasTypeError: If any parameters is of a wrong type
        :return: (sppasImage) The image with the vowels applied on it

        """
        # Check the image to be tagged
        img = self.__check_image(image)

        # Draw a circle for each given vowel
        self.draw_pos_circles(img, fuzzy_points)

        # Draw the vowel name in the middle of the circle
        self.draw_pos_names(img, fuzzy_points)

        return img

    # -----------------------------------------------------------------------

    def draw_pos_circles(self, img: sppasImage, fuzzy_points: list) -> None:
        """Draw vowel positions on an image at given fuzzy points.

        :param img: (sppasImage) The image to draw vowel positions on
        :param fuzzy_points: (list[sppasFuzzyPoint]) The coordinates of vowels
        :return: (None)

        """
        if isinstance(fuzzy_points, list) is False:
            raise sppasTypeError(fuzzy_points, "list")
        if isinstance(img, sppasImage) is False:
            raise sppasTypeError(img, "sppasImage")

        for index, current_fuzzy_point in enumerate(fuzzy_points):
            # Get the coordinates of the vowel: (x,y) and radius.
            if current_fuzzy_point is None or isinstance(current_fuzzy_point, sppasFuzzyPoint) is False:
                continue

            x, y = current_fuzzy_point.get_midpoint()
            radius = max(5, current_fuzzy_point.get_radius())

            # Fix the color of the circle of the i-th vowel
            bgr = self.get_vowel_color(index)
            # Draw the circle with a gradient color to white.
            # It is stripped to mimic transparency.
            for _r in range(1, radius, 4):
                blue = min(255, bgr[0] + (_r * 3))
                green = min(255, bgr[1] + (_r * 3))
                red = min(255, bgr[2] + (_r * 3))
                img.surround_point((x, y), (blue, green, red), 2, _r)

    # -----------------------------------------------------------------------

    def draw_pos_names(self, img: sppasImage, fuzzy_points: list) -> None:
        """Draw vowel position names on an image at given fuzzy points.

        :param img: (sppasImage) The image to draw vowel positions on
        :param fuzzy_points: (list[sppasFuzzyPoint]) The coordinates of vowels
        :return: (None)

        """
        if isinstance(fuzzy_points, list) is False:
            raise sppasTypeError(fuzzy_points, "list")
        if isinstance(img, sppasImage) is False:
            raise sppasTypeError(img, "sppasImage")

        for index, current_fuzzy_point in enumerate(fuzzy_points):
            # Get the coordinates of the vowel: (x,y) and radius.
            if current_fuzzy_point is None or isinstance(current_fuzzy_point, sppasFuzzyPoint) is False:
                continue
            x, y = current_fuzzy_point.get_midpoint()
            radius = max(6, current_fuzzy_point.get_radius())

            # Draw the vowel name in the middle of the circle
            if self.__vowel_name_option:
                text = self.get_vowel_text(index)
                if x >= 0 and y >= 0 and len(text) > 0:
                    img.put_text((x - (radius // 2), y + (radius // 2)), (250, 250, 250), self.__thickness, text)

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __check_image(self, image: numpy.ndarray) -> sppasImage:
        """Check the given image and return it as a sppasImage object.

        :param image: (numpy.ndarray) The image to check
        :return: (sppasImage) The converted image
        :raises: sppasTypeError: If any parameters is of a wrong type

        """
        if isinstance(image, sppasImage) is True:
            img = image.copy()
        elif isinstance(image, numpy.ndarray) is True:
            img = sppasImage(input_aray=image)
        else:
            raise sppasTypeError(image, "sppasImage")

        return img
