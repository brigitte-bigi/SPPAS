# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.metadata.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Represent a set of metadata and an identifier.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from collections import OrderedDict
import uuid

from sppas.core.config import sg
from sppas.core.coreutils import sppasUnicode

# ---------------------------------------------------------------------------


class sppasMetaData(object):
    """Dictionary of meta data including a required 'id'.

    Meta data keys and values are unicode strings.

    """

    def __init__(self):
        """Create a sppasMetaData instance.

        Add a GUID-like in the dictionary of metadata, with key "id".

        """
        self.__metadata = OrderedDict()
        self.gen_id()

    # -----------------------------------------------------------------------

    def get_id(self):
        """Return the identifier of this object."""
        return self.__metadata['id']

    # -----------------------------------------------------------------------

    def gen_id(self):
        """Re-generate an 'id'."""
        self.__metadata['id'] = str(uuid.uuid4())

    # -----------------------------------------------------------------------

    def is_meta_key(self, entry):
        """Check if an entry is a key in the list of metadata.

        :param entry: (str) Entry to check
        :returns: (Boolean)

        """
        return entry in self.__metadata

    # -----------------------------------------------------------------------

    def get_meta(self, entry, default=""):
        """Return the value of the given key.

        :param entry: (str) Entry to be checked as a key.
        :param default: (str) Default value to return if entry is not a key.
        :returns: (str) meta data value or default value

        """
        return self.__metadata.get(entry, default)

    # -----------------------------------------------------------------------

    def get_meta_keys(self):
        """Return the list of metadata keys."""
        return self.__metadata.keys()

    # -----------------------------------------------------------------------

    def set_meta(self, key, value):
        """Set or update a metadata.

        :param key: (str) The key of the metadata.
        :param value: (str) The value assigned to the key.

        key, and value are formatted and stored in unicode.

        """
        if value is None:
            value = ""

        su = sppasUnicode(key)
        key = su.to_strip()

        su = sppasUnicode(value)
        value = su.to_strip()

        self.__metadata[key] = value

    # -----------------------------------------------------------------------

    def pop_meta(self, key):
        """Remove a metadata from its key.

        :param key: (str)

        """
        if key == 'id':
            raise ValueError("Identifier key can't be removed of the metadata.")
        if key in self.__metadata:
            del self.__metadata[key]

    # -----------------------------------------------------------------------
    # Add default metadata
    # -----------------------------------------------------------------------

    def add_license_metadata(self, idx):
        """Add metadata about the license applied to the object (GPLv3)."""
        # Elan
        self.set_meta('file_license_text_%s' % idx,
                      'GNU AGPL V3')
        self.set_meta('file_license_url_%s' % idx,
                      'https://www.gnu.org/licenses/gpl-3.0.en.html')

    # -----------------------------------------------------------------------

    def add_software_metadata(self):
        """Add metadata about this software.

        TODO: CHECK IF KEYS NOT ALREADY EXISTING.

        """
        self.set_meta('software_name', sg.__name__)
        self.set_meta('software_version', sg.__version__)
        self.set_meta('software_url', sg.__url__)
        self.set_meta('software_author', sg.__author__)
        self.set_meta('software_contact', sg.__contact__)
        self.set_meta('software_copyright', sg.__copyright__)

    # -----------------------------------------------------------------------

    def add_language_metadata(self):
        """Add metadata about the language (und).

        TODO: CHECK IF KEYS NOT ALREADY EXISTING.

        """
        # Elan
        self.set_meta('language_iso', "iso639-3")
        self.set_meta('language_code_0', "und")
        self.set_meta('language_name_0', "Undetermined")
        self.set_meta('language_url_0', "https://iso639-3.sil.org/code/und")

    # -----------------------------------------------------------------------

    def add_project_metadata(self):
        """Add metadata about the project this object is included-in.

        Currently do not assign any value.
        TODO: CHECK IF KEYS NOT ALREADY EXISTING.

        """
        # annotation pro
        self.set_meta("project_description", "")
        self.set_meta("project_corpus_owner", "")
        self.set_meta("project_corpus_type", "")
        self.set_meta("project_license", "")
        self.set_meta("project_environment", "")
        self.set_meta("project_collection", "")
        self.set_meta("project_title", "")
        self.set_meta("project_noises", "")

    # -----------------------------------------------------------------------

    def add_annotator_metadata(self, name="", version="", version_date=""):
        """Add metadata about an annotator.

        :param name: (str)
        :param version: (str)
        :param version_date: (str)

        TODO: CHECK IF KEYS ARE NOT ALREADY EXISTING.

        """
        # subtitle, transcriber, elan
        self.set_meta("annotator_name", name)

        # transcriber
        self.set_meta("annotator_version", version)

        # transcriber
        self.set_meta("annotator_version_date", version_date)

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self.__metadata)

# ---------------------------------------------------------------------------


class sppasDefaultMeta(sppasMetaData):
    """Dictionary of default meta data in SPPAS.

    Many annotation tools are using metadata... Moreover, each annotation
    tool is encoding data with its own formalism. SPPAS aio API enables
    metadata to store information related to the read data in order to
    give them back when writing the data, either in the same file format
    or to export in another format. Such option is possible only if some
    kind of "generic" metadata names are fixed.

    """

    def __init__(self):
        """Instantiate a default set of meta data."""
        super(sppasDefaultMeta, self).__init__()

    # -----------------------------------------------------------------------

    def speaker(self):
        """Add metadata related to a speaker.

        For compatibility with sclite, transcriber, xtrans, elan

        """
        # sclite, transcriber
        self.set_meta("speaker_id", "")

        # sclite, xtrans, transcriber, elan
        self.set_meta("speaker_name", "")

        # xtrans, transcriber
        self.set_meta("speaker_type", "")

        # xtrans, transcriber
        self.set_meta("speaker_dialect", "")

        # transcriber
        self.set_meta("speaker_accent", "")

        # transcriber
        self.set_meta("speaker_scope", "")  # (local|global)

        # other
        self.set_meta("speaker_current_occupation", "")
        self.set_meta("speaker_current_city", "")
        self.set_meta("speaker_current_country", "")

        self.set_meta("speaker_past_occupation", "")
        self.set_meta("speaker_education", "")

        self.set_meta("speaker_birth_date", "")
        self.set_meta("speaker_birth_city", "")
        self.set_meta("speaker_birth_country", "")

        self.set_meta("speaker_language", "")

    # -----------------------------------------------------------------------

    def tier(self):
        """Add metadata related to a tier.

        For compatibility with audacity and annotation pro.

        """
        # audacity, annotation pro
        self.set_meta("tier_is_closed", "")

        # audacity, annotation pro
        self.set_meta("tier_height", "")

        # audacity, annotation pro
        self.set_meta("tier_is_selected", "")

    # -----------------------------------------------------------------------

    def media(self):
        """Add metadata related to a media.

        For compatibility with sclite, xtrans, subtitle, elan, annotation pro.

        """
        # sclite, xtrans
        self.set_meta("media_channel", "")

        # subtitle
        self.set_meta("media_shift_delay", "")

        # elan, annotation pro
        self.set_meta("media_file", "")
        self.set_meta("media_path", "")

        # annotation pro
        self.set_meta("media_sample_rate", "")
