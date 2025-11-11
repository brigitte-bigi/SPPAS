# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.structs.basecompare.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Manage one language installed in the resources folder.

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

import os

from sppas.core.config import paths
from sppas.core.config import annots
from sppas.src.utils import sppasDirUtils

from .structsexc import LangTypeError
from .structsexc import LangPathError
from .structsexc import LangNameError

# ----------------------------------------------------------------------------


class sppasLangResource(object):
    """Manage information of a resource for a language.

    In most of the automatic annotations, we have to deal with language
    resources. Here, we store information about the type of resources,
    the path to get them, etc.

    """

    RESOURCES_TYPES = ["file", "directory"]

    def __init__(self):
        """Create a sppasLangResource instance.

        """
        # All available language resources (type, path, filename, extension)
        self._rtype = ""
        self._rpath = ""
        self._rname = ""
        self._rext = ""
        self._rlang = True   # is it a language resource?

        # The list of languages the resource can provide
        self.langlist = list()

        # The selected language
        self.lang = ""

        # The language resource of the selected language
        self.langresource = ""

    # ------------------------------------------------------------------------

    def reset(self):
        """Set all members to their default value."""
        self._rtype = ""
        self._rpath = ""
        self._rname = ""
        self._rext = ""
        self._rlang = True   # is that a language resource?

        self.langlist = []
        self.lang = ""
        self.langresource = ""

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def is_lang_resource(self):
        """Return False if the given resource is not representing a language."""
        return self._rlang

    # ------------------------------------------------------------------------

    def get_lang(self):
        """Return the language name.

        Language names in SPPAS are commonly represented in iso-639-3.
        It is a code that aims to define three-letter identifiers for all
        known human languages. "und" is representing an undetermined language.
        See <http://www-01.sil.org/iso639-3/> for details...

        :returns: (str) Language code or an empty string if no lang was set.

        """
        return self.lang

    # ------------------------------------------------------------------------

    def get_langlist(self):
        """Return the list of available languages.

        :returns: List of str

        """
        return self.langlist

    # ------------------------------------------------------------------------

    def get_langresource(self):
        """Return the resource name defined for the given language."""
        if self._rlang is True:
            # The resource is language dependent
            # Is there a resource available for this language?
            if self.lang in self.langlist:
                if len(self._rname) > 0:
                    return self.langresource + self.lang + self._rext
                else:
                    return os.path.join(self.langresource, self.lang + self._rext)

        return self.langresource

    # ------------------------------------------------------------------------

    def get_resourcetype(self):
        """Return the language type."""
        return self._rtype

    # ------------------------------------------------------------------------

    def get_resourceext(self):
        """Return the language extension."""
        return self._rext

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_type(self, resource_type):
        """Set the type of the resource.

        :param resource_type: (str) One of "file" or "directory".

        """
        resource_type = str(resource_type)
        if resource_type not in sppasLangResource.RESOURCES_TYPES:
            self.reset()
            raise LangTypeError(resource_type)

        self._rtype = resource_type

    # ------------------------------------------------------------------------

    def set_path(self, resource_path):
        """Fix the language resource path.

        :param resource_path: (str) Relative path to find the resource.

        """
        resource_path = str(resource_path)

        folder = os.path.join(paths.resources, resource_path)
        if os.path.exists(folder) is False:
            self.reset()
            raise LangPathError(folder)

        self._rpath = resource_path

    # ------------------------------------------------------------------------

    def set_filename(self, resource_filename):
        """Fix the language resource filename.

        :param resource_filename: (str) Resource filename.

        """
        self._rname = str(resource_filename)

    # ------------------------------------------------------------------------

    def set_extension(self, resource_extension):
        """Fix the language resource file extension.

        :param resource_extension: (str) Resource filename extension.

        """
        self._rext = str(resource_extension)

    # ------------------------------------------------------------------------

    def set(self, rtype, rpath, rname="", rext="", rlang=True):
        """Set resources then fix the list of available languages.

        :param rtype: (str) Resource type. One of: "file" or "directory"
        :param rpath: (str) Resource path
        :param rname: (str) Resource file name
        :param rext: (str)  Resource extension
        :param rlang: (bool) Language-dependent resource

        """
        self.reset()

        # Fix the language resource basis information
        self.set_type(rtype)
        self.set_path(rpath)
        self.set_filename(rname)
        self.set_extension(rext)
        self._rlang = rlang

        directory = os.path.join(paths.resources, self._rpath)

        # Fix the language resource information
        if len(self._rname) > 0:
            self.langresource = os.path.join(paths.resources, self._rpath, self._rname)
        else:
            self.langresource = directory

        # Fix the list of available languages
        if rlang is True:
            if rtype == "file":
                if len(rext) > 0:
                    sd = sppasDirUtils(directory)
                    for selectedfile in sd.get_files(self._rext):
                        filename, fext = os.path.splitext(selectedfile)
                        filename = os.path.basename(filename)
                        if filename.startswith(self._rname):
                            self.langlist.append(filename.replace(self._rname, ""))
            else:
                self._rext = ""
                if len(self._rname) > 0:
                    for dirname in os.listdir(directory):
                        if dirname.startswith(rname) is True:
                            self.langlist.append(dirname.replace(self._rname, ""))

    # ------------------------------------------------------------------------

    def set_lang(self, lang, forced=False):
        """Set the language if valid.

        To reset the language, fix lang to None.

        :param lang: (str) The language must be either UNDETERMINED or one of the language of the list.
        :param forced: (bool) Force the language to be assigned even if it is not validated.
        :raises: LangNameError: Invalid given lang

        """
        if lang is None:
            self.lang = ""
            return

        if forced is False and lang.lower() != annots.UNDETERMINED and lang not in self.langlist:
            raise LangNameError(lang)

        self.lang = lang
