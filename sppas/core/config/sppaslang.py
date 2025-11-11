# -*- coding: UTF-8 -*-
"""
:filename: sppas.config.sppaslang.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Translation system of SPPAS.

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

    -------------------------------------------------------------------------

"""

from __future__ import annotations
import gettext
import logging

from .settings import sg
from .settings import paths

# ---------------------------------------------------------------------------


class TranslatorManager:
    """Translator manager for internationalization (i18n) of messages.

    Manage translations and the global language setting for messages.

    Each translation domain can be loaded on demand. The manager caches
    these domain-specific translators to improve performance.

    The language to use is determined from system preferences or explicitly
    set by the user via `set_language()`.

    """

    def __init__(self, lang: str = "en"):
        """Initialize with default values."""
        self._po_path = paths.po     # Path to translation files
        self._default_lang = [lang]  # Always a list for gettext compatibility
        self._lang = sg.get_lang_list(lang)  # List of language candidates
        self._domain_cache = {}      # Cached gettext translators by domain

    # -----------------------------------------------------------------------

    def _load_translation(self, domain: str):
        """Attempt to load a translation for a given domain.

        First tries the full language list (self._lang).
        If it fails, falls back to self._default_lang.
        If all attempts fail, returns a dummy translator that returns original messages.

        :param domain: (str) Translation domain (e.g., "sppas")
        :return: (GNUTranslations | NullTranslations) A gettext translation object with `gettext()` method

        """
        try:
            t = gettext.translation(domain, self._po_path, self._lang)
            logging.debug(f"Translator for domain {domain} initialized with "
                          f"languages: {self._lang}")
            logging.debug(f" ... Loaded languages: {t.info().get('language', 'unknown')}")
            return t
        except IOError:
            logging.warning(f"Can't load translation for domain: {domain} {self._lang}.")
            try:
                t = gettext.translation(domain, self._po_path, self._default_lang)
                logging.debug(f"Translator for domain {domain} initialized with "
                              f"default languages: {self._default_lang}.")
                logging.debug(f" ... Loaded languages: {t.info().get('language', 'unknown')}")
                return t
            except IOError:
                logging.error(f"No translation available for domain '{domain}' "
                              f"in path {self._po_path}.")
                # Return a fallback that just echoes messages
                return gettext.NullTranslations()

    # -----------------------------------------------------------------------

    def get_translator(self, domain: str):
        """Return a cached translator for the given domain, or load it.

        """
        if domain not in self._domain_cache:
            self._domain_cache[domain] = self._load_translation(domain)

        return self._domain_cache[domain]

    # -----------------------------------------------------------------------

    def gettext(self, message: str, domain: str | None = None) -> str:
        """Translate a message using the specified domain, or return it unchanged.

        :param message: (str) Text to translate
        :param domain: (str|None) Translation domain, or None to return the raw message
        :return: (str) Translated message

        """
        if domain is not None:
            # logging.debug(f" =====>>>>> want to translate {message} in {domain}")
            _domain_translator = self.get_translator(domain)
            message = _domain_translator.gettext(message)
            # logging.debug(f" ==========================>>>> Got: {message}")
            # HERE IS THE PROBLEM: message is in French even if languages = ['en', 'fr']

        return message

    # -----------------------------------------------------------------------

    def get_default_lang(self) -> str:
        """Return the default language code (e.g., "en", "fr")."""
        return self._default_lang[0]


# ---------------------------------------------------------------------------
# Global translator manager, initialized with system-preferred language.
# It remains unset until set_language() is explicitly called.
# ---------------------------------------------------------------------------


if 'translator' not in globals():
    languages = sg.get_lang_list()
    if len(languages) > 0:
        translator = TranslatorManager(languages[0])
    else:
        translator = None

# ---------------------------------------------------------------------------
# Public API to set the global translation language
# ---------------------------------------------------------------------------


def set_language(lang: str | None = None):
    """Set the current language for translations.

    This method initializes or re-initializes the global translator.

    :param lang: Language code (e.g., "en", "fr"). If None, tries system default.

    """
    logging.debug("Set translator, with requested language: {:s}".format(lang))
    global translator
    if lang is None:
        lang = sg.get_lang_list(sg.__lang__)[0]
    translator = TranslatorManager(lang)
