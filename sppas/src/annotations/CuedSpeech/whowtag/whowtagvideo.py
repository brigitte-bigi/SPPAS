# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.video_cued.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: Tag a video with the Cued Speech keys.

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

from sppas.core.coreutils import sppasError
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasIOError
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import serialize_labels
from sppas.src.anndata import sppasTranscription
from sppas.src.imgdata import sppasImage
from sppas.src.videodata import sppasVideoReaderBuffer
from sppas.src.videodata import sppasBufferVideoWriter
from sppas.src.anndata import sppasFuzzyPoint
from sppas.src.annotations.annotationsexc import AnnotationOptionError

from ..whatkey.phonestokeys import CuedSpeechKeys

from .gencoordstier import sppasHandCoordsGenerator
from .whowimgtag import sppasImageVowelPosTagger
from .whowimgtag import sppasImageHandTagger

# ---------------------------------------------------------------------------


class CuedSpeechVideoTagger:
    """Create a video with hands tagged on the face of a video.
    
    """

    OPTIONS = {
        "handsset": "drawncue",
        "handsfilter": "",
        "infotext": False,
        "vowelspos": False
    }

    def __init__(self, cue_rules: CuedSpeechKeys = CuedSpeechKeys()):
        """Create a new instance.

        :param cue_rules: (CuedSpeechKeys) Rules and codes for vowel positions and hand shapes

        """
        self.__gencoords = sppasHandCoordsGenerator()

        # A buffer of images in order to read/write a video
        self.__video_buffer = sppasVideoReaderBuffer()
        self.__video_writer = sppasBufferVideoWriter()
        self.__video_path = None

        # Rule-based system to convert a sequence of phonemes into keys
        if isinstance(cue_rules, CuedSpeechKeys) is False:
            raise sppasTypeError(type(cue_rules), "CuedSpeechKeys")

        # Fix options for this instance
        self.__options = dict()
        for key in CuedSpeechVideoTagger.OPTIONS:
            self.__options[key] = CuedSpeechVideoTagger.OPTIONS[key]

        self._img_vowel_tagger = sppasImageVowelPosTagger(cue_rules)
        self._img_hand_tagger = sppasImageHandTagger(cue_rules)

        self.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------
    # Object Overrides
    # -----------------------------------------------------------------------

    def __del__(self):
        self.close()

    # -----------------------------------------------------------------------
    # Getters & Setters
    # -----------------------------------------------------------------------

    def set_cue_rules(self, cue_rules: CuedSpeechKeys) -> None:
        """Set the CuedSpeechKeys used to tag the video.

        :param cue_rules: (CuedSpeechKeys) The instance of the cuedSpeechKeys to set
        :raises: : sppasTypeError: If the parameter is not an instance of the CuedSpeechKeys class

        """
        if isinstance(cue_rules, CuedSpeechKeys) is False:
            raise sppasTypeError(cue_rules, "CuedSpeechKeys")

        self._img_hand_tagger.set_cue_rules(cue_rules)
        self._img_vowel_tagger.set_cue_rules(cue_rules)
        self.__gencoords.set_cue_rules(cue_rules)

    # -----------------------------------------------------------------------

    def load_hands(self, prefix: str) -> None:
        """Load the hand pictures with given name.

        :param prefix: (str) A hand set name (handcue, ...)
        :raises: sppasIOError: If no hands are loaded (not found the hands files)

        """
        success = self._img_hand_tagger.load_hands(prefix)
        if success is False:
            raise sppasIOError(f"Hand pictures with name {prefix} not loaded.")

    # -----------------------------------------------------------------------

    def load(self, video_path: str) -> None:
        """Open the video.

        Closes automatically the video if already was an open video.

        :param video_path: (str) File path of the input video
        :raises: VideoBrowseError: Can't open/read the video

        """
        self.close()

        # Open the video file
        self.__video_buffer.open(video_path)
        self.__video_path = video_path

        # Adjust the video writer
        self.__video_writer.set_fps(self.__video_buffer.get_framerate())

    # -----------------------------------------------------------------------

    def is_loaded(self) -> bool:
        """Return the information of if a video is loaded or not.

        :return: (bool) True if the buffer is currently opened or False else

        """
        if self.__video_buffer is None:
            return False

        return self.__video_buffer.is_opened()

    # -----------------------------------------------------------------------

    def close(self) -> None:
        """Release video streams."""
        self.__video_buffer.close()
        self.__video_writer.close()

    # -----------------------------------------------------------------------

    def is_opened(self) -> bool:
        """Return the information of if the writer is currently opened.

        :return: (bool) True if the video writer is open or False else.

        """
        return self.__video_writer.is_opened()

    # -----------------------------------------------------------------------

    def set_option(self, option_key: str, option_value: object) -> None:
        """Set an option of the video tagger.

        Available options are :
            - handsset
            - handsfilter
            - infotext
            - vowelspos

        :param option_key: (str) Name of the option
        :param option_value: (any) Value of the option
        :raises: AnnotationOptionError: If the given key is unknown

        """
        if option_key in self.__options.keys():
            self.__options[option_key] = option_value
        else:
            raise AnnotationOptionError(option_key)

    # -----------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------

    def tag_with_keys(self, transcription: sppasTranscription, output: str) -> list:
        """Tag the video with the given keys.

        The possible tiers of the given transcription are:
            - CS-ShapeProbas: probabilities of the shapes of the hand
            - CS-PosProbas: probabilities of the positions of the hand
            - CS-VowelsCoords: Coordinates of the position of the vowels
            - CS-TargetCoords: Coordinates of the target sight
            - CS-HandAngle: Coordinates of the target sight
            - PhonAlign: Time-aligned phonemes

        The video streams (buffer/writer) are not released... Use close().

        :param transcription: (sppasTranscription) The transcription to use to tag the video.
        :param output: (str) Output video filename
        :raises: sppasError: If no video is load.
        :return: (list) created files -- expected 1

        """
        # Check the buffer
        if self.is_loaded() is False:
            raise sppasError("No video in the buffer. Nothing can be tagged.")

        # Load the options
        self.__load_options()

        # Search and get all tiers
        self.__check_tiers(transcription)

        # Fix the image hand tagger for the video
        if self._img_hand_tagger.hand_mode() is True:
            _tagger = self._img_hand_tagger
        else:
            _tagger = None

        # Create the tier "CS-HandCoords" with coordinates of the target position, S0 and S9.
        hand_coords_tier = self.__gencoords.hands_to_handcoords(
            transcription.find("CS-ShapeProbas"),
            transcription.find("CS-TargetCoords"),
            transcription.find("CS-HandAngle"),
            transcription.find("CS-FaceHeight"),
            _tagger
        )

        # Browse the video, one buffer at a time
        result = list()
        index = 0  # index of the first image of each buffer
        nb_buffer = 0  # buffer number
        read_next = True  # indicator to know if we reached the end of the video or not

        self.__video_buffer.seek_buffer(0)
        image_duration = 1. / self.__video_buffer.get_framerate()

        # foreach image in the video
        while read_next:
            logging.info(f" ... buffer number {nb_buffer + 1}")

            # Fill-in the buffer with images
            read_next = self.__video_buffer.next()
            start_time = index * image_duration

            # Tag the images of the buffer with hands and/or vowel coords
            self.__tag_buffer(start_time,
                              hand_coords_tier,
                              transcription.find("CS-ShapeProbas"),
                              transcription.find("CS-PosProbas"),
                              transcription.find("CS-VowelsCoords"),
                              transcription.find("PhonAlign"))

            # Save the current result in a video
            if output is not None:
                new_files = self.__video_writer.write_video(self.__video_buffer, output, "")
                result.extend(new_files)

            nb_buffer += 1
            index += len(self.__video_buffer)

        # reload the video if the user wants to re-tag the video with the same instance of CuedSpeechVideoTagger
        self.load(self.__video_path)

        return result

    # -----------------------------------------------------------------------
    # Public Statics Methods
    # -----------------------------------------------------------------------

    @staticmethod
    def get_hands_filters() -> list:
        """List of all available hands filters.

        :return: (list[str]) A list of all hands filters.

        """
        return [
            "cartoon",
            "sights",
            "skeleton",
            "sticks"
        ]

    # -----------------------------------------------------------------------

    @staticmethod
    def get_annotation_index(tier: sppasTier, timepoint) -> int:
        """Return the index corresponding to the given time point.

        :param tier: (sppasTier) The tier that contains the annotation who searched
        :param timepoint: (sppasPoint or float) The time to search for the index

        :return: (int) The index or -1 if no index associated with the given time point

        """
        if tier is None:
            annotation_index = -1

        elif tier.is_point():
            annotation_index = tier.index(timepoint)

        else:
            # bound=2 : include begin, include end
            annotation_index = tier.mindex(timepoint, bound=2)

        return annotation_index

    # -----------------------------------------------------------------------

    @staticmethod
    def get_annotation_index_starting_to(tier: sppasTier, timepoint,
                                         start_index: int) -> int:
        """Return the next index corresponding to the given time point starting to the start_index parameter.

        :param tier: (sppasTier) The tier that  contains the annotation who searched
        :param timepoint: (sppasPoint or float) The time to search for the index
        :param start_index: (int) The index to start to search for the index

        :return: (int) The next annotation index that corresponding with the given timepoint
                 Or -1 if no annotation found

        """
        if tier is None:
            return -1

        if start_index >= len(tier):
            return -1
        elif start_index <= 0:
            return CuedSpeechVideoTagger.get_annotation_index(tier, timepoint)

        new_index = start_index
        while new_index != -1:
            # annotation founded
            if tier[new_index].get_lowest_localization() <= timepoint <= tier[new_index].get_highest_localization():
                break

            new_index += 1
            if new_index == len(tier):  # end of the tier
                new_index = -1

            # I went too far, do not continue with the next annotations.
            if timepoint > tier[new_index].get_highest_localization():
                new_index = -1

        return new_index

    # -----------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------

    def __load_options(self) -> None:
        """Check the activated options and load the corresponding resources."""
        # Load the hands set, none by default
        hand_set = self.__options.get("handsset")
        if len(hand_set) > 0:
            self.load_hands(hand_set)
            logging.info(f"Successfully loaded the hands set '{hand_set}'.")
            hand_filter = self.__options.get("handsfilter")

            # Apply a filter, if any
            if len(hand_filter) > 0:
                self._img_hand_tagger.apply_hands_filter(hand_filter)
                logging.info(f"Successfully applied the hands filter '{hand_filter}'.")
        else:
            logging.info("No hands set was defined. The video is tagged with badges.")

    # -----------------------------------------------------------------------

    def __check_tiers(self, transcription: sppasTranscription) -> None:
        """Find the tiers used to tag the video.

        Searched tiers (on the order of the return list):
            - CS-ShapeProbas: probabilities of the shapes of the hand
            - CS-PosProbas: probabilities of the positions of the hand
            - CS-VowelsCoords: Coordinates of the position of the vowels
            - PhonAlign: Time-aligned phonemes

        """
        tiers = list()

        # Try to get the shape probabilities tiers
        tiers.append(transcription.find("CS-ShapeProbas"))
        if tiers[0] is None:
            logging.error("Missing tier with shape probabilities.")

        # Try to get the position probabilities tier
        tiers.append(transcription.find("CS-PosProbas"))
        if tiers[1] is None:
            logging.error("Missing tier with position probabilities.")

        # Try to get the vowel poitions tier
        tiers.append(transcription.find("CS-VowelsCoords"))
        if tiers[2] is None:
            logging.error("Missing tier with vowels coords.")

        # Try to get the time-aligned phonemes tier
        tiers.append(transcription.find("PhonAlign"))
        if tiers[3] is None:
            logging.error("Missing tier with time-aligned phonemes.")

        # Target coordinates
        tiers.append(transcription.find("CS-TargetCoords"))
        if tiers[4] is None:
            logging.error("Missing tier with target coordinates.")

        # Angle values
        tiers.append(transcription.find("CS-HandAngle"))
        if tiers[5] is None:
            logging.error("Missing tier with angle values.")

        # Face height
        tiers.append(transcription.find("CS-FaceHeight"))
        if tiers[6] is None:
            logging.error("Missing tier with face heights.")

        if None in tiers:
            raise sppasError("At least one of the expected tiers was not found in the transcription. "
                             "Video tagging is aborted. See logging for details.")

    # -----------------------------------------------------------------------

    def __tag_buffer(self, start_time: float,
                     coords_tier, shape_tier, pos_tier, vowels_tier, info_tier) -> None:
        """Browse the buffer and tag the images.

        :param start_time: (float) The time when the tag begin
        :param coords_tier: (sppasTier or None) The sights of the hand for the target, S0 and S9
        :param pos_tier: (sppasTier or None) Positions and probabilities (CS-PosProbas)
        :param shape_tier: (sppasTier or None) Shape codes and probabilities (CS-ShapeProbas)
        :param vowels_tier: (sppasTier or None) The vowels positions (CS-VowelsCoords)
        :param info_tier: (sppasTier or None) The phonemes, used to print on the image in debug mode (PhonAlign)

        """
        image_duration = 1. / self.__video_buffer.get_framerate()
        radius = 0.0005  # image_duration / 4.

        pos_index = shape_index = vowels_index = info_index = coords_index = -1

        start_buffer_index, _ = self.__video_buffer.get_buffer_range()
        iter_images = self.__video_buffer.__iter__()

        for i in range(len(self.__video_buffer)):
            # Get the current frame number in the video stream
            video_image_number = start_buffer_index + i

            # Get the current image, and add alpha channel.
            img = next(iter_images)
            if img is None:
                # It seems that something went wrong when estimating the remaining nb of frames...
                logging.warning("No frame at index {:d}.".format(video_image_number))
                continue
            img = img.ialpha(254)

            # Get the middle time of the current image
            s = start_time + (i * image_duration)
            middle_time = s + (image_duration / 2.)
            point = sppasPoint(middle_time, radius)

            # Get the annotations index during the image
            coords_index = self.get_annotation_index_starting_to(coords_tier, point, coords_index)
            pos_index = self.get_annotation_index_starting_to(pos_tier, point, pos_index)
            shape_index = self.get_annotation_index_starting_to(shape_tier, point, shape_index)
            vowels_index = self.get_annotation_index_starting_to(vowels_tier, point, vowels_index)
            info_index = self.get_annotation_index_starting_to(info_tier, point, info_index)

            # Extract data from the tiers
            sights = self.__extract_coords_data(coords_tier, coords_index)
            shape_text, shapes = self.__extract_shape_data(shape_tier, shape_index)
            pos_text, score = self.__extract_position_data(pos_tier, pos_index)
            vowels_positions = self.__extract_vowels_data(vowels_tier, vowels_index)

            # Slap the hand on the face, or the badge if no hand set was defined
            if shape_index != -1 and pos_index != -1 and len(sights) > 0 and sights[0] is not None:
                img = self._img_hand_tagger.slap_on(img, shapes, sights)

            # Draw vowels' positions if the option is activated
            if self.__options["vowelspos"] is True and len(vowels_positions) > 0:
                img = self._img_vowel_tagger.slap_on(img, vowels_positions)

            # Put text of debug information if the option is activated
            if self.__options["infotext"] is True:
                # Write the information
                info_text = "Info: "
                if info_index != -1:
                    info_text += str(round(info_tier[info_index].get_lowest_localization().get_midpoint(), 3))
                    info_text += " "
                    info_text += serialize_labels(info_tier[info_index].get_labels())

                # Tag the image with the information (frame/shape/position/key)
                frame_text = f"Frame: {video_image_number} ({round(middle_time, 3)},{round(radius, 3)})"
                self.__put_debug_texts(img, [frame_text, shape_text, pos_text, info_text])

            # set tagged image on the video buffer
            self.__video_buffer.set_at(img.ibgra_to_bgr(), i)

    # -----------------------------------------------------------------------

    def __put_debug_texts(self, img: sppasImage, texts: list) -> None:
        """Put debug information on the given image.

        :param img: (sppasImage) The image to put the text on it.
        :param texts: (list) The list that contains all texts to put in the image.

        """
        step = 30

        for i, text in enumerate(texts):
            img.put_text((100, (i + 1) * step), (10, 10, 10), 1, text)

    # -----------------------------------------------------------------------
    # Private Static Methods
    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_coords_data(coords_tier, index) -> list:
        """Extract the sights data to compute the hand scale factor.

        If the index equal to -1, this function returns a list of None.

        :param coords_tier: (sppasTier or None) The tier that contains the sights
        :param index: (int) The index of the annotation
        :return: (list) A list of the coords for s0, s9, target

        Example of returned list:
        [sppasFuzzyPoint: (368,780), sppasFuzzyPoint: (432,684), sppasFuzzyPoint: (540,573)]

        """
        sights = [None, None, None]

        # get the coords
        if coords_tier is not None and index != -1:
            return coords_tier[index].get_labels()
            #for sight_label in coords_tier[index].get_labels():
                # get the sppasFuzzyPoint with coordinates of the sight label
                # and add to the list
                # if sight_label.get_key() == "sights_00":
                #     sights[0] = sight_label.get_best().get_typed_content()
                # elif sight_label.get_key() == "sights_09":
                #     sights[1] = sight_label.get_best().get_typed_content()
                # elif sight_label.get_key() == "target":
                #     sights[2] = sight_label.get_best().get_typed_content()

        return [None, None, None]

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_shape_data(shape_tier: sppasTier, index: int) -> tuple:
        """Extract the shape data (shapes codes and scores) from a shape tier.

        :param shape_tier: (sppasTier) The tier that contains our shape data
        :param index: (int) The index of the annotation
        :return: (str, list) The shape text information and the list of shapes codes and scores

        """
        shape_text = "Shape: "
        shapes = list()

        for shape_label in shape_tier[index].get_labels():
            for tag, score in shape_label:
                shape_code = tag.get_typed_content()

                if score is None:
                    score = 1.

                shape_text += shape_code
                shapes.append((shape_code, score))

        return shape_text, shapes

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_position_data(pos_tier, index: int) -> tuple:
        """Extract the position data from the position tiers.

        :param pos_tier: (sppasTier or None) The tier that contains the positions text information
        :param index: (int) The index of the annotation
        :return: (str) The position text information and the position probability

        """
        pos_text = "Pos: "
        score = 1

        # get the text information
        if pos_tier is not None:
            for pos_label in pos_tier[index].get_labels():
                score = pos_label.get_score(pos_label.get_best())

                for tag, score in pos_label:
                    pos_text += tag.get_typed_content()

        return pos_text, score

    # -----------------------------------------------------------------------

    @staticmethod
    def __extract_vowels_data(vowels_tier, index: int) -> list:
        """Extract the vowels data from the vowels tier.

        If the vowels tier is None or the index equal to -1 return an empty list by default.

        :param vowels_tier: (sppasTier or None) The tier that contains our vowels data
        :param index: (int) The index of the annotation
        :return: (list) A list of all vowels positions

        """
        vowels_positions = list()

        if vowels_tier is not None and index != -1:
            for vowel_label in vowels_tier[index].get_labels():
                # Get the sppasFuzzyPoint() of the vowel
                pos = vowel_label.get_best().get_typed_content()
                vowels_positions.append(pos)

        return vowels_positions
