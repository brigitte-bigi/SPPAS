# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.CuedSpeech.sppascuedspeech.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SPPAS integration of the Cued Speech automatic annotation.

.. _This file is part of AutoCuedSpeech: <https://auto-cuedspeech.org/>
.. _Originally developed in SPPAS: <https://sppas.org/>
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

from sppas.core.config import cfg
from sppas.core.config import annots
from sppas.core.coreutils import sppasEnableFeatureError

from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasMedia
from sppas.src.videodata import sppasVideoReader
from sppas.src.resources import sppasHandResource

from sppas.src.annotations.baseannot import sppasBaseAnnotation
from sppas.src.annotations.searchtier import sppasFindTier
from sppas.src.annotations.annotationsexc import NoInputError
from sppas.src.annotations.annotationsexc import EmptyOutputError
from sppas.src.annotations.autils import sppasFiles
from sppas.src.annotations.annotationsexc import AnnotationOptionError

from .whatkey.phonestokeys import CuedSpeechKeys
from .whatkey.whatkey import sppasWhatKeyPredictor
from .whenhand.whenhandtrans import sppasWhenHandTransitionPredictor
from .wherecue.wherecue import sppasWhereCuePredictor

from .whowtag import CuedSpeechVideoTagger
from .annsonframes import sppasAnnsOnFrames

# ---------------------------------------------------------------------------


