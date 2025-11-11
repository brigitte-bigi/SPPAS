# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.annotations.Anonym.anonymaudio.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Anonymization of segments of a channel.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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

import random
from audioopy.channel import Channel
from audioopy.channelformatter import ChannelFormatter
from audioopy.audioframes import AudioFrames
from audioopy.audioconvert import AudioConverter

from sppas.src.calculus import fmean

# ----------------------------------------------------------------------------


class ChannelAnonymizer(ChannelFormatter):
    """Anonymize segments of a channel of an audio stream.

    """
    # 10ms of "m" sampled at 16,000Hz, so 160 sample values
    HUM_SAMPLES = [-286, -283, -256, -193, -73, 119, 374, 654, 909, 1102,
                   1220, 1272, 1272, 1234, 1171, 1090, 998, 901, 802, 707,
                   618, 535, 459, 384, 297, 184, 41, -123, -284, -416,
                   -502, -532, -508, -438, -333, -204, -60, 89, 232, 363,
                   475, 563, 624, 660, 679, 692, 709, 734, 762, 783,
                   785, 759, 700, 611, 496, 362, 218, 74, -63, -184,
                   -281, -349, -384, -386, -359, -311, -252, -192, -136, -84,
                   -34, 20, 80, 149, 226, 310, 395, 477, 551, 610,
                   650, 667, 656, 617, 552, 466, 367, 264, 165, 77,
                   2, -61, -112, -154, -189, -218, -242, -259, -269, -271,
                   -262, -239, -202, -149, -80, 1, 89, 179, 264, 337,
                   394, 433, 453, 455, 444, 420, 387, 349, 307, 262,
                   215, 167, 117, 65, 10, -48, -105, -161, -209, -248,
                   -273, -281, -273, -246, -192, -96, 64, 292, 564, 833,
                   1055, 1205, 1282, 1299, 1273, 1217, 1140, 1048, 948, 844,
                   740, 640, 546, 460, 380, 296, 197, 70, -81, -241]

    def __init__(self, channel):
        """Create a ChannelAnonymizer instance.

        :param channel: (Channel) The channel to work on.

        """
        super(ChannelAnonymizer, self).__init__(channel)
        self._mm = ChannelAnonymizer.HUM_SAMPLES

        # The mm sample is width=2, rate=16000Hz.
        # Re-sample its frames to match the channel width et rate.
        if channel.get_framerate() != 16000 or channel.get_sampwidth != 2:
            # Turn samples into frames
            frames = AudioConverter().samples2frames([ChannelAnonymizer.HUM_SAMPLES], 2, nchannels=1)
            # Change sample width of mm
            if channel.get_sampwidth() != 2:
                frames = AudioFrames(frames, 2, nchannels=1).change_sampwidth(channel.get_sampwidth())
            # Change rate of mm
            if channel.get_framerate() != 16000:
                frames = AudioFrames(frames, channel.get_sampwidth(), nchannels=1).resample(16000, channel.get_framerate())
            # Get samples back
            self._mm = AudioConverter().unpack_data(frames, channel.get_sampwidth(), nchannels=1)[0]

        # Estimate average values in "m" signal
        pos_mm = list()
        neg_mm = list()
        for value in self._mm:
            if value > 0.:
                pos_mm.append(value)
            else:
                neg_mm.append(value)
        self.__avg_pos_mm = fmean(pos_mm)
        self.__avg_neg_mm = fmean(neg_mm)

    # -----------------------------------------------------------------------

    def ianonymize(self, segments):
        """Anonymize the channel into the given time intervals (in seconds).

        :param segments: (list of tuples) List of (start time, end time) time values

        """
        # Frames of the non-anonymized channel
        frames = self._channel.get_frames()
        # index of the lastly added frame into the newly anonymized frames
        prev = 0
        new_frames = b""

        for i in range(len(segments)):
            # Segment begin time and segment end time
            sbt, set = segments[i]
            duration = set - sbt
            # Turn time values into index of frame
            sbf = int(sbt * self._framerate * self._sampwidth)
            rest = sbf % self._sampwidth
            sbf = sbf - rest
            sef = int(set * self._framerate * self._sampwidth)
            rest = sef % self._sampwidth
            sef = sef - rest

            # A non-anonymized segment in the hole
            if sbf > prev:
                new_frames += frames[prev:sbf]

            # Anonymize the frames into the segment
            sgmt_frames = frames[sbf:sef]

            # Turn frames into samples
            samples_all = AudioConverter().unpack_data(sgmt_frames, self._sampwidth, nchannels=1)
            samples = samples_all[0]
            # Make the samples anonymized
            self.mm_samples(samples)
            # Turn anonymized samples into frames
            anon_frames = AudioConverter().samples2frames([samples], self._sampwidth, nchannels=1)
            assert len(anon_frames) == len(sgmt_frames)

            # Set the anonymized segment to the new frames
            new_frames += anon_frames
            # prepare next round
            prev = sef

        # end
        if prev < len(frames):
            new_frames += frames[prev:]

        return Channel(self._framerate, self._sampwidth, new_frames)

    # -----------------------------------------------------------------------

    def mm_samples(self, samples):
        """Turn the samples into a sequence of "m" by preserving intensity.

        :param samples: (list of int)
        :return: (None)

        """
        i = len(self._mm)
        while i < len(samples):
            current = samples[i-len(self._mm):i]
            max_sample = max(current)
            min_sample = min(current)

            # Extract positive values and negative values
            pos_samples = list()
            neg_samples = list()
            for value in current:
                if value > 0.:
                    pos_samples.append(value)
                else:
                    neg_samples.append(value)

            # Estimate average of each set of values
            pos_mean = fmean(pos_samples)
            neg_mean = fmean(neg_samples)
            sampmm = self.mul_mm(pos_avg_amp=pos_mean, neg_avg_amp=neg_mean)

            for c, value in enumerate(self._mm):
                if value > 0:
                    new_value = int((sampmm[c] + pos_mean) / 2.)
                    current[c] = min(max_sample, new_value)
                else:
                    new_value = int((sampmm[c] + neg_mean) / 2.)
                    current[c] = max(min_sample, new_value)

            samples[i-len(self._mm):i] = current
            i = i + len(self._mm)

    # -----------------------------------------------------------------------

    def mul_mm(self, pos_avg_amp, neg_avg_amp):
        """Return "m" samples adapted to the given average amplitudes.

        :param pos_avg_amp: (float) Expected average of the positive samples value
        :param neg_avg_amp: (float) Expected average of the negative samples value
        :return: (list of int)

        """
        coeff_pos = self.__avg_pos_mm / pos_avg_amp
        coeff_neg = self.__avg_neg_mm / neg_avg_amp
        mm_amp = list()
        for c, value in enumerate(self._mm):
            if value > 0:
                mm_amp.append(int(self._mm[c] / coeff_pos))
            else:
                mm_amp.append(int(self._mm[c] / coeff_neg))

        return mm_amp

    # -----------------------------------------------------------------------

    @staticmethod
    def noise_samples_by_shuffle1(samples, duration):
        """Turn the sample into noises by preserving the intensity.

        :param samples: (list of int)
        :param duration: (float) Duration of the samples, in seconds.
        :return: (None)

        """
        # 1st pass: multiply intensity by an intensity factor
        for i, value in enumerate(samples):
            samples[i] = int(float(value) * 0.9)

        # Nb of step if we consider a step is 10ms
        nb_steps = int(duration * 100.)
        nb_samples_in_step = int(len(samples) / nb_steps)
        i = 0
        while i <= nb_steps:
            # randomize the list of samples of this part
            k = nb_samples_in_step
            if ((i + 1) * nb_samples_in_step) > len(samples):
                k = len(samples) - (i * nb_samples_in_step)
            samples[i * nb_samples_in_step:(i + 1) * nb_samples_in_step] = random.sample(
                samples[i * nb_samples_in_step:(i + 1) * nb_samples_in_step], k)
            i += 1

    # -----------------------------------------------------------------------

    @staticmethod
    def noise_samples_by_shuffle2(samples, duration):
        """Makes anonymized samples by preserving the intensity.

        :param samples: (list of int)
        :param duration: (float) Duration of the samples, in seconds.
        :return: (None)

        """
        # 1st pass: multiply intensity by an intensity factor
        for i, value in enumerate(samples):
            samples[i] = int(float(value) * 0.9)

        # Nb of step if we consider a step is 10ms
        nb_steps = int(duration * 100.)
        nb_samples_in_step = int(len(samples) / nb_steps)
        i = 0
        while i <= nb_steps:
            # randomize the list of samples of this part
            k = nb_samples_in_step
            if ((i + 1) * nb_samples_in_step) > len(samples):
                k = len(samples) - (i * nb_samples_in_step)
            # Extract positive values and negative values
            pos_samples = list()
            neg_samples = list()
            for value in samples[i * nb_samples_in_step:(i + 1) * nb_samples_in_step]:
                if value > 0.:
                    pos_samples.append(value)
                else:
                    neg_samples.append(value)
            # Shuffle each list
            random.shuffle(pos_samples)
            random.shuffle(neg_samples)
            p = len(pos_samples) - 1
            n = len(neg_samples) - 1
            # Set randomized values to the samples
            for idx in range(k):
                if samples[(i * nb_samples_in_step) + idx] > 0:
                    samples[(i * nb_samples_in_step) + idx] = pos_samples[p]
                    p = p - 1
                else:
                    samples[(i * nb_samples_in_step) + idx] = neg_samples[n]
                    n = n - 1
            i = i + 1
