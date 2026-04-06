# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.Syll.rules.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Rules of the syllabification system.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

from sppas.core.config import symbols
from sppas.core.config import separators
from sppas.core.coreutils import sppasUnicode

# ----------------------------------------------------------------------------


class SyllRules(object):
    """Manager of a set of rules for syllabification.

    The rules we propose follow usual phonological statements for most of the
    corpus. A configuration file indicates phonemes, classes and rules.
    This file can be edited and modified to adapt the syllabification.

    The syllable configuration file is a simple ASCII text file that the user
    can change as needed.

    """

    BREAK_SYMBOL = "#"

    # -----------------------------------------------------------------------

    def __init__(self, filename=None):
        """Create a new SyllRules instance.

        :param filename: (str) Name of the file with the rules.

        """
        self.__filename = filename
        self.general = dict()    # list of general rules
        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules
        self.phonclass = dict()  # list of tuple (phoneme, class)

        if filename is not None:
            self.load(filename)
        else:
            self.reset()

    # ------------------------------------------------------------------------

    def get_filename(self):
        """Return the name of the file with rules or None."""
        return self.__filename

    # ------------------------------------------------------------------------

    def reset(self):
        """Reset the set of rules."""
        self.__filename = None
        self.general = dict()  # list of general rules
        self.general["VV"] = 0
        self.general["VXV"] = 0
        self.general["VXXV"] = 1
        self.general["VXXXV"] = 1
        self.general["VXXXXV"] = 1
        self.general["VXXXXXV"] = 2
        self.general["VXXXXXV"] = 3
        self.general["VXXXXXXV"] = 3

        self.exception = dict()  # list of exception rules
        self.gap = dict()        # list of gap rules

        self.phonclass = dict()  # list of tuple (phoneme, class)
        for phone in symbols.all:
            self.phonclass[phone] = SyllRules.BREAK_SYMBOL

    # ------------------------------------------------------------------------

    def load(self, filename):
        """Load the rules from a file.

        :param filename: (str) Name of the file with the rules.

        """
        self.reset()

        with open(filename, "r") as f:
            lines = f.readlines()
            f.close()

        for line_nb, line in enumerate(lines, 1):
            sp = sppasUnicode(line)
            line = sp.to_strip()

            wds = line.split()
            if len(wds) == 3:
                if wds[0] == "PHONCLASS":
                    self.phonclass[wds[1]] = wds[2]

                elif wds[0] == "GENRULE":
                    self.general[wds[1]] = int(wds[2])

                elif wds[0] == "EXCRULE":
                    self.exception[wds[1]] = int(wds[2])

            if len(wds) == 7:
                if wds[0] == "OTHRULE":
                    s = " ".join(wds[1:6])
                    self.gap[s] = int(wds[6])

        self.__filename = filename

    # ------------------------------------------------------------------------

    def get_class(self, phoneme):
        """Return the class identifier of the phoneme.

        If the phoneme is unknown, the break symbol is returned.

        :param phoneme: (str) A phoneme
        :returns: class of the phoneme or break symbol

        """
        return self.phonclass.get(phoneme, SyllRules.BREAK_SYMBOL)

    # ------------------------------------------------------------------------

    def get_struct(self, phoneme):
        """Return the struct identifier of the phoneme.

        If the phoneme is unknown, the break symbol is returned.

        :param phoneme: (str) A phoneme
        :returns: Either 'V' or 'C' or break symbol

        """
        classe = self.phonclass.get(phoneme, SyllRules.BREAK_SYMBOL)
        if classe == SyllRules.BREAK_SYMBOL:
            return SyllRules.BREAK_SYMBOL
        if classe in ('V', 'W'):
            return "V"
        return "C"

    # ------------------------------------------------------------------------

    def is_exception(self, rule):
        """Return True if the rule is an exception rule.

        :param rule: (str)

        """
        return rule in self.exception

    # ------------------------------------------------------------------------

    def get_boundary(self, phonemes):
        """Get the index of the syllable boundary (EXCRULES or GENRULES).

        Phonemes are separated with the symbol defined by separators.phonemes
        variable.

        :param phonemes: (str) Sequence of phonemes to syllabify
        :returns: (int) boundary index or -1 if phonemes don't match any rule.

        """
        sp = sppasUnicode(phonemes)
        phonemes = sp.to_strip()
        phon_list = phonemes.split(separators.phonemes)
        classes = ""
        for phon in phon_list:
            classes += self.get_class(phon)

        # search into exception
        if classes in self.exception:
            return self.exception[classes]

        # search into general
        for key, val in self.general.items():
            if len(key) == len(phon_list):
                return val

        return -1

    # ------------------------------------------------------------------------

    def get_class_rules_boundary(self, classes):
        """Get the index of the syllable boundary (EXCRULES or GENRULES).

        :param classes: (str) The class sequence to syllabify
        :returns: (int) boundary index or -1 if it does not match any rule.

        """
        # search into exception
        if classes in self.exception:
            return self.exception[classes]

        # search into general
        for key, val in self.general.items():
            if len(key) == len(classes):
                return val

        return 0

    # ------------------------------------------------------------------------

    def get_gap(self, phonemes):
        """Return the shift to apply (OTHRULES).

        :param phonemes: (str) Phonemes to syllabify
        :returns: (int) boundary shift

        """
        for gp in self.gap:
            if gp == phonemes:
                return self.gap[gp]

            # Search by replacing a phoneme by "ANY"
            if gp.find("ANY") > -1:
                r = gp.split()
                phons = phonemes.split()
                new_phonemes = ""
                if len(r) == len(phons):
                    # For each phoneme, replace the ANY
                    for ph in range(len(r)):
                        if r[ph] == "ANY":
                            new_phonemes += "ANY "
                        else:
                            new_phonemes += phons[ph] + " "
                    new_phonemes = new_phonemes.strip()

                if gp == new_phonemes:
                    return self.gap[gp]

        return 0