class sppasCuedSpeech(sppasBaseAnnotation):
    """SPPAS integration of the automatic Cued Speech key-code generation.

    """

    def __init__(self, log=None):
        """Create a new instance.

        Log is used for a better communication of the annotation process and its
        results. If None, logs are redirected to the default logging system.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasCuedSpeech, self).__init__("cuedspeech.json", log)
        self.__lang = "und"

        # A rule-based system to convert a sequence of phonemes into keys
        # This is a language-dependent resource
        self.__cued = CuedSpeechKeys()

        # Tiers generator of keys.
        # It answers the "What?" question.
        self.__genkey = sppasWhatKeyPredictor()

        # Tiers generator of hand shapes and hand positions.
        # It answers the "When?" question.
        self.__genhand = sppasWhenHandTransitionPredictor(predictor_version=self._options["handtrans"])

        # Tiers generator of vowels & hand coordinates.
        # It answers the "Where?" question. Requires sights.
        self.__gencue = sppasWhereCuePredictor()

        # Video tagger: instantiated when running if video tag option is enabled.
        # It answers the "How?" question.
        self.__tagger = None

        # Allows to adjust annotations boundaries on frames of the video
        self.__ann_on_media = sppasAnnsOnFrames(fps=60.)

    # -----------------------------------------------------------------------

    def load_resources(self, config_filename, lang="und", **kwargs):
        """Fix the keys from a configuration file.

        :param config_filename: Name of the configuration file with the keys
        :param lang: (str) Iso639-3 of the language or "und" if unknown.

        """
        # Load rules of the given language
        self.__lang = lang
        if lang != "und":
            self.__cued.load(config_filename)

        # Set rules to predictors
        self.__genkey.set_cue_rules(self.__cued)
        self.__genhand.set_cue_rules(self.__cued)
        self.__gencue.set_cue_rules(self.__cued)

        # The annotation will export a video with tagged hands
        if self._options['createvideo'] is True:
            self.__set_video_tagger()

    # -----------------------------------------------------------------------

    def __set_video_tagger(self):
        if cfg.feature_installed("video") is False or cfg.feature_installed("cuedspeech") is False:
            logging.warning("Cued Speech Video Tagger can't be enabled. "
                            "Either feature 'video' or 'cuedspeech' or both are not installed.")
            self.__tagger = None
        else:
            try:
                if self.__tagger is None:
                    self.__tagger = CuedSpeechVideoTagger(self.__cued)
                    for key in CuedSpeechVideoTagger.OPTIONS:
                        if key in self._options:
                            self.__tagger.set_option(key, self._options[key])
                else:
                    self.__tagger.set_cue_rules(self.__cued)

            except Exception as e:
                self.__tagger = None
                logging.warning("Cued Speech Video Tagger can't be enabled: {:s}"
                                "".format(str(e)))

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - inputpattern1, inputpattern2, inputpattern3, outputpattern,
            - createvideo: boolean
            - handtrans: version of the hand transition estimator model
            - handangle: version of the hand angle estimator model
            - handsset: name of the hand pictures set, or empty string to draw badges
            - angleface: boolean (hand angle is corrected by face angle)
            - infotext: boolean
            - vowelspos: boolean

        :param options: (sppasOption)

        """

        for opt in options:
            key = opt.get_key()

            if "createvideo" == key:
                self.set_create_video(opt.get_value())

            elif "pattern" in key:
                self._options[key] = opt.get_value()

            elif "handtrans" == key:
                self.set_when_handtrans_version(opt.get_value())

            elif "handangle" == key:
                self.set_where_handangle_version(opt.get_value())

            elif "handpos" == key:
                self.set_where_handposition_version(opt.get_value())

            elif "angleface" == key:
                self.set_where_angleface_correction(opt.get_value())

            elif key in CuedSpeechVideoTagger.OPTIONS:
                self._options[key] = opt.get_value()
                if self.__tagger is not None:
                    self.__tagger.set_option(key, opt.get_value())
                    self._options[key] = opt.get_value()
            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_when_handtrans_version(self, version=4):
        """Fix the version of the hand transition times generator.

        :param version: (int)

        """
        all_versions = self.__genhand.get_whenpredictor_versions()
        version = int(version)
        if version not in all_versions:
            msg = "Invalid version number '{}' for transition times. Expected one of {}"\
                  "".format(version, all_versions)
            self.logfile.print_message(msg, status=annots.error)
            version = 4

        self.__genhand.set_whenpredictor_version(version)
        self._options['handtrans'] = version

    # -----------------------------------------------------------------------

    def set_where_handposition_version(self, version=1):
        """Fix the version of the vowel' positions generator.

        :param version: (int)

        """
        all_versions = self.__gencue.get_wherepositionpredictor_versions()
        version = int(version)
        if version not in all_versions:
            msg = ("Invalid version number '{}' for vowels positions predictor. "
                   "Expected one of {}").format(version, all_versions)
            self.logfile.print_message(msg, status=annots.error)
            version = 1

        self.__gencue.set_wherepositionpredictor_version(version)
        self._options['handpos'] = version

    # -----------------------------------------------------------------------

    def set_where_handangle_version(self, version: int = 1):
        """Fix the version of the hand angle generator.

        :param version: (int)

        """
        all_versions = self.__gencue.get_whereanglepredictor_versions()
        version = int(version)
        if version not in all_versions:
            msg = "Invalid version number '{}' for angle predictor. Expected one of {}"\
                  "".format(version, all_versions)
            self.logfile.print_message(msg, status=annots.error)
            version = 1

        self.__gencue.set_whereanglepredictor_version(version)
        self._options['handangle'] = version

    # -----------------------------------------------------------------------

    def set_where_angleface_correction(self, value: bool = False):
        """Whether correct tha hand angle or not with the face one.

        :param value: (bool)

        """
        value = bool(value)
        self.__gencue.set_angle_use_face(value)
        self._options['angleface'] = value

    # -----------------------------------------------------------------------

    def set_create_video(self, create=True):
        """Fix the createvideo option.

        :param create: (bool)

        """
        create = bool(create)
        self._options['createvideo'] = create
        if create is True:
            self.__set_video_tagger()
        else:
            self.__tagger = None

    # -----------------------------------------------------------------------
    # CS what/when/where predictions
    # -----------------------------------------------------------------------

    def convert(self, phonemes, media):
        """Syllabify labels of a time-aligned phones tier.

        :param phonemes: (sppasTier) time-aligned phonemes tier
        :param media: (sppasMedia) a media representing the video file
        :returns: (sppasTier*6)

        """
        # What? Create the tiers with the CS keys from the phonemes
        cs_segments = self.__genkey.phons_to_segments(phonemes)
        cs_keys, cs_class, cs_struct = self.__genkey.segments_to_keys(cs_segments, phonemes.get_first_point(), phonemes.get_last_point())

        # When? Predict hand shapes and hand positions
        cs_pos, cs_shapes = self.__genhand.when_hands(cs_keys, cs_segments)

        return cs_segments, cs_keys, cs_class, cs_struct, cs_shapes, cs_pos

    # -----------------------------------------------------------------------

    def make_video(self, video_file, trs, output):
        """Create a video with the tagged keys.

        :param video_file: (str) Filename of the given video
        :param trs: (sppasTranscription) All required tiers to tag the video
        :param output: (str) Output file name

        """
        if cfg.feature_installed("video") is True and self.__tagger is not None:
            self.logfile.print_message("Create the tagged video", status=annots.info)
            self.__tagger.load(video_file)
            self.__tagger.tag_with_keys(trs, output)
            self.__tagger.close()
        else:
            self.logfile.print_message(
                f"To tag a video, the video support feature must be enabled "
                f"({cfg.feature_installed('video')}) and a video tagger must"
                f" be instantiated ({self.__tagger is not None})."
                "", status=annots.error)

    # -----------------------------------------------------------------------
    # Manage files
    # -----------------------------------------------------------------------

    def get_inputs(self, input_files):
        """Return the media and the annotated filenames.

        :param input_files: (list)
        :raise: NoInputError
        :return: (str, str) Names of the 3 expected files

        """
        ext = self.get_input_extensions()
        media_ext = [e.lower() for e in ext[1]]
        phons_ext = [e.lower() for e in ext[0]]
        sights_ext = [e.lower() for e in ext[2]]
        media = None
        annot_phons = None
        annot_sights = None
        pphones = self._options["inputpattern1"]
        psights = self._options["inputpattern3"]

        for filename in input_files:
            if filename is None:
                continue
            fn, fe = os.path.splitext(filename)
            if media is None and fe in media_ext:
                media = filename
            elif annot_phons is None and fe.lower() in phons_ext and fn.endswith(pphones):
                annot_phons = filename
            elif annot_sights is None and fe.lower() in sights_ext and fn.endswith(psights):
                annot_sights = filename

        if annot_phons is None:
            logging.error("The annotated file with time-aligned phonemes was not found.")
            raise NoInputError

        return media, annot_phons, annot_sights

    # -----------------------------------------------------------------------

    def create_media(self, video_filename):
        """Create a sppasMedia() instance from a video filename.

        """
        if video_filename is None:
            return None

        extm = os.path.splitext(video_filename.lower())[1]
        video_media = sppasMedia(os.path.abspath(video_filename), mime_type="video/" + extm)
        # Get the fps and set it in the metadata
        try:
            vid = sppasVideoReader()
            vid.open(video_filename)
            video_media.set_meta("fps", str(vid.get_framerate()))
            video_media.set_meta("duration", str(vid.get_duration()))
            video_media.set_meta("size", str(vid.get_size()))
            vid.close()
        except:
            pass
        return video_media

    # -----------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def run(self, input_files, output=None):
        """Run the automatic annotation process on an input.

        :param input_files: (list of str) time-aligned phonemes, and optionally video, csv files
        :param output: (str) the output name
        :returns: (sppasTranscription)

        """
        try:

            do_vid = False
            file_video, file_phons, file_sights = self.get_inputs(input_files)

            # Create a sppasMedia with the given input video (if any)
            video_media = self.create_media(file_video)

            # Get the tier from which we'll generate CS annotations
            parser = sppasTrsRW(file_phons)
            trs_input = parser.read()
            tier_phon = sppasFindTier.aligned_phones(trs_input)

            # Predict what and when cueing the given phonemes
            trs_output = sppasTranscription(self.name)
            self._set_trs_metadata(trs_output, file_phons)
            tier_cs, tier_key, tier_class, tier_struct, tier_shapes_transitions, tier_pos_transitions = self.convert(tier_phon, video_media)

            trs_output.append(tier_cs)
            trs_output.append(tier_struct)
            trs_output.append(tier_key)
            trs_output.append(tier_class)
            trs_output.append(tier_shapes_transitions)
            trs_output.append(tier_pos_transitions)

            # Predict where are the vowels relatively to the given sights, where
            # to tag the hand, what is the angle of the hand and its size by
            # predicting S0 and S9 of the hand.
            trs_coords = sppasTranscription(self.name)
            self._set_trs_metadata(trs_coords, file_phons)
            if file_sights is not None:
                if video_media is not None:
                    trs_coords.add_media(video_media)
                    # Adjust positions to correspond to frames of the video
                    adjusted_pos = tier_pos_transitions.copy()
                    self._set_media_to_tier(adjusted_pos, video_media, adjust=True)
                    trs_coords.append(adjusted_pos)
                    # Adjust shapes to correspond to frames of the video
                    adjusted_shapes = tier_shapes_transitions.copy()
                    self._set_media_to_tier(adjusted_shapes, video_media, adjust=True)
                    trs_coords.append(adjusted_shapes)
                    # Eval where from the video sights and adjusted pos&shapes
                    trs_coords = self.__gencue.predict_where(file_sights, adjusted_pos, adjusted_shapes)
                else:
                    # Eval where from the video sights and estimated pos&shapes
                    trs_coords = self.__gencue.predict_where(file_sights, tier_pos_transitions, tier_shapes_transitions)
                trs_coords.append(tier_phon)
                for tier in trs_coords:
                    self._set_media_to_tier(tier, video_media, adjust=False)

                # Create a video with the keys
                if self._options['createvideo']:

                    # Video tagger of cued keys
                    if len(input_files) > 2:
                        if file_video is not None and file_sights is not None:
                            do_vid = True
                            self.make_video(file_video, trs_coords, output)

                    if do_vid is False:
                        self.logfile.print_message(
                            "The option to tag the video was enabled but no video/csv "
                            "corresponding to the annotated file {:s} was found."
                            "".format(input_files[0]), status=-1)
            else:
                logging.info("No sights available.")

            if output is None:
                return trs_output

            # Save in a file
            outputs = list()
            output_file = self.fix_out_file_ext(output)
            if len(trs_output) > 0:
                parser = sppasTrsRW(output_file)
                parser.write(trs_output)
                outputs.append(output_file)
            else:
                raise EmptyOutputError

            if output is not None:
                coords_output = output_file.replace(self.get_output_pattern(), "-coords")
                parser = sppasTrsRW(coords_output)
                parser.write(trs_coords)
                outputs.append(coords_output)

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
        return outputs

    # ----------------------------------------------------------------------

    def get_output_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-cuedspeech")

    def get_input_patterns(self):
        """Pattern this annotation expects for its input filename."""
        return [
            self._options.get("inputpattern1", "-palign"),  # required phonemes
            self._options.get("inputpattern2", ""),         # optional image/video
            self._options.get("inputpattern3", "-sights")   # optional csv/xra sights
        ]

    # -----------------------------------------------------------------------

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename.

        Priority is given to video files, then image files.

        """
        media_ext = list(sppasFiles.get_informat_extensions("VIDEO"))
        for img_ext in sppasFiles.get_informat_extensions("IMAGE"):
            media_ext.append(img_ext)
        return [
            sppasFiles.get_informat_extensions("ANNOT_ANNOT"),
            media_ext,
            [".xra", ".csv"]
        ]

    # -----------------------------------------------------------------------

    @staticmethod
    def get_hands_sets() -> list:
        """List of all hands sets in the resources.cuedspeech folder.

        :return: (list) A list of all hands sets available.

        """
        hand_manager = sppasHandResource()
        hand_manager.automatic_loading()

        return hand_manager.get_hand_sets_identifiers()

    # -----------------------------------------------------------------------

    @staticmethod
    def get_hands_filters() -> list:
        """List of all available hands filters.

        :return: (list) A list of all hands filters.

        """
        return CuedSpeechVideoTagger.get_hands_filters()

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _set_media_to_tier(self, tier, media, adjust=False):
        """Set the media to the tier and adjust annotation boundaries.

        """
        if media is None:
            return
        tier.set_media(media)
        fps = media.get_meta("fps", None)
        if fps is not None and adjust is True:
            # Move all points to match with the frames of the media
            self.__ann_on_media.fps = fps
            self.__ann_on_media.adjust_boundaries(tier)

    # -----------------------------------------------------------------------

    def _set_trs_metadata(self, trs, filename):
        trs.set_meta('annotation_result_of', filename)
        trs.set_meta('language_iso', "iso639-3")
        trs.set_meta('language_name_0', "Undetermined")
        if len(self.__lang) == 3:
            trs.set_meta('language_code_0', self.__lang)
            trs.set_meta('language_url_0', "https://iso639-3.sil.org/code/" + self.__lang)
        else:
            trs.set_meta('language_code_0', "und")
            trs.set_meta('language_url_0', "https://iso639-3.sil.org/code/und")
