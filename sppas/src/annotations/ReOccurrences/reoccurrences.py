# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.ReOccurrences.reoccurrences.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Re-Occurrences detection.

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


class ReOccurences(object):
    """Manager for a set of re-occurrences annotations.

    """

    def __init__(self):
        super(ReOccurences, self).__init__()

    # -----------------------------------------------------------------------

    @staticmethod
    def compare_labels(label1, label2):
        """Compare two labels.

        :param label1: (sppasLabel)
        :param label2: (sppasLabel)
        :returns: (bool) Number of tags they have in common

        """
        tags1 = [tag.get_typed_content() for tag, score in label1]
        tags2 = [tag.get_typed_content() for tag, score in label2]
        union = tags1 + tags2
        diff = set(union)

        return len(union) - len(diff)

    # -----------------------------------------------------------------------

    @staticmethod
    def eval(ann1, anns2):
        """Return the list of re-occurrences.

        An annotation in anns2 is matching ann1 if all labels of ann1 are
        in ann2. It is not one-to-one: some labels of ann2 could not match
        those of ann1.

        :param ann1: (sppasAnnotation)
        :param anns2: (list of sppasAnnotation)
        :returns: (list of sppasAnnotation)

        """
        reocc = list()
        for ann2 in anns2:

            # Evaluate if all labels of ann1 are also in ann2
            match = False
            for label1 in ann1.get_labels():
                match = False
                for label2 in ann2.get_labels():
                    equals = ReOccurences.compare_labels(label1, label2)
                    # we've found that a label of ann2 is matching label1
                    # we can stop to search it anymore. label1 == label2
                    if equals > 0:
                        match = True
                        break

                # As soon as a label1 is missing in ann2, we can stop:
                # ann2 is not a re-occurrence of ann1
                if match is False:
                    break

            if match is True:
                reocc.append(ann2)

        return list(set(reocc))
