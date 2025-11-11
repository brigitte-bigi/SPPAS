"""
:filename: sppas.src.annotations.CuedSpeech.whowtag.handfilters.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Tag an image with a custom filter only for the cued speech hands.

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
import cv2
import inspect
import numpy as np

from sppas.core.coreutils import sppasValueError
from sppas.core.coreutils import sppasTypeError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasSights

from .handproperties import sppasHandProperties

# -----------------------------------------------------------------------


class sppasHandFilters:
    """Apply filters on hand pictures.

    :example:
    >>> f = sppasHandFilters()
    >>> f.get_filter_names()
    ["cartoon", "sights", "skeleton", "sticks", "tgtline"]

    """

    def __init__(self,
                 radius: int = 20,
                 circles_color: tuple = (0, 100, 200),
                 line_thickness: int = 10,
                 lines_color: tuple = (60, 50, 40)
                 ):
        """Create an instance of the sppasHanddFilters class.

        :param radius: (int) Radius of the circles.
        :param circles_color: (tuple) Color of the circles in (B, G, R)
        :param line_thickness: (int) Thickness of the lines.
        :param lines_color: (tuple) Color of the lines in (B, G, R)

        """
        sppasHandFilters.__check_init_parameters(radius, circles_color, line_thickness, lines_color)
        self.__radius = radius
        self.__circles_color = circles_color
        self.__line_thickness = line_thickness
        self.__lines_color = lines_color

        # The sights hidden depending on the hand shape
        self.__sights_hidden = {
            "0": [2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 18, 19, 20],
            "1": [2, 3, 4, 11, 12, 15, 16, 19, 20],
            "2": [2, 3, 4, 15, 16, 19, 20],
            "3": [2, 3, 4, 7, 8],
            "4": [2, 3, 4],
            "5": [],
            "6": [11, 12, 15, 16, 19, 20],
            "7": [15, 16, 19, 20],
            "8": [2, 3, 4, 15, 16, 19, 20]
        }

        # The list of the edges linking the hand sights
        self.__sights_link = [
            (0, 1),
            (0, 5),
            (0, 17),
            (1, 2),
            (2, 3),
            (3, 4),
            (5, 6),
            (5, 9),
            (6, 7),
            (7, 8),
            (9, 10),
            (9, 13),
            (10, 11),
            (11, 12),
            (13, 14),
            (13, 17),
            (14, 15),
            (15, 16),
            (17, 18),
            (18, 19),
            (19, 20)
        ]

    # -----------------------------------------------------------------------

    @staticmethod
    def get_filter_names() -> list:
        """Return the list of available filters."""
        fcts = list()
        for func in inspect.getmembers(sppasHandFilters, predicate=inspect.isroutine):
            if (callable(getattr(sppasHandFilters, func[0])) and
                    func[0].startswith("_") is False and
                    func[0] != "get_filter_names"):
                fcts.append(func[0])
        return fcts

    # -----------------------------------------------------------------------
    # PUBLIC METHODS
    # -----------------------------------------------------------------------

    def cartoon(self, hand_properties: sppasHandProperties, shape_code: str) -> sppasImage:
        """Apply a cartoon filter on a hand image.

        :param hand_properties: (sppasHandProperties) An hands set
        :param shape_code: (str) The hand shape code
        :raises sppasTypeError: If the parameter doesn't have a type expected
        :raises sppasValueError: If the 'shape_code' parameter value is unknown
        :return: (sppasImage) The image with the filter applied on it

        """
        hand_img = hand_properties.image()
        sights = hand_properties.get_sights()
        self.__check_fct_parameters(hand_img, shape_code, sights)
        return hand_img.icartoon()

    # -----------------------------------------------------------------------

    def sights(self, hand_properties: sppasHandProperties, shape_code: str) -> sppasImage:
        """Apply a sights filter on a hand image.

        Put a circle for each sight on the hand linked with line.

        :param hand_properties: (sppasHandProperties) An hands set
        :param shape_code: (str) The hand shape code
        :raises sppasTypeError: If the parameter doesn't have a type expected
        :raises sppasValueError: If the 'shape_code' parameter value is unknown
        :return: (sppasImage) The image with the filter applied on it

        """
        hand_img = hand_properties.image()
        sights = hand_properties.get_sights()
        self.__check_fct_parameters(hand_img, shape_code, sights)

        # Remove alpha-channel.
        data, red, green, blue = sppasHandFilters.__img_to_data(hand_img)

        # Apply sights filter
        data = self.__apply_sights(data, shape_code, sights)

        # Get back the alpha channel and return hand
        return sppasHandFilters.__data_to_img(data, red, green, blue)

    # -----------------------------------------------------------------------

    def skeleton(self, hand_properties: sppasHandProperties, shape_code: str) -> sppasImage:
        """Apply a skeleton image filter from a hand image.

        :param hand_properties: (sppasHandProperties) An hands set
        :param shape_code: (str) The hand shape code
        :raises: sppasTypeError: If the parameter doesn't have a type expected
        :raises: sppasValueError: If the 'shape_code' parameter value is unknown
        :return: (sppasImage) The skeleton image

        """
        hand_img = hand_properties.image()
        sights = hand_properties.get_sights()
        self.__check_fct_parameters(hand_img, shape_code, sights)

        # Create a blank image
        img = sppasImage(0).blank_image(hand_img.width, hand_img.height)

        # Apply sights filter
        self.__apply_sights(img, shape_code, sights)

        # Turn black background into transparent
        temp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(temp, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(img)
        bgra = [b, g, r, alpha]
        img = sppasImage(input_array=cv2.merge(bgra, 4))

        return img

    # -----------------------------------------------------------------------

    def sticks(self, hand_properties: sppasHandProperties, shape_code: str) -> sppasImage:
        """Draw sticks on a specific hand image of a hand set.

        :param hand_properties: (sppasHandProperties) An hands set
        :param shape_code: (str) The hand shape code
        :raises: sppasTypeError: If the parameter doesn't have a type expected
        :raises: sppasValueError: If the 'shape_code' parameter value is unknown
        :return: (sppasImage) The skeleton image

        """
        hand_img = hand_properties.image()
        sights = hand_properties.get_sights()
        self.__check_fct_parameters(hand_img, shape_code, sights)

        # Remove alpha-channel.
        data, red, green, blue = sppasHandFilters.__img_to_data(hand_img)

        # Apply sticks only for specific hand keys (3 and 8)
        if shape_code == "3":
            s5_x, s5_y, _, _ = sights.get_sight(5)
            s6_x, s6_y, _, _ = sights.get_sight(6)
            data = cv2.line(data, (s5_x, s5_y), (s6_x, s6_y), self.__lines_color, self.__line_thickness)

        elif shape_code == "8":
            s5_x, s5_y, _, _ = sights.get_sight(5)
            s8_x, s8_y, _, _ = sights.get_sight(8)
            data = cv2.line(data, (s5_x, s5_y), (s8_x, s8_y), self.__lines_color, self.__line_thickness)

            s9_x, s9_y, _, _ = sights.get_sight(9)
            s12_x, s12_y, _, _ = sights.get_sight(12)
            data = cv2.line(data, (s9_x, s9_y), (s12_x, s12_y), self.__lines_color, self.__line_thickness)

        # Apply circle on the target sight
        data = cv2.circle(data, hand_properties.target_coords(), self.__radius, self.__circles_color, -1)

        # Get back the alpha channel and return hand
        return sppasHandFilters.__data_to_img(data, red, green, blue)

    # -----------------------------------------------------------------------

    def tgtline(self, hand_properties: sppasHandProperties, shape_code: str) -> sppasImage:
        """Draw a circle on the target sight and a line on S0-S9.

        :param hand_properties: (sppasHandProperties) An hands set
        :param shape_code: (str) The hand shape code
        :raises: sppasTypeError: If the parameter doesn't have a type expected
        :raises: sppasValueError: If the 'shape_code' parameter value is unknown
        :return: (sppasImage) The skeleton image

        """
        hand_img = hand_properties.image()
        sights = hand_properties.get_sights()
        self.__check_fct_parameters(hand_img, shape_code, sights)

        # Remove alpha-channel.
        data, red, green, blue = sppasHandFilters.__img_to_data(hand_img)

        # Draw S0-S9 line
        s0_x, s0_y, _, _ = sights.get_sight(0)
        s9_x, s9_y, _, _ = sights.get_sight(9)
        data = cv2.line(data, (s9_x, s9_y), (s0_x, s0_y), self.__lines_color, self.__line_thickness)

        # Apply a circle on the target sight
        data = cv2.circle(data, hand_properties.target_coords(), self.__radius, self.__circles_color, -1)

        # Get back the alpha channel and return hand
        return sppasHandFilters.__data_to_img(data, red, green, blue)

    # -----------------------------------------------------------------------
    # PRIVATE METHODS
    # -----------------------------------------------------------------------

    @staticmethod
    def __img_to_data(img):
        # Remove alpha-channel. The transparency is turned into white.
        bgr_img = img.ibgra_to_bgr()
        # Turn black into white
        data = np.array(bgr_img)
        # Original value
        r1, g1, b1 = 0, 0, 0
        # Value that we want to replace it with
        r2, g2, b2 = 255, 255, 255
        red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data[:, :, :3][mask] = [r2, g2, b2]
        return data, red, green, blue

    # -----------------------------------------------------------------------

    @staticmethod
    def __data_to_img(data, red, green, blue):
        # Values that we replaced transparency with
        r2, g2, b2 = 255, 255, 255
        # Get back the alpha channel
        img = sppasImage(input_array=cv2.cvtColor(data, cv2.COLOR_RGB2RGBA))
        # Turn back white to transparency
        mask = (red == r2) & (green == g2) & (blue == b2)
        img[:, :, :4][mask] = [r2, g2, b2, 0]
        return img

    # -----------------------------------------------------------------------

    @staticmethod
    def __check_init_parameters(radius, circles_color, line_thickness, lines_color) -> None:
        """Check filters parameters and raise exception if one of them has a problem.

        :param radius: (int) The radius of the circles
        :param circles_color: (tuple[int, int, int]) The color of the circles
        :param line_thickness: (int) The thickness of the lines
        :param lines_color: (tuple[int, int, int]) The color of the lines

        :raises: sppasTypeError: If a parameter doesn't have a type expected
        :raises: sppasValueError: If a parameter value is not correct

        """
        # check colors
        if isinstance(circles_color, (tuple, list)) is False or isinstance(lines_color, (tuple, list)) is False:
            raise sppasTypeError(circles_color, "tuple")

        if len(circles_color) != 3 and len(lines_color) == 3:
            raise sppasValueError("colors", len(circles_color) + len(lines_color))

        # check integer
        if isinstance(radius, int) is False:
            raise sppasTypeError(radius, "int")

        if isinstance(line_thickness, int) is False:
            raise sppasTypeError(line_thickness, "int")

        if radius < 1:
            raise sppasValueError("radius", radius)

        if line_thickness < 1:
            raise sppasValueError("line_thickness", line_thickness)

    # -----------------------------------------------------------------------

    def __check_fct_parameters(self, hand_img: sppasImage, shape_code: str, sights: sppasSights) -> None:
        """Check filters parameters and raise exception if one of them has a problem.

        :param hand_img: (sppasImage) The hand shape image
        :param shape_code: (str) The hand shape code
        :param sights: (sppasSight) The sights of hand shape
        :raises: sppasTypeError: If a parameter doesn't have a type expected
        :raises: sppasValueError: If a parameter value is not correct

        """
        if isinstance(hand_img, sppasImage) is False:
            raise sppasTypeError(hand_img, "sppasImage")

        if isinstance(sights, sppasSights) is False:
            raise sppasTypeError(sights, "sppasSights")

        if shape_code not in self.__sights_hidden:
            raise sppasValueError("shape_code", shape_code)

    # -----------------------------------------------------------------------

    def __apply_sights(self, img: np.ndarray, shape_code: str, sights: sppasSights) -> np.ndarray:
        """Put the sights circles and the connected lines on the given image.

        :param img: (numpy.ndarray) The hand shape image
        :param shape_code: (str) The hand shape code
        :param sights: (sppasSight) The sights of hand shape
        :return: (numpy.ndarray) The image with the sights and connected lines on it

        """
        # Add a sight '-1' placed before the s0
        s0_x, s0_y, _, _ = sights.get_sight(0)
        s9_x, s9_y, _, _ = sights.get_sight(9)

        if s9_x - s0_x > 0:
            s_arm_x = s0_x - abs(s9_x - s0_x)
        else:
            s_arm_x = s0_x + abs(s9_x - s0_x)

        if s9_y - s0_y > 0:
            s_arm_y = s0_y - abs(s9_y - s0_y)
        else:
            s_arm_y = s0_y + abs(s9_y - s0_y)

        # Put the line and the circle for the new sight
        img = cv2.line(img, (s_arm_x, s_arm_y), (s0_x, s0_y), self.__lines_color, self.__line_thickness)
        img = cv2.circle(img, (s_arm_x, s_arm_y), self.__radius, self.__circles_color, -1)

        # Put the line between each sight linked
        for item in self.__sights_link:
            if item[0] not in self.__sights_hidden[shape_code] and item[1] not in self.__sights_hidden[shape_code]:
                start_x, start_y, _, _ = sights.get_sight(item[0])
                end_x, end_y, _, _ = sights.get_sight(item[1])

                img = cv2.line(img, (start_x, start_y), (end_x, end_y), self.__lines_color, self.__line_thickness)

        # Put the circle for each sight
        for i in range(len(sights)):
            if i not in self.__sights_hidden[shape_code]:
                x, y, _, _ = sights.get_sight(i)
                img = cv2.circle(img, (x, y), self.__radius, self.__circles_color, -1)

        return img
