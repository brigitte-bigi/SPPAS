# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.aio.subtitle.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Input/Output of subtitles formats (.sub, .srt...).

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

SubViewer is a utility for adding and synchronizing subtitles to video
content. It was created by David Dolinski in 1999.
Precision in time is 10ms.

SubRip is a free software program for Windows which "rips" (extracts)
subtitles and their timings from video. It is free software, released
under the GNU AGPL. SubRip is also the name of the widely used and broadly
compatible subtitle text file format created by this software.
Precision in time is 1ms.

WebVTT (Web Video Text Tracks) is a World Wide Web Consortium (W3C) standard
for displaying timed text in connection with the HTML5 <track> element.
Main differences from SubRip are:
 - WebVTT's first line starts with WEBVTT after the optional UTF-8 byte order mark
 - There is space for optional header data between the first line and the first cue
 - Timecode fractional values are separated by a full stop instead of a comma
 - Timecode hours are optional
 - The frame numbering/identification preceding the timecode is optional
 - Comments identified by the word NOTE can be added
 - Metadata information can be added in a JSON-style format
 - Chapter information can be optionally specified
 - Only supports extended characters as UTF-8
 - CSS in a separate file defined in the companion HTML document for C tags is used instead of the FONT tag
 - Cue settings allow the customization of cue positioning on the video

LRC is a plain-text format created for the karaoke display of song lyrics,
associating a "[mm:ss.xx]" timestamp to each line. Its "enhanced" (A2)
extension adds a "<mm:ss.xx>" timestamp before each word, for a word by
word synchronization. LRC has no notion of an "end" time: only a begin is
given, for a line and optionally for each of its words.
Main differences from SubRip:
 - the timestamp precision is the hundredth of a second, with no hour part
 - a single timestamp is given per line/word, there is no "end" time
 - optional header tags ([ar:], [ti:], [al:], [by:], [offset:]) give the
   artist, title, album, creator and a timing offset of the song

