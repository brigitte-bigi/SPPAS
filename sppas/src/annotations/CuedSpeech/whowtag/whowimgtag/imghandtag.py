# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.videotagger.sppas_image_hand_tagger.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Tag an image with the hand.

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
import math
import numpy
import cv2

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasKeyError
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import sppasCoords

from sppas.src.annotations.CuedSpeech.whatkey.phonestokeys import CuedSpeechKeys
from sppas.src.annotations.CuedSpeech.whowtag.handproperties import sppasHandProperties
from sppas.src.annotations.CuedSpeech.whowtag.handsset import sppasHandsSet

# -----------------------------------------------------------------------


class sppasImageHandTagger:
    """Overlay the picture of a hand or a badge on an image.

    This class loads a hand set

    """

    def __init__(self, cue_rules: CuedSpeechKeys = CuedSpeechKeys()):
        """The constructor of the SppasImageHandTagger class.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes
                          Optional parameter, new instance of CuedSpeechKeys class by default
        :raises: sppasTypeError: If the parameter are not an instance of CuedSpeechKeys class

        """
        if not isinstance(cue_rules, CuedSpeechKeys):
            raise sppasTypeError(cue_rules, "CuedSpeechKeys")

        self.__cued = cue_rules

        # Vowel code index. Loaded from the config file.
        self._vrank = tuple(self.__cued.get_vowels_codes())

        # Options
        self.__badge_color = (64, 64, 64)

        # Pictures of the hands and their properties -- need to be loaded
        self.__hands = sppasHandsSet(cue_rules)
        self.__hand_mode = False

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechKeys):
        """Set the CuedSpeechKeys used to tag the video.

        :param cue_rules: (CuedSpeechKeys) The instance of the cuedSpeechKeys to set

        """
        self.__cued = cue_rules
        self._vrank = tuple(self.__cued.get_vowels_codes())
        self.__hands.set_cue_rules(self.__cued)

    # -----------------------------------------------------------------------

    def apply_hands_filter(self, filter_name: str):
        """Apply a filter on all hands images loaded.

        :param filter_name: (str) The name of the filter to apply
        :raises: sppasError: If no hands are loaded
        :raises: sppasValueError: If the given name of the filter is unknown

        """
        self.__hands.apply_hands_filter(filter_name)

    # -----------------------------------------------------------------------

    def get_vowel_rank(self, vowel_code: str) -> int:
        """Get the index from the code of a vowel passed as parameter.

        :param vowel_code: (str) The character code of the vowel
                           One of these characters (for French language) : n, b, c, s, m, t
        :return: (int) The index of the vowel or -1 if the vowel doesn't exist

        """
        if vowel_code in self._vrank:
            return self._vrank.index(vowel_code)

        return -1

    # -----------------------------------------------------------------------

    def load_hands(self, prefix: str) -> bool:
        """Load the hands sets (hands image and sights annotations).

        The hand mode is automatically enabled if all hand pictures and sights
        are properly loaded.

        :param prefix: (str) Prefix in hand image filenames
        :raises: sppasIOError: If a hands set found has a missing file (image or annotation)
        :raises: sppasIOError: Or if a file to read is not found
        :return: (bool) True if the hands set has correctly loaded or False else

        """
        hands_loaded_count = self.__hands.load(prefix)

        self.__hand_mode = hands_loaded_count > 0
        return self.__hand_mode

    # -----------------------------------------------------------------------

    def hand_mode(self) -> bool:
        """Return True if the hand mode is enabled: a handset is defined."""
        return self.__hand_mode

    # -----------------------------------------------------------------------

    def enable_hand_mode(self, value: bool = True) -> None:
        """Allows to add the pictures of a hand.

        :param value: (bool) True to add a hand, False to draw a badge
        :raises: sppasError: If we activate the hand mode, but we don't have hands loaded

        """
        if value is True and len(self.__hands) == 0:
            raise sppasError("Hand mode can't be enable: no hand pictures loaded.")

        self.__hand_mode = value

    # -----------------------------------------------------------------------

    def angle_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Return the angle of the given sight compared to S0-S9 axis.

        :param shape_code: (str) Hand shape vowel code
        :param sight_index: (int) The index of the sight
        :return: (int) the computed angle
        :raises: IntervalRangeException: If the index is negative or out of bounds

        """
        return self.__hands.angle_to_s0(shape_code, sight_index)

    # -----------------------------------------------------------------------

    def distance_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Get the distance between s0 and a sight of the hand.

        :param shape_code: (str) Shape code name
        :param sight_index: (int) The index of the sight
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (int) the computed distance

        """
        return self.__hands.distance_to_s0(shape_code, sight_index)

    # -----------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------

    def slap_on(self, image: numpy.ndarray, shapes: tuple, hand_sights: list | None) -> sppasImage:
        """Overlay a hand to the given image.

        hand_sights is the list of S0, S9 and target finger coordinates
        where the hand sights have to be put on the image.
        For example:
        [sppasFuzzyPoint: (368,780), sppasFuzzyPoint: (432,684), sppasFuzzyPoint: (540,573)],

        :param image: (sppasImage or numpy.ndarray) The image that we want tag the hand on it
        :param shapes: (list[str, float]) One or two consonant names and their probabilities
        :param hand_sights: (list|None) The s0, s9 and target coords. Used to compute the scale factor
        :return: (sppasImage) The image with the hand applied on it
        :raises: sppasTypeError: If the parameters have the wrong type

        """
        # Set the image to be tagged
        img = self.__check_image(image)
        # Nothing to do
        if len(shapes) == 0:
            return img
        # No S0, S9 coords to scale the hand
        if hand_sights is None:
            hand_sights = list()

        for i in reversed(range(len(shapes))):
            shape_code, shape_proba = shapes[i]
            if self.__hand_mode is True:
                # Make use of S0 coordinates
                x, y, _ = self.get_coordinates(hand_sights, "sights_00")
                scale_factor = self.__eval_hand_scale(shape_code, hand_sights)
                angle = self.__eval_hand_rotate_angle(shape_code, hand_sights)
                img = self.__tag_image_with_hand(img, shape_code, shape_proba, x, y, angle, scale_factor)

            else:
                # Make use of target coordinates
                x, y, r = self.get_coordinates(hand_sights, "target")
                img = self.__tag_image_with_badge(img, shape_code, shape_proba, x, y, r)

        return img

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    @staticmethod
    def get_coordinates(sights: list, label_key: str) -> tuple | None:
        """Return the coordinates of the given sights for the given label.

        :param sights: (list) List of sppasLabel() with sppasFuzzyPoint representing hand sights
        :param label_key: (str) The key of the label to search for coordinates
        :return: (tuple|None) The (x,y,radius) coordinates of the given sights

        """
        for sight_label in sights:
            if sight_label.get_key() == label_key:
                tag = sight_label.get_best()
                point = tag.get_typed_content()
                x, y = point.get_midpoint()
                return x, y, point.get_radius()
        return None

    # -----------------------------------------------------------------------

    def __eval_hand_scale(self, shape_code: str, sights: list) -> float:
        """Estimate the scale factor for the image of the hand.

        :param shape_code: (str) The code of the hand shape
        :param sights: (list[sppasFuzzyPoint]) The sights to compute the scale factor
        :return: (float) The scale factor computed

        """
        default_value = 0.4

        # Get the actual distance of the hand image
        hand_distance = self.__hands.distance(shape_code)
        if hand_distance == 0:
            return default_value

        # Compute the distance of the hand from the sights in the sppasLabel() list
        s0_x, s0_y, _ = self.get_coordinates(sights, "sights_00")
        s9_x, s9_y, _ = self.get_coordinates(sights, "sights_09")
        dist_x = abs(s9_x - s0_x)
        dist_y = abs(s9_y - s0_y)
        real_distance = sppasHandProperties.pythagoras(dist_x, dist_y)

        # Return the scale factor
        return real_distance / float(hand_distance)

    # -----------------------------------------------------------------------

    def __eval_hand_rotate_angle(self, shape_code: str, sights: list) -> int:
        """Estimate the rotate angle to the hand corresponds with the sights generated.

        :param shape_code: (str) The hand shape code
        :param sights: (list[sppasFuzzyPoint]) A list that contains the s0, s5, s8, s9 and s12
        :return: (int) The hand rotate angle in degree

        """
        s0_x, s0_y, _ = self.get_coordinates(sights, "sights_00")
        s9_x, s9_y, _ = self.get_coordinates(sights, "sights_09")

        # compute the triangle angle
        opposite = abs(s9_y - s0_y)
        hypotenuse = sppasHandProperties.pythagoras(abs(s9_x - s0_x), abs(s9_y - s0_y))
        if 0. <= opposite*hypotenuse <= 1.:
            return 0

        angle = math.degrees(math.asin(float(opposite) / float(hypotenuse)))

        # find the rotate hand angle
        # case left side triangle
        if s9_x - s0_x > 0:
            # case top-left triangle
            if s9_y - s0_y > 0:
                angle = -angle

            # else case bottom-left triangle, the angle is already correct

        # case right side triangle
        else:
            # case top-right triangle
            if s9_y - s0_y > 0:
                angle += 180
            # case bottom-right triangle
            else:
                angle = 180 - angle

        # /!\ IMPORTANT /!\
        # Reverse the angle value because the y-axis is inverted (top to bottom)
        angle = -angle

        # Get index of the target from its shape code
        target = self.__cued.get_shape_target(shape_code)

        # addition the default hand angle in the image
        angle += self.__hands.angle(shape_code)
        angle -= self.__hands.angle_to_s0(shape_code, target)

        return int(round(angle, 0))

    # -----------------------------------------------------------------------

    def __tag_image_with_hand(self, img: sppasImage,
                              shape_code: str, shape_proba: float,
                              x: int, y: int, angle: int,
                              scale_factor: float = 0.20) -> sppasImage:
        """Add a cued speech hand shape on an image.

        The hand with the passed parameters is automatically resized, rotated and cropped.

        :param img: (sppasImage) The image that we want to put the hand on it
        :param shape_code: (str) The code of the hand shape
        :param shape_proba: (float) The probability of the shape to define the transparency
        :param x: (int) The X coordinate of the S0, where to place the hand
        :param y: (int) The Y coordinate of S0, where to place the hand
        :param angle: (int) The degree angle to rotate the hand
        :param scale_factor: (float) Optional parameter, 0.20 by default
                                    The scale factor of the hand to be proportional with the face (image)
        :return: (sppasImage) The image with the hand applied on it

        """
        # Get the image matching the hand shape
        hand_img = self.__hands.image(shape_code)
        if hand_img is None:
            raise sppasKeyError(self.__cued.get_consonants_codes(), shape_code)

        # Get image size and target point coordinates
        original_hand_width, original_hand_height = hand_img.size()
        s0_x, s0_y = self.__hands.get_sight(shape_code, 0)

        # Resize image and redefine target_point coordinates
        hand_img = hand_img.iresize(int(float(original_hand_width) * scale_factor),
                                    int(float(original_hand_height) * scale_factor))
        s0_x = int(float(s0_x) * scale_factor)
        s0_y = int(float(s0_y) * scale_factor)
        resize_hand_width, resize_hand_height = hand_img.size()

        # The transparency of the hand is proportional to the proba of the shape
        shape_proba = min(shape_proba * 1.25, 1)
        if shape_proba < 1:
            hand_img = hand_img.ialpha(int(shape_proba * 255.), direction=-1)

        # Enlarge the image to ensure that the hand won't be cropped
        # at the time of rotating it
        hand_img = hand_img.icenter(width=img.width, height=img.height)
        s0_x = s0_x + ((img.width - resize_hand_width) // 2)
        s0_y = s0_y + ((img.height - resize_hand_height) // 2)

        # Rotate of a given angle.
        # By default, the rotation center is the center of the image.
        # In our case, the rotation center is the target finger in order that
        # its coordinates don't change.
        hand_img = hand_img.irotate(angle, center=(s0_x, s0_y), redimension=False)

        # Shift coords to match the target point with the one in our hand picture
        top_left_corner_x = x - s0_x
        top_left_corner_y = y - s0_y
        crop_x = 0
        crop_y = 0

        if top_left_corner_x < 0:
            crop_x = -top_left_corner_x
            top_left_corner_x = 0

        if top_left_corner_y < 0:
            crop_y = -top_left_corner_y
            top_left_corner_y = 0

        if crop_x > 0 or crop_y > 0:
            hand_img = hand_img.icrop(sppasCoords(crop_x, crop_y,
                                                  max(0, hand_img.width - crop_x), max(0, hand_img.height - crop_y)))

        # The image of the hand is ready. Overlays on the back image.
        img = img.ioverlay(hand_img, sppasCoords(top_left_corner_x, top_left_corner_y))

        return img

    # -----------------------------------------------------------------------

    def __tag_image_with_badge(self, img: sppasImage,
                               code: str, shape_proba: float,
                               x: int, y: int, radius: int) -> sppasImage:
        """Tag the image with a circle and a text inside.

        :param img: (sppasImage) The image that we want to put the circle and text inside on it
        :param code: (str) The code of the hand shape
        :param shape_proba: (float) The probability of the hand shape to define the transparency
        :param x: (int) The X coordinate (abscissa) where we want to add the hand
        :param y: (int) The Y coordinate (ordinate) where we want to add the hand
        :param radius: (int) The radius of the circle
        :return: (sppasImage) The image with the circle and text inside applied on it

        """
        if radius is None:
            radius = 20

        # a circle filled in gray and surrounded by a white line
        cv2.circle(img, (x, y), radius - 2, self.__badge_color, -1)
        cv2.circle(img, (x, y), radius, (5, 5, 5), 3)

        if shape_proba < 1.:
            # define the color of the text and put it in the middle of the circle
            b = int(250. * shape_proba)
            img.put_text((x - (radius // 2), y + (radius // 2)), (b, b, b), 1, code)
        else:
            img.put_text((x - (radius // 2), y + (radius // 2)), (250, 250, 250), 2, code)

        return img

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
