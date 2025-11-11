"""
:filename: sppas.src.annotations.CuedSpeech.whowtag.whowimgtag.gencoords.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Generate coordinates of S0 and S9 sights of the hand.

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

import math
import logging

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel

from sppas.src.annotations.CuedSpeech.whatkey import CuedSpeechCueingRules

# ---------------------------------------------------------------------------


class sppasHandCoords:
    """Estimate the coordinates of the S0 and S9 points of the hand.

    This class estimates the coordinates of the S0 and S9 hand points,
    enabling precise placement of the hand in an image based on:

    - the (x, y) coordinates of the target position,
    - a list of tuples specifying shape code(s) and their probabilities,
    - the angle to apply to the S0–S9 axis,
    - the face size in pixels.

    Example input values when the hand shape is neutral (shape "0"):

    - target: (447, 864)
    - shapes: [('0', 1.0)]
    - vowel_angle: 45
    - face_height: 259

    Example return value:
    [(426, 682, 'target'), (346, 831, 'sights_00'), (409, 733, 'sights_09')]

    Example input values for a shape transition from neutral to shape "3":

    - target: (426, 682)
    - shapes: [('3', 0.320), ('0', 0.680)]
    - vowel_angle: 57
    - face_height: 260

    Example return value:
    [(426, 682, 'target'), (346, 831, 'sights_00'), (409, 733, 'sights_09')]

    """

    def __init__(self, cue_rules: CuedSpeechCueingRules = CuedSpeechCueingRules(), img_hand_tagger = None):
        """Create a new instance.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        # Rule-based system. Contains the list of vowel codes.
        self.__cued = None
        # Vowel code index. Loaded from the config file.
        self._vrank = ()
        # Image Hand Tagger -- allows to properly estimate the distances for a given handset
        self.__hand_tagger = None

        # Set given parameters, checking types
        self.set_hand_tagger(img_hand_tagger)
        self.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechCueingRules) -> None:
        """Set new rules.

        :param cue_rules: (CuedSpeechCueingRules) Rules and codes for vowel positions and hand shapes

        """
        if isinstance(cue_rules, CuedSpeechCueingRules) is False:
            raise sppasTypeError(str(type(cue_rules)), "CuedSpeechCueingRules")

        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = cue_rules

        # Vowel code index. Loaded from the config file.
        self._vrank = tuple(self.__cued.get_vowels_codes())

    # -----------------------------------------------------------------------

    def get_vowel_rank(self, vowel_code):
        """Return an index from the code of a vowel or -1.

        :param vowel_code: (char) One of n, b, c, s, m, t for French.

        """
        if vowel_code in self._vrank:
            return self._vrank.index(vowel_code)

        return -1

    # -----------------------------------------------------------------------

    def set_hand_tagger(self, hand_tagger) -> None:
        """Set the hand tagger or None.

        :param hand_tagger: (sppasImageHandTagger) Allows to get hand sights of the choose handset

        """
        if hand_tagger is None:
            self.__hand_tagger = None
        else:
            if hasattr(hand_tagger, "slap_on") is True:
                self.__hand_tagger = hand_tagger
            else:
                raise sppasTypeError(str(type(hand_tagger)), "sppasImageHandTagger")

    # -----------------------------------------------------------------------
    # Workers
    # -----------------------------------------------------------------------

    def eval_hand_points(self, target, shapes, vowel_angle, face_height):
        """A solution to return hand coords from target, angle and face height.

        It allows to fix where to place the hand, i.e., S0 and S9 coordinates,
        in an image based on:

        :param target: (tuple) x,y coordinates of the targeted position
        :param shapes: (list) List of tuples describing the shape and its probability
        :param vowel_angle: (float) Angle to be applied to S0-S9 axes
        :param face_height: (int) Size of the face, in pixels
        :return: (list) [target, S0, S9] with coordinates of hand points

        The returned list contains sppasLabel() instances with:

        - sppasFuzzyPoint() to store the coordinates of hand points
        - label key to indicate its definition ('target' or 'sights_00' or 'sights_09')

        """
        names = ['sights_00', 'sights_09']
        hand_pts = [self.__create_label(target[0], target[1], "target")]

        try:
            if len(shapes) == 1:
                _pts = self.target_to_hand_sights(shapes[0][0], target, vowel_angle, face_height)
                if None not in _pts:
                    hand_pts.append(self.__create_label(_pts[0][0], _pts[0][1], names[0]))
                    hand_pts.append(self.__create_label(_pts[1][0], _pts[1][1], names[1]))

            else:
                _pts1 = self.target_to_hand_sights(shapes[0][0], target, vowel_angle, face_height)
                _pts2 = self.target_to_hand_sights(shapes[1][0], target, vowel_angle, face_height)
                if None not in _pts1 and None not in _pts2:
                    for i, pt1 in enumerate(_pts1):
                        # Use the probability of the shapes to fix the points
                        pt2 = _pts2[i]
                        proba1 = shapes[0][1]
                        proba2 = shapes[1][1]
                        # Estimate the center between the 2 positions because the hand can't
                        # be at two different places at the same time
                        p_x = int((proba1 * pt1[0]) + (proba2 * pt2[0]))
                        p_y = int((proba1 * pt1[1]) + (proba2 * pt2[1]))
                        hand_pts.append(self.__create_label(p_x, p_y, names[i]))

            return hand_pts
        except:
            import traceback
            print(traceback.format_exc())
            return list()

    # -----------------------------------------------------------------------

    def angle_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Return the angle of the given sight compared to S0-S9 axis.

        :param shape_code: (str) Hand shape vowel code
        :param sight_index: (int) The index of the sight
        :return: (int) the computed angle
        :raises: IntervalRangeException: If the index is negative or out of bounds

        """
        # No hand tagger defined. Use default values.
        if self.__hand_tagger is None:
            if shape_code == "0":
                return 30
            else:
                return 0
        else:
            # A hand tagger is defined. Use its real values.
            return self.__hand_tagger.angle_to_s0(shape_code, sight_index)

    # -----------------------------------------------------------------------

    def distance_to_s0(self, shape_code: str, sight_index: int = 0) -> int:
        """Get the distance between s0 and a sight of the hand.

        :param shape_code: (str) Shape code name
        :param sight_index: (int) The index of the sight
        :raises: IntervalRangeException: If the index is negative or out of bounds
        :return: (int) the computed distance

        """
        if self.__hand_tagger is None:
            # A default hand model
            if sight_index == 9:
                return 71
            elif sight_index == 12:
                return 172
            elif sight_index == 5:
                return 73
            elif sight_index == 8:
                return 165
            else:
                return 0

        return self.__hand_tagger.distance_to_s0(shape_code, sight_index)

    # -----------------------------------------------------------------------

    def target_to_hand_sights(self, shape_code, target, angle, face_height):
        """Estimate coordinates of S0 and S9 sights of the hand.

        The given angle is the one between the target and the S0 sight
        relatively to the vertical axis.

        :param shape_code: (char) Consonant shape name. If unknown, '0' is used instead.
        :param target: (tuple(x,y))
        :param angle: (int) Value between -360 and 360 in the unit circle
        :param face_height: (int) Height of the face
        :return: tuple(x0, y0), tuple(x9, y9) or (None, None) if error in distance estimation

        Target(x,y)
        *-------------------A'(x0,y)
        |  \\ alpha          |
        |      \\            |
        |         \\         |
        |            \\sigma |
        |               \\   |
       A(x,y0)-----------S(x0,y0)

        alpha = angle - 90
        hypotenuse = [TS] ; adjacent = [AS] ; opposite = [AT]

        sinus(any_angle) = opposite / hypotenuse
        sinus(ATS) = AS / TS    = >  AS = sin(sigma) * TS    = >  y0 = y + sin(sigma) * hypotenuse
        sinus(AST) = AT / TS    = >  AT = sin(alpha) * TS    = >  x0 = x + sin(alpha) * hypotenuse

        """
        # Estimate a ratio between the observed S0-S9 and the expected one.
        # Use |S0,S9| as reference distance to estimate the ratio,
        # because these sights are always visible, whatever the shape.
        ref_dist = self.distance_to_s0(shape_code, 9)
        if int(round(ref_dist, 0)) == 0:
            logging.error("Distance between S0 and S9 is 0. "
                          "It probably means there's a problem in hand sights.")
            return None, None
        ratio = (face_height * 0.45) / ref_dist

        # Estimate (x,y) coords of S0, regarding the target
        # ----------------------------------------------------
        # Get the expected distance between S0 and the target and the
        # adjusted alpha regarding the given hand
        alpha = angle - 90

        target_index = self.__cued.get_shape_target(shape_code)
        alpha = alpha - self.angle_to_s0(shape_code, target_index)
        dist = self.distance_to_s0(shape_code, target_index)

        hypotenuse = dist * ratio
        sigma = 90 - alpha

        # Eval S0 coords
        x_s0 = target[0] + int(self.sinus(alpha) * hypotenuse)
        y_s0 = target[1] + int(self.sinus(sigma) * hypotenuse)

        # Estimate (x,y) coords of S9, regarding S0
        # --------------------------------------------
        # Get the expected distance(S0, S9), ie the hypotenuse
        hypotenuse = ref_dist * ratio
        # Define the angles
        alpha = angle - 90
        sigma = 90 - alpha
        # Eval S9 coords
        x_s9 = x_s0 - int(self.sinus(alpha) * hypotenuse)
        y_s9 = y_s0 - int(self.sinus(sigma) * hypotenuse)

        return (x_s0, y_s0), (x_s9, y_s9)

    # -----------------------------------------------------------------------

    @staticmethod
    def sinus(degree):
        """Return sinus value of the given degree.

        To find the sine of degrees, it must first be converted into radians
        with the math.radians() method.

        :param degree: (int, float) A degree value
        :return: Sine value in degrees.

        """
        degree = float(degree) % 360.
        return math.sin(math.radians(degree))

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __create_label(self, x, y, s):
        tag = sppasTag((x, y), tag_type="point")
        label = sppasLabel(tag)
        label.set_key(s)
        return label