"""

import codecs
import datetime
import re

from sppas.core.config import sg
from sppas.core.coreutils import b

from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioMultiTiersError
from ..anndataexc import AioFormatError
from ..ann.annotation import sppasAnnotation
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval

from .aioutils import format_labels
from .aioutils import serialize_labels
from .basetrsio import sppasBaseIO

# ---------------------------------------------------------------------------


class sppasBaseSubtitles(sppasBaseIO):
    """SPPAS base class for subtitle formats.

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseSubtitles instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasBaseSubtitles, self).__init__(name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = True
        self._accept_empty_tier = False
        self._accept_metadata = False
        self._accept_comments = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_time(time_string):
        """Convert a time in "%H:%M:%S,%m" format into seconds."""
        time_string = time_string.strip()
        dt = (datetime.datetime.strptime(time_string, '%H:%M:%S,%f') -
              datetime.datetime.strptime('', ''))
        return dt.total_seconds()

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_time(second_count: int) -> str:
        """Convert a time in seconds into "%H:%M:%S,%f" format.

        :param second_count: (int) Seconds to convert.
        :return: (str) Formatted time in "%H:%M:%S,%f" format.

        """
        dt = datetime.datetime.utcfromtimestamp(second_count)
        return dt.strftime('%H:%M:%S,%f')[:-3]

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """In subtitles, the localization is a time value, so a float."""
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")
        return sppasPoint(midpoint, radius=0.02)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_text(text):
        """Remove HTML tags, etc."""
        text = text.replace('<b>', '')
        text = text.replace('<B>', '')
        text = text.replace('</b>', '')
        text = text.replace('</B>', '')

        text = text.replace('<i>', '')
        text = text.replace('<I>', '')
        text = text.replace('</i>', '')
        text = text.replace('</I>', '')

        text = text.replace('<u>', '')
        text = text.replace('<U>', '')
        text = text.replace('</u>', '')
        text = text.replace('</U>', '')

        text = text.replace('<font>', '')
        text = text.replace('<FONT>', '')
        text = text.replace('</font>', '')
        text = text.replace('</FONT>', '')

        text = text.replace('[br]', '\n')

        return text

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_location(ann, precision=3):
        """Extract location to serialize the timestamps.

        :param ann: (sppasAnnotation)
        :param precision: (int) precision in time (expected value is 2 or 3)

        """
        if ann.location_is_point() is False:
            begin = sppasBaseSubtitles._format_time(
                round(ann.get_lowest_localization().get_midpoint(),
                      precision))
            end = sppasBaseSubtitles._format_time(
                round(ann.get_highest_localization().get_midpoint(),
                      precision))

        else:
            # SubRip does not support point based annotation
            # so we'll make a 1 second subtitle
            begin = sppasBaseSubtitles._format_time(
                round(ann.get_lowest_localization().get_midpoint(),
                      precision))
            end = sppasBaseSubtitles._format_time(
                round(ann.get_highest_localization().get_midpoint(),
                      precision) + 1.)

        return '{:s} --> {:s}\n'.format(begin, end)

    # -----------------------------------------------------------------------

    @staticmethod
    def _is_silence(ann):
        """Return True if the best tag of the annotation is a silence.

        :param ann: (sppasAnnotation) The annotation to be evaluated.
        :return: (bool) True if the best tag of the annotation is a silence.

        """
        return ann.get_best_tag().is_silence()

# ---------------------------------------------------------------------------


class sppasSubRip(sppasBaseSubtitles):
    """SPPAS reader/writer for SRT format.

    The SubRip text file format (SRT) is used by the SubRip program to save
    subtitles ripped from video files or DVDs.
    It is free software, released under the GNU AGPL.

    Each subtitle is represented as a group of lines. Subtitles are separated
    subtitles by a blank line.

        - first line of a subtitle is an index (starting from 1);
        - the second line is a timestamp interval,
          in the format %H:%M:%S,%m and the start and end of
          the range separated by -->;
        - optionally: a specific positioning by pixels, in the form
          X1:number Y1:number X2:number Y2:number;
        - the third line is the label.
          The HTML <b>, <i>, <u>, and <font> tags are allowed.

    """

    def __init__(self, name=None):
        """Initialize a new sppasSubRip instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSubRip, self).__init__(name)

        self.default_extension = "srt"
        self.software = "SubRip"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a SRT file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()

        tier = self.create_tier('Trans-SubRip')

        # Ignore BOM
        if b(lines[0]).startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][1:]

        # Ignore an optional header (or blank lines)
        i = 0
        while sppasBaseIO.is_number(lines[i].strip()[0:1]) is False:
            i += 1

        # Content of the file
        while i < len(lines):
            ann_lines = list()
            while i < len(lines) and lines[i].strip() != '':
                ann_lines.append(lines[i].strip())
                i += 1
            a = sppasSubRip._parse_subtitle(ann_lines)
            if a is not None:
                tier.append(a)
            i += 1

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """Parse a single subtitle.

        The subtitle can be written on several lines. In this case, one
        sppasLabel() is created for each line.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 3:
            return None

        # time stamps
        start, stop = map(sppasBaseSubtitles._parse_time,
                          lines[1].split('-->'))
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # create the annotation without label
        a = sppasAnnotation(sppasLocation(time))

        # optional position (in pixels), saved as metadata of the annotation
        if 'X1' in lines[2] and 'Y1' in lines[2]:
            # parse position: X1:number Y1:number X2:number Y2:number
            positions = lines[2].split(" ")
            for position in positions:
                coord, value = position.split(':')
                a.set_meta("position_pixel_"+coord, value)
            lines.pop(2)

        # labels
        text = ""
        for line in lines[2:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")
        if len(labels) > 0:
            a.set_labels(labels)

        return a

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubRip")

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            if self.is_empty() is False:
                number = 1
                last = len(self[0])
                for ann in self[0]:

                    text = serialize_labels(
                        ann.get_labels(), separator="\n", empty="", alt=True)

                    # no label defined, or empty label, or silence -> no subtitle!
                    if len(text) == 0 or sppasBaseSubtitles._is_silence(ann) is True:
                        continue

                    subtitle = ""
                    # first line: the number of the annotation
                    subtitle += str(number) + "\n"
                    # 2nd line: the timestamps
                    subtitle += sppasBaseSubtitles._serialize_location(
                        ann,
                        precision=3)
                    # 3rd line: optionally the position on screen
                    subtitle += sppasSubRip._serialize_metadata(ann)
                    # the text
                    subtitle += text + "\n"
                    if number < last:
                        # a blank line
                        subtitle += "\n"

                    # next!
                    fp.write(subtitle)
                    number += 1

            fp.close()

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_metadata(ann):
        """Extract metadata to serialize the position on screen."""
        text = ""
        if ann.is_meta_key("position_pixel_X1"):
            x1 = ann.get_meta("position_pixel_X1")
            if ann.is_meta_key("position_pixel_Y1"):
                y1 = ann.get_meta("position_pixel_Y1")
                if ann.is_meta_key("position_pixel_X2"):
                    x2 = ann.get_meta("position_pixel_X2")
                    if ann.is_meta_key("position_pixel_Y2"):
                        y2 = ann.get_meta("position_pixel_Y2")
                        text += "X1:{:s} Y1:{:s} X2:{:s} Y2:{:s}\n" \
                                "".format(x1, y1, x2, y2)
        return text

# ---------------------------------------------------------------------------


class sppasWebVTT(sppasBaseSubtitles):
    """SPPAS reader/writer for VTT format.

    ONLY THE WRITER IS IMPLEMENTED YET.

    """

    def __init__(self, name=None):
        """Initialize a new sppasWebVTT instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasWebVTT, self).__init__(name)

        self.default_extension = "vtt"
        self.software = "Subs for Web"

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        Not fully implemented.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("WebVTT")

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            if self.is_empty() is False:
                # Header
                fp.write("WEBVTT\n\n")
                # fp.write("WEBVTT Kind: captions; Language: en\n\n")

                number = 1
                last = len(self[0])
                for ann in self[0]:

                    text = serialize_labels(ann.get_labels(), separator=" ", empty="", alt=True)

                    # no label defined, or empty label, or silence -> no subtitle!
                    if len(text) == 0 or sppasBaseSubtitles._is_silence(ann) is True:
                        continue

                    subtitle = ""
                    # first line: the number of the annotation
                    subtitle += str(number) + "\n"
                    # 2nd line: the timestamps (WebVTT uses a full stop
                    # instead of a comma as the decimal separator)
                    subtitle += sppasBaseSubtitles._serialize_location(
                        ann,
                        precision=3).replace(",", ".")
                    # 3rd line: optionally the position on screen
                    # subtitle += sppasSubRip._serialize_metadata(ann)
                    # the text
                    subtitle += text + "\n"
                    if number < last:
                        # a blank line
                        subtitle += "\n"

                    # next!
                    fp.write(subtitle)
                    number += 1

            fp.close()

# ---------------------------------------------------------------------------


class sppasSubViewer(sppasBaseSubtitles):
    """SPPAS reader/writer for SUB format.

    The SubViewer text file format (SUB) is used by the SubViewer program to
    save subtitles of videos.

    """

    def __init__(self, name=None):
        """Initialize a new sppasBaseSubtitles instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasSubViewer, self).__init__(name)

        self.default_extension = "sub"
        self.software = "SubViewer"

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a SUB file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fp:
            lines = fp.readlines()
            fp.close()

        tier = self.create_tier('Trans-SubViewer')

        # Ignore BOM
        if b(lines[0]).startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][1:]

        # Header
        i = 0
        header_lines = list()
        while sppasBaseIO.is_number(lines[i].strip()[0:1]) is False:
            header_lines.append(lines[i].strip())
            i += 1
        self._parse_header(header_lines)

        # Content of the file
        while i < len(lines):
            ann_lines = list()
            while i < len(lines) and lines[i].strip() != '':
                ann_lines.append(lines[i].strip())
                i += 1
            a = sppasSubViewer._parse_subtitle(ann_lines)
            if a is not None:
                tier.append(a)
            i += 1

    # -----------------------------------------------------------------------

    def _parse_header(self, lines):
        """Parse the header lines to get metadata.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        for line in lines:
            if line.startswith('[TITLE]'):
                self.set_name(line[7:])
            elif line.startswith('[AUTHOR]'):
                self.set_meta('annotator_name', line[8:])
            elif line.startswith('[PRG]'):
                self.set_meta("prg_editor_name", line[4:])
            elif line.startswith('[FILEPATH]'):
                self.set_meta("file_path", line[:10])
            elif line.startswith('[DELAY]'):
                self.set_meta("media_shift_delay", line[:7])

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_subtitle(lines):
        """Parse a single subtitle.

        :param lines: (list) the lines of a subtitle (index, timestamps, label)

        """
        if len(lines) < 2:
            return None

        # time stamps
        time_stamp = lines[0].replace(",", " ")
        time_stamp = time_stamp.replace(".", ",")
        start, stop = map(sppasBaseSubtitles._parse_time, time_stamp.split())
        time = sppasInterval(sppasBaseSubtitles.make_point(start),
                             sppasBaseSubtitles.make_point(stop))

        # labels
        text = ""
        for line in lines[1:]:
            text += sppasBaseSubtitles._format_text(line) + "\n"
        labels = format_labels(text.rstrip(), separator="\n")

        return sppasAnnotation(sppasLocation(time), labels)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) != 1:
            raise AioMultiTiersError("SubViewer")

        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:

            fp.write(self._serialize_header())
            if self.is_empty() is False:
                for ann in self[0]:

                    text = serialize_labels(ann.get_labels(),
                                            separator="[br]", empty="", alt=True)

                    # no label defined, or empty label, or silence -> no subtitle!
                    if len(text) == 0 or sppasBaseSubtitles._is_silence(ann) is True:
                        continue

                    # the timestamps
                    subtitle = sppasBaseSubtitles._serialize_location(
                        ann,
                        precision=2)
                    subtitle = subtitle.replace(",", ".")
                    subtitle = subtitle.replace(" --> ", ",")
                    # the text
                    subtitle += text + "\n"
                    # a blank line
                    subtitle += "\n"

                    # next!
                    fp.write(subtitle)

            fp.close()

    # -----------------------------------------------------------------------

    def _serialize_header(self):
        """Convert metadata into an header.

        [INFORMATION]
        [TITLE]SubViewer file example
        [AUTHOR]FK
        [SOURCE]FK
        [PRG]gedit
        [FILEPATH]/extdata
        [DELAY]0
        [CD TRACK]0
        [COMMENT]
        [END INFORMATION]
        [SUBTITLE]
        [COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial

        """
        header = "[INFORMATION]"
        header += "\n"
        header += "[TITLE]"
        header += self.get_name()
        header += "\n"
        header += "[AUTHOR]"
        if self.is_meta_key("annotator_name"):
            header += self.get_meta("annotator_name")
        header += "\n"
        header += "[SOURCE]"
        header += "\n"
        header += "[PRG]"
        header += "\n"
        header += "[FILEPATH]"
        header += "\n"
        header += "[DELAY]"
        header += "\n"
        header += "[CD TRACK]"
        header += "\n"
        header += "[COMMENT]"
        header += "\n"
        header += "[END INFORMATION]"
        header += "\n"
        header += "[SUBTITLE]"
        header += "\n"
        header += "[COLF]&HFFFFFF,[STYLE]bd,[SIZE]18,[FONT]Arial"
        header += "\n"
        header += "\n"

        return header

# ---------------------------------------------------------------------------


class sppasLRC(sppasBaseSubtitles):
    """SPPAS reader/writer for LRC format (karaoke lyrics).

    LRC only gives a begin time -- for a line, and optionally for each of
    its words with the "enhanced"/A2 extension -- so it's turned into two
    hierarchized tiers:

        - "Tokens": one interval per word. Its begin is the word own
          timestamp; its end is either the middle between this timestamp
          and the next word's one, or 1 second later, whichever is the
          closest.
        - "Transcription": one interval per line, sharing its begin and
          end with the first and the last "Tokens" interval it's made of.

    Both tiers are linked with a "TimeAlignment" hierarchy, "Tokens" --
    the finer tier -- being the parent of "Transcription".

    A line with no word-level tag only feeds "Transcription" with the
    whole line text, and "Tokens" with a single interval -- sharing the
    line bounds -- made of one label per token, without any individual
    timestamp.

    """

    MAX_WORD_DURATION = 1.

    LINE_TAG = re.compile(r"^\[(\d{1,3}):(\d{2})[.,](\d{2,3})\](.*)$")
    WORD_TAG = re.compile(r"<(\d{1,3}):(\d{2})[.,](\d{2,3})>")
    HEADER_TAG = re.compile(r"^\[([a-zA-Z]+):\s*(.*)\]$")

    # Header tag -> metadata key
    HEADER_META = (
        ("ar", "lrc_artist"),
        ("ti", "lrc_title"),
        ("al", "lrc_album"),
        ("by", "lrc_creator"),
        ("offset", "lrc_offset"),
    )

    def __init__(self, name=None):
        """Initialize a new sppasLRC instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        super(sppasLRC, self).__init__(name)

        self.default_extension = "lrc"
        self.software = "Karaoke LRC"

        self._accept_multi_tiers = True
        self._accept_hierarchy = True

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_lrc_time(time_string):
        """Convert a "mm:ss.xx" LRC timestamp into seconds."""
        minutes, seconds = time_string.split(":")
        return (int(minutes) * 60.) + float(seconds.replace(",", "."))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_lrc_time(second_count):
        """Convert a time in seconds into a "mm:ss.xx" LRC timestamp."""
        total = round(second_count, 2)
        minutes = int(total // 60)
        seconds = round(total - (minutes * 60), 2)
        return "{:02d}:{:05.2f}".format(minutes, seconds)

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a LRC file and fill the Transcription.

        :param filename: (str)

        """
        with codecs.open(filename, 'r', sg.__encoding__) as fp:
            lines = fp.readlines()

        if len(lines) > 0 and b(lines[0]).startswith(codecs.BOM_UTF8):
            lines[0] = lines[0][1:]

        entries = list()
        for raw_line in lines:
            line = raw_line.strip()
            if len(line) == 0:
                continue

            match = sppasLRC.LINE_TAG.match(line)
            if match is None:
                self._parse_header_line(line)
                continue

            line_begin = sppasLRC._parse_lrc_time(
                "{:s}:{:s}.{:s}".format(match.group(1), match.group(2), match.group(3)))
            rest = match.group(4)
            words = sppasLRC._parse_words(rest, line_begin)
            if words is None:
                text = rest.strip()
                if len(text) == 0:
                    continue
                entries.append((line_begin, None, text))
            else:
                if len(words) == 0:
                    continue
                entries.append((line_begin, words, None))

        self._create_tiers(entries)

    # -----------------------------------------------------------------------

    def _parse_header_line(self, line):
        """Parse a "[key: value]" header line and store it as metadata.

        :param line: (str) A single line of the file, without its tags.

        """
        match = sppasLRC.HEADER_TAG.match(line)
        if match is None:
            return

        key = match.group(1).lower()
        value = match.group(2).strip()
        for header_key, meta_key in sppasLRC.HEADER_META:
            if header_key == key:
                self.set_meta(meta_key, value)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_words(rest, line_begin):
        """Split the text following a line tag into timed words.

        :param rest: (str) The text of the line, after its "[mm:ss.xx]" tag.
        :param line_begin: (float) The timestamp of the line, in seconds.
        :returns: (list of tuple(float, str)) or None if "rest" has no
        word-level tag.

        """
        tags = list(sppasLRC.WORD_TAG.finditer(rest))
        if len(tags) == 0:
            return None

        words = list()

        # Text before the first tag, if any, is implicitly at line_begin.
        leading_text = rest[:tags[0].start()].strip()
        if len(leading_text) > 0:
            words.append((line_begin, leading_text))

        for i, tag in enumerate(tags):
            begin = sppasLRC._parse_lrc_time(
                "{:s}:{:s}.{:s}".format(tag.group(1), tag.group(2), tag.group(3)))
            text_end = tags[i + 1].start() if (i + 1) < len(tags) else len(rest)
            text = rest[tag.end():text_end].strip()
            if len(text) > 0:
                words.append((begin, text))

        return words

    # -----------------------------------------------------------------------

    def _create_tiers(self, entries):
        """Create the "Tokens" and "Transcription" tiers from parsed lines.

        :param entries: (list) Each entry is a tuple
        (line_begin, words, plain_text) with either "words" (list of
        tuple(float, str)) or "plain_text" (str) set, depending on
        whether the line has word-level tags.

        """
        # Flatten every line into a single chronological list of events,
        # so that the end of an event can be deduced from the begin of
        # the very next one, whatever tier it belongs to.
        events = list()
        for line_index, (line_begin, words, plain_text) in enumerate(entries):
            if words is None:
                events.append((line_index, True, line_begin, plain_text))
            else:
                for begin, text in words:
                    events.append((line_index, False, begin, text))

        transcription_tier = self.create_tier("Transcription")
        tokens_tier = self.create_tier("Tokens")

        line_items = dict()
        for i, (line_index, is_plain, begin, text) in enumerate(events):
            if (i + 1) < len(events):
                next_begin = events[i + 1][2]
                end = begin + min((next_begin - begin) / 2., sppasLRC.MAX_WORD_DURATION)
            else:
                end = begin + sppasLRC.MAX_WORD_DURATION

            location = sppasLocation(sppasInterval(
                sppasLRC.make_point(begin), sppasLRC.make_point(end)))
            ann = sppasAnnotation(location)
            if is_plain:
                ann.set_labels(format_labels(text, separator=" "))
            else:
                ann.set_labels(format_labels(text))
            tokens_tier.append(ann)

            line_items.setdefault(line_index, list()).append((begin, end, text))

        for line_index, (line_begin, words, plain_text) in enumerate(entries):
            items = line_items[line_index]
            line_end = items[-1][1]
            full_text = " ".join(text for _, _, text in items)

            location = sppasLocation(sppasInterval(
                sppasLRC.make_point(line_begin), sppasLRC.make_point(line_end)))
            ann = sppasAnnotation(location)
            ann.set_labels(format_labels(full_text))
            transcription_tier.append(ann)

        self.add_hierarchy_link("TimeAlignment", tokens_tier, transcription_tier)

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write a transcription into a file.

        :param filename: (str)

        """
        if len(self) == 1:
            self._write_lines(filename, self[0])
            return

        if len(self) != 2:
            raise AioMultiTiersError("LRC")

        tokens_tier = None
        transcription_tier = None
        for tier in self:
            parent = self.get_hierarchy().get_parent(tier)
            if parent is not None and \
                    self.get_hierarchy().get_hierarchy_type(tier) == "TimeAlignment":
                transcription_tier = tier
                tokens_tier = parent

        if tokens_tier is None or transcription_tier is None:
            raise AioFormatError(
                "a 'TimeAlignment' hierarchy link between the 'Tokens' "
                "and the 'Transcription' tiers")

        self._write_lines(filename, transcription_tier, tokens_tier)

    # -----------------------------------------------------------------------

    def _write_header(self, fp):
        """Write the "[key: value]" header lines, from the metadata."""
        header = ""
        for header_key, meta_key in sppasLRC.HEADER_META:
            if self.is_meta_key(meta_key):
                header += "[{:s}:{:s}]\n".format(header_key, self.get_meta(meta_key))
        if len(header) > 0:
            fp.write(header + "\n")

    # -----------------------------------------------------------------------

    def _write_lines(self, filename, transcription_tier, tokens_tier=None):
        """Write a LRC file from a "Transcription" tier and its "Tokens".

        :param filename: (str)
        :param transcription_tier: (sppasTier) Line by line lyrics.
        :param tokens_tier: (sppasTier) Word by word timestamps, or None
        to write a line-only, non-enhanced LRC file.

        """
        with codecs.open(filename, 'w', sg.__encoding__, buffering=8096) as fp:
            self._write_header(fp)

            for line_ann in transcription_tier:
                line_text = serialize_labels(
                    line_ann.get_labels(), separator=" ", empty="", alt=True)
                if len(line_text) == 0:
                    continue

                begin = line_ann.get_lowest_localization()
                line_begin = sppasLRC._format_lrc_time(begin.get_midpoint())

                if tokens_tier is None:
                    fp.write("[{:s}]{:s}\n".format(line_begin, line_text))
                    continue

                end = line_ann.get_highest_localization()
                subtitle = "[{:s}]".format(line_begin)
                for word_ann in tokens_tier.find(begin, end):
                    labels = word_ann.get_labels()
                    word_text = serialize_labels(
                        labels, separator=" ", empty="", alt=True)
                    if len(labels) > 1:
                        # No individual timestamp for this chunk of tokens.
                        subtitle += word_text + " "
                    else:
                        word_begin = sppasLRC._format_lrc_time(
                            word_ann.get_lowest_localization().get_midpoint())
                        subtitle += "<{:s}>{:s} ".format(word_begin, word_text)

                fp.write(subtitle.rstrip() + "\n")
