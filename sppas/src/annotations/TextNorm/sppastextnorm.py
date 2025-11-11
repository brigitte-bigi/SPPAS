# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TextNorm.sppastextnorm.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  SPPAS integration of Text Normalization automatic annotation.

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
import logging

from sppas.core.config import paths
from sppas.core.coreutils import info

from sppas.src.resources import sppasDictRepl
from sppas.src.resources import sppasVocabulary

from sppas.src.anndata import sppasTrsRW
from sppas.src.anndata import sppasTranscription
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from ..baseannot import sppasBaseAnnotation
from ..searchtier import sppasFindTier
from ..annotationsexc import AnnotationOptionError
from ..annotationsexc import EmptyInputError
from ..annotationsexc import EmptyOutputError
from ..annotationsexc import NoTierInputError

from .tiernorm import TierNormalizer

# ---------------------------------------------------------------------------


class sppasTextNorm(sppasBaseAnnotation):
    """Text normalization automatic annotation.

    """
    def __init__(self, log=None):
        """Create a sppasTextNorm instance without any linguistic resources.

        :param log: (sppasLog) Human-readable logs.

        """
        super(sppasTextNorm, self).__init__("textnorm.json", log)
        self.__normalizer = TierNormalizer(logfile=log)

    # -----------------------------------------------------------------------

    def load_resources(self, vocab_filename, lang="und", **kwargs):
        """Fix the list of words of a given language.

        It allows a better tokenization, and enables the language-dependent
        modules like num2letters.

        :param vocab_filename: (str) File with the orthographic transcription
        :param lang: (str) the language code

        """
        if os.path.isfile(vocab_filename) is True:
            voc = sppasVocabulary(vocab_filename)
        else:
            voc = sppasVocabulary()
            logging.warning("Vocabulary file {:s} for language {:s} not found."
                            "".format(vocab_filename, lang))
        self.__normalizer = TierNormalizer(voc, lang, logfile=self.logfile)
        self.logfile.print_message((info(1164, "annotations")).format(len(voc)), indent=0)

        # Replacement dictionary
        replace_filename = os.path.join(paths.resources, "repl", lang + ".repl")
        if os.path.isfile(replace_filename) is True:
            dict_replace = sppasDictRepl(replace_filename, nodump=True)
        else:
            dict_replace = sppasDictRepl()
            logging.warning('Replacement vocabulary not found.')
        self.__normalizer.set_repl(dict_replace)
        self.logfile.print_message((info(1166, "annotations")).format(len(dict_replace)), indent=0)

        # Punctuations dictionary
        punct_filename = os.path.join(paths.resources, "vocab", "Punctuations.txt")
        if os.path.isfile(punct_filename) is True:
            vocab_punct = sppasVocabulary(punct_filename, nodump=True)
        else:
            vocab_punct = sppasVocabulary()
        self.__normalizer.set_punct(vocab_punct)

        # Number dictionary
        number_filename = os.path.join(paths.resources, 'num', lang.lower() + '_num.repl')
        if os.path.exists(number_filename) is True:
            numbers = sppasDictRepl(number_filename, nodump=True)
        else:
            numbers = sppasDictRepl()
            logging.warning('Dictionary of numbers not found.')
        self.__normalizer.set_num(numbers)

    # -----------------------------------------------------------------------
    # Methods to fix options
    # -----------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options. Available options are:

            - faked
            - std
            - custom

        :param options: (sppasOption)

        """
        for opt in options:

            key = opt.get_key()
            if key == "faked":
                self.set_faked(opt.get_value())

            elif key == "std":
                self.set_std(opt.get_value())

            elif key == "custom":
                self.set_custom(opt.get_value())

            elif key == "occ_dur":
                self.set_occ_dur(opt.get_value())

            elif key == "tok_speech":
                self.set_tok_not_sil(opt.get_value())

            elif "pattern" in key:
                self._options[key] = opt.get_value()

            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_faked(self, value):
        """Fix the faked option.

        :param value: (bool) Create a faked tokenization

        """
        self._options['faked'] = value

    # -----------------------------------------------------------------------

    def set_std(self, value):
        """Fix the std option.

        :param value: (bool) Create a standard tokenization

        """
        self._options['std'] = value

    # -----------------------------------------------------------------------

    def set_custom(self, value):
        """Fix the custom option.

        :param value: (bool) Create a customized tokenization

        """
        self._options['custom'] = value

    # -----------------------------------------------------------------------

    def set_occ_dur(self, value):
        """Fix the occurrences and duration tiers generation option.

        :param value: (bool) Create a tier with nb of tokens and duration

        """
        self._options['occ_dur'] = value

    # -----------------------------------------------------------------------

    def set_tok_not_sil(self, value):
        """Fix the token is speech tiers generation option.

        :param value: (bool) nb of tokens estimated without not-events ones

        """
        self._options["tok_speech"] = value

    # -----------------------------------------------------------------------
    # Methods to tokenize series of data
    # -----------------------------------------------------------------------

    def convert(self, tier):
        """Text normalization of all labels of a tier.

        :param tier: (sppasTier) the orthographic transcription (standard or EOT)
        :returns: A tuple with 3 tiers named:
            - "Tokens-Faked",
            - "Tokens-Std",
            - "Tokens-Custom"

        """
        if tier is None:
            raise IOError('No tier found.')
        if tier.is_empty() is True:
            raise EmptyInputError(name=tier.get_name())

        tokens_faked = None
        if self._options['faked'] is True:
            actions = ['replace', "tokenize", "numbers", "lower", "punct"]
            tokens_faked = self.__normalizer.normalize_tier(tier, actions)
            tokens_faked.set_name("Tokens")

        tokens_std = None
        if self._options['std'] is True:
            actions = ['std', 'replace', "tokenize", "numbers", "lower", "punct"]
            tokens_std = self.__normalizer.normalize_tier(tier, actions)
            tokens_std.set_name("Tokens-Std")

        tokens_custom = None
        if self._options['custom'] is True:
            actions = ['std', 'tokenize']
            tokens_custom = self.__normalizer.normalize_tier(tier, actions)
            tokens_custom.set_name("Tokens-Custom")

        # Align Faked and Standard
        if tokens_faked is not None and tokens_std is not None:
            self.__force_align_tiers(tokens_std, tokens_faked)

        return tokens_faked, tokens_std, tokens_custom

    # ------------------------------------------------------------------------

    def occ_dur(self, tier):
        """Create a tier with labels and duration of each annotation.

        :param tier:

        """
        occ = sppasTier('Occ%s' % tier.get_name())
        dur = sppasTier('Dur%s' % tier.get_name())
        for ann in tier:
            labels = ann.get_labels()
            nb_occ = len(labels)
            if self._options["tok_speech"] is True:
                # Do not count all labels but only the ones with no events
                nb_occ = 0
                for label in labels:
                    if label.get_best().is_speech() is True:
                        nb_occ += 1
            location = ann.get_location()
            duration = location.get_best().duration().get_value()
            occ.create_annotation(
                location.copy(),
                sppasLabel(sppasTag(nb_occ, tag_type="int"))
            )
            dur.create_annotation(
                ann.get_location().copy(),
                sppasLabel(sppasTag(round(duration, 4), tag_type="float"))
            )
        return occ, dur

    # ------------------------------------------------------------------------
    # Apply the annotation on one given file
    # -----------------------------------------------------------------------

    def get_inputs(self, input_files):
        """Return the the tier with aligned tokens.

        :param input_files: (list)
        :raise: NoTierInputError
        :return: (sppasTier)

        """
        tier = None
        annot_ext = self.get_input_extensions()

        for filename in input_files:
            if filename is None:
                continue
            fn, fe = os.path.splitext(filename)
            if tier is None and fe in annot_ext[0]:
                parser = sppasTrsRW(filename)
                trs_input = parser.read()
                tier = sppasFindTier.transcription(trs_input)
                if tier is not None:
                    if self.logfile:
                        self.logfile.print_message("Input tier to be normalized: "
                                                   "{}".format(tier.get_name()), indent=1)
                    return tier

        # Check input tier
        logging.error("No tier with an orthographic transcription was found.")
        raise NoTierInputError

    # -----------------------------------------------------------------------

    def run(self, input_files, output=None):
        """Run the automatic annotation process on an input.

        :param input_files: (list of str) orthographic transcription
        :param output: (str) the output file name
        :returns: (sppasTranscription)

        """
        # Get input tier to tokenize
        tier_input = self.get_inputs(input_files)

        # Tokenize the tier
        tier_faked_tokens, tier_std_tokens, tier_custom = self.convert(tier_input)

        # Create the transcription result
        trs_output = sppasTranscription(self.name)
        if tier_faked_tokens is not None:
            trs_output.append(tier_faked_tokens)
        if tier_std_tokens is not None:
            trs_output.append(tier_std_tokens)
        if tier_custom is not None:
            trs_output.append(tier_custom)

        if len(trs_output) > 0:
            if self._options["occ_dur"] is True:
                tier_occ, tier_dur = self.occ_dur(trs_output[0])
                trs_output.append(tier_occ)
                trs_output.append(tier_dur)
                # trs_output.add_hierarchy_link("TimeAssociation", trs_output[0], tier_occ)
                # trs_output.add_hierarchy_link("TimeAssociation", trs_output[0], tier_dur)

        trs_output.set_meta('text_normalization_result_of', input_files[0])
        trs_output.set_meta('language_iso', "iso639-3")
        trs_output.set_meta('language_name_0', "Undetermined")
        if len(self.__normalizer.lang) == 3:
            trs_output.set_meta('language_code_0', self.__normalizer.lang)
            trs_output.set_meta('language_url_0', "https://iso639-3.sil.org/code/"+self.__normalizer.lang)
        else:
            trs_output.set_meta('language_code_0', "und")
            trs_output.set_meta('language_url_0', "https://iso639-3.sil.org/code/und")

        # Save in a file
        if output is not None:
            if len(trs_output) > 0:
                output_file = self.fix_out_file_ext(output)
                parser = sppasTrsRW(output_file)
                parser.write(trs_output)
                return [output_file]
            else:
                raise EmptyOutputError

        return trs_output

    # -----------------------------------------------------------------------

    def get_output_pattern(self):
        """Pattern this annotation uses in an output filename."""
        return self._options.get("outputpattern", "-token")

    # -----------------------------------------------------------------------
    # Private: some workers...
    # -----------------------------------------------------------------------

    def __force_align_tiers(self, std_tier, faked_tier):
        """Force standard spelling and faked spelling to share the same
        number of tokens.

        :param std_tier: (sppasTier)
        :param faked_tier: (sppasTier)

        """
        if self._options['std'] is False:
            return

        i = 0
        # for each annotation of both tiers
        for ann_std, ann_faked in zip(std_tier, faked_tier):
            i += 1
            # for each label of both annotations
            for label_std, label_faked in zip(ann_std.get_labels(), ann_faked.get_labels()):
                # for each alternative tag of each label
                for ((text_std, s1), (text_faked, s2)) in zip(label_std, label_faked):
                    try:
                        texts, textf = self.__align_tiers(text_std.get_content(),
                                                          text_faked.get_content())
                        text_std.set_content(texts)
                        text_faked.set_content(textf)

                    except:
                        self.logfile.print_message(
                            "Standard/Faked tokens matching error, "
                            "at interval {:d}\n".format(i), indent=2, status=1)
                        self.logfile.print_message(text_std.get_content(), indent=3)
                        self.logfile.print_message(text_faked.get_content(), indent=3)
                        self.logfile.print_message("Fall back on faked.", indent=3, status=3)
                        text_std.set_content(text_faked.get_content())

    # -----------------------------------------------------------------------

    def __align_tiers(self, std, faked):
        """Align standard spelling tokens with faked spelling tokens.

        :param std: (str)
        :param faked: (str)
        :returns: a tuple of std and faked

        """
        stds = std.split()
        fakeds = faked.split()
        if len(stds) == len(fakeds):
            return std, faked

        tmp = []
        for f in fakeds:
            toks = f.split('_')
            for t in toks:
                tmp.append(t)
        fakeds = tmp[:]

        num_tokens = len(stds)
        i = 0
        while i < num_tokens:
            if "'" in stds[i]:
                if not stds[i].endswith("'") and fakeds[i].endswith("'"):
                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            if "-" in stds[i]:
                if not stds[i].endswith("-") and "-" not in fakeds[i]:

                    fakeds[i] = fakeds[i] + fakeds[i+1]
                    del fakeds[i+1]

            num_underscores = stds[i].count('_')
            if num_underscores > 0:
                if not self.__normalizer.vocab.is_unk(stds[i]):
                    n = num_underscores + 1
                    fakeds[i] = "_".join(fakeds[i:i+n])
                    del fakeds[i+1:i+n]

            i += 1

        if len(stds) != len(fakeds):
            raise ValueError
        return std, " ".join(fakeds)
