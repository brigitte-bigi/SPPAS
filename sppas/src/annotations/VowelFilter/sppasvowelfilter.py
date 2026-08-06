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
    Lancien et al. (2023).

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
        if len(self._options) > 0:
            self.print_options()

        if len(file_names) == 0:
            return list()
        if progress:
            progress.update(0, "")

        # First pass: collect the features of the vowels of all the files.
        self.__filter = VowelFilterEstimator(self._options['threshold'])
        all_inputs = list()
        for input_files in file_names:
            try:
                inputs = self._fix_inputs(input_files)
                formants_filename, syll_filename = self.get_inputs(inputs)
            except Exception as e:
                logging.critical(str(e))
                continue

            self.print_diagnosis(*inputs)
            try:
                tier_f1, tier_f2, syll_tier = self.__read_tiers(formants_filename, syll_filename)
                self.__filter.collect(tier_f1, tier_f2, syll_tier)
            except Exception as e:
                self.logfile.print_message(str(e), indent=2, status=annots.error)
                continue
            all_inputs.append((formants_filename, syll_filename))

        # Estimate the distributions the filtering is based on.
        nb_profiles = self.__filter.estimate()
        self.logfile.print_message(
            "Estimated {:d} distributions of {:d} vowel classes."
            "".format(nb_profiles, len(self.__filter.get_class_names())),
            indent=1, status=annots.info)
        self.logfile.print_newline()

        # Second pass: filter each file with the estimated distributions.
        files_processed_success = list()
        for i, (formants_filename, syll_filename) in enumerate(all_inputs):
            if progress:
                progress.set_fraction(round(float(i)/float(len(all_inputs)), 2))
                progress.set_text(os.path.basename(formants_filename))

            self.print_filename(formants_filename)
            try:
                out_name = self.__filter_file(formants_filename, syll_filename)
            except Exception as e:
                self.logfile.print_message(str(e), indent=2, status=annots.error)
            else:
                files_processed_success.append(out_name)
                self.logfile.print_message(out_name, indent=1, status=annots.ok)
            self.logfile.print_newline()

        if progress:
            progress.update(1, "")

        return files_processed_success

    # -----------------------------------------------------------------------

    def get_inputs(self, input_files: list) -> tuple:
        """Return the filename with formants and the one with syllables.

        :param input_files: (list) The inputs of a file root
        :raises: NoTierInputError: No file with formant values
        :return: (str, str) Formants filename and syllables filename or None

        """
        patterns = self.get_input_patterns()
        formants_filename = None
        syll_filename = None

        for filename in input_files:
            fn, _ = os.path.splitext(filename)
            if formants_filename is None and fn.endswith(patterns[0]) is True:
                formants_filename = filename
            elif syll_filename is None and len(patterns[1]) > 0 and fn.endswith(patterns[1]) is True:
                syll_filename = filename

        if formants_filename is None:
            logging.error("No file with formant values, i.e. with pattern '{:s}'."
                          "".format(patterns[0]))
            raise NoTierInputError

        if self._options['coda'] is False:
            return formants_filename, None

        return formants_filename, syll_filename

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
        tier_f1, tier_f2, syll_tier = self.__read_tiers(formants_filename, syll_filename)
        new_f1, new_f2, distances_tier = self.__filter.filter(tier_f1, tier_f2, syll_tier)

        self.logfile.print_message(
            "Filtered {:d} formant values among {:d}."
            "".format(self.__filter.get_nb_filtered(), self.__filter.get_nb_values()),
            indent=2, status=annots.info)

        trs_output = sppasTranscription(self.name)
        trs_output.set_meta('annotation_result_of', formants_filename)
        trs_output.append(new_f1)
        trs_output.append(new_f2)
        trs_output.append(distances_tier)

        output_file = self.fix_out_file_ext(self.get_out_name(formants_filename))
        parser = sppasTrsRW(output_file)
        parser.write(trs_output)

        return output_file

    # -----------------------------------------------------------------------

    @staticmethod
    def __read_tiers(formants_filename: str, syll_filename: str) -> tuple:
        """Return the tiers with formant values and the one with syllables.

        :param formants_filename: (str) Name of a file with formant values
        :param syll_filename: (str) Name of a file with syllables, or None
        :raises: NoTierInputError: A tier with formant values is missing
        :return: (sppasTier, sppasTier, sppasTier)

        """
        parser = sppasTrsRW(formants_filename)
        trs_input = parser.read()

        tier_f1 = sppasFindTier.formants(trs_input, "F1")
        tier_f2 = sppasFindTier.formants(trs_input, "F2")
        if tier_f1 is None or tier_f2 is None:
            logging.error("Tiers with names 'F1' and 'F2' not found in {:s}."
                          "".format(formants_filename))
            raise NoTierInputError

        if syll_filename is None:
            return tier_f1, tier_f2, None

        parser = sppasTrsRW(syll_filename)
        trs_syll = parser.read()
        syll_tier = sppasFindTier.aligned_syllables(trs_syll)
        if syll_tier is None:
            logging.warning("No tier with time-aligned syllables in {:s}. The "
                            "position of the vowels is ignored.".format(syll_filename))

        return tier_f1, tier_f2, syll_tier
