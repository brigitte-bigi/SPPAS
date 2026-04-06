# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TextNorm.tokenize.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: Tokenization module for the multilingual text norm system.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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
import re

from sppas.core.coreutils import sppasUnicode

# ---------------------------------------------------------------------------


class sppasTokenSegmenter(object):
    """Create words from tokens on the basis of a lexicon.

    This is a totally language independent method, based on a longest
    matching algorithm to aggregate tokens into words. Words of a lexicon
    are found and:

     1/ unbind or not if they contain a separator character:

        - rock'n'roll -> rock'n'roll
        - I'm -> I 'm
        - it's -> it 's

     2/ bind using a character separator like for example, with '_':

        - parce que -> parce_que
        - rock'n roll -> rock'n_roll

    """

    SEPARATOR = "_"
    STICK_MAX = 7

    # -------------------------------------------------------------------------

    def __init__(self, vocab=None):
        """Create a new sppasTokenSegmenter instance.

        :param vocab: (Vocabulary)

        """
        self.__vocab = vocab
        self.__separator = sppasTokenSegmenter.SEPARATOR
        self.__aggregate_max = sppasTokenSegmenter.STICK_MAX

    # -------------------------------------------------------------------------

    def set_aggregate_max(self, value=STICK_MAX):
        """Fix the maximum number of words to stick.

        This is a language dependant value. For French, it's 5 with the word:
        "au fur et à mesure". But it can be more to stick phrases instead of
        words for example.

        :param value: (int) Maximum number of tokens to aggregate/stick.

        """
        value = int(value)
        if value < 1:
            raise ValueError('set_aggregate_max: value should be > 0.')
        
        if value > 100:
            raise ValueError('set_aggregate_max: value should be < 100.')

        self.__aggregate_max = value

    # -------------------------------------------------------------------------

    def set_separator(self, char=SEPARATOR):
        """Fix the character to separate tokens.

        :param char: (char) Separator character. Can be an empty string.

        """
        char = str(char)
        if len(char) > 0:
            char = char[0]

        self.__separator = char

    # -------------------------------------------------------------------------

    def __stick_longest_lr(self, phrase, separator):
        """Return the longest first word of a phrase.

        A longest matching algorithm is applied from left to right.

        :param phrase: (str)
        :returns: tuple of (index of the first longest token, the longest token)

        """
        tab_toks = phrase.split(" ")
        token = tab_toks[0]
        i = len(tab_toks)

        if self.__vocab is None:
            return 1, token

        while i > 0:
            # try to aggregate all tokens -- the longest token
            token = separator.join(tab_toks)

            # next round will try without the last token
            tab_toks.pop()
            i -= 1

            # stop the "while" when the token is in the vocabulary
            if self.__vocab.is_unk(token) is False:
                break
            # new in SPPAS 4.10 to get the same result with
            # L'assiette // l'assiette
            if self.__vocab.is_unk(token.lower()) is False:
                break

        # the first real token is the first given token
        return i, sppasUnicode(token).to_strip()

    # -----------------------------------------------------------------------

    def bind(self, utt):
        """Bind tokens of an utterance using a specific character.

        :param utt: (list) List of tokens of an utterance (a transcription, a sentence, ...)
        :returns: A list of strings

        """
        new_utt = list()

        idx_start = 0
        while idx_start < len(utt):

            # use the longest matching to aggregate the current token with the next ones
            idx_end = min(len(utt), idx_start+self.__aggregate_max+1)
            phrase = " ".join(utt[idx_start:idx_end])
            idx_end, word = self.__stick_longest_lr(sppasUnicode(phrase).to_strip(), self.__separator)

            new_utt.append(word)
            idx_start += idx_end + 1

        return new_utt

    # -----------------------------------------------------------------------

    def unbind(self, utt):
        """Unbind tokens containing - or ' or . depending on rules.

        :param utt: (list) List of tokens of an utterance (a transcription, a sentence, ...)
        :returns: A list of strings

        """
        new_utt = list()
        for tok in utt:
            is_unknown = self.__vocab.is_unk(tok.lower().strip())
            is_sampa = tok.startswith('/') and tok.endswith('/')
            is_buzz = tok.startswith('$') and tok.endswith('$')
            is_trunc = tok.endswith('-')
            # a missing compound word?
            #   --> an unknown token
            #   --> containing a special character
            #   --> that is not a truncated word
            #   --> not in a sampa sequence!
            # example: L'abat-jour, d'entre, paris-marseille
            if is_unknown is True \
                    and ("-" in tok or "'" in tok or "." in tok) \
                    and is_sampa is False\
                    and is_buzz is False\
                    and is_trunc is False:

                # KEEP the special chars in the array!
                tab_split = re.split("([-'.])", tok)
                tab_tok = list(entry for entry in tab_split if len(entry) > 0)
                idx_start = 0
                while idx_start < len(tab_tok):

                    # use the longest matching to aggregate the current token with the next ones
                    idx_end = min(len(tab_tok), idx_start + 5)
                    phrase = " ".join(tab_tok[idx_start:idx_end])
                    idx_end, word = self.__stick_longest_lr(sppasUnicode(phrase).to_strip(), "")
                    new_utt.append(word)
                    idx_start += idx_end + 1

            else:
                new_utt.append(sppasUnicode(tok).to_strip())

        return new_utt
