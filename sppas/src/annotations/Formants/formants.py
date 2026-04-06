"""
:filename: sppas.src.annotations.Formants.formants.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Main extractor for any available method.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

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

    -------------------------------------------------------------------------

"""

from __future__ import annotations
import logging
import audioopy

from sppas.core.config import symbols
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasAnnotation
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasInterval
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag
from sppas.src.anndata import serialize_labels

from .lpc_formants import LPCFormantEstimator
from .lpc_formants import AutocorrelationLPCFormantEstimator
from .lpc_formants import BurgLPCFormantEstimator
from .praat_formants import PraatBurgFormantsEstimator
from .praat_formants import PraatSLFormantsEstimator
from .praat_formants import PraatKeepAllFormantsEstimator
from .audio_processing_pipeline import AudioProcessingPipeline
from .audio_processing_pipeline import HammingWindow
from .audio_processing_pipeline import Resampler
from .audio_processing_pipeline import PreEmphasizer
from .audio_processing_pipeline import RmsComputer
from .audio_segment_loader import SegmentLoader

# ---------------------------------------------------------------------------


class MethodFormantsEstimator(object):
    """Represent a formants estimation method with its audio processing pipeline.

    """

    __slots__ = ("__estimator", "__pipeline")

    def __init__(self, estimator: object, pipeline: AudioProcessingPipeline):
        """Initialize the method.

        :param estimator: (object) Instance of formants estimator.
        :param pipeline: (AudioProcessingPipeline or None)

        """
        if estimator is None:
            raise TypeError("Estimator instance required.")
        if pipeline is not None and isinstance(pipeline, AudioProcessingPipeline) is False:
            raise TypeError("Pipeline must be AudioProcessingPipeline or None.")

        self.__estimator = estimator
        self.__pipeline = pipeline

    # -----------------------------------------------------------------------

    def get_estimator(self) -> object:
        """Return the formants estimator object."""
        return self.__estimator

    # -----------------------------------------------------------------------

    def get_pipeline(self) -> AudioProcessingPipeline:
        return self.__pipeline

# ---------------------------------------------------------------------------


class MethodFormantsFactory(object):
    """Factory to define formants estimation methods.

    This class encapsulates the estimator classes  and their associated
    audio processing pipelines.

    """

    @staticmethod
    def create_all():
        """Return all available formants estimation methods.

        :return: (dict) Mapping method name → MethodFormantsEstimator instance

        """
        methods = dict()

        # Autocorrelation LPC with 8kHz resampling
        methods["autocorrelation"] = MethodFormantsEstimator(
            AutocorrelationLPCFormantEstimator,
            AudioProcessingPipeline([
                RmsComputer(),
                Resampler(target_sr=8000),
                PreEmphasizer(0.97),
                HammingWindow()
            ])
        )

        # Burg LPC with 12kHz resampling
        methods["burg"] = MethodFormantsEstimator(
            BurgLPCFormantEstimator,
            AudioProcessingPipeline([
                RmsComputer(),
                Resampler(target_sr=12000),
                PreEmphasizer(0.99),
                HammingWindow()
            ])
        )

        # Praat-based estimators, no preprocessing pipeline required
        methods["praat_burg"] = MethodFormantsEstimator(PraatBurgFormantsEstimator, None)
        methods["praat_keepall"] = MethodFormantsEstimator(PraatKeepAllFormantsEstimator, None)
        methods["praat_sl"] = MethodFormantsEstimator(PraatSLFormantsEstimator, None)

        return methods

# ---------------------------------------------------------------------------


