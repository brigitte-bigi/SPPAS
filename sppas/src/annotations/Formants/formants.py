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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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


class FormantsPass(object):
    """Represent an analysis pass of a formants estimation method.

    A pass is an audio processing pipeline and the formants which can be
    reliably estimated with it. A method requires as many passes as the
    formants it estimates require different pipelines: the resampling rate
    of a pipeline is limiting the highest formant it can estimate.

    """

    __slots__ = ("__pipeline", "__formants")

    def __init__(self, pipeline: AudioProcessingPipeline, formants: tuple):
        """Initialize the pass.

        :param pipeline: (AudioProcessingPipeline or None)
        :param formants: (tuple) Ranks of the estimated formants, i.e. (1, 2)
        :raises: TypeError: The given pipeline is not a valid one.
        :raises: ValueError: No formant is estimated by the pass.

        """
        if pipeline is not None and isinstance(pipeline, AudioProcessingPipeline) is False:
            raise TypeError("Pipeline must be AudioProcessingPipeline or None.")
        if len(formants) == 0:
            raise ValueError("A pass must estimate at least one formant.")

        self.__pipeline = pipeline
        self.__formants = tuple(formants)

    # -----------------------------------------------------------------------

    def get_pipeline(self) -> AudioProcessingPipeline:
        """Return the audio processing pipeline of the pass."""
        return self.__pipeline

    # -----------------------------------------------------------------------

    def get_formants(self) -> tuple:
        """Return the ranks of the formants estimated by the pass."""
        return self.__formants

    # -----------------------------------------------------------------------

    def get_sample_rate(self) -> int:
        """Return the sample rate the signal is analyzed with, or zero."""
        if self.__pipeline is None:
            return 0

        return self.__pipeline.get_target_sr()

# ---------------------------------------------------------------------------


