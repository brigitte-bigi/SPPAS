# -*- coding : UTF-8 -*-
"""
:filename: sppas.anndata.aio.readwrite.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The annotated files main reader/writer.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from __future__ import annotations
import logging
import os
from collections import OrderedDict

from sppas.core.coreutils import IOExtensionError
from sppas.core.coreutils import u
from sppas.src.utils.datatype import sppasTime

from ..anndataexc import AioEncodingError
from ..anndataexc import AioError

from .text import sppasRawText
from .text import sppasCSV
from .sclite import sppasCTM
from .sclite import sppasSTM
from .xtrans import sppasTDF
from .praat import sppasTextGrid
from .praat import sppasPitchTier
from .praat import sppasIntensityTier
from .phonedit import sppasMRK
from .phonedit import sppasSignaix
from .htk import sppasLab
from .subtitle import sppasSubRip
from .subtitle import sppasSubViewer
from .subtitle import sppasWebVTT
from .table import sppasTRA
from .table import sppasARFF
from .table import sppasXRFF
from .transcriber import sppasTRS
from .audacity import sppasAudacity
from .anvil import sppasAnvil
from .elan import sppasEAF
from .annotationpro import sppasANT
from .annotationpro import sppasANTX
from .xra import sppasXRA

# ---------------------------------------------------------------------------


class sppasTrsRW(object):
    """Main parser of annotated data: Reader and writer of annotated data.

    All the 3 types of annotated files are supported: ANNOT, MEASURE, TABLE.

    """
    # A dictionary to associate a file extension and a class to instantiate.
    TRANSCRIPTION_TYPES = OrderedDict()

    # ANNOT
    TRANSCRIPTION_TYPES[sppasXRA().default_extension] = sppasXRA
    TRANSCRIPTION_TYPES[sppasTextGrid().default_extension] = sppasTextGrid
    TRANSCRIPTION_TYPES[sppasAnvil().default_extension] = sppasAnvil
    TRANSCRIPTION_TYPES[sppasEAF().default_extension] = sppasEAF
    TRANSCRIPTION_TYPES[sppasANT().default_extension] = sppasANT
    TRANSCRIPTION_TYPES[sppasANTX().default_extension] = sppasANTX
    TRANSCRIPTION_TYPES[sppasTRS().default_extension] = sppasTRS
    TRANSCRIPTION_TYPES[sppasMRK().default_extension] = sppasMRK
    TRANSCRIPTION_TYPES[sppasSignaix().default_extension] = sppasSignaix
    TRANSCRIPTION_TYPES[sppasLab().default_extension] = sppasLab
    TRANSCRIPTION_TYPES[sppasSubRip().default_extension] = sppasSubRip
    TRANSCRIPTION_TYPES[sppasSubViewer().default_extension] = sppasSubViewer
    TRANSCRIPTION_TYPES[sppasWebVTT().default_extension] = sppasWebVTT
    TRANSCRIPTION_TYPES[sppasCTM().default_extension] = sppasCTM
    TRANSCRIPTION_TYPES[sppasSTM().default_extension] = sppasSTM
    TRANSCRIPTION_TYPES[sppasAudacity().default_extension] = sppasAudacity
    TRANSCRIPTION_TYPES[sppasTDF().default_extension] = sppasTDF
    TRANSCRIPTION_TYPES[sppasCSV().default_extension] = sppasCSV
    TRANSCRIPTION_TYPES[sppasRawText().default_extension] = sppasRawText
    # TABLE
    TRANSCRIPTION_TYPES[sppasTRA().default_extension] = sppasTRA
    TRANSCRIPTION_TYPES[sppasARFF().default_extension] = sppasARFF
    TRANSCRIPTION_TYPES[sppasXRFF().default_extension] = sppasXRFF
    # MEASURE
    TRANSCRIPTION_TYPES[sppasIntensityTier().default_extension] = sppasIntensityTier
    TRANSCRIPTION_TYPES[sppasPitchTier().default_extension] = sppasPitchTier

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions():
        """Return the whole list of supported extensions (case-sensitive)."""
        return list(sppasTrsRW.TRANSCRIPTION_TYPES.keys())

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions_in() -> list:
        """Return the list of supported extensions if the reader exists."""
        e = list()
        for ext in list(sppasTrsRW.TRANSCRIPTION_TYPES.keys()):
            fp = FileFormatProperty(extension=ext)
            if fp.get_reader() is True:
                e.append(ext)

        return e

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions_out() -> list:
        """Return the list of supported extensions if the writer exists."""
        e = list()
        for ext in list(sppasTrsRW.TRANSCRIPTION_TYPES.keys()):
            fp = FileFormatProperty(extension=ext)
            if fp.get_writer() is True:
                e.append(ext)

        return e

    # -----------------------------------------------------------------------

    @staticmethod
    def annot_extensions() -> list:
        """Return the list of ANNOT extensions (case-sensitive)."""
        e = list()
        for ext in list(sppasTrsRW.TRANSCRIPTION_TYPES.keys()):
            fp = FileFormatProperty(extension=ext)
            if fp.get_trs_type() == "ANNOT":
                e.append(ext)

        return e

    # -----------------------------------------------------------------------

    @staticmethod
    def measure_extensions() -> list:
        """Return the list of MEASURE extensions (case-sensitive)."""
        e = list()
        for ext in list(sppasTrsRW.TRANSCRIPTION_TYPES.keys()):
            fp = FileFormatProperty(extension=ext)
            if fp.get_trs_type() == "MEASURE":
                e.append(ext)

        return e

    # -----------------------------------------------------------------------

    @staticmethod
    def table_extensions() -> list:
        """Return the list of TABLE extensions (case-sensitive)."""
        e = list()
        for ext in list(sppasTrsRW.TRANSCRIPTION_TYPES.keys()):
            fp = FileFormatProperty(extension=ext)
            if fp.get_trs_type() == "TABLE":
                e.append(ext)

        return e

    # -----------------------------------------------------------------------

    def __init__(self, filename: str):
        """Create a Transcription reader-writer.

        :param filename: (str)

        """
        self.__filename = u(filename)

    # -----------------------------------------------------------------------

    def get_filename(self) -> str:
        """Return the filename."""
        return self.__filename

    # -----------------------------------------------------------------------

    def set_filename(self, filename: str) -> None:
        """Set a new filename. 

        :param filename: (str)

        """
        self.__filename = u(filename)
        
    # -----------------------------------------------------------------------

    def read(self, heuristic: bool = False) -> object:
        """Read a transcription from a file.

        :param heuristic: (bool) if the extension of the file is unknown, use
        a heuristic to detect the format, then to choose the reader-writer.
        :return: sppasTranscription reader-writer

        """
        try:
            trs = sppasTrsRW.create_trs_from_extension(self.__filename)
        except IOExtensionError:
            if heuristic is True:
                trs = sppasTrsRW.create_trs_from_heuristic(self.__filename)
            else:
                raise

        if os.path.exists(self.__filename) is False:
            raise AioError(self.__filename)

        try:
            # Add metadata about the file
            fn = u(self.__filename)
            trs.set_meta('file_reader', trs.__class__.__name__)
            trs.set_meta('file_name', os.path.basename(fn))
            trs.set_meta('file_path', os.path.dirname(fn))
            trs.set_meta('file_ext', os.path.splitext(fn)[1])
            trs.set_meta('file_read_date', sppasTime().now)

            # Read the file content dans store into a Transcription()
            trs.read(self.__filename)

        except UnicodeError as e:
            raise AioEncodingError(filename=self.__filename, error_msg=str(e))
        except IOError:
            raise
        except Exception:
            raise

        return trs

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_extension(filename: str) -> object:
        """Return a transcription according to a given filename.

        Only the extension of the filename is used.

        :param filename: (str) Name of the annotated file
        :raises: IOExtensionError: un-supported extension
        :return: (sppasTranscription)

        """
        extension = os.path.splitext(filename)[1][1:]
        logging.debug("Parse an annotated file: {:s}".format(filename))
        for ext in sppasTrsRW.TRANSCRIPTION_TYPES.keys():
            if ext.lower() == extension.lower():
                return sppasTrsRW.TRANSCRIPTION_TYPES[ext]()

        raise IOExtensionError(filename)

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_heuristic(filename: str) -> object:
        """Return a transcription according to a given filename.

        The given file is opened and a heuristic allows to fix the format.

        :param filename: (str)
        :return: (Transcription)

        """
        for file_reader in sppasTrsRW.TRANSCRIPTION_TYPES.values():
            try:
                if file_reader.detect(filename) is True:
                    return file_reader()
            except:
                continue
        return sppasRawText()

    # -----------------------------------------------------------------------

    def write(self, transcription):
        """Write a transcription into a file.

        :param transcription: (sppasTranscription)

        """
        trs_rw = sppasTrsRW.create_trs_from_extension(self.__filename)
        trs_rw.set(transcription)

        # Add metadata about the file
        trs_rw.set_meta('file_writer', trs_rw.__class__.__name__)
        trs_rw.set_meta('file_name', os.path.basename(self.__filename))
        # The path can be already assigned -- to be hidden for example
        if trs_rw.is_meta_key("file_path") is False:
            trs_rw.set_meta('file_path', os.path.dirname(self.__filename))
        trs_rw.set_meta('file_ext', os.path.splitext(self.__filename)[1])
        trs_rw.set_meta('file_write_date', "{:s}".format(sppasTime().now))
        file_version = int(trs_rw.get_meta("file_version", "0")) + 1
        trs_rw.set_meta('file_version', str(file_version))

        try:
            trs_rw.write(self.__filename)
        except UnicodeError as e:
            raise AioEncodingError(self.__filename, str(e))
        except Exception:
            raise

# ---------------------------------------------------------------------------


class FileFormatProperty(object):
    """Represent one format and its properties.

    """

    def __init__(self, extension: str):
        """Create a FileFormatProperty instance.

        :param extension: (str) File name extension.

        """
        self._extension = extension
        if extension.startswith(".") is False:
            self._extension = "." + extension

        self._instance = None
        self._software = "Unknown"
        for ext in sppasTrsRW.TRANSCRIPTION_TYPES.keys():
            if ext.lower() == extension.lower():
                self._instance = sppasTrsRW.TRANSCRIPTION_TYPES[ext]()
                self._software = self._instance.software

        try:
            self._instance.read("")
        except NotImplementedError:
            self._reader = False
        except Exception:
            self._reader = True
        try:
            self._instance.write("")
        except NotImplementedError:
            self._writer = False
        except Exception:
            self._writer = True

    # -----------------------------------------------------------------------

    def get_extension(self) -> str:
        """Return the extension, including the initial dot."""
        return self._extension

    def get_software(self) -> str:
        """Return the name of the software matching the extension."""
        return self._software

    def get_reader(self) -> bool:
        """Return True if SPPAS can read files of the extension."""
        return self._reader

    def get_writer(self) -> bool:
        """Return True if SPPAS can write files of the extension."""
        return self._writer

    def get_trs_type(self) -> str | None:
        """Return the transcription type: ANNOT, MEASURE, TABLE or None."""
        if self._instance is None:
            return None
        return self._instance.trs_type

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __str__(self):
        return 'FileFormatProperty() of extension {!s:s}' \
               ''.format(self._extension)
