# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.filesext.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Link between a file extension and an icon name.

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

from sppas.core.config import sppasExtensionsSettings
from sppas.src.anndata import sppasTrsRW
from sppas.src.videodata import video_extensions
from sppas.src.imgdata import image_extensions

# ---------------------------------------------------------------------------


class FileAnnotIcon(object):
    """Represents the link between a file extension and an icon name.

    All supported file formats of 'anndata' are linked to an icon file.
    All 'wav' files are linked to an icon file.

    """

    def __init__(self):
        """Constructor of a FileAnnotIcon.

        Set the name of the icon for all known extensions of annotations.

        Create a dictionary linking a file extension to the name of the
        software it comes from. It is supposed this name is matching an
        icon in PNG format.

        """
        self.__exticon = dict()

        # Add multimedia extensions
        with sppasExtensionsSettings() as s:
            for ext in s.AUDIO:
                self.__exticon[ext.upper()] = "audio"
        for ext in image_extensions:
            self.__exticon[ext.upper()] = "image"
        for ext in video_extensions:
            self.__exticon[ext.upper()] = "video"

        # Add annotated files extensions
        for ext in sppasTrsRW.TRANSCRIPTION_TYPES:
            software = sppasTrsRW.TRANSCRIPTION_TYPES[ext]().software
            if ext.startswith(".") is False:
                ext = "." + ext
            self.__exticon[ext.upper()] = software

    # -----------------------------------------------------------------------

    def get_icon_name(self, ext):
        """Return the name of the icon matching the given extension.

        A default icon is returned if the extension is unknown.
        It is supposed that the icon is available in the set of icons in
        SPPAS (it is not verified).

        :param ext: (str) An extension of an annotated or an audio file.
        :returns: (str) Name of an icon

        """
        if ext.startswith(".") is False:
            ext = "." + ext
        soft = self.__exticon.get(ext.upper(), "files-unk-file")
        return soft

    # -----------------------------------------------------------------------

    def get_software(self):
        return [self.__exticon[ext] for ext in self.__exticon]

    def get_extensions(self):
        return list(self.__exticon.keys())

    # -----------------------------------------------------------------------

    def get_names(self):
        """Return the list of known icon names."""
        names = list()
        for ext in self.__exticon:
            n = self.get_icon_name(ext)
            if n not in names:
                names.append(n)

        return names