class MethodFormantsEstimator(object):
    """Represent a formants estimation method with its analysis passes.

    """

    __slots__ = ("__estimator", "__passes")

    def __init__(self, estimator: object, passes: list):
        """Initialize the method.

        :param estimator: (object) Instance of formants estimator.
        :param passes: (list) The FormantsPass instances of the method
        :raises: TypeError: No estimator or an invalid pass is given.

        """
        if estimator is None:
            raise TypeError("Estimator instance required.")
        for a_pass in passes:
            if isinstance(a_pass, FormantsPass) is False:
                raise TypeError("A method requires FormantsPass instances.")

        self.__estimator = estimator
        self.__passes = list(passes)

    # -----------------------------------------------------------------------

    def get_estimator(self) -> object:
        """Return the formants estimator object."""
        return self.__estimator

    # -----------------------------------------------------------------------

    def get_passes(self) -> list:
        """Return the analysis passes of the method."""
        return self.__passes

    # -----------------------------------------------------------------------

    def get_formants(self) -> tuple:
        """Return the sorted ranks of all the formants the method estimates."""
        _formants = list()
        for a_pass in self.__passes:
            for rank in a_pass.get_formants():
                if rank not in _formants:
                    _formants.append(rank)

        return tuple(sorted(_formants))

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
            [FormantsPass(
                AudioProcessingPipeline([
                    RmsComputer(),
                    Resampler(target_sr=8000),
                    PreEmphasizer(0.97),
                    HammingWindow()
                ]),
                (1, 2))]
        )

        # Burg LPC with 12kHz resampling
        methods["burg"] = MethodFormantsEstimator(
            BurgLPCFormantEstimator,
            [FormantsPass(
                AudioProcessingPipeline([
                    RmsComputer(),
                    Resampler(target_sr=12000),
                    PreEmphasizer(0.99),
                    HammingWindow()
                ]),
                (1, 2))]
        )

        # Praat-based estimators, no preprocessing pipeline required
        methods["praat_burg"] = MethodFormantsEstimator(
            PraatBurgFormantsEstimator, [FormantsPass(None, (1, 2))])
        methods["praat_keepall"] = MethodFormantsEstimator(
            PraatKeepAllFormantsEstimator, [FormantsPass(None, (1, 2))])
        methods["praat_sl"] = MethodFormantsEstimator(
            PraatSLFormantsEstimator, [FormantsPass(None, (1, 2))])

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

    # LPC order used when it is neither fixed nor derivable from a sample rate
    DEFAULT_ORDER = 12

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

        # LPC order -- 0 to derive it from the sample rate of each pass
        self.__order = 0

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

    def get_order(self, sample_rate: int = 0) -> int:
        """Return the LPC order, the derived one if it was not fixed.

        The order of an LPC analysis depends on the sample rate of the
        analyzed signal: two poles are required for each formant of the
        [0; sample_rate/2] range, plus two for the spectral slope.

        :param sample_rate: (int) Sample rate to derive the order from
        :return: (int) The fixed order, or the derived one

        """
        if self.__order > 0:
            return self.__order
        if sample_rate <= 0:
            return FormantsEstimator.DEFAULT_ORDER

        return 2 * (sample_rate // 1000) + 2

    def set_order(self, value: int) -> None:
        """Set the LPC order: 0 to derive it from the sample rate.

        :param value: (int) Order value, between 6 and samplerate/100, or 0
        :raises: TypeError: Given value is not an integer.
        :raises: ValueError: Given value is not zero nor a valid order.

        """
        if isinstance(value, int) is False:
            raise TypeError(f"Given value {value} is not an integer.")
        if value != 0 and value < 6:
            raise ValueError(f"Given value must be 0 or at least 6. Got {value} instead.")

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

    def estimate(self, audio_filename: str, palign_tier: sppasTier) -> list:
        """Estimate formants for the given sound in a time interval.

        The estimated values of all the enabled methods are stored into the
        F1 and F2 tiers. The values of each method are also stored into their
        own tier, except if only one method is enabled: its tiers would be
        identical to the F1 and F2 ones.

        :param audio_filename: (str) Filename of a mono-audio file
        :param palign_tier: (sppasTier) Tier with time-aligned phonemes
        :return: (list of sppasTier) Estimated formants in tiers
        :raises: ValueError: No method enabled

        """
        if len(self.__methods) == 0:
            raise ValueError("At least one of the estimator methods has to be enabled.")
        audio_pcm = audioopy.aio.open(audio_filename)

        # Estimate RMS threshold -- if auto mode
        if self.__min_rms_threshold == 0:
            self.__auto_min_threshold(audio_pcm)

        # Prepare data -- the threshold is a metadata of the tiers
        tiers = self.__create_formant_tiers()
        method_tiers = self.__create_method_tiers()
        estimators = self.__create_estimators(audio_filename)

        # Estimate a formant value for each identified phoneme
        self.__estimate_annotations(palign_tier, estimators, audio_pcm, tiers, method_tiers)

        audio_pcm.close()

        return self.__gather_tiers(tiers, method_tiers)

    # ----------------------------------------------------------------------------

    def __estimate_annotations(self, palign_tier: sppasTier, estimators: dict,
                               audio_pcm: audioopy.AudioPCM, tiers: dict,
                               method_tiers: dict) -> None:
        """Estimate and store the formants of each phoneme of the tier.

        :param palign_tier: (sppasTier) Tier with time-aligned phonemes
        :param estimators: (dict) The instantiated estimators
        :param audio_pcm: (AudioPCM) Audio object
        :param tiers: (dict) Tier of each formant rank
        :param method_tiers: (dict) Tier of each formant rank and method

        """
        for ann in palign_tier:

            # Check if annotation is a phoneme
            phon = serialize_labels(ann.get_labels(), separator="_", empty="", alt=False)
            if len(phon) == 0 or ann.get_best_tag().get_content() in symbols.phone:
                continue

            self.__estimate_annotation(ann, phon, estimators, audio_pcm, tiers, method_tiers)

    # ----------------------------------------------------------------------------

    def __estimate_annotation(self, ann: sppasAnnotation, phon: str, estimators: dict,
                              audio_pcm: audioopy.AudioPCM, tiers: dict, method_tiers: dict) -> None:
        """Estimate and store the formants of one phoneme.

        :param ann: (sppasAnnotation) Annotation of a time-aligned phoneme
        :param phon: (str) The phoneme
        :param estimators: (dict) The instantiated estimators
        :param audio_pcm: (AudioPCM) Audio object
        :param tiers: (dict) Tier of each formant rank
        :param method_tiers: (dict) Tier of each formant rank and method

        """
        # Determine time window around the phoneme center
        center_start_time, center_end_time = self.__get_segment_times(ann)

        if self.__out_type == "center":
            # Estimate or get formants in this window only -- at the center
            values = self.__apply_methods(estimators, audio_pcm, center_start_time, center_end_time)
            self.__append_annotations(tiers, method_tiers, phon, ann.get_location(), values)
            return

        # Estimate or get formants in all windows of the phoneme
        values = self.__estimate_windows(ann, phon, estimators, audio_pcm, tiers, method_tiers)
        if self.__out_type == "mean" and values is not None:
            self.__append_annotations(tiers, method_tiers, phon, ann.get_location(), values)

    # ----------------------------------------------------------------------------

    def __estimate_windows(self, ann: sppasAnnotation, phon: str, estimators: dict,
                           audio_pcm: audioopy.AudioPCM, tiers: dict, method_tiers: dict):
        """Estimate the formants of each window of a phoneme.

        Each window is stored if the output type is "all", or the mean values
        of all the windows are returned if it is "mean".

        :return: (dict|None) Mean value of each formant rank, or None

        """
        start_time = self.__get_first_window_time(ann)
        end_time = start_time + (2 * self.__half_win_dur)
        sums = self.__create_sums()
        nb_windows = 0

        while end_time < ann.get_highest_localization():
            values = self.__apply_methods(estimators, audio_pcm, start_time, end_time)
            if self.__out_type == "all":
                loc = sppasLocation(sppasInterval(sppasPoint(start_time), sppasPoint(end_time)))
                self.__append_annotations(tiers, method_tiers, phon, loc, values)
            else:
                FormantsEstimator.__add_values(sums, values)
                nb_windows += 1

            # prepare next loop
            start_time += 2 * self.__half_win_dur
            end_time = start_time + (2 * self.__half_win_dur)

        if nb_windows == 0:
            return None

        return FormantsEstimator.__mean_values(sums, nb_windows)

    # ----------------------------------------------------------------------------

    def __create_sums(self) -> dict:
        """Return the summed value of each formant rank, initialized to zero."""
        sums = dict()
        for rank in self.__get_ranks():
            sums[rank] = [0.] * len(self.__get_methods(rank))

        return sums

    # ----------------------------------------------------------------------------

    @staticmethod
    def __add_values(sums: dict, values: dict) -> None:
        """Add the values of a window to the summed ones."""
        for rank in values:
            for i in range(len(values[rank])):
                sums[rank][i] += values[rank][i]

    # ----------------------------------------------------------------------------

    @staticmethod
    def __mean_values(sums: dict, nb_windows: int) -> dict:
        """Return the mean value of each formant rank of all the windows."""
        means = dict()
        for rank in sums:
            means[rank] = [v/nb_windows for v in sums[rank]]

        return means

    # ----------------------------------------------------------------------------

    def __get_first_window_time(self, ann: sppasAnnotation) -> float:
        """Return the start time of the first window of a phoneme."""
        start_time, _ = self.__get_segment_times(ann)
        too_far = False
        while start_time > ann.get_lowest_localization():
            start_time -= 2 * self.__half_win_dur
            too_far = True
        if too_far is True:
            start_time += 2 * self.__half_win_dur

        return start_time

    # ----------------------------------------------------------------------------

    def __create_estimators(self, audio_filename: str) -> dict:
        """Return the instantiated estimator of each enabled method.

        :param audio_filename: (str) Filename of a mono-audio file
        :return: (dict) Estimator instance or class of each method name

        """
        estimators = dict()
        for name in self.__methods:
            estimator_class = self.__available_methods[name].get_estimator()
            if "praat" in name:
                estimators[name] = estimator_class(audio_filename)
            else:
                estimators[name] = estimator_class

        return estimators

    # ----------------------------------------------------------------------------

    def __get_ranks(self) -> tuple:
        """Return the sorted ranks of the formants the enabled methods estimate."""
        ranks = list()
        for name in self.__methods:
            for rank in self.__available_methods[name].get_formants():
                if rank not in ranks:
                    ranks.append(rank)

        return tuple(sorted(ranks))

    # ----------------------------------------------------------------------------

    def __get_methods(self, rank: int) -> list:
        """Return the enabled methods estimating the formant of the given rank.

        :param rank: (int) Rank of a formant, i.e. 1 for F1
        :return: (list) Names of the methods, in their enabling order

        """
        names = list()
        for name in self.__methods:
            if rank in self.__available_methods[name].get_formants():
                names.append(name)

        return names

    # ----------------------------------------------------------------------------

    def __gather_tiers(self, tiers: dict, method_tiers: dict) -> list:
        """Return all the created tiers, the ones of the methods at the end."""
        all_tiers = list()
        for rank in sorted(tiers):
            all_tiers.append(tiers[rank])
        for name in self.__methods:
            for rank in sorted(tiers):
                if (rank, name) in method_tiers:
                    all_tiers.append(method_tiers[(rank, name)])

        return all_tiers

    # ----------------------------------------------------------------------------

    def __create_formant_tiers(self) -> dict:
        """Return the tier of each estimated formant, with its metadata.

        A tier is storing the values of all the enabled methods estimating
        its formant.

        :return: (dict) Tier of each formant rank

        """
        tiers = dict()
        for rank in self.__get_ranks():
            names = self.__get_methods(rank)
            tier = sppasTier("F%d" % rank)
            for i, m in enumerate(names):
                tier.set_meta("formants_estimator_method_%d" % i, m)
            self.__set_options_metadata(tier, names)
            tiers[rank] = tier

        return tiers

    # ----------------------------------------------------------------------------

    def __create_method_tiers(self) -> dict:
        """Return the tier of each formant and method, with its metadata.

        No tier is created if only one method is enabled: its tiers would be
        identical to the ones of the formants.

        :return: (dict) Tier of each (formant rank, method name)

        """
        method_tiers = dict()
        if len(self.__methods) == 1:
            return method_tiers

        for rank in self.__get_ranks():
            for name in self.__get_methods(rank):
                tier = sppasTier("F%d-%s" % (rank, name))
                tier.set_meta("formants_estimator_method_0", name)
                self.__set_options_metadata(tier, [name])
                method_tiers[(rank, name)] = tier

        return method_tiers

    # ----------------------------------------------------------------------------

    def __set_options_metadata(self, tier: sppasTier, method_names: list) -> None:
        """Add the options the given methods depend on to the metadata.

        The LPC options are only used by the self-implemented methods, so
        they are not added to a tier of a Praat-based method.

        :param tier: (sppasTier) Tier to add the metadata to
        :param method_names: (list) Names of the methods of the tier

        """
        tier.set_meta("output_type", self.__out_type)
        tier.set_meta("win_length", str(round(2*self.__half_win_dur, 3)))
        tier.set_meta("rms_threshold", str(self.__min_rms_threshold))

        for name in method_names:
            if "praat" not in name:
                tier.set_meta("floor_freq", str(self.__floor_frequency))
                break

        # The LPC order depends on the sample rate of each analysis pass, so
        # it is a metadata of the tiers of a single method only.
        if len(method_names) == 1 and "praat" not in method_names[0]:
            tier.set_meta("lpc_order", self.__serialize_orders(method_names[0]))

    # ----------------------------------------------------------------------------

    def __serialize_orders(self, method_name: str) -> str:
        """Return the LPC order of each analysis pass of the given method.

        :param method_name: (str) Name of an enabled method
        :return: (str) The orders, separated by a comma

        """
        _orders = list()
        for a_pass in self.__available_methods[method_name].get_passes():
            _orders.append(str(self.get_order(a_pass.get_sample_rate())))

        return ",".join(_orders)

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

    def __append_annotations(self, tiers: dict, method_tiers: dict, phon: str,
                             loc: sppasLocation, values: dict) -> None:
        """Append the estimated values of a phoneme to the given tiers.

        :param tiers: (dict) Tier of each formant rank
        :param method_tiers: (dict) Tier of each formant rank and method
        :param phon: (str) The phoneme
        :param loc: (sppasLocation) Where the values were estimated
        :param values: (dict) Estimated value of each formant rank

        """
        for rank in values:
            # Create annotations and add to the tiers only if at least
            # one method returned a valid value.
            if sum(values[rank]) > 0:
                self.__append_annotation(tiers[rank], phon, loc.copy(), values[rank])

            # Add the value of a method to its own tier, if it estimated one.
            for i, name in enumerate(self.__get_methods(rank)):
                if (rank, name) in method_tiers and values[rank][i] > 0:
                    self.__append_annotation(
                        method_tiers[(rank, name)], phon, loc.copy(), [values[rank][i]])

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

    def __apply_methods(self, estimators: dict, audio_pcm: audioopy.AudioPCM,
                        start_time: float, end_time: float) -> dict:
        """Apply all active methods and return the value of each formant.

        The value of a formant is a list with the value of each of the
        methods estimating it, in their enabling order. It is zero for a
        method which didn't estimate any value.

        :param estimators: (dict) The instantiated estimators
        :param audio_pcm: (AudioPCM) Audio object
        :param start_time: (float)
        :param end_time: (float)
        :return: (dict) Estimated values of each formant rank

        """
        by_method = dict()
        for name in self.__methods:
            by_method[name] = self.__apply_passes(name, estimators, audio_pcm, start_time, end_time)

        values = dict()
        for rank in self.__get_ranks():
            values[rank] = [by_method[name].get(rank, 0) for name in self.__get_methods(rank)]

        return values

    # ----------------------------------------------------------------------------

    def __apply_passes(self, name: str, estimators: dict, audio_pcm: audioopy.AudioPCM,
                       start_time: float, end_time: float) -> dict:
        """Apply the passes of a method and return its estimated formants.

        Each pass estimates the formants it declared, in their rank order.

        :param name: (str) Name of an enabled method
        :param estimators: (dict) The instantiated estimators
        :param audio_pcm: (AudioPCM) Audio object
        :param start_time: (float)
        :param end_time: (float)
        :return: (dict) Estimated value of each formant rank of the method

        """
        values = dict()
        for a_pass in self.__available_methods[name].get_passes():
            if "praat" in name:
                result = estimators[name].compute(start_time, end_time, a_pass.get_formants())
            else:
                result = self.__estimate_formants(
                    audio_pcm, (start_time, end_time), estimators[name], a_pass.get_pipeline())

            for i, rank in enumerate(a_pass.get_formants()):
                if result is not None and i < len(result):
                    values[rank] = result[i]
                else:
                    values[rank] = 0

        return values

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
            estimator.set_order(self.get_order(sr))

        return estimator.compute(self.__floor_frequency)
