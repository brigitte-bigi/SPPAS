# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.media.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Represent a media -- a recording file.

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

import mimetypes

from sppas.core.coreutils import u

from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasMedia(sppasMetaData):
    """Generic representation of a media file.

    """

    def __init__(self, filename, media_id=None, mime_type=None):
        """Create a new sppasMedia instance.

        :param filename: (str) File name of the media
        :param media_id: (str) Identifier of the media
        :param mime_type: (str) Mime type of the media

        """
        super(sppasMedia, self).__init__()

        self.__url = filename
        self.__mime = ""
        self.__content = ""

        if media_id is not None:
            self.set_meta('id', media_id)

        if mime_type is None:
            m = mimetypes.guess_type(self.__url)
            if m[0] is None:
                mime_type = "audio/basic"
            else:
                mime_type = m[0]
        self.__mime = mime_type

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the URL of the media."""
        return self.__url

    # -----------------------------------------------------------------------

    def get_mime_type(self):
        """Return the mime type of the media."""
        return self.__mime

    # -----------------------------------------------------------------------

    def get_content(self):
        """Return the content of the media."""
        return self.__content

    # -----------------------------------------------------------------------

    def set_content(self, content):
        """Set the content of the media.

        :param content: (str)

        """
        self.__content = u(content)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __repr__(self):
        return "Media: id={:s} url={:s} mime={:s}" \
               "".format(self.get_meta('id'), self.__url, self.__mime)

    # -----------------------------------------------------------------------

    def __eq__(self, other):
        """Return True if other is strictly identical to self (even id)."""
        if isinstance(other, sppasMedia) is False:
            return False
        if self.__url != other.get_filename():
            return False
        if self.__mime != other.get_mime_type():
            return False

        for meta_key in self.get_meta_keys():
            if self.get_meta(meta_key) != other.get_meta(meta_key):
                return False
        for meta_key in other.get_meta_keys():
            if self.get_meta(meta_key) != other.get_meta(meta_key):
                return False

        return True

    # -----------------------------------------------------------------------

    def __ne__(self, other):
        return not self == other