class FormantsEstimator:
    """Formants estimator for F1/F2 values.

    It uses a standard preprocessing pipeline and aligned phonemes to estimate
    formant trajectories over voiced segments.

    """

    # Output type allows to define how many formant values are estimated in
    # a given interval and how to deal with them:
    # - center: return the value at the center of the interval
    # - mean: return the mean of all estimated values in the interval
    # - all: return all values estimated in the interval
    OUTPUT_TYPES = ("center", "mean", "all")

    # -----------------------------------------------------------------------

    def __init__(self, out_type: str = "center"):
        """Initialize formants estimator.

        :param out_type: (str) Type of formants output result.

        """
        # List of all available methods to estimate formants:
        self.__available_methods = MethodFormantsFactory.create_all()

        # Method names to be used to estimate the formant values:
        self.__methods = list()

        # For a window, the half window duration:
        self.__half_win_dur = 0.015

        # Ignore segments with a local RMS lower than this threshold (0=auto):
        self.__min_rms_threshold = 0

        # Do not return a formant value lower than this frequency:
        self.__floor_frequency = 70.0

        # LPC order
        self.__order = 12

        # Returned result among "center", "mean", "all"
        self.__out_type = "center"
        self.set_output_type(out_type)

    # ------------------------------------------------------------------------
    # Getters dans setters
    # ------------------------------------------------------------------------

    def set_output_type(self, out_type: str = "center"):
        """Set the output type among the available types.

        :param out_type: (str) Type of formants output result.
        :raises: ValueError: if out_type is invalid.

        """
        if out_type not in FormantsEstimator.OUTPUT_TYPES:
            raise ValueError("out_type must be one of {0}".format(FormantsEstimator.OUTPUT_TYPES))
        self.__out_type = out_type

    def get_output_type(self) -> str:
        """Return the selected type of output."""
        return self.__out_type

    # ------------------------------------------------------------------------

    def set_win_dur(self, value: float) -> None:
        """Set the window duration in seconds.

        :param value: (float)
        :raises: TypeError: Given value is not a number.
        :raises: ValueError: Given value must range 0.01 - 0.1.

        """
        if isinstance(value, float) is False:
            raise TypeError(f"Given value {value} is not a float number.")
        if value <= 0.010 or value > 0.100:
            raise ValueError(f"Given value {value} is not between 0.010 and 0.100.")

        self.__half_win_dur = float(value) / 2.

    def get_half_win_dur(self) -> float:
        """Return the window duration."""
        return self.__half_win_dur * 2.

    # ------------------------------------------------------------------------

    def get_rms_threshold(self):
        """Return the RMS threshold value."""
        return self.__rms_threshold

    def set_rms_threshold(self, value):
        """Set the RMS threshold value: 0 for automatic.

        :param value: (int) RMS threshold value (0=auto).
        :raises: TypeError: Given value is not an integer.
        :raises: ValueError: Given value must be between a positive integer.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError(f"Given value {value} is not an integer.")
        if value < 0:
            raise ValueError(f"Given value must be a positive integer. Got {value} instead.")

        self.__rms_threshold = int(value)

    # -----------------------------------------------------------------------

    def get_floor_frequency(self) -> float:
        """Return the minimum frequency to consider."""
        return self.__floor_frequency

    def set_floor_frequency(self, value: float) -> None:
        """Set the minimum frequency to consider for formants.

        :param value: (float)
        :raises: TypeError: Given value is not a number.
        :raises: ValueError: Given value must be between 50 and 500.

        """
        if isinstance(value, (int, float)) is False:
            raise TypeError(f"Given value {value} is not an integer.")
        if value < 50. or value > 500.:
            raise ValueError(f"Given value must range 50 - 500Hz. Got {value} instead.")

        self.__floor_frequency = value

    # -----------------------------------------------------------------------

    def get_order(self) -> int:
        """Return the LPC order."""
        return self.__order

    def set_order(self, value: int) -> None:
        """Set the LPC order.

        :param value: (int) Order value, between 6 and samplerate/100
        :raises: TypeError: Given value is not an integer.

        """
        if isinstance(value, int) is False:
            raise TypeError(f"Given value {value} is not an integer.")
        self.__order = value

    # ------------------------------------------------------------------------
    # Formants estimation methods
    # ------------------------------------------------------------------------

    def get_available_method_names(self) -> tuple:
        """Return names of the available methods."""
        return tuple(self.__available_methods.keys())

    # -----------------------------------------------------------------------

    def get_enabled_method_names(self) -> tuple:
        """Return a copy of the list of active method names.

        :return: (tuple) Names of the currently selected methods

        """
        return tuple(self.__methods)

    # ------------------------------------------------------------------------

    def enable_method(self, name: str, value: bool = True) -> None:
        """Enable or disable a method by name from the available list.

        This method registers a method as enabled or disabled by its name.
        It must exist in the available methods list.

        :param name: (str) Name of the method
        :param value: (bool) Whether the method should be enabled or not.
        :raises: KeyError: If the method name is unknown

        """
        if name not in self.__available_methods:
            raise KeyError(f"Unknown method name: {name}")

        if value is True and name not in self.__methods:
            self.__methods.append(name)

        elif value is False and name in self.__methods:
            self.__methods.remove(name)

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def estimate(self, audio_filename: str, palign_tier: sppasTier) -> tuple:
        """Estimate formants for the given sound in a time interval.

        :param audio_filename: (str) Filename of a mono-audio file
        :param palign_tier: (sppasTier) Tier with time-aligned phonemes
        :return: (sppasTier, sppasTier) Estimated formants in two tiers
        :raises: ValueError: No method enabled

        """
        if len(self.__methods) == 0:
            raise ValueError("At least one of the estimator methods has to be enabled.")
        # Prepare data
        t1 = self.__create_formant_tier("F1")
        t2 = self.__create_formant_tier("F2")
        audio_pcm = audioopy.aio.open(audio_filename)

        # Estimate RMS threshold -- if auto mode
        if self.__min_rms_threshold == 0:
            self.__auto_min_threshold(audio_pcm)

        # Instantiate the estimators -- or not, it depends of the estimator!
        estimators = dict()
        for name in self.__methods:
            method = self.__available_methods[name]
            estimator_class = method.get_estimator()
            if "praat" in name:
                estimators[name] = estimator_class(audio_filename)
            else:
                estimators[name] = estimator_class

        # Estimate a formant value for each identified phoneme
        for ann in palign_tier:

            # Check if annotation is a phoneme
            phon = serialize_labels(ann.get_labels(), separator="_", empty="", alt=False)
            if len(phon) == 0 or ann.get_best_tag().get_content() in symbols.phone:
                continue

            # Determine time window around the phoneme center
            center_start_time, center_end_time = self.__get_segment_times(ann)

            if self.__out_type == "center":
                # Estimate or get formants in this window only -- at the center
                f1, f2 = self.__apply_methods(estimators, audio_pcm, center_start_time, center_end_time)
                self.__append_annotations(t1, t2, phon, ann.get_location(), f1, f2)
            else:
                # Estimate of get_formants in all windows of the phoneme
                start_time = center_start_time
                too_far = False
                while start_time > ann.get_lowest_localization():
                    start_time -= 2 * self.__half_win_dur
                    too_far = True
                if too_far is True:
                    start_time += 2 * self.__half_win_dur
                end_time = start_time + (2 * self.__half_win_dur)
                sum_f1 = [0.]*len(self.__methods)
                sum_f2 = [0.]*len(self.__methods)
                _nb = 0
                while end_time < ann.get_highest_localization():
                    # Estimate or get formants in this window
                    f1, f2 = self.__apply_methods(estimators, audio_pcm, start_time, end_time)
                    if self.__out_type == "all":
                        loc = sppasLocation(sppasInterval(sppasPoint(start_time), sppasPoint(end_time)))
                        self.__append_annotations(t1, t2, phon, loc, f1, f2)
                    else:
                        for i in range(len(self.__methods)):
                            sum_f1[i] += f1[i]
                            sum_f2[i] += f2[i]
                        _nb += 1
                    # prepare next loop
                    start_time += 2 * self.__half_win_dur
                    end_time = start_time + (2 * self.__half_win_dur)

                if self.__out_type == "mean" and _nb > 0:
                    f1 = [v/_nb for v in sum_f1]
                    f2 = [v/_nb for v in sum_f2]
                    self.__append_annotations(t1, t2, phon, ann.get_location(), f1, f2)

        audio_pcm.close()
        return t1, t2

    # ----------------------------------------------------------------------------

    def __create_formant_tier(self, tier_name: str) -> sppasTier:
        """Add metadata describing the estimator to the tier.

        :param tier_name: (str) Name of the tier

        """
        tier = sppasTier(tier_name)
        for i, m in enumerate(self.__methods):
            tier.set_meta("formants_estimator_method_%d" % i, m)
        tier.set_meta("output_type", self.__out_type)
        tier.set_meta("win_length", str(round(2*self.__half_win_dur, 3)))
        return tier

    # ----------------------------------------------------------------------------

    @staticmethod
    def __append_annotation(tier: sppasTier, phon: str, location: sppasLocation, values: list):
        """Append annotation to the given location.

        """
        if len(values) > 0:
            tags = list()
            for f in values:
                tags.append(sppasTag(int(f), "int"))
            label = sppasLabel(tags)
            label.set_key(phon)
            tier.create_annotation(location, [label])
        else:
            tier.create_annotation(location, [])

    # ----------------------------------------------------------------------------

    def __append_annotations(self, t1, t2, phon, loc, f1, f2):
        """Append annotations to the given tiers.

        """
        # Create annotations and add to the tiers only if at least
        # one method returned a valid value.
        if (sum(f1) * sum(f2)) > 0:
            self.__append_annotation(t1, phon, loc, f1)
            self.__append_annotation(t2, phon, loc.copy(), f2)

    # ----------------------------------------------------------------------------

    def __auto_min_threshold(self, audio_pcm: audioopy.AudioPCM) -> None:
        """Automatically set the RMS threshold from the first channel.

        :param audio_filename: (AudioPCM) Audio filename

        """
        audio_pcm.extract_channel(0)
        channel = audio_pcm.get_channel(0)
        cs = audioopy.ipus.ChannelSilences(channel)
        self.__min_rms_threshold = cs.fix_threshold_vol()
        logging.info(f"Fixed RMS threshold of {self.__min_rms_threshold}.")

    # ----------------------------------------------------------------------------

    def __get_segment_times(self, ann: sppasAnnotation) -> tuple:
        """Return (start_time, end_time) around phoneme center.

        :param ann: (sppasAnnotation) Represent a phoneme annotation
        :return: (float, float) Start and end times of the phoneme center

        """
        begin = ann.get_lowest_localization().get_midpoint()
        end = ann.get_highest_localization().get_midpoint()
        center_time = (begin + end) / 2
        _start_time = center_time - self.__half_win_dur
        _end_time = center_time + self.__half_win_dur

        return _start_time, _end_time

    # ----------------------------------------------------------------------------

    def __apply_methods(self, estimators: list, audio_pcm: audioopy.AudioPCM, start_time: float, end_time: float) -> tuple:
        """Apply all active methods and return F1/F2 values.

        :param audio_pcm: (AudioPCM) Audio object
        :param start_time: (float)
        :param end_time: (float)
        :return: (tuple) List of estimated f1 values and list of estimated f2 values

        """
        f1 = list()
        f2 = list()

        for name in self.__methods:

            method = self.__available_methods[name]
            pipeline = method.get_pipeline()

            if "praat" in name:
                result = estimators[name].compute(start_time, end_time)
            else:
                estimator = estimators[name]
                result = self.__estimate_formants(audio_pcm, (start_time, end_time), estimator, pipeline)

            if result is not None:
                f1.append(result[0])
                f2.append(result[1])
            else:
                f1.append(0)
                f2.append(0)

        return f1, f2

    # ----------------------------------------------------------------------------

    def __estimate_formants(self,
                            audio: audioopy.AudioPCM,
                            segment: tuple,
                            estimator_class,
                            pipeline: AudioProcessingPipeline) -> tuple:
        """Estimate formants for a given segment using a specified estimator and pipeline.

        :param audio: (AudioPCM) An AudiooPy-compatible object with read_frames/seek.
        :param segment: A tuple (start_time, end_time) in seconds.
        :param estimator_class: A formant estimator class (must implement compute()).
        :param pipeline: An audio preprocessing pipeline instance (must have .run()).
        :return: A list of formant values (typically [F1, F2]), or None if skipped.

        """
        # Load and preprocess the segment
        loader = SegmentLoader(audio, pipeline)
        result = loader.load(segment[0], segment[1], self.__min_rms_threshold)
        if result is None:
            return None

        signal, sr = result

        # Instantiate the estimator and compute formants
        estimator = estimator_class(signal, sr, segment[0], segment[1])
        if isinstance(estimator, LPCFormantEstimator):
            estimator.set_order(self.__order)

        return estimator.compute(self.__floor_frequency)
