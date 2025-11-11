# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TextNorm.cutparser.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Parse cut elements of a text.

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

import os
import logging

try:
    # python 3
    from html.parser import HTMLParser
except:
    # python 2
    from HTMLParser import HTMLParser


# ---------------------------------------------------------------------------


class ParseCut(HTMLParser):
    """Parse a cut string with an HTML-style syntax."""

    def reset(self):
        """Override to add custom members."""
        HTMLParser.reset(self)
        self.cut_from = None
        self.cut_to = None
        self.event = None

    # -----------------------------------------------------------------------

    # Defining what the methods should output when called by HTMLParser.
    def handle_starttag(self, tag, attrs):
        """Override.

        It seems that the parser does not properly parse some tags. For example,
        the following does not work:
        <cut unit="ms" from="958.333" to="1458.333"/>
        but the following does:
        <cut unit="ms" from="958.333" to="1458.333" />
        It seems that HTMLParser requires a whitespace before the ending "/";
        if not, the "/" is appended to the last value - here: 1458.333/

        To be more robust, this method is trying to deal with this problem.

        """
        # Only parse the 'cut' tag.
        if tag == "cut":
            self.reset()
            unit = ""
            cut_from = None
            cut_to = None
            for att_key, att_value in attrs:
                if att_value is None:
                    continue
                if att_key == "unit":
                    unit = att_value
                elif att_key == "from":
                    cut_from = att_value
                elif att_key == "to":
                    cut_to = att_value
                elif att_key == "event":
                    if att_value.endswith("/") is True:
                        att_value = att_value[:-1]
                    self.event = att_value

            if cut_from is not None and cut_to is not None:
                if cut_from.endswith("/"):
                    cut_from = cut_from[:-1]
                if cut_to.endswith("/"):
                    cut_to = cut_to[:-1]
                self.cut_from = ParseCut.to_seconds(cut_from, unit)
                self.cut_to = ParseCut.to_seconds(cut_to, unit)

    # -----------------------------------------------------------------------

    @staticmethod
    def to_seconds(value, unit=None):
        """Convert from/to values into seconds.

        :param value: (int, float) A time value
        :param unit: (str) Either "ms", "sec", or None for "HH:MM:sec.ms
        :return: (float) Time value in seconds

        """
        if unit == "sec":
            return float(value)
        elif unit == "ms":
            return float(value) / 1000.
        else:
            return sum(float(x) * 60 ** i for i, x in enumerate(reversed(value.split(':'))))

# ---------------------------------------------------------------------------


class TextCutParser:
    """Parse a text depending on the <cut> elements it includes.

    """

    def __init__(self):
        """Create a text parser."""
        self.__parser = ParseCut()

    # -----------------------------------------------------------------------

    def parse_cut(self, text, begin=None, end=None):
        """Return the list of cuts of the best tag of a label.

        Caution: Recursion is used...

        :param text: (str)
        :param begin: (float, in or None)
        :param end: (float, int or None)
        :return: List of tuple(text,from,to) in seconds

        """
        cuts = list()
        if "<cut " not in text or "/>" not in text:
            return list()

        # Both "<cut " and "/>" were found. Parse the text.
        cut_idx_start = text.index("<cut ")
        cut_idx_end = text.index("/>")
        before_text = text[0:cut_idx_start]
        after_text = text[cut_idx_end+2:len(text)]
        s, e, event_name = self.parse_cut_htmltag(text[cut_idx_start:cut_idx_end+2])
        cuts.append((before_text, begin, s))
        cuts.append((event_name, s, e))

        if "<cut " in after_text and "/>" in after_text:
            # Recursion is here
            cuts.extend(self.parse_cut(after_text, e, end))
        else:
            cuts.append((after_text, e, end))

        return cuts

    # -----------------------------------------------------------------------

    def parse_cut_htmltag(self, text):
        """Return start time and end time in seconds from a cut tag.

        Example: With the text '<cut unit="ms" s="633" e="1233"/>', this
        method returns (0.633, 1.233).

        :param text: (str) An HTML element "<cut from="XX:XX" to="YY:YY.234"/>
        :return: tuple(float, float)

        """
        self.__parser.reset()
        self.__parser.feed(text)
        if self.__parser.cut_from is None or self.__parser.cut_to is None:
            raise Exception("The <cut /> tag must contain 'from' and 'to'. "
                            "Got '{}' instead.".format(text))
        event = "dummy"
        if self.__parser.event is not None:
            event = self.__parser.event
        return self.__parser.cut_from, self.__parser.cut_to, event
