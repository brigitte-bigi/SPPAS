"""
:filename: sppas.src.annotations.CuedSpeech.wherecue.targetprobas.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Remaining PoC code. To be cleaned up!

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

    ---------------------------------------------------------------------

"""

import logging

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from ..whatkey import CuedSpeechCueingRules

# ---------------------------------------------------------------------------


class TargetProbabilitiesEstimator:
    """Generate the probabilities of the targets (pos&shape).

    For each image of the video (each interval in vowels_coords tier), an
    interval with the probability of the shape, and another one with the
    probability of the position are estimated.

    """

    def __init__(self, cue_rules: CuedSpeechCueingRules = CuedSpeechCueingRules()):
        """Create a new instance.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        # Rule-based system. Contains the list of vowel codes.
        self.__cued = None
        # Vowel code index. Loaded from the config file.
        self._vrank = ()

        self.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------

    def get_vowel_rank(self, vowel_code):
        """Return an index from the code of a vowel or -1.

        :param vowel_code: (char) One of n, b, c, s, m, t for French.

        """
        if vowel_code in self._vrank:
            return self._vrank.index(vowel_code)

        return -1

    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechCueingRules) -> None:
        """Set new rules.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes
        :raises: sppasTypeError: given parameter is not CuedSpeechCueingRules

        """
        if isinstance(cue_rules, CuedSpeechCueingRules) is False:
            raise sppasTypeError("cue_rules", "CuedSpeechCueingRules")

        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = cue_rules

        # Vowel code index. Loaded from the config file.
        self._vrank = tuple(self.__cued.get_vowels_codes())

    # -----------------------------------------------------------------------

    def positions_discretization(self, tier_pos_coords, tier_pos_transitions):
        """Generate the probabilities of the positions for each annotation in tier_pos_coords.

        Discretizing the transitions between a position to the next 
        one implies to assign a probability to the source and to the 
        destination during the whole transition time.
        
        :param tier_pos_coords: (sppasTier) Tier with coordinates of the vowel positions and neutral
        :param tier_pos_transitions: (sppasTier) Tier with transition intervals between vowels
        :return: (sppasTier) Tier "CS-PosProbas" with probabilities for each position 
        
        """
        pos_tier = sppasTier("CS-PosProbas")

        # Discretize positions and estimate their probabilities during transitions
        pos_probas = self.__discretize_positions(tier_pos_transitions, tier_pos_coords)
        if len(pos_probas) != len(tier_pos_coords):
            raise Exception("Target vowels probas estimation: {:d} != {:d}"
                            "".format(len(pos_probas), len(tier_pos_coords)))

        # Create a tier from the list
        for i, ann in enumerate(tier_pos_coords):
            loc = ann.get_location()
            tags, scores = self.__probas_to_lists(pos_probas[i])
            # Create the label by taking into account the fact that 2 tags can
            # have the same content (transition from a position to the same one).
            label = sppasLabel(None)
            for t in range(len(tags)):
                label.append(tags[t], score=scores[t], add=False)
            pos_tier.create_annotation(loc.copy(), [label])

        return pos_tier

    # -----------------------------------------------------------------------

    def shapes_discretization(self, tier_pos_coords, tier_shapes_transitions):
        """Generate the probabilities of the shapes for each annotation in tier_pos_coords.

        Discretizing the transitions between a shape to the next 
        one implies to assign a probability to the source and to the 
        destination during the whole transition time.

        :param tier_pos_coords: (sppasTier) Tier with coordinates of the vowel positions and neutral
        :param tier_shapes_transitions: (sppasTier) Tier with transition intervals between shapes
        :return: (sppasTier) Tier "CS-ShapeProbas" with probabilities for each shape 

        """
        shape_tier = sppasTier("CS-ShapeProbas")

        # Discretize shapes and estimate their probabilities during transitions
        shape_probas = self.__discretize_shapes(tier_shapes_transitions, tier_pos_coords)
        if len(shape_probas) != len(tier_pos_coords):
            raise Exception("Target consonants probas estimation: {:d} != {:d}"
                            "".format(len(shape_probas), len(tier_pos_coords)))

        # Create a tier from the list
        for i, ann in enumerate(tier_pos_coords):
            loc = ann.get_location()

            tags, scores = self.__probas_to_lists(shape_probas[i])
            label = sppasLabel(None)
            for t in range(len(tags)):
                label.append(tags[t], score=scores[t], add=False)
            shape_tier.create_annotation(loc.copy(), [label])

        return shape_tier

    # -----------------------------------------------------------------------

    def hands_to_target_coords(self, hand_pos_probas, vowels_coords):
        """Generate the coordinates of the target finger.

        :param hand_pos_probas: (sppasTier) Tier with hand position probabilities
        :param vowels_coords: (sppasTier) Tier with coordinates of the vowels and neutral
        :return: (sppasTier) CS-TargetCoords

        """
        # Estimate the coordinates of the hand
        position_coords = self.__eval_hand_target_coords_straight(hand_pos_probas, vowels_coords)
        if len(position_coords) != len(vowels_coords):
            raise Exception("Target vowels coords estimation: {:d} != {:d}"
                            "".format(len(position_coords), len(vowels_coords)))

        # Turn position coordinates into a sppasTier with sppasFuzzyPoint()
        pos_tier = sppasTier("CS-TargetCoords")
        for i, ann in enumerate(vowels_coords):
            loc = ann.get_location()

            if len(position_coords[i]) == 1:
                # position_coords[i][0] is a tuple (point, proba)
                x, y, r = position_coords[i][0][0]
                label_pos = sppasLabel(sppasTag((x, y, r), tag_type="point"))

            elif len(position_coords[i]) == 2:
                pos1 = position_coords[i][0]
                (x1, y1, r1) = pos1[0]
                tag1 = sppasTag((x1, y1, r1), tag_type="point")
                pos2 = position_coords[i][1]
                (x2, y2, r2) = pos2[0]
                tag2 = sppasTag((x2, y2, r2), tag_type="point")
                label_pos = sppasLabel([tag1, tag2], [pos1[1], pos2[1]])

            else:
                label_pos = sppasLabel(None)

            pos_tier.create_annotation(loc.copy(), [label_pos])

        return pos_tier

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __discretize_positions(self, hand_pos, vowels_coords_tier):
        """Return proba of the hand position for each ann in given tier.

        :return: (sppasTier)

        """
        positions = list()
        cur_pos = [self.__cued.get_neutral_vowel()]
        i = 0
        while i < len(vowels_coords_tier):
            loc = vowels_coords_tier[i].get_location().get_best()

            # Get/Set the position at the current moment
            new_content = self.__get_label_contents_at(hand_pos, loc)
            if new_content is None:
                # This is not a transition period but a target one.
                if len(cur_pos) == 2:
                    # This is the first occurrence after a transition period
                    cur_pos.pop(0)
            else:
                cur_pos = new_content

            c1 = cur_pos[0]
            if len(cur_pos) == 1:
                # The hand is at a target position c1.
                positions.append(((c1, 1.), ))
                i += 1

            else:
                # Transition period from c1 to c2
                c2 = cur_pos[1]

                # To where the hand is going?
                new_pos = cur_pos
                nb_img = 0
                while new_pos == cur_pos:
                    if (i + nb_img) == len(vowels_coords_tier):
                        break
                    nb_img += 1
                    if (i + nb_img) == len(vowels_coords_tier):
                        break
                    loc = vowels_coords_tier[i + nb_img].get_location().get_best()
                    new_pos = self.__get_label_contents_at(hand_pos, loc)

                # there are nb images to change the position from cur_pos[0]
                # to the one of cur_pos[1].
                if nb_img == 1:
                    p2 = 0.65
                elif nb_img == 2:
                    p2 = 0.40
                else:
                    # The first step proba is higher than the other ones
                    p_step_straight = 1. / float(nb_img)
                    p2 = max(0.1, p_step_straight)
                positions.append(((c1, 1. - p2), (c2, p2)))
                i += 1
                proba_step = (1. - p2) / float(nb_img+1)
                for j in range(1, nb_img):
                    proba_pos2 = p2 + round((j+1) * proba_step, 2)
                    positions.append(((c1, 1 - proba_pos2), (c2, proba_pos2)))
                    i += 1

        return positions

    # -----------------------------------------------------------------------

    def __discretize_shapes(self, hand_shapes, vowels_coords_tier):
        """Return proba of the hand shape for each ann in given tier.

        :return: (sppasTier)

        """
        shapes = list()
        cur_shape = [self.__cued.get_neutral_consonant()]
        i = 0
        while i < len(vowels_coords_tier):
            loc = vowels_coords_tier[i].get_location().get_best()

            # Get/Set the shape at the current moment
            new_content = self.__get_label_contents_at(hand_shapes, loc)
            if new_content is None:
                # This is not a transition period but a target one.
                if len(cur_shape) == 2:
                    cur_shape.pop(0)
            else:
                cur_shape = new_content

            c1 = cur_shape[0]
            if len(cur_shape) == 1:
                # The hand is at a target shape c1.
                shapes.append(((c1, 1.), ))
                i += 1

            else:
                # Transition period from c1 to c2
                c2 = cur_shape[1]

                # To where the fingers are changing?
                new_shape = cur_shape
                nb_img = 0
                while new_shape == cur_shape:
                    if (i + nb_img) == len(vowels_coords_tier):
                        break
                    nb_img += 1
                    if (i + nb_img) == len(vowels_coords_tier):
                        break
                    loc = vowels_coords_tier[i + nb_img].get_location().get_best()
                    new_shape = self.__get_label_contents_at(hand_shapes, loc)

                # there are nb images to change the shape from cur_shape[0]
                # to the one of cur_shape[1]
                if nb_img == 1:
                    shapes.append(((c1, 0.25), (c2, 0.75)))
                    i += 1

                elif nb_img == 2:
                    shapes.append(((c1, 0.45), (c2, 0.55)))
                    shapes.append(((c1, 0.15), (c2, 0.85)))
                    i += 2

                elif nb_img == 3:
                    shapes.append(((c1, 0.6), (c2, 0.4)))
                    shapes.append(((c1, 0.25), (c2, 0.75)))
                    shapes.append(((c1, 0.1), (c2, 0.9)))
                    i += 3

                else:
                    # The first step proba is higher than the other ones
                    p = 0.35
                    shapes.append(((c1, 1. - p), (c2, p)))
                    i += 1

                    # use nb_img instead of nb_img+1 because of the last two steps
                    proba_step = (1. - p) / float(nb_img)
                    for j in range(1, nb_img - 2):
                        proba_shape1 = p + round((j+1) * proba_step, 2)
                        proba_shape0 = 1. - proba_shape1
                        shapes.append(((c1, proba_shape0), (c2, proba_shape1)))
                        i += 1

                    # but the last 2 steps are lower than the other ones
                    proba_shape1 = 1. - (proba_step / 2.)
                    proba_shape0 = 1. - proba_shape1
                    shapes.append(((c1, proba_shape0), (c2, proba_shape1)))
                    i += 1

                    proba_shape1 = 1. - (proba_step / 4.)
                    proba_shape0 = 1. - proba_shape1
                    shapes.append(((c1, proba_shape0), (c2, proba_shape1)))
                    i += 1

        return shapes

    # -----------------------------------------------------------------------

    def __eval_hand_target_coords_straight(self, hand_pos_probas, vowels_coords_tier):
        """Return coords of the hand position for each ann in given tier.

        Coordinates are following a straight line to go from a position to
        the next one. It is ignoring the fact that keys have a different
        target finger: it is a straight line from a target position to the
        next one.

        :return: (list)

        """
        pos_coords = list()

        for i in range(len(hand_pos_probas)):
            # The coordinates (x, y) and radius of all the vowels on the face
            labels = vowels_coords_tier[i].get_labels()
            vowels_coords = [label.get_best().get_typed_content() for label in labels]

            # The current position(s) of the hand
            #  - 1 if the key is reached => proba=1
            #  - 2 if moving => the best proba the closest to the corresponding vowel
            cur_vowels = list()
            cur_probas = list()
            for label in hand_pos_probas[i].get_labels():
                for tag, score in label:
                    cur_vowels.append(tag.get_content())
                    cur_probas.append(score)

            # The (x, y) and r of the first current vowel
            from_vowel_idx = self._vrank.index(cur_vowels[0])
            coord1 = vowels_coords[from_vowel_idx]
            x1, y1 = coord1.get_midpoint()
            r1 = coord1.get_radius()

            if len(cur_vowels) == 1:
                # The hand is at a target position.
                # There's no "trajectory model" yet, so the center of the coords
                # stored in "all_vowels" is used.
                pos_coords.append([((x1, y1, r1), 1.)])

            elif len(cur_vowels) == 2:
                # The hand is moving, the position is changing.
                try:
                    to_vowel_idx = self._vrank.index(cur_vowels[1])
                except ValueError:
                    logging.error("Unknown vowel: {}".format(cur_vowels[1]))
                    continue
                coord2 = vowels_coords[to_vowel_idx]
                x2, y2 = coord2.get_midpoint()
                r2 = coord2.get_radius()

                if from_vowel_idx == to_vowel_idx and r2 is not None:
                    # The current position is also the next one. so x1=x2 / y1=y2
                    if cur_probas[0] > cur_probas[1]:
                        x2 = x2 - r2
                        y2 = y2 + r2
                    else:
                        x1 = x1 - r2
                        y1 = y1 + r2

                # Estimate the new coord by using the probability
                dx = x2 - x1
                dy = y2 - y1
                x = x1 + int(float(dx) * cur_probas[1])
                y = y1 + int(float(dy) * cur_probas[1])
                r = 1
                if r1 is not None and r2 is not None:
                    dr = r2 - r1
                    r = r1 + int(float(dr) * cur_probas[1])
                pos_coords.append([((x, y, r), 1.)])

            else:
                pos_coords.append([])
                logging.error("No vowel at index {:d}".format(i))

        return pos_coords

    # -----------------------------------------------------------------------

    def __eval_hand_target_coords_fixed(self, hand_pos_probas, vowels_coords_tier):
        """Return coords of the hand position for each ann in given tier.

        The hand does not move from a position to the next one.
        Its position is the one of the vowel.

        :return: (list)

        """
        pos_coords = list()

        for i in range(len(hand_pos_probas)):
            # Extract information from the given tiers
            labels = vowels_coords_tier[i].get_labels()
            vowels_coords = [label.get_best().get_typed_content() for label in labels]
            cur_vowels = list()
            cur_probas = list()
            for label in hand_pos_probas[i].get_labels():
                for tag, score in label:
                    cur_vowels.append(tag.get_content())
                    cur_probas.append(score)

            from_vowel_idx = self._vrank.index(cur_vowels[0])
            coord1 = vowels_coords[from_vowel_idx]
            x1, y1 = coord1.get_midpoint()
            r1 = coord1.get_radius()

            if len(cur_vowels) == 1:
                # The hand is at a target position.
                # Use the center of the coords stored in all_vowels.
                pos_coords.append([((x1, y1, r1), 1.)])

            elif len(cur_vowels) == 2:
                to_vowel_idx = self._vrank.index(cur_vowels[1])
                coord2 = vowels_coords[to_vowel_idx]
                x2, y2 = coord2.get_midpoint()
                r2 = coord2.get_radius()
                if from_vowel_idx == to_vowel_idx:
                    # The current position is also the next one.
                    xm = x2 - r2
                    ym = y2 + r2
                    pos_coords.append([((xm, ym, r2), cur_probas[1])])

                else:
                    pos_coords.append([((x1, y1, r1), cur_probas[0]), ((x2, y2, r2), cur_probas[1])])

            else:
                pos_coords.append([])
                logging.error("No vowel at index {:d}".format(i))

        return pos_coords

    # -----------------------------------------------------------------------

    def __create_tier(self, transition_tier, vowels_coords, consonant=True):
        """Create a tier with a content for each given vowels coords."""
        if consonant is True:
            tier = sppasTier("CS-Shapes")
            cur_content = [self.__cued.get_neutral_consonant()]
        else:
            tier = sppasTier("CS-Positions")
            cur_content = [self.__cued.get_neutral_vowel()]

        for ann in vowels_coords:
            loc = ann.get_location().get_best()
            # Create the ann at the given location
            new_content = self.__get_label_contents_at(transition_tier, loc)
            if new_content is None:
                # This is not a transition period but a target one.
                if len(cur_content) == 2:
                    cur_content.pop(0)
            labels = [sppasLabel(sppasTag(c)) for c in cur_content]
            tier.create_annotation(ann.get_location().copy(), labels)

        return tier

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_label_contents_at(tier, point):
        """Return the list of label contents of the annotation at the given moment."""
        content = None
        ann_idx = tier.mindex(point, bound=2)
        if ann_idx != -1:
            # A key is matching the image time
            labels = tier[ann_idx].get_labels()
            if len(labels) == 1:
                content = [labels[0].get_best().get_content()]
            elif len(labels) == 2:
                c1 = labels[0].get_best().get_content()
                c2 = labels[1].get_best().get_content()
                content = [c1, c2]
            else:
                raise ValueError("One or two labels were expected. "
                                 "Got {:d} instead.".format(len(labels)))

        return content

    # -----------------------------------------------------------------------

    @staticmethod
    def __probas_to_lists(probas):
        """Return the tags and scores of the given list of probabilities."""
        tags = list()
        scores = list()
        for s in probas:
            tags.append(sppasTag(s[0]))
            scores.append(s[1])
        return tags, scores
