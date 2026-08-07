# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.VowelFilter.sppasvowelfilter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: SPPAS integration of the filtering of erroneous formant values.

.. _This file is part of SPPAS: <https://sppas.org/>
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
import os

from sppas.core.config import annots
from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier

from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import NoTierInputError
from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..autils import sppasFiles

from .vowel_filter import VowelFilterEstimator

# ----------------------------------------------------------------------------


class sppasVowelFilter(sppasBaseAnnotation):
    """SPPAS integration of the filtering of erroneous formant values.

    Erroneous F1/F2 values are identified with the Mahalanobis distance of
    the tokens to the expected values of their vowel class, as proposed by
    Lancien et al. (2023). Each pair of tiers created by the Formants
    annotation for a method is filtered with its own distributions.

    Such distributions can't be estimated on a file independently of the
    others: they require all the tokens of a corpus. This annotation is then
    pre-processing a set of files instead of annotating a file, so that it
    only proposes the 'batch_processing' method.

    """

    def __init__(self, log=None):
        """Create a new sppasVowelFilter instance.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasVowelFilter, self).__init__("vowelfilter.json", log)

        # The filtering estimator. Its distributions are estimated on all
        # the files to be filtered.
        self.__filter = VowelFilterEstimator()

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if "threshold" == key:
                self.set_threshold(opt.get_value())

            elif "coda" == key:
                self.set_coda(opt.get_value())

            elif "pattern" in key:
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------
    # Getters and Setters
    # -----------------------------------------------------------------------

    def get_threshold(self) -> float:
        return self._options['threshold']

    def get_coda(self) -> bool:
        return self._options['coda']

    # -----------------------------------------------------------------------

    def set_threshold(self, value: float) -> None:
        """Set the maximum distance of a token to the profile of its class.

        :param value: (float) Number of standard deviations
        :raises: TypeError: Given value is not a number.
        :raises: ValueError: Given value is not a positive number.

        """
        self.__filter.set_threshold(value)
        self._options['threshold'] = float(value)

    # -----------------------------------------------------------------------

    def set_coda(self, value: bool) -> None:
        """Set whether the syllable position is part of the vowel class.

        :param value: (bool) Add the position of the vowel to its class

        """
        self._options['coda'] = bool(value)

    # -----------------------------------------------------------------------
    # Apply the filtering on a set of files
    # -----------------------------------------------------------------------

    def batch_processing(self, file_names, progress=None):
        """Filter the erroneous formant values of a bunch of files.

        The feature distributions are estimated on the tokens of all the
        given files, then each file is filtered with these distributions.

        :param file_names: (list) List of inputs
        :param progress: ProcessProgressTerminal() or ProcessProgressDialog()
        :return: (list of str) List of created files

        """
        if len(file_names) == 0:
            return list()
        if len(self._options) > 0:
            self.print_options()
        if progress:
            progress.update(0, "")

        # First pass: collect the features of the vowels of all the files.
        self.__filter = VowelFilterEstimator(self._options['threshold'])
        _all_inputs = self.__collect_all(file_names)

        # Estimate the distributions the filtering is based on.
        self.__print_profiles(self.__filter.estimate())

        # Second pass: filter each file with the estimated distributions.
        _files_processed_success = self.__filter_all(_all_inputs, progress)
        if progress:
            progress.update(1, "")

        return _files_processed_success

    # -----------------------------------------------------------------------

    def __print_profiles(self, nb_profiles: int) -> None:
        """Print the number of estimated distributions in the user log.

        :param nb_profiles: (int) Number of estimated distributions

        """
        self.logfile.print_message(
            "Estimated {:d} distributions of {:d} vowel classes."
            "".format(nb_profiles, len(self.__filter.get_class_names())),
            indent=1, status=annots.info)

    # -----------------------------------------------------------------------

    def __collect_all(self, file_names: list) -> list:
        """Add the vowels of all the given files to the estimator.

        :param file_names: (list) List of inputs
        :return: (list) The (formants, syllables) file names of each valid input

        """
        _all_inputs = list()
        for input_files in file_names:
            try:
                _inputs = self._fix_inputs(input_files)
                _formants_filename, _syll_filename = self.get_inputs(_inputs)
            except Exception as e:
                logging.critical(str(e))
                continue

            self.print_diagnosis(*_inputs)
            try:
                _pairs, _syll_tier = self.__read_tiers(_formants_filename, _syll_filename)
                for tier_f1, tier_f2 in _pairs:
                    self.__filter.collect(tier_f1, tier_f2, _syll_tier)
            except Exception as e:
                self.logfile.print_message(str(e), indent=2, status=annots.error)
                continue

            _all_inputs.append((_formants_filename, _syll_filename))

        return _all_inputs

    # -----------------------------------------------------------------------

    def __filter_all(self, all_inputs: list, progress=None) -> list:
        """Filter each of the given files with the estimated distributions.

        :param all_inputs: (list) The (formants, syllables) file names
        :param progress: ProcessProgressTerminal() or ProcessProgressDialog()
        :return: (list of str) List of created files

        """
        _files_processed_success = list()
        for i, (formants_filename, syll_filename) in enumerate(all_inputs):
            if progress:
                progress.set_fraction(round(float(i)/float(len(all_inputs)), 2))
                progress.set_text(os.path.basename(formants_filename))

            self.print_filename(formants_filename)
            try:
                _out_name = self.__filter_file(formants_filename, syll_filename)
            except Exception as e:
                self.logfile.print_message(str(e), indent=2, status=annots.error)
            else:
                _files_processed_success.append(_out_name)
                self.logfile.print_message(_out_name, indent=1, status=annots.ok)
            self.logfile.print_newline()

        return _files_processed_success

    # -----------------------------------------------------------------------

    def get_inputs(self, input_files: list) -> tuple:
        """Return the filename with formants and the one with syllables.

        :param input_files: (list) The inputs of a file root
        :raises: NoTierInputError: No file with formant values
        :return: (str, str) Formants filename and syllables filename or None

        """
        _patterns = self.get_input_patterns()
        _formants_filename = None
        _syll_filename = None

        for filename in input_files:
            _fn, _ = os.path.splitext(filename)
            if _formants_filename is None and _fn.endswith(_patterns[0]) is True:
                _formants_filename = filename
            elif _syll_filename is None and len(_patterns[1]) > 0 and _fn.endswith(_patterns[1]) is True:
                _syll_filename = filename

        if _formants_filename is None:
            logging.error("No file with formant values, i.e. with pattern '{:s}'."
                          "".format(_patterns[0]))
            raise NoTierInputError

        if self._options['coda'] is False:
            return _formants_filename, None

        return _formants_filename, _syll_filename

    # -----------------------------------------------------------------------
    # Patterns and extensions of the files
    # -----------------------------------------------------------------------

    def get_output_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-vfilter")

    def get_input_patterns(self):
        """Pattern this annotation expects for its input filename."""
        return [
            self._options.get("inputpattern1", "-formants"),   # formant values
            self._options.get("inputpattern2", "-syll")        # syllables
        ]

    # -----------------------------------------------------------------------

    @staticmethod
    def get_input_extensions():
        """Extensions that the annotation expects for its input filename."""
        return [
            sppasFiles.get_informat_extensions("ANNOT_ANNOT"),
            sppasFiles.get_informat_extensions("ANNOT_ANNOT")
        ]

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __filter_file(self, formants_filename: str, syll_filename: str) -> str:
        """Filter the formant values of a file and save the result.

        The distributions are estimated on all the files of the corpus, so
        that a file can't be filtered independently of the others.

        :param formants_filename: (str) Name of a file with formant values
        :param syll_filename: (str) Name of a file with syllables, or None
        :return: (str) Name of the created file

        """
        _pairs, _syll_tier = self.__read_tiers(formants_filename, syll_filename)

        _trs_output = sppasTranscription(self.name)
        _trs_output.set_meta('annotation_result_of', formants_filename)

        for tier_f1, tier_f2 in _pairs:
            _tiers = self.__filter.filter(tier_f1, tier_f2, _syll_tier)
            for filtered_tier in _tiers:
                _trs_output.append(filtered_tier)

            self.logfile.print_message(
                "{:s}: filtered {:d} formant values among {:d}."
                "".format(tier_f1.get_name(), self.__filter.get_nb_filtered(),
                          self.__filter.get_nb_values()),
                indent=2, status=annots.info)

        _output_file = self.fix_out_file_ext(self.get_out_name(formants_filename))
        _parser = sppasTrsRW(_output_file)
        _parser.write(_trs_output)

        return _output_file

    # -----------------------------------------------------------------------

    @staticmethod
    def __read_tiers(formants_filename: str, syll_filename: str) -> tuple:
        """Return the tiers with formant values and the one with syllables.

        :param formants_filename: (str) Name of a file with formant values
        :param syll_filename: (str) Name of a file with syllables, or None
        :raises: NoTierInputError: A tier with formant values is missing
        :return: (list, sppasTier) Pairs of F1/F2 tiers and syllables tier

        """
        _parser = sppasTrsRW(formants_filename)
        _trs_input = _parser.read()

        _pairs = sppasVowelFilter.__get_formant_pairs(_trs_input)
        if len(_pairs) == 0:
            logging.error("No tier with formant values found in {:s}."
                          "".format(formants_filename))
            raise NoTierInputError

        return _pairs, sppasVowelFilter.__read_syll_tier(syll_filename)

    # -----------------------------------------------------------------------

    @staticmethod
    def __get_formant_pairs(trs) -> list:
        """Return the pairs of F1/F2 tiers to be filtered, one of each method.

        The F1 and F2 tiers are storing the values of all the methods into
        alternative tags of a single label, so that a value can't be assigned
        to the method it comes from: they are used only if the Formants
        annotation enabled one method, i.e. if it didn't create a tier for
        each of them.

        :param trs: (sppasTranscription) The read formant values
        :return: (list) List of (F1 tier, F2 tier)

        """
        _pairs = list()
        for tier in trs:
            _name = tier.get_name()
            if _name.startswith("F1-") is False:
                continue
            _tier_f2 = trs.find("F2-" + _name[3:], case_sensitive=False)
            if _tier_f2 is not None:
                _pairs.append((tier, _tier_f2))

        if len(_pairs) == 0:
            _tier_f1 = sppasFindTier.formants(trs, "F1")
            _tier_f2 = sppasFindTier.formants(trs, "F2")
            if _tier_f1 is not None and _tier_f2 is not None:
                _pairs.append((_tier_f1, _tier_f2))

        return _pairs

    # -----------------------------------------------------------------------

    @staticmethod
    def __read_syll_tier(syll_filename: str) -> sppasTier:
        """Return the tier with time-aligned syllables of a file.

        :param syll_filename: (str) Name of a file with syllables, or None
        :return: (sppasTier|None)

        """
        if syll_filename is None:
            return None

        _parser = sppasTrsRW(syll_filename)
        _trs_syll = _parser.read()
        _syll_tier = sppasFindTier.aligned_syllables(_trs_syll)
        if _syll_tier is None:
            logging.warning("No tier with time-aligned syllables in {:s}. The "
                            "position of the vowels is ignored.".format(syll_filename))

        return _syll_tier
