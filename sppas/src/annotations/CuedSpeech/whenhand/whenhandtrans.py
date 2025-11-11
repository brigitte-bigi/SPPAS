# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whenhand.whenhandtrans.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  CS hand transitions generator. Answer the "When?" question.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######  ########  ########     ###     ######
    ##    ## ##     ## ##     ##   ## ##   ##    ##     the automatic
    ##       ##     ## ##     ##  ##   ##  ##            annotation
     ######  ########  ########  ##     ##  ######        and
          ## ##        ##        #########       ##        analysis
    ##    ## ##        ##        ##     ## ##    ##         of speech
     ######  ##        ##        ##     ##  ######

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

import logging

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import serialize_labels

from ..whatkey.keysrules import CuedSpeechCueingRules
from ..whatkey.whatkeyexc import sppasCuedRulesValueError

from .transitions import WhenTransitionPredictor

# ---------------------------------------------------------------------------


class PredictedWhenHand:
    """Store predicted results, for internal use.

    1. (float) Start time value
    2. (float) End time value
    3. (tuple|list) List of tags of the source and target annotations
    4. (str) Identifier of the source annotation
    5. (str) Identifier of the target annotation

    """

    def __init__(self):
        self.__start = list()
        self.__end = list()
        self.__tags = list()
        self.__src_id = list()
        self.__tgt_id = list()

    # -----------------------------------------------------------------------

    def append(self, s: float, e: float, t: tuple, src: str, tgt: str) -> None:
        """Append a new predicted hand movement.

        The degenerated interval is invalid. It is turned into a valid one
        by shifting the given start value backward (-10ms).

        :param s: (float) Start time value
        :param e: (float) End time value
        :param t: (list|tuple) List of tags (source, target)
        :param src: (str) Source annotation identifier
        :param tgt: (str) Target annotation identifier

        """
        # At least 10ms between start and end value is required.
        if round(s, 2) == round(e, 2):
            if s > 0.01:
                s -= 0.01
            else:
                e = s + 0.01

        self.__start.append(s)
        self.__end.append(e)
        self.__tags.append(t)
        self.__src_id.append(src)
        self.__tgt_id.append(tgt)

    # -----------------------------------------------------------------------

    def get_start(self, item: int) -> float:
        """Return the start value of the given item index.

        :param item: (int) Index of the item to get
        :return: (float) Time value

        """
        return self.__start[item]

    def set_start(self, item: int, s: float):
        """Set the start value of the given item index.

        :param item: (int) Index of the item to set
        :param s: (float) Start value of the item

        """
        self.__start[item] = s

    # -----------------------------------------------------------------------

    def get_end(self, item: int) -> float:
        """Return the end value of the given item index.

        :param item: (int) Index of the item to get
        :return: (float) Time value

        """
        return self.__end[item]

    def set_end(self, item: int, e: float):
        """Set the end value of the given item index.

        :param item: (int) Index of the item to set
        :param e: (float) End value of the item

        """
        self.__end[item] = e

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __getitem__(self, item):
        """Return start, end, tags, source_id, target_id of the given item."""
        if item > len(self.__start):
            return None
        return (self.__start[item], self.__end[item],
                self.__tags[item], self.__src_id[item], self.__tgt_id[item])

    def __len__(self):
        """Return the number of items in the predicted results."""
        return len(self.__start)

    def __str__(self):
        """Return a string to represent the predicted results."""
        s = list()
        for i in range(len(self.__start)):
            s.append(("{:.3f} {:.3f} {:s} {:s} {:s}"
                      "").format(self.__start[i], self.__end[i],
                                 str(self.__tags[i]),
                                 self.__src_id[i], self.__tgt_id[i]))
        return "\n".join(s)

# ---------------------------------------------------------------------------


