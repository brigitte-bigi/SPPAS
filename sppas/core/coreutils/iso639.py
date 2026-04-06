"""
:filename: sppas.coreutils.iso639.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Match iso639 codes with ISO 639 codes and their names.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2025  Brigitte Bigi, CNRS
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

from dataclasses import dataclass

from .exceptions import LanguageNotFoundError

# ---------------------------------------------------------------------------


@dataclass
class LanguageInfo:
    """Represents information about a specific language.

    :example:
    >>> language = LanguageInfo('en', 'English')
    >>> language.iso639_1_code
    'en'
    >>> language.language_name
    'English'

    """
    iso639_1_code: str  # The ISO-639-1 code of the language
    language_name: str  # The human-readable name of the language

# ---------------------------------------------------------------------------


class ISO639:
    """Manage language information based on ISO 639-3 codes.

    This class provides a lookup table that maps ISO 639-3 codes to their
    corresponding ISO 639-1 codes and human-readable language names.

    :example:
    >>> iso = ISO639()
    >>> language_info = iso.get_language_info('eng')
    >>> language_info.iso639_1_code
    'en'
    >>> language_info.language_name
    'English'
    >>> iso.get_language_info('xyz')
    Traceback (most recent call last):
        ...
    LanguageNotFoundError: Language code 'xyz' not found.

    """

    LANGUAGES = {
        'eng': LanguageInfo('en', 'English'),  # English
        'fra': LanguageInfo('fr', 'Français'),  # français
        'fre': LanguageInfo('fr', 'Français standard'),  # français (standard)
        'frq': LanguageInfo('fr', 'Français québécois'),  # français (québécois)
        'spa': LanguageInfo('es', 'Español'),  # español
        'deu': LanguageInfo('de', 'Deutsch'),  # Deutsch
        'ita': LanguageInfo('it', 'Italiano'),  # italiano
        'ben': LanguageInfo('bn', 'বাংলা'),  # বাংলা (Bangla)
        'cat': LanguageInfo('ca', 'Català'),  # català
        'cmn': LanguageInfo('zh', '普通话'),  # 普通话 (Putonghua)
        'hun': LanguageInfo('hu', 'Magyar'),  # magyar
        'jpn': LanguageInfo('ja', '日本語'),  # 日本語 (Nihongo)
        'kor': LanguageInfo('ko', '한국어'),  # 한국어 (Hangugeo)
        'mas': LanguageInfo('', 'Maa'),  # Maa (no international standard)
        'nan': LanguageInfo('', 'Bân-lâm-gú'),  # 閩南語 (Bân-lâm-gú, Southern Min)
        'pcm': LanguageInfo('', 'Naijá'),  # Naijá ou Nigerian Pidgin
        'pes': LanguageInfo('', 'فارسی'),  # فارسی (Fârsi)
        'pol': LanguageInfo('pl', 'Polski'),  # polski
        'por': LanguageInfo('pt', 'Português'),  # português
        'vie': LanguageInfo('vi', 'Tiếng Việt'),  # tiếng Việt
        'yue': LanguageInfo('zh', '廣東話'),  # 廣東話 (Gwóngdūng wá)
    }

    # -----------------------------------------------------------------------

    @staticmethod
    def get_language_info(iso639_3_code: str) -> LanguageInfo:
        """Return the corresponding LanguageInfo object for a given ISO 639-3 code.

        :param iso639_3_code: (str) The 3-letter ISO 639-3 code for the language.
        :return: (LanguageInfo) The corresponding LanguageInfo object.
        :raises: ValueError: If the provided ISO 639-3 code is not found in the lookup table.

        """
        iso639_3_code = iso639_3_code.lower()
        language_info = ISO639.LANGUAGES.get(iso639_3_code)
        if language_info is None:
            raise LanguageNotFoundError(iso639_3_code)
        return language_info
