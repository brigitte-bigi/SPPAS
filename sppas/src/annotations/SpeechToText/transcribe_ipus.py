# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.SpeechToText.transcribe_ipus.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Match IPUs and orthographic transcription.

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

from __future__ import annotations
import os
import shutil
import audioopy.aio
from audioopy import AudioPCM

from sppas.src.utils import sppasFileUtils
from sppas.src.anndata.anndataexc import AnnDataTypeError
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata.aio.aioutils import serialize_labels
from sppas.src.annotations.annotationsexc import EmptyInputError
from sppas.src.annotations.annotationsexc import NoChannelInputError
from sppas.src.annotations.annotationsexc import AudioChannelError
from sppas.src.annotations import sppasFindTier
from sppas.src.annotations import sppasSearchIPUs
from sppas.src.annotations import sppasFillIPUs
from sppas.src.annotations import sppasFiles

from .whisper import WhisperSTT

# ---------------------------------------------------------------------------


class WhisperSTTonIPUs(object):
    """Prepare the data to be used by SPPAS automatic segmentation.

    """

    def __init__(self, language: str | None = None):
        """Create a SPPAS Automatic IPUs segmentation.

        """
        # One of them is used to segment speech:
        self.__ann_fillipus = sppasFillIPUs(log=None)
        self.__ann_searchipus = sppasSearchIPUs(log=None)
        # the following parameter is language dependent (at least 0.200 for
        # French, or 0.250 for English). Default is 0.200:
        self.__ann_searchipus.set_min_sil(0.400)
        # the following parameters depend on the audio quality (the worse,
        # the higher). Default is 0.020:
        self.__ann_searchipus.set_shift_start(0.040)
        self.__ann_searchipus.set_shift_end(0.040)

        # Instantiate STT systems
        self._whisper = WhisperSTT(model="base", language=language)

    # -----------------------------------------------------------------------

    def get_inputs(self, input_files):
        """Return the audio channel, the tier with IPUs.

        :param input_files: (list)
        :raise: NoTierInputError
        :return: (Channel, sppasTier)

        """
        # Get the tier and the channel
        audio_ext = sppasFiles.get_outformat_extensions("AUDIO")
        annot_ext = sppasFiles.get_outformat_extensions("ANNOT")
        tier = None
        channel = None
        audio_filename = ""
        for filename in input_files:
            if filename is None:
                continue
            if os.path.isdir(filename):
                continue

            fn, fe = os.path.splitext(filename)

            if channel is None and fe in audio_ext:
                audio_speech = audioopy.aio.open(filename)
                n = audio_speech.get_nchannels()
                if n != 1:
                    audio_speech.close()
                    raise AudioChannelError(n)
                idx = audio_speech.extract_channel()
                channel = audio_speech.get_channel(idx)
                audio_filename = filename
                audio_speech.close()

            elif tier is None and fe in annot_ext:
                parser = sppasTrsRW(filename)
                trs_input = parser.read()
                # a raw transcription or an already aligned one is expected.
                tier = sppasFindTier.transcription(trs_input)

        # Check input tier
        if tier is not None:

            if "raw" in tier.get_name().lower() and tier.is_point() is False:
                raise AnnDataTypeError(tier.get_name(), 'PointTier')
            if tier.is_empty() is True:
                raise EmptyInputError(tier.get_name())

            # Check input channel
            if channel is None:
                raise NoChannelInputError

            # Set the media to the input tier
            extm = os.path.splitext(audio_filename)[1].lower()[1:]
            media = sppasMedia(os.path.abspath(audio_filename), mime_type="audio/"+extm)
            tier.set_media(media)

        return channel, tier

    # -----------------------------------------------------------------------

    def ipussegments(self, input_files):
        """Perform IPUs segmentation fully automatically.

        :param input_files: List of required and optional input files (audio + text)
        :return: (sppasTier)
        :raises: IOError: Whisper not enabled

        """
        input_channel, input_tier = self.get_inputs(input_files)

        if input_tier is None:
            # search for the IPUs and execute STT on each one
            if self._whisper.enabled is False:
                raise IOError("No transcription is given and Whisper STT system is not enabled.")
            return self.__do_search_and_stt(input_channel)

        elif "raw" in input_tier.get_name().lower():
            # fill in the IPUs with the orthographic transcription
            return self.__ann_fillipus.convert(input_channel, input_tier)

        else:
            return input_tier

    # -----------------------------------------------------------------------

    def __do_search_and_stt(self, input_channel):
        """Search for IPUs and transcribe with a STT.

        """
        tier = self.__ann_searchipus.convert(input_channel)
        tier.set_name("TransSTT")
        framerate = input_channel.get_framerate()
        duration = input_channel.get_duration()

        # -----------------------------------------------------------------------
        # Split the audio file into IPUs and transcribe automatically
        # -----------------------------------------------------------------------
        # Create a working directory
        working_dir = sppasFileUtils().set_random()
        os.mkdir(working_dir)

        # Browse through the IPUs in order to create its ortho transcription
        for i, ann in enumerate(tier):

            # is an IPU?
            text = serialize_labels(ann.get_labels(), separator="_", empty="", alt=False)
            if len(text) == 0 or ann.get_best_tag().is_silence():
                continue

            # get localization information
            begin = ann.get_lowest_localization().get_midpoint()
            begin = max(0, begin - 0.1)
            end = ann.get_highest_localization().get_midpoint()

            # create audio output of the IPU
            fn_i = os.path.join(working_dir, "ipu_{:04d}.wav".format(i+1))
            extracter = input_channel.extract_fragment(int(begin*framerate), int(end*framerate))
            audio_out = AudioPCM()
            audio_out.append_channel(extracter)
            audioopy.aio.save(fn_i, audio_out)

            # Launch STT on the given IPU audio file
            # =======================================
            tags = list()
            if self._whisper.enabled is True:
                txt = self._whisper.transcribe(fn_i)
                tags.append(sppasTag(txt))
            ann.append_label(sppasLabel(tags))

        # Make some cleaning: delete the working dir
        shutil.rmtree(working_dir)

        return tier
