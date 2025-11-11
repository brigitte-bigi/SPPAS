"""
:filename: sppas.src.annotations.Align.aligners.basicalign.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  An aligner to set the same duration to each sound.

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

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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

from sppas.core.config import separators

from .basealigner import BaseAligner
from .alignerio import palign

# ---------------------------------------------------------------------------


class BasicAligner(BaseAligner):
    """Basic automatic alignment system.

    This segmentation assign the same duration to each phoneme.
    In case of phonetic variants, the first shortest pronunciation is
    selected.

    """

    def __init__(self, model_dir=None):
        """Create a BasicAligner instance.

        This class allows to align one unit assigning the same duration to
        each phoneme. It selects the shortest sequence in case of variants.

        :param model_dir: (str|None) Ignored.

        """
        super(BasicAligner, self).__init__()

        self._extensions = [palign().extension]
        self._outext = palign().extension
        self._name = "basic"

    # -----------------------------------------------------------------------

    def run_alignment(self, input_wav, output_align):
        """Perform the speech segmentation.

        Assign the same duration to each phoneme.

        :param input_wav: (str/float/None) audio input file name, or its duration, or None
        :param output_align: (str) the output file name
        :return: Empty string.

        """
        if input_wav is None:
            duration = 0.

        elif isinstance(input_wav, float) is True:
            duration = input_wav

        else:
            try:
                import audioopy.aio
                wav_speech = audioopy.aio.open(input_wav)
                duration = wav_speech.get_duration()
            except:
                duration = 0.

        self.run_basic(duration, output_align)

        return ""

    # ------------------------------------------------------------------------

    def run_basic(self, duration=None, output_align=None):
        """Perform the speech segmentation.

        Assign the same duration to each phoneme.

        :param duration: (float) the duration of the audio input
        :param output_align: (str) the output file name
        :return: the List of tuples (begin, end, phone)

        """
        # Remove variants:
        # Select the first-shorter pronunciation of each token
        phones_list = []
        phonetization = self._phones.strip().split()
        tokenization = self._tokens.strip().split()
        select_phonetization = []
        delta = 0.
        for pron in phonetization:
            token = BasicAligner.select_shortest(pron)
            phones_list.extend(
                token.split(separators.phonemes))
            select_phonetization.append(
                token.replace(separators.phonemes, " "))

        # Estimate the duration of a phoneme (in centi-seconds) from
        # the given total duration
        if duration is None:
            return self.__gen_time_alignment(
                select_phonetization, tokenization, phones_list, output_align)

        else:
            if len(phones_list) > 0:
                delta = (duration / float(len(phones_list))) * 100.

            # Generate the time-aligned result
            if delta < 1. or len(select_phonetization) == 0:
                return self.__gen_index_alignment([],
                                                  [],
                                                  [],
                                                  int(duration*100.),
                                                  output_align)

            return self.__gen_index_alignment(select_phonetization,
                                              tokenization,
                                              phones_list,
                                              int(delta),
                                              output_align)

    # ------------------------------------------------------------------------
    # private
    # ------------------------------------------------------------------------

    def __gen_index_alignment(self, phonetization, tokenization, phoneslist, phonesdur, output_align=None):
        """Write an alignment in an output file with indexes for the localization.

        :param phonetization: (list) phonetization of each token
        :param tokenization: (list) each token
        :param phoneslist: (list) each phone
        :param phonesdur: (int) the duration of each phone in centi-seconds
        :param output_align: (str) the output file name

        """
        timeval = 0
        alignments = []
        for phon in phoneslist:
            tv1 = timeval
            tv2 = timeval + phonesdur - 1
            alignments.append((tv1, tv2, phon))
            timeval = tv2 + 1

        if len(alignments) == 0:
            alignments = [(0, int(phonesdur), "")]

        self.__write_alignments(phonetization, tokenization, alignments, output_align)
        return alignments

    # ------------------------------------------------------------------------

    def __gen_time_alignment(self, phonetization, tokenization, phoneslist, output_align=None):
        """Write an alignment in an output file with faked time values.

        :param phonetization: (list) phonetization of each token
        :param tokenization: (list) each token
        :param phoneslist: (list) each phone
        :param output_align: (str) the output file name

        """
        time_value_start = 0.
        alignments = []
        for phon in phoneslist:
            time_value_end = time_value_start + self.__get_phoneme_duration(phon)
            alignments.append((time_value_start, time_value_end, phon))
            time_value_start = time_value_end

        if len(alignments) == 0:
            alignments = [(0., 0., "")]

        self.__write_alignments(phonetization, tokenization, alignments, output_align)
        return alignments

    # ------------------------------------------------------------------------

    def __write_alignments(self, phonetization, tokenization, alignments, output_align):
        """Write an alignment in an output file."""
        if output_align is not None:
            output_align = output_align + "." + self._outext
            palign().write(phonetization, tokenization, alignments, output_align)

    # ------------------------------------------------------------------------

    @staticmethod
    def select_shortest(pron):
        """Return the first of the shortest pronunciations of an entry.

        :param pron: (str) The phonetization of a token
        :return: (str) pronunciation

        """
        if len(pron) == 0:
            return ""

        tab = pron.split(separators.variants)
        if len(tab) == 1:
            return pron.strip()

        i = 0
        m = len(tab[0].strip())
        for n, p in enumerate(tab):
            if len(p.strip()) < m:
                i = n
                m = len(p.strip())

        return tab[i].strip()

    # ------------------------------------------------------------------------

    @staticmethod
    def __get_phoneme_duration(pron):
        """Get the duration of a phoneme.

        :param pron: (str) Representation of a phoneme.
        :return: (float) duration

        """
        if pron in ("#", "@", "+", "sp", "sil", "dummy", "noise", "laugh"):
            return 0.5

        return 0.12
