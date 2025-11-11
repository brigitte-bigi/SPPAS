# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.annlabel.tag.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Represent one of tags of a label.

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

from sppas.core.config import symbols
from sppas.core.coreutils import sppasUnicode
from sppas.core.coreutils import b

from ...anndataexc import AnnDataTypeError
from ...anndataexc import AnnUnkTypeError

from .tagtypes import sppasFuzzyPoint
from .tagtypes import sppasFuzzyRect

# ---------------------------------------------------------------------------


class sppasTag(object):
    """Represent one of the possible tags of a label.

    A sppasTag is a data content of any type.
    By default, the type of the data is "str" and the content is empty, but
    internally the sppasTag stores 'None' values because None is 16 bits and
    an empty string is 37.

    A sppasTag() content can be one of the following types:

        1. string/unicode - (str)
        2. integer - (int)
        3. float - (float)
        4. boolean - (bool)
        5. point - (sppasFuzzyPoint)
        6. rect - (sppasFuzzyRect)

    Get access to the content with the get_content() method and to the typed
    content with get_typed_content().

        >>> t1 = sppasTag("2")                      # "2" (str)
        >>> t2 = sppasTag(2)                        # "2" (str)
        >>> t3 = sppasTag(2, tag_type="int")        # 2 (int)
        >>> t4 = sppasTag("2", tag_type="int")      # 2 (int)
        >>> t5 = sppasTag("2", tag_type="float")    # 2. (float)
        >>> t6 = sppasTag("true", tag_type="bool")  # True (bool)
        >>> t7 = sppasTag(0, tag_type="bool")       # False (bool)
        >>> t8 = sppasTag((27, 32), tag_type="point")  # x=27, y=32 (point)
        >>> t9 = sppasTag((27, 32, 3), tag_type="point")  # x=27, y=32 (point), radius=3
        >>> t10 = sppasTag((27, 32, 320, 200), tag_type="rect")

    """

    TAG_TYPES = ("str", "float", "int", "bool", "point", "rect")

    # ------------------------------------------------------------------------

    def __init__(self, tag_content, tag_type=None):
        """Initialize a new sppasTag instance.

        :param tag_content: (any) Data content
        :param tag_type: (str): The type of this content.\
        One of: ('str', 'int', 'float', 'bool', 'point', 'rect').

        'str' is the default tag_type.

        """
        self.__tag_content = ""
        self.__tag_type = None
        
        self.set_content(tag_content, tag_type)

    # ------------------------------------------------------------------------

    def set(self, other):
        """Set self members from another sppasTag instance.

        :param other: (sppasTag)

        """
        if isinstance(other, sppasTag) is False:
            raise AnnDataTypeError(other, "sppasTag")

        self.set_content(other.get_content())
        self.__tag_type = other.get_type()

    # -----------------------------------------------------------------------

    def get_content(self):
        """Return an unicode string corresponding to the content.

        Also returns a unicode string in case of a list (elements are
        separated by a whitespace).

        :returns: (unicode)

        """
        return self.__tag_content

    # ------------------------------------------------------------------------

    def get_typed_content(self):
        """Return the content value, in its appropriate type.

        Excepted for strings which are systematically returned as unicode.

        """
        if self.__tag_type is not None:

            if self.__tag_type == "int":
                return int(self.__tag_content)

            elif self.__tag_type == "float":
                return float(self.__tag_content)

            elif self.__tag_type == "bool":
                if self.__tag_content.lower() == "true":
                    return True
                else:
                    return False

            elif self.__tag_type == "point":
                x, y, r = sppasFuzzyPoint.parse(self.__tag_content)
                return sppasFuzzyPoint((x, y), r)

            elif self.__tag_type == "rect":
                x, y, w, h, r = sppasFuzzyRect.parse(self.__tag_content)
                return sppasFuzzyRect((x, y, w, h), r)

        return self.__tag_content

    # ------------------------------------------------------------------------

    def set_content(self, tag_content, tag_type=None):
        """Change content of this sppasTag.

        :param tag_content: (any) New text content for this sppasTag
        :param tag_type: The type of this tag.\
        Default is 'str' to represent an unicode string.
        :raise: AnnUnkTypeError, AnnDataTypeError

        """
        # Check type
        if tag_type is not None and tag_type not in sppasTag.TAG_TYPES:
            raise AnnUnkTypeError(tag_type)
        if tag_type == "str":
            tag_type = None

        # Check content depending on the given type
        if tag_content is None:
            tag_content = ""

        if tag_type == "float":
            try:
                tag_content = float(tag_content)
            except ValueError:
                raise AnnDataTypeError(tag_content, "float")

        elif tag_type == "int":
            try:
                tag_content = int(tag_content)
            except ValueError:
                raise AnnDataTypeError(tag_content, "int")

        elif tag_type == "bool":
            if tag_content not in ('False', 'True'):
                # always works. Never raises ValueError!
                tag_content = bool(tag_content)

        elif tag_type == "point":
            # tag_content is either a sppasFuzzyPoint()
            # or a tuple with 2 or 3 integers.
            if isinstance(tag_content, str) is True:
                x, y, r = sppasFuzzyPoint.parse(tag_content)
                tag_content = sppasFuzzyPoint((x, y), r)

            elif isinstance(tag_content, sppasFuzzyPoint) is False:
                if isinstance(tag_content, tuple) is True:
                    if len(tag_content) not in (2, 3):
                        raise AnnDataTypeError("sppasTag", "tuple(int,int)")
                    p = sppasFuzzyPoint((tag_content[0], tag_content[1]))
                    if len(tag_content) == 3:
                        p.set_radius(tag_content[2])
                    tag_content = p
                else:
                    raise AnnDataTypeError("sppasTag", "tuple(int,int)")

        elif tag_type == "rect":
            # tag_content is either a sppasFuzzyRect()
            # or a tuple with 4 or 5 integers.
            if isinstance(tag_content, str) is True:
                x, y, w, h, r = sppasFuzzyRect.parse(tag_content)
                tag_content = sppasFuzzyRect((x, y, w, h), r)

            elif isinstance(tag_content, sppasFuzzyRect) is False:
                if isinstance(tag_content, tuple) is True:
                    if len(tag_content) not in (4, 5):
                        raise AnnDataTypeError("sppasTag", "tuple(int,int,int,int)")
                    p = sppasFuzzyRect((tag_content[0], tag_content[1], tag_content[2], tag_content[3]))
                    if len(tag_content) == 5:
                        p.set_radius(tag_content[4])
                    tag_content = p
                else:
                    raise AnnDataTypeError("sppasTag", "tuple(int,int,int,int)")

        # we systematically convert data into strings
        self.__tag_type = tag_type
        tag_content = str(tag_content)
        su = sppasUnicode(tag_content)
        self.__tag_content = su.to_strip()

    # ------------------------------------------------------------------------

    def copy(self):
        """Return a deep copy of self."""
        return sppasTag(self.__tag_content, self.__tag_type)

    # ------------------------------------------------------------------------

    def get_type(self):
        """Return the type of the tag content."""
        if self.__tag_type is None:
            return "str"
        return self.__tag_type

    # ------------------------------------------------------------------------

    def is_empty(self):
        """Return True if the tag is an empty string."""
        return self.__tag_content == ""

    # -----------------------------------------------------------------------

    def is_speech(self):
        """Return True if the tag is not a silence."""
        return not (self.is_silence() or
                    self.is_pause() or
                    self.is_laugh() or
                    self.is_noise() or
                    self.is_dummy())

    # -----------------------------------------------------------------------

    def is_silence(self):
        """Return True if the tag is a silence."""
        if self.__tag_type is None or self.__tag_type == "str":
            # create a list of silence symbols from the list of all symbols
            silences = list()
            for symbol in symbols.all:
                if symbols.all[symbol] == "silence":
                    silences.append(symbol)

            if self.__tag_content in silences:
                return True

            # HACK. Exception for the French CID corpus:
            if self.__tag_content.startswith("gpf_"):
                return True

        return False

    # -----------------------------------------------------------------------

    def is_pause(self):
        """Return True if the tag is a short pause."""
        # create a list of pause symbols from the list of all symbols
        pauses = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "pause":
                pauses.append(symbol)

        return self.__tag_content in pauses

    # -----------------------------------------------------------------------

    def is_laugh(self):
        """Return True if the tag is a laughing."""
        # create a list of laughter symbols from the list of all symbols
        laugh = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "laugh":
                laugh.append(symbol)

        return self.__tag_content in laugh

    # -----------------------------------------------------------------------

    def is_noise(self):
        """Return True if the tag is a noise."""
        # create a list of noise symbols from the list of all symbols
        noises = list()
        for symbol in symbols.all:
            if symbols.all[symbol] == "noise":
                noises.append(symbol)

        return self.__tag_content in noises

    # -----------------------------------------------------------------------

    def is_dummy(self):
        """Return True if the tag is a dummy label."""
        return self.__tag_content == "dummy"

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Tag: {!s:s},{!s:s}".format(b(self.get_content()), self.get_type())

    # -----------------------------------------------------------------------

    def __str__(self):
        return "{!s:s} ({!s:s})".format(b(self.get_content()), self.get_type())

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Compare 2 tags."""
        if isinstance(other, sppasTag):
            return self.get_typed_content() == other.get_typed_content()
        return False

    # -----------------------------------------------------------------------

    def __hash__(self):
        return hash((self.__tag_content, self.__tag_type))

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        if isinstance(other, sppasTag):
            return self.get_typed_content() != other.get_typed_content()
        return True
