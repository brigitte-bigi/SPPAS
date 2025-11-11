# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.whatkey.whatkey.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Keys generation of the Cued Speech from time-aligned phonemes.

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
import logging

from sppas.core.config import symbols
from sppas.core.coreutils import info
from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel

from .phonestokeys import CuedSpeechKeys

# ---------------------------------------------------------------------------


class sppasWhatKeyPredictor(object):
    """Cued Speech keys automatic generator from a sequence of phonemes.

    """

    # Back to neutral shape and/or position if silence > threshold
    # Fixed from our experience of Cued Speech.
    NEUTRAL_POSITION_THRESHOLD = 1.8
    NEUTRAL_SHAPE_THRESHOLD = 1.2

    # -----------------------------------------------------------------------

    def __init__(self, cue_rules: CuedSpeechKeys = CuedSpeechKeys()):
        """Instantiate a CS generator.

        :param cue_rules: (CuedSpeechKeys) Rules to convert phonemes to keys

        """
        self.__cued = None
        self.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechKeys) -> None:
        """Set new rules.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        if isinstance(cue_rules, CuedSpeechKeys) is False:
            raise sppasTypeError("cue_rules", "CuedSpeechKeys")

        # Rule-based system to convert a sequence of phonemes into keys
        self.__cued = cue_rules

    # -----------------------------------------------------------------------
    # Generators
    # -----------------------------------------------------------------------

    def phons_to_segments(self, phonemes: sppasTier) -> sppasTier:
        """Convert time-aligned phonemes into CS segments.

        PhonAlign:            |  b   | O~ |  Z |  u |  R   |
        CS-PhonSegments:      |  b O~     |  Z u    |  R   |

        :param phonemes: (sppasTier) time-aligned phonemes tier
        :return: (sppasTier) Phonemes grouped into key segments

        """
        if isinstance(phonemes, sppasTier) is False:
            raise sppasTypeError("phons", "sppasTier")

        segments_tier = sppasTier("CS-PhonSegments")
        segments_tier.set_meta('cued_speech_segments_of_tier', phonemes.get_name())

        # Create a tier without the separators, i.e. keep only the phonemes.
        # The intervals are like the Time Groups of TGA, i.e. sequences of
        # phonemes ONLY, ignoring silences, pauses, dummy, noises, laugh...
        intervals = sppasWhatKeyPredictor._phon_to_intervals(phonemes)

        # Create key segments for each sequence of phonemes in the intervals
        for interval in intervals:
            # get the index of the phonemes containing the 'begin' value of the interval
            start_phon_idx = phonemes.lindex(interval.get_lowest_localization())
            if start_phon_idx == -1:
                start_phon_idx = phonemes.mindex(interval.get_lowest_localization(), bound=-1)

            # get the index of the phonemes containing the end of the interval
            end_phon_idx = phonemes.rindex(interval.get_highest_localization())
            if end_phon_idx == -1:
                end_phon_idx = phonemes.mindex(interval.get_highest_localization(), bound=1)

            # generate key segments within the interval
            if start_phon_idx != -1 and end_phon_idx != -1:
                self.__gen_key_segments(phonemes, start_phon_idx, end_phon_idx, segments_tier)
            else:
                logging.warning((info(1224, "annotations")).format(interval))

        return segments_tier

    # -----------------------------------------------------------------------

    def segments_to_keys(self,
                         segments: sppasTier,
                         start_point: sppasPoint | None = None,
                         end_point: sppasPoint = None) -> tuple:
        """Create tiers with the CS denomination and the class of each phoneme.

        CS-PhonSegments:      |  b O~     |  Z u    |   R   |   #   |
        CS-PhonStructs:       |  C V      |  C V    |   C   |       |
        CS-Keys:              |  4 m      |  1 c    |  3 n  |  0 n  |
        CS-KeysClass:         |  C V      |  C V    |  C N  |  N N  |

        :param segments: (sppasTier) A tier in which key segments
        :param start_point: (sppasPoint)
        :param end_point: (sppasPoint)
        :returns: (sppasTier, sppasTier, sppasTier) CS-Keys CS-KeysClass CS-PhonStructs

        """
        key_tier = sppasTier("CS-Keys")
        key_tier.set_meta('cued_speech_key_of_tier', segments.get_name())
        class_tier = sppasTier("CS-KeysClass")
        class_tier.set_meta('cued_speech_phonclass_of_tier', segments.get_name())
        struct_tier = sppasTier("CS-PhonStructs")
        struct_tier.set_meta('cued_speech_struct_of_tier', segments.get_name())

        for ann in segments:
            phons = [label.copy() for label in ann.get_labels()]
            if len(phons) == 0:
                raise ValueError("A CS key should contain at least one phoneme."
                                 "Got {:d} instead.".format(len(phons)))
            if len(phons) > 2:
                raise ValueError("A CS key should contain at max two phonemes."
                                 "Got {:d} instead.".format(len(phons)))
            if len(phons) == 1:
                content = phons[0].get_best().get_content()
                if self.__cued.get_class(content) == "V":
                    phons.insert(0, sppasLabel(sppasTag("cnil")))
                elif self.__cued.get_class(content) == "C":
                    phons.append(sppasLabel(sppasTag("vnil")))
                else:
                    phons.insert(0, sppasLabel(sppasTag(symbols.unk)))

            consonant = phons[0].get_best().get_content()
            consonant_class = self.__cued.get_class(consonant)
            vowel = phons[1].get_best().get_content()
            vowel_class = self.__cued.get_class(vowel)

            # CS-Keys labels
            labels = self.__create_labels(
                self.__cued.get_key(consonant), self.__cued.get_key(vowel),
                phons[0].get_key(), phons[1].get_key())
            a1 = ann.copy()
            a1.set_labels(labels)
            key_tier.append(a1)

            # CS-PhonClass labels
            labels = self.__create_labels(
                consonant_class, vowel_class,
                phons[0].get_key(), phons[1].get_key())
            a2 = ann.copy()
            a2.set_labels(labels)
            class_tier.append(a2)

            # CS-Structs labels
            labels = self.__create_labels(
                consonant_class if consonant_class != "N" else None,
                vowel_class if vowel_class != "N" else None,
                phons[0].get_key(), phons[1].get_key())
            a3 = ann.copy()
            a3.set_labels(labels)
            struct_tier.append(a3)

        # Fill gaps with the neutral
        self.__fill_key_segments(key_tier, class_tier, start_point, end_point)

        return key_tier, class_tier, struct_tier

    # -----------------------------------------------------------------------
    # Utilities:
    # -----------------------------------------------------------------------

    @staticmethod
    def _phon_to_intervals(phonemes: sppasTier) -> sppasTier:
        """Create a tier with only the intervals to be syllabified.

        We could use symbols.phone only, but for backward compatibility,
        the symbols used in previous versions of SPPAS are added here.

        :param phonemes: (sppasTier)
        :return: a tier with consecutive filled intervals.

        """
        stop = list(symbols.phone.keys())
        stop.append('#')
        stop.append('@@')
        stop.append('+')
        stop.append('gb')
        stop.append('lg')

        return phonemes.export_to_intervals(stop)

    # -----------------------------------------------------------------------
    # Private: the heart of the generators
    # -----------------------------------------------------------------------

    def __gen_key_segments(self, tier_palign, from_p, to_p, tier_key_segs):
        """Perform the key generation of a sequence of phonemes.

        :param tier_palign: (sppasTier) Time-aligned phonemes
        :param from_p: (int) index of the first phoneme to be syllabified
        :param to_p: (int) index of the last phoneme to be syllabified
        :param tier_key_segs: (sppasTier)

        """
        # Extract the phonemes (only the best one of each annotation)
        phons = list()
        for ann in tier_palign[from_p:to_p+1]:
            tag = ann.get_best_tag()
            phons.append(tag.get_typed_content())

        # create the sequence of key' segments
        # syll_keys is a list of tuples (begin index, end index)
        syll_keys = self.__cued.syllabify(phons)

        # add the key segments into the output tier
        for i, syll in enumerate(syll_keys):
            start_idx, end_idx = syll
            # end_idx is either equal to start_idx or to start_idx+1

            # create the location
            a1 = tier_palign[start_idx + from_p].get_lowest_localization().copy()
            a3 = tier_palign[end_idx + from_p].get_highest_localization().copy()
            location = sppasLocation(sppasInterval(a1, a3))

            # create the labels:
            # one phoneme in PhonAlign ==> one label with key = phoneme id.
            labels = list()
            for ann in tier_palign[from_p + start_idx:from_p + end_idx + 1]:
                tag = ann.get_best_tag()
                label = sppasLabel(tag.copy())
                label.set_key(key=ann.get_id())
                labels.append(label)

            # add the key segment into the output tier
            tier_key_segs.create_annotation(location, labels)

        return tier_key_segs

    # -----------------------------------------------------------------------

    def __fill_key_segments(self, tier_keys, tier_class, start_point, end_point):
        """Fill the gaps with the neutral shape and neutral position.

        :param tier_keys: (sppasTier)
        :param tier_class: (sppasTier)

        """
        if len(tier_keys) == 0:
            return

        cn = self.__cued.get_neutral_consonant()  # shape
        vn = self.__cued.get_neutral_vowel()      # position
        prev = None
        prev_shape_key = None
        prev_pos_key = None
        prev_shape_class = None
        prev_pos_class = None
        current_pos_key = None
        current_shape_key = None

        # Start with the Neutral shape and position, from the beginning
        if start_point is not None and tier_keys[0].get_lowest_localization() > start_point:
            interval = sppasInterval(start_point.copy(), tier_keys[0].get_lowest_localization())
            labels = [sppasLabel(sppasTag(cn)), sppasLabel(sppasTag(vn))]
            annotation = sppasAnnotation(sppasLocation(interval), labels)
            tier_keys.add(annotation)
            prev_shape_key = cn
            prev_pos_key = vn
            labels = [sppasLabel(sppasTag(self.__cued.NEUTRAL_CLASS)), sppasLabel(sppasTag(self.__cued.NEUTRAL_CLASS))]
            annotation = sppasAnnotation(sppasLocation(interval.copy()), labels)
            tier_class.add(annotation)
            prev_shape_class = self.__cued.NEUTRAL_CLASS
            prev_pos_class = self.__cued.NEUTRAL_CLASS

        for a, ac in zip(tier_keys, tier_class):
            fill_hole = False

            if prev is not None and prev.get_highest_localization() < a.get_lowest_localization():
                # There's a hole between the previous and the current annotation.
                # May this hole being a key? It depends on its duration...
                interval = sppasInterval(prev.get_highest_localization(), a.get_lowest_localization())
                duration = interval.duration().get_value()
                if prev_shape_key == 's' and duration > sppasWhatKeyPredictor.NEUTRAL_SHAPE_THRESHOLD:
                    # The shape is neutral in the hole
                    current_shape_key = cn
                    current_shape_class = self.__cued.NEUTRAL_CLASS  # "N"
                    fill_hole = True
                else:
                    current_shape_key = prev_shape_key
                    current_shape_class = prev_shape_class
                if prev_pos_key is not None and duration > sppasWhatKeyPredictor.NEUTRAL_POSITION_THRESHOLD:
                    # The position is neutral in the hole
                    current_pos_key = vn
                    current_pos_class = self.__cued.NEUTRAL_CLASS  # "N"
                    fill_hole = True
                    # It necessarily implies the shape is neutral!
                    current_shape_key = cn
                    current_shape_class = self.__cued.NEUTRAL_CLASS  # "N"
                else:
                    current_pos_key = prev_pos_key
                    current_pos_class = prev_pos_class

                if fill_hole is True:
                    labels = [sppasLabel(sppasTag(current_shape_key)),
                              sppasLabel(sppasTag(current_pos_key))]
                    annotation = sppasAnnotation(sppasLocation(interval), labels)
                    tier_keys.add(annotation)

                    labels = [sppasLabel(sppasTag(current_shape_class)),
                              sppasLabel(sppasTag(current_pos_class))]
                    annotation = sppasAnnotation(sppasLocation(interval), labels)
                    tier_class.add(annotation)

                    prev = annotation
                    prev_shape_key = current_shape_key
                    prev_shape_class = current_shape_class
                    prev_pos_key = current_pos_key
                    prev_pos_class = current_pos_class

            if fill_hole is False:
                prev = a
                prev_shape_key = a.get_labels()[0].get_best().get_content()
                prev_shape_class = ac.get_labels()[0].get_best().get_content()
                prev_pos_key = a.get_labels()[1].get_best().get_content()
                prev_pos_class = ac.get_labels()[1].get_best().get_content()

        # End with the Neutral shape and position, to the end time
        if end_point is not None and tier_keys[-1].get_highest_localization() < end_point:
            interval = sppasInterval(tier_keys[-1].get_highest_localization(), end_point.copy())
            labels = [sppasLabel(sppasTag(cn)), sppasLabel(sppasTag(vn))]
            annotation = sppasAnnotation(sppasLocation(interval), labels)
            tier_keys.add(annotation)
            labels = [sppasLabel(sppasTag(self.__cued.NEUTRAL_CLASS)), sppasLabel(sppasTag(self.__cued.NEUTRAL_CLASS))]
            annotation = sppasAnnotation(sppasLocation(interval.copy()), labels)
            tier_class.add(annotation)

    # -----------------------------------------------------------------------

    @staticmethod
    def __create_labels(consonant, vowel, ann_key_c, ann_key_v):
        # Create the tags
        tag_c = None
        if consonant is not None:
            tag_c = sppasTag(consonant)
        tag_v = None
        if vowel is not None:
            tag_v = sppasTag(vowel)

        # Create the labels
        cs_c = sppasLabel(tag_c)
        cs_c.set_key(ann_key_c)
        cs_v = sppasLabel(tag_v)
        cs_v.set_key(ann_key_v)

        # Return labels in a list
        return [cs_c, cs_v]
