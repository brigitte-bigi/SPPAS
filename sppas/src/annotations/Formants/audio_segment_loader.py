"""
:filename: sppas.src.annotations.Formants.audio_segment_loader.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Extract, convert, and validate audio segments from a reader.

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

from audioopy import AudioPCM

from sppas.src.annotations.Formants.audio_processing_pipeline import AudioProcessingPipeline

# ---------------------------------------------------------------------------


class SegmentLoader:
    """Extract and process audio segments using a pipeline.

    This class loads a segment of raw frames from an audio stream,
    applies a pipeline of processing steps, and optionally filters
    out segments that are too quiet.

    :example:
    >>> loader = SegmentLoader(audio_reader, pipeline)
    >>> result = loader.load(1.0, 1.05, rms_threshold=0)
    >>> if result is not None:
    >>>     signal, sr = result

    """

    def __init__(self, audio_reader: AudioPCM, pipeline: AudioProcessingPipeline):
        """Initialize the segment loader.

        :param audio_reader: (object) Open audio file with read/seek interface.
        :param pipeline: (AudioPipeline) Configured processing steps.
        :raises: TypeError: On invalid arguments.

        """
        if not hasattr(audio_reader, "seek") or not hasattr(audio_reader, "read_frames"):
            raise TypeError("audio_reader must implement seek() and read_frames().")

        if isinstance(pipeline, AudioProcessingPipeline) is False:
            raise TypeError("pipeline must be an instance of AudioPipeline or a subclass of AudioPipeline.")

        self._reader = audio_reader
        self._pipeline = pipeline

    # -----------------------------------------------------------------------

    def load(self, start_time: float, end_time: float, rms_threshold: float = 0.):
        """Load and preprocess the segment, or return None if too silent.

        :param start_time: (float) Start of the segment in seconds.
        :param end_time: (float) End of the segment in seconds.
        :param rms_threshold: (float) Minimum RMS to consider the segment usable.
        :return: (signal, sr, rms) or None if segment is silent.

        """
        # Extract segment from channel
        _frames, framerate = self.extract_segment(start_time, end_time)

        # Run pipeline
        signal, sr, rms = self._pipeline.run(_frames, self._reader.get_sampwidth(), framerate)

        return (signal, sr) if rms > rms_threshold else None

    # -----------------------------------------------------------------------

    def extract_segment(self, start_time: float, end_time: float):
        """Extract a signal segment from an AudioPCM-compatible object.

        :param start_time: Start time in seconds.
        :param end_time: End time in seconds.
        :return: A tuple (frames, sample_rate)

        """
        # Compute sample indices
        framerate = self._reader.get_framerate()
        start_frame = int(start_time * framerate)
        end_frame = int(end_time * framerate)

        # Read raw frames
        self._reader.seek(start_frame)
        nframes = end_frame - start_frame
        frames = self._reader.read_frames(nframes)

        return frames, framerate

