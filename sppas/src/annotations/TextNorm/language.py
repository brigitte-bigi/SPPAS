# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TextNorm.language.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Language name definition.

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


class sppasLangISO:
    """Language name definition.

    todo: parse a iso639-3 json file to load all language names.

    """

    lang_list = ["cmn", "jpn", "yue", "zho", "cdo", "cjy", "cmo", "cpx",
                 "czh", "czo", "czt", "gan", "hak", "hsn", "ltc", "lzh",
                 "mnp", "och", "wuu", "ben"]  # TODO: add languages

    # -----------------------------------------------------------------------

    @staticmethod
    def without_whitespace(lang):
        """Return true if 'lang' is not using whitespace.

        Mandarin Chinese or Japanese languages return True, but English
        or French return False.

        :param lang: (str) iso639-3 language code or a string starting with
            such code, like "yue" or "yue-chars" for example.
        :returns: (bool)

        """
        for l in sppasLangISO.lang_list:
            if l in lang:
                return True

        for l in sppasLangISO.lang_list:
            if lang.startswith(l):
                return True

        return False
