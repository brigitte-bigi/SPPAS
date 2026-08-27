# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.aio.basetrsio.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Base class for any transcription input/output.

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

from sppas.core.config import cfg

from ..transcription import sppasTranscription
from ..anndataexc import AnnDataTypeError
from ..anndataexc import CtrlVocabContainsError
from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..ann.annlocation import sppasLocation
from ..ann.annlocation import sppasPoint
from ..ann.annlocation import sppasInterval
from ..ann.annlabel import sppasLabel
from ..ann.annlabel import sppasTag

# ---------------------------------------------------------------------------


class sppasBaseIO(sppasTranscription):
    """Base object for readers and writers of annotated data.

    """

    # Name of the tier a format is using to hold what it can't hold
    # otherwise, and keyword of its first annotation.
    UNSUPPORTED_TIER_NAME = "DoNotEdit"
    UNSUPPORTED_KEYWORD = "Metadata"

    # The natures of the information such a tier is holding.
    UNSUPPORTED_TYPES = ("metadata", "ctrl_vocab", "media")

    # A format serializing the labels of an annotation separated by a
    # whitespace has to declare it: the whitespaces of the entries are
    # turned into underscores, and they stay so when read back.
    UNSUPPORTED_NO_WHITESPACE = False

    # The identifier of an object is re-generated at each reading: it is
    # never preserved. The other metadata SPPAS assigns by itself are
    # preserved only if their value was changed.
    GENERATED_META = "id"

    @staticmethod
    def detect(filename):
        """Check whether a file is of the appropriate format or not."""
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def is_number(s):
        """Check whether a string is a number or not.

        :param s: (str or unicode)
        :returns: (bool)

        """
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """Initialize a new Transcription reader-writer instance.

        :param name: (str) A transcription name.

        """
        super(sppasBaseIO, self).__init__(name)

        self.default_extension = None
        self.software = "und"
        self.trs_type = "ANNOT"

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_empty_tier = False
        self._accept_metadata = False
        self._accept_comments = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_tag_types = False
        self._accept_tag_geometry = False
        self._accept_radius = True
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def multi_tiers_support(self):
        """Return True if it supports to read and write several tiers.

        :returns: boolean

        """
        return self._accept_multi_tiers

    # -----------------------------------------------------------------------

    def no_tiers_support(self):
        """Return True if it supports to write no tier.

        :returns: boolean

        """
        return self._accept_no_tiers

    # -----------------------------------------------------------------------

    def empty_tier_support(self):
        """Return True if it supports to write a tier with no annotation.

        A format without this support requires the empty tiers to be
        removed before writing.

        :returns: boolean

        """
        return self._accept_empty_tier

    # -----------------------------------------------------------------------

    def metadata_support(self):
        """Return True if it supports to read and write metadata.

        :returns: boolean

        """
        return self._accept_metadata

    # -----------------------------------------------------------------------

    def comments_support(self):
        """Return True if it supports to read and write comments.

        The comments are holding the information a format can't hold
        otherwise, like the metadata of a format without metadata support.

        :returns: boolean

        """
        return self._accept_comments

    # -----------------------------------------------------------------------

    def ctrl_vocab_support(self):
        """Return True if it supports to read and write a controlled vocab.

        :returns: boolean

        """
        return self._accept_ctrl_vocab

    # -----------------------------------------------------------------------

    def media_support(self):
        """Return True if it supports to read and write a link to a media.

        :returns: boolean

        """
        return self._accept_media

    # -----------------------------------------------------------------------

    def hierarchy_support(self):
        """Return True if it supports a hierarchy between tiers.

        :returns: boolean

        """
        return self._accept_hierarchy

    # -----------------------------------------------------------------------

    def point_support(self):
        """Return True if it supports tiers with localizations as points.

        :returns: boolean

        """
        return self._accept_point

    # -----------------------------------------------------------------------

    def interval_support(self):
        """Return True if it supports tiers with localizations as intervals.

        :returns: boolean

        """
        return self._accept_interval

    # -----------------------------------------------------------------------

    def disjoint_support(self):
        """Return True if it supports tiers with localizations as disjoint.

        :returns: boolean

        """
        return self._accept_disjoint

    # -----------------------------------------------------------------------

    def alternative_localization_support(self):
        """Return True if it supports to alternative localizations.

        If support with or without a score, it returns true.

        :returns: boolean

        """
        return self._accept_alt_localization

    # -----------------------------------------------------------------------

    def alternative_tag_support(self):
        """Return True if it supports alternative tags.

        If support with or without a score, it returns true.

        :returns: boolean

        """
        return self._accept_alt_tag

    # -----------------------------------------------------------------------

    def tag_types_support(self):
        """Return True if it supports the typed tags.

        The typed tags are the ones of type "bool", "int" or "float":
        a format without this support converts them into "str".

        :returns: boolean

        """
        return self._accept_tag_types

    # -----------------------------------------------------------------------

    def tag_geometry_support(self):
        """Return True if it supports the geometric tags.

        The geometric tags are the ones of type "point" or "rect":
        a format without this support converts them into "str".

        :returns: boolean

        """
        return self._accept_tag_geometry

    # -----------------------------------------------------------------------

    def radius_support(self):
        """Return True if it supports the radius value.

        :returns: boolean

        """
        return self._accept_radius

    # -----------------------------------------------------------------------

    def gaps_support(self):
        """Return True if it supports gaps between annotations of a tier.

        :returns: boolean

        """
        return self._accept_gaps

    # -----------------------------------------------------------------------

    def overlaps_support(self):
        """Return True if it supports overlaps between annotations of a tier.

        :returns: boolean

        """
        return self._accept_overlaps

    # -----------------------------------------------------------------------
    # What a format can't hold
    # -----------------------------------------------------------------------

    def unsupported_entries(self):
        """Return the information this format can't hold.

        Each entry is a tuple (nature, owner, key, value): the nature is
        one of UNSUPPORTED_TYPES, the owner is the name of the tier the
        information belongs to -- or an empty string for the transcription
        itself -- and the key/value pair is the information.

        :returns: (list of tuples)

        """
        entries = list()

        if self.metadata_support() is False:
            generated = sppasTranscription()
            for key in self.get_meta_keys():
                if sppasBaseIO.__is_generated(generated, key,
                                              self.get_meta(key)) is True:
                    continue
                entries.append(("metadata", "", key, self.get_meta(key)))
            for tier in self:
                for key in tier.get_meta_keys():
                    if sppasBaseIO.__is_generated(generated, key,
                                                  tier.get_meta(key)) is True:
                        continue
                    entries.append(
                        ("metadata", tier.get_name(), key, tier.get_meta(key)))

        if self.ctrl_vocab_support() is False:
            for ctrl_vocab in self.get_ctrl_vocab_list():
                owners = [tier.get_name() for tier in self
                          if tier.get_ctrl_vocab() == ctrl_vocab]
                if len(owners) == 0:
                    owners = [""]
                for owner in owners:
                    for tag in ctrl_vocab:
                        entries.append(("ctrl_vocab", owner,
                                        ctrl_vocab.get_name(),
                                        tag.get_content()))

        if self.media_support() is False:
            for media in self.get_media_list():
                owners = [tier.get_name() for tier in self
                          if tier.get_media() == media]
                if len(owners) == 0:
                    owners = [""]
                for owner in owners:
                    entries.append(("media", owner, media.get_filename(),
                                    media.get_mime_type()))

        return entries

    # -----------------------------------------------------------------------

    def fill_unsupported_entry(self, nature, owner, key, value):
        """Fill the object an entry belongs to.

        This is what a reader has to call for each entry it found, whatever
        the way this format is holding them.

        :param nature: (str) One of UNSUPPORTED_TYPES
        :param owner: (str) Name of a tier, or an empty string
        :param key: (str) The key of the information
        :param value: (str) The value of the information
        :returns: (bool) The entry was assigned to an object

        The tags of a controlled vocabulary are entries of their own: the
        vocabulary is assigned to its tier as soon as it contains all the
        tags of this tier.

        """
        if nature not in sppasBaseIO.UNSUPPORTED_TYPES:
            return False
        tier = None
        if len(owner) > 0:
            tier = self.find(owner)
            if tier is None:
                return False

        if nature == "metadata":
            if tier is None:
                self.set_meta(key, value)
            else:
                tier.set_meta(key, value)
            return True

        if nature == "ctrl_vocab":
            ctrl_vocab = self.get_ctrl_vocab_from_name(key)
            if ctrl_vocab is None:
                ctrl_vocab = sppasCtrlVocab(key)
                self.add_ctrl_vocab(ctrl_vocab)
            ctrl_vocab.add(sppasTag(value))
            if tier is not None:
                try:
                    tier.set_ctrl_vocab(ctrl_vocab)
                except CtrlVocabContainsError:
                    # the tier is using tags this vocabulary doesn't contain
                    # yet: the next entries are adding them, and the next
                    # attempt to assign will succeed
                    pass
            return True

        # nature is "media"
        media = None
        for existing in self.get_media_list():
            if existing.get_filename() == key:
                media = existing
        if media is None:
            media = sppasMedia(key, mime_type=value)
            self.add_media(media)
        if tier is not None:
            tier.set_media(media)
        return True

    # -----------------------------------------------------------------------

    def create_unsupported_tier(self):
        """Create a tier with the information this format can't hold.

        The tier is named UNSUPPORTED_TIER_NAME and its first annotation is
        holding the keyword UNSUPPORTED_KEYWORD. Each of the next
        annotations is holding one entry: the key, the value, the nature
        and the owner, in this order, one in each of its labels. The nature
        and the owner are labels because no format needing this tier is
        writing the metadata of an annotation.

        A format declaring UNSUPPORTED_NO_WHITESPACE gets the whitespaces
        of the entries turned into underscores: it is the only way for such
        a format to tell one label from the next one when reading back.

        The time span of the transcription is shared into intervals of equal
        duration, one for each annotation.

        The tier is created only if the user is maintaining interoperability
        -- the default --, if there's something to preserve, and if this
        format is able to hold one tier more.

        :returns: (sppasTier) The created tier, or None

        """
        if cfg.interoperability is False:
            return None
        if self.multi_tiers_support() is False:
            return None
        entries = self.unsupported_entries()
        if len(entries) == 0:
            return None

        begin = self.get_min_loc()
        end = self.get_max_loc()
        if begin is None or end is None:
            return None

        # The keyword is the first annotation, then one for each entry
        first = begin.get_midpoint()
        last = end.get_midpoint()
        nb = len(entries) + 1
        tier = self.create_tier(sppasBaseIO.UNSUPPORTED_TIER_NAME)
        tier.create_annotation(
            sppasBaseIO.__unsupported_location(first, last, nb, 0),
            [sppasLabel(sppasTag(sppasBaseIO.UNSUPPORTED_KEYWORD))])

        for i, (nature, owner, key, value) in enumerate(entries):
            tier.create_annotation(
                sppasBaseIO.__unsupported_location(first, last, nb, i+1),
                [sppasLabel(sppasTag(self.__unsupported_content(key))),
                 sppasLabel(sppasTag(self.__unsupported_content(value))),
                 sppasLabel(sppasTag(self.__unsupported_content(nature))),
                 sppasLabel(sppasTag(self.__unsupported_content(owner)))])

        return tier

    # -----------------------------------------------------------------------

    def parse_unsupported_tier(self):
        """Fill the objects with the tier this format was holding them in.

        The tier is removed of the transcription: it was a way to write, not
        an information of the annotated data.

        :returns: (bool) The tier was found and its entries were assigned

        """
        tier = self.find(sppasBaseIO.UNSUPPORTED_TIER_NAME)
        if tier is None or len(tier) == 0:
            return False
        keyword = sppasBaseIO.__unsupported_tag(tier[0], 0)
        if keyword != sppasBaseIO.UNSUPPORTED_KEYWORD:
            return False

        for i, ann in enumerate(tier):
            if i == 0:
                continue
            self.fill_unsupported_entry(
                sppasBaseIO.__unsupported_tag(ann, 2),
                sppasBaseIO.__unsupported_tag(ann, 3),
                sppasBaseIO.__unsupported_tag(ann, 0),
                sppasBaseIO.__unsupported_tag(ann, 1))

        self.pop(self.get_tier_index(sppasBaseIO.UNSUPPORTED_TIER_NAME))
        return True

    # -----------------------------------------------------------------------

    @staticmethod
    def __is_generated(generated, key, value):
        """Return True if SPPAS assigned this metadata by itself.

        :param generated: (sppasTranscription) A newly created object
        :param key: (str) The key of the metadata
        :param value: (str) The value of the metadata
        :returns: (bool)

        """
        if key == sppasBaseIO.GENERATED_META:
            return True
        if generated.is_meta_key(key) is False:
            return False
        return generated.get_meta(key) == value

    # -----------------------------------------------------------------------

    @staticmethod
    def __unsupported_location(first, last, nb, index):
        """Return the location of the index-th annotation of nb, in a span.

        The interval bounds are evaluated from the bounds of the span, so
        that the last one is ending exactly at the end of the span.

        :param first: (float) Begin of the time span
        :param last: (float) End of the time span
        :param nb: (int) Number of annotations sharing the span
        :param index: (int) Index of the annotation, starting from zero

        """
        duration = last - first
        begin = first + (duration * index / nb)
        end = first + (duration * (index+1) / nb)
        return sppasLocation(sppasInterval(sppasPoint(begin),
                                           sppasPoint(end)))

    # -----------------------------------------------------------------------

    def __unsupported_content(self, content):
        """Return the content of a tag this format is able to write.

        :param content: (str) The key, value, nature or owner of an entry
        :returns: (str)

        """
        if self.UNSUPPORTED_NO_WHITESPACE is False:
            return content
        return content.replace(" ", "_")

    # -----------------------------------------------------------------------

    @staticmethod
    def __unsupported_tag(ann, index):
        """Return the content of the best tag of a label, or an empty string."""
        labels = ann.get_labels()
        if index >= len(labels):
            return ""
        tag = labels[index].get_best()
        if tag is None:
            return ""
        return tag.get_content()

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set(self, other):
        """Set self with other content.

        :param other: (sppasTranscription)

        """
        if isinstance(other, sppasTranscription) is False:
            raise AnnDataTypeError(other, "sppasTranscription")

        for key in other.get_meta_keys():
            self.set_meta(key, other.get_meta(key))
        self._name = other.get_name()
        self._media = other.get_media_list()
        self._ctrlvocab = other.get_ctrl_vocab_list()
        self._tiers = other.get_tier_list()
        self._hierarchy = other.get_hierarchy()

    # -----------------------------------------------------------------------

    def read(self, filename):
        """Read a file and fill the transcription.

        :param filename: (str)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def write(self, filename):
        """Write the transcription into a file.

        :param filename: (str)

        """
        raise NotImplementedError