class sppasWhenHandTransitionPredictor:
    """Create the CS coding scheme from time-aligned phonemes.

    From the time-aligned keys, this class can estimate the moments of the
    hand shape transitions (consonants) and the moments of the hand position
    transitions (vowels).

    It aims to predict when the hand changes both its position and its shape.
    It results in two tiers indicating intervals with transitions:

        - CS-HandPositions predicting [M1,M2] intervals when position is changing;
        - CS-HandShapes predicting [D1,D2] intervals when shape is changing.

    """

    def __init__(self,
                 predictor_version=WhenTransitionPredictor.DEFAULT,
                 cue_rules=CuedSpeechCueingRules()):
        """Instantiate a CS generator.

        :param cue_rules: (CuedSpeechKeys) Rules to convert phonemes => keys

        """
        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = None
        self.set_cue_rules(cue_rules)

        # Hand transition prediction system: predict [D1, D2] and [M1, M2]
        self.__transitions = WhenTransitionPredictor()
        # Version of the generator
        self.set_whenpredictor_version(predictor_version)

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

    # -----------------------------------------------------------------------

    def get_whenpredictor_version(self) -> int:
        """Return the version number of the generation system."""
        return self.__transitions.get_version_number()

    # -----------------------------------------------------------------------

    @staticmethod
    def get_whenpredictor_versions() -> list:
        """Return the list of version numbers of the generation system."""
        return WhenTransitionPredictor.version_numbers()

    # -----------------------------------------------------------------------

    def set_whenpredictor_version(self, value: int) -> None:
        """Set the prediction system version.

        - 0: no time estimation.
        - 1: system based on P. Duchnowski et al. (1998)
        - 2: system based on P. Duchnowski et al. (2000)
        - 3: system based on V. Attina (2005) synchronization model
        - 4: empirical rules from B. Bigi & Datha
        - 5: revised rules by B. Bigi

        :raises: sppasKeyError:
        :raises: TypeError:

        """
        value = int(value)
        self.__transitions = WhenTransitionPredictor(value)

    # -----------------------------------------------------------------------

    def shape_is_neutral(self, s: str) -> bool:
        """Return True if the given character is the neutral shape.

        :param s: (str) Character representing a shape
        :return: (bool) The shape is neutral

        """
        return s == self.__cued.get_neutral_consonant()

    # -----------------------------------------------------------------------

    def position_is_neutral(self, p: str) -> bool:
        """Return True if the given character is the neutral position.

        :param p: (str) Character representing a position
        :return: (bool) The position is neutral

        """
        return p == self.__cued.get_neutral_vowel()

    # -----------------------------------------------------------------------

    def get_a1a3_avg_duration(self):
        """Return the average of stored [A1;A3] durations or the fixed one.

        If there's not enough known [A1;A3] durations, the fixed value is
        returned.

        """
        return self.__transitions.get_a1a3_avg_duration()

    # -----------------------------------------------------------------------

    def has_nil_pos(self, phns: str) -> bool:
        """Return True if the given string does not contain a vowel.

        :param phns: (str) Phonemes of a key in the form "C-V" or "V" or "C"
        :return: (bool) True if the phns are of "C" structure

        """
        return self.__cued.get_class(phns) == 'C' if '-' not in phns else False

    # -----------------------------------------------------------------------

    def has_nil_shape(self, phns: str) -> bool:
        """Return True if the given string does not contain a consonant.

        :param phns: (str) Phonemes of a key in the form "C-V" or "V" or "C"
        :return: (bool) True if the phns are of "V" structure

        """
        return self.__cued.get_class(phns) == 'V' if '-' not in phns else False

    # -----------------------------------------------------------------------

    def asset_a1a3(self, tier_keys: sppasTier) -> None:
        """Reset then store all [a1;a3] values in the transitions model.

        :param tier_keys: (sppasTier)

        """
        self.__transitions.reset_key_intervals()
        for ii in range(len(tier_keys)):
            ann = tier_keys[ii]
            interval = ann.get_location()
            labels = ann.get_labels()
            if len(labels) != 2:
                logging.error("Expected 2 labels of annotation: {:s}".format(str(ann)))
                raise sppasCuedRulesValueError(serialize_labels(labels))
            a1 = interval.get_lowest_localization().get_midpoint()
            a3 = interval.get_highest_localization().get_midpoint()
            cur_pos = labels[1].copy()
            is_neutral = self.position_is_neutral(cur_pos.get_best().get_content())
            self.__transitions.set_a(a1, a3, store=not is_neutral)

    # -----------------------------------------------------------------------

    def when_hands(self, tier_keys: sppasTier, tier_segments: sppasTier) -> tuple:
        """Create two tiers with the transition periods of the hand.

        :param tier_keys: (sppasTier)
        :param tier_segments: (sppasTier) Tier with name 'CS-PhonSegments', phonemes of each key
        :return: (sppasTier, sppasTier) Position transitions and Shape transitions
        :raises: sppasCuedRulesValueError

        """
        if len(tier_keys)*len(tier_segments) == 0:
            # Create an empty tier.
            cs_pos = sppasTier("CS-HandPositions")
            cs_shapes = sppasTier("CS-HandShapes")
        else:
            # Predict the [m1;m2] and [d1;d2] time values from the model
            positions_moves, shapes_moves = self.predict_transitions(tier_keys, tier_segments)
            cs_pos = self.predicted_to_tier(positions_moves)
            cs_pos.set_name("CS-HandPositions")
            cs_shapes = self.predicted_to_tier(shapes_moves)
            cs_shapes.set_name("CS-HandShapes")

        cs_pos.set_meta('cued_speech_position_of_keys_tier', tier_keys.get_name())
        cs_shapes.set_meta('cued_speech_shape_of_keys_tier', tier_keys.get_name())
        cs_pos.set_meta('cued_speech_position_of_phns_tier', tier_segments.get_name())
        cs_shapes.set_meta('cued_speech_shape_of_phns_tier', tier_segments.get_name())

        return cs_pos, cs_shapes

    # -----------------------------------------------------------------------

    def predict_transitions(self, tier_keys: sppasTier, tier_segments: sppasTier) -> tuple:
        """Return the predicted position transitions and shape transitions.

        The two returned lists contain:

        - the estimated m1 and m2 values (in seconds), or d1 and d2;
        - the transition position in a tuple with origin and target; and
        - the origin/target annotation identifiers.

        :param tier_keys: (sppasTier)
        :param tier_segments: (sppasTier) Tier with name 'CS-PhonSegments', phonemes of each key
        :return: tuple(PredictedWhenHand, PredictedWhenHand)
        :raises: sppasCuedRulesValueError

        """
        pos_moves = PredictedWhenHand()
        shp_moves = PredictedWhenHand()

        # Store all [a1;a3] values in the transitions model.
        # It allows to estimate the average duration on the whole tier.
        self.asset_a1a3(tier_keys)

        # No transition needs to be estimated to the first key.
        ann = tier_keys[0]
        labels = ann.get_labels()
        prev_shape = labels[0].copy()
        prev_pos = labels[1].copy()
        interval = ann.get_location()
        key_rank_ipu = 1
        # Corresponding phonemes sequence
        prev_phns = self.__get_phones(tier_segments, interval)

        # For the next keys
        for ii in range(1, len(tier_keys)):
            ann = tier_keys[ii]
            # Target position and the corresponding phonemes
            labels = ann.get_labels()
            # The hand shape of this annotation = the consonant = 1st label
            cur_shape = labels[0].copy()
            cur_pos = labels[1].copy()
            cur_phns = self.__get_phones(tier_segments, ann.get_location())
            # Target [A1;A3] values
            interval = ann.get_location()
            a1 = interval.get_lowest_localization().get_midpoint()
            a3 = interval.get_highest_localization().get_midpoint()

            # if the target is a long silence: move to neutral position.
            if self.position_is_neutral(cur_pos.get_best().get_content()) is True:
                # This is a long silence because of the neutral key position.
                key_rank_ipu = 0

            self.__transitions.set_a(a1, a3, store=False)

            # Position transition prediction, except if no movement needed
            if prev_pos != cur_pos or (prev_pos == cur_pos and prev_pos != 's') or \
                    (prev_pos == cur_pos and prev_pos == 's' and prev_shape == cur_shape):
                m1, m2 = self.__transitions.predict_m(
                    rank=key_rank_ipu,
                    is_nil_shape=self.has_nil_shape(cur_phns),
                    is_nil_pos=self.has_nil_pos(cur_phns),
                )
                # Add into the list
                prev_pos.set_key(prev_phns)
                cur_pos.set_key(cur_phns)
                pos_moves.append(m1, m2, (prev_pos, cur_pos), tier_keys[ii-1].get_id(), ann.get_id())

            # Shape transition prediction, except if no movement needed
            if cur_shape != prev_shape:
                d1, d2 = self.__transitions.predict_d(
                    rank=key_rank_ipu,
                    is_nil_shape=self.has_nil_shape(cur_phns),
                    is_nil_pos=self.has_nil_pos(cur_phns),
                )
                shp_moves.append(d1, d2, (prev_shape, cur_shape), tier_keys[ii-1].get_id(), ann.get_id())

            # Prepare for the next key
            prev_shape = cur_shape
            prev_pos = cur_pos
            prev_phns = cur_phns
            key_rank_ipu += 1

        return pos_moves, shp_moves

    # -----------------------------------------------------------------------

    @staticmethod
    def predicted_to_tier(predicted: PredictedWhenHand) -> sppasTier:
        """Turn the given values into sppasPoint.

        :param predicted: (PredictedWhenHand) Result of the prediction model.
        :return: (sppasTier) Predicted values turned into a sppasTier

        """
        tier = sppasTier("CS-Predicted")
        prev_end = sppasPoint(0.)
        for i in range(len(predicted)):
            start, end, tags, source_id, target_id = predicted[i]

            # Turn start and end into sppasPoint
            if prev_end >= start:
                p1 = prev_end.copy()
            else:
                p1 = sppasPoint(start)

            # Cancel overlaps of midpoints. Use radius to store the overlapped period.
            next_start = None if i+1 == len(predicted) else predicted[i+1][0]
            radius = None
            if next_start is not None and end > next_start:
                radius = (end - next_start) / 2.
                if end-radius > start:
                    end = end - radius
                else:
                    radius = (end - start) / 2.
            p2 = sppasPoint(end, radius)
            if p2 > p1:
                p2 = sppasPoint(end)

            # Create the annotation
            if p2 > p1:
                tier.create_annotation(sppasLocation(sppasInterval(p1, p2)), list(tags))
                tier.set_meta("from_id", source_id)
                tier.set_meta("to_id", target_id)
                prev_end = p2
            else:
                prev_end = p1

        return tier

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __get_phones(tier, interval) -> str:
        """Return the serialized best label of the tier in the given interval."""
        begin = interval.get_lowest_localization()
        end = interval.get_highest_localization()
        anns = tier.find(begin, end)
        if len(anns) > 0:
            return serialize_labels(anns[0].get_labels(), separator="-")
        return ""
