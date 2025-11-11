# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.ReOccurrences.reoccset.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  data structure for a set of re-occurrences.

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

from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasTag
from sppas.src.anndata import sppasLabel

from sppas.src.structs import sppasBaseSet

# ---------------------------------------------------------------------------


class sppasAnnReOccSet(sppasBaseSet):
    """Manager for a set of re-occurrences annotations.

    A sppasAnnReOccSet() manages a dictionary with:

        - key: an annotation
        - value: a list of re-occurring annotations

    """

    def __init__(self):
        """Create a sppasAnnReOccSet instance."""
        super(sppasAnnReOccSet, self).__init__()

    # -----------------------------------------------------------------------

    def copy(self):
        """Make a deep copy of self.

        Overridden to return a sppasAnnSet() instead of a sppasBaseSet().

        """
        d = sppasAnnReOccSet()
        for data, value in self._data_set.items():
            d.append(data, value)

        return d

    # -----------------------------------------------------------------------

    def to_tier(self):
        """Create tiers from the data set.

        :returns: (List of sppasTier)

        """
        tier_src = sppasTier("Src")
        tier_nb = sppasTier("SrcNbReOcc")
        tier_reocc = sppasTier("ReOcc")

        for i, ann in enumerate(self._data_set):

            anns_reocc = self._data_set[ann]

            # the "source" annotation
            new_ann1 = tier_src.create_annotation(
                ann.get_location().copy(),
                sppasLabel(sppasTag("S" + str(i))))
            self.__ann_copy_metadata(ann, new_ann1)

            # the "nb re-occ" annotation
            new_ann2 = tier_nb.create_annotation(
                ann.get_location().copy(),
                sppasLabel(sppasTag(len(anns_reocc), "int")))
            self.__ann_copy_metadata(ann, new_ann2)

            # the "values", i.e. the re-occurrences themselves
            for reocc in anns_reocc:
                label = sppasLabel(sppasTag("R" + str(i)))
                already = tier_reocc.find(reocc.get_lowest_localization(),
                                          reocc.get_highest_localization(),
                                          overlaps=False)
                if len(already) == 0:
                    tier_reocc.create_annotation(
                        reocc.get_location().copy(),
                        label)
                else:
                    already[0].append_label(label)

        return [tier_src, tier_nb, tier_reocc]

    # -----------------------------------------------------------------------

    def __ann_copy_metadata(self, src, dest):
        """Copy all metadata, except the 'id'."""
        for key in src.get_meta_keys():
            if key != 'id':
                dest.set_meta(key, src.get_meta(key))

    # -----------------------------------------------------------------------

    def __and__(self, other):
        """Implements the '&' operator between 2 data sets.

        Overridden to return a sppasAnnReOccSet() instead of a sppasBaseSet().

        """
        d = sppasAnnReOccSet()
        for data in self:
            if data in other:
                d.append(data, self.get_value(data))
                d.append(data, other.get_value(data))

        return d
