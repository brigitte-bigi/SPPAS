# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whowtag.gencoordstier.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Generate coordinates of S0 and S9 sights from tiers.

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

from sppas.src.anndata import sppasTier

from ..whatkey import CuedSpeechCueingRules

from .whowimgtag import sppasHandCoords

# ---------------------------------------------------------------------------

MSG_ERROR_MISMATCH = "The given {:d} coordinates in CSV/XRA file doesn't " \
                     "match the number of frames of the video {:d}"

# ---------------------------------------------------------------------------


class sppasHandCoordsGenerator(object):
    """Create a tier indicating the position of 3 points of the hand.

    - point 1: target position
    - point 2: S0
    - point 3: S9

    For each given tier intervals, it estimates the coordinates of the S0
    and S9 points, enabling precise placement of the hand based on:

    - the coordinates of the target position,
    - the shape code(s) and their probabilities,
    - the angle to apply to the S0–S9 axis,
    - the face size in pixels.

    """

    def __init__(self, cue_rules: CuedSpeechCueingRules = CuedSpeechCueingRules()):
        """Create a new instance.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        self.__hand_coords = sppasHandCoords(cue_rules)

    # -----------------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechCueingRules) -> None:
        """Set new rules.

        :param cue_rules: (CuedSpeechCueingRules) Rules and codes for vowel positions and hand shapes

        """
        # Rule-based system to convert a sequence of phonemes into keys
        self.__hand_coords.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------
    # Worker
    # -----------------------------------------------------------------------

    def hands_to_handcoords(self, hand_shape, hand_target, wrist_angles, face_heights, img_hand_tagger=None):
        """Generate the coords of points of the hand.

        :param hand_shape: (sppasTier) Tier with hand shape transitions probabilities
        :param hand_target: (sppasTier) Tier with hand target coordinates
        :param wrist_angles: (sppasTier) Tier with angle value
        :param face_heights: (sppasTier) Tier with height of the face
        :param img_hand_tagger: (sppasImageHandTagger) Allows to get hand sights of the choose handset
        :return: (sppasTier) CS-HandCoords

        """
        if len(hand_target) != len(hand_shape):
            raise Exception("Hand targets != Hand shapes: {:d} != {:d}"
                            "".format(len(hand_target), len(hand_shape)))
        self.__hand_coords.set_hand_tagger(img_hand_tagger)

        # Estimate sights S0 and S9
        hand_coords_tier = sppasTier("CS-HandCoords")
        for i, ann in enumerate(hand_target):
            loc = ann.get_location()  # a point
            labels = ann.get_labels()
            # A target coord is expected
            if len(labels) > 0:
                target_point = labels[0].get_best().get_typed_content().get_midpoint()

                # One or two shapes
                shapes = list()
                for shape_label in hand_shape[i].get_labels():
                    for tag, score in shape_label:
                        shp = tag.get_typed_content()
                        if score is None:
                            score = 1. / len(shape_label)
                        shapes.append((shp, score))

                # Estimator
                angle = wrist_angles[i].get_labels()[0].get_best().get_typed_content()
                face_height = face_heights[i].get_labels()[0].get_best().get_typed_content()

                # Get 3 hand coords from target, angle and face height: target, S0, S9.
                # Example: [(426, 682, 'target'), (346, 831, 'sights_00'), (409, 733, 'sights_09')]
                # stored in a list of sppasLabel(sppasFuzzyPoint()) to represent the coordinates.
                point_labels = self.__hand_coords.eval_hand_points(target_point, shapes, angle, face_height)
                hand_coords_tier.create_annotation(loc.copy(), point_labels)

            else:
                hand_coords_tier.create_annotation(loc.copy(), [])

        return hand_coords_tier
