# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.ann.annset.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Manager for a set of annotations.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

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

    ---------------------------------------------------------------------

"""

from sppas.src.structs import sppasBaseSet

from ..tier import sppasTier

from .annlabel import sppasLabel
from .annlabel import sppasTag

# ---------------------------------------------------------------------------


class sppasAnnSet(sppasBaseSet):
    """Manager for a set of annotations.

    Mainly used with the data that are the result of the tier filter system.
    A sppasAnnSet() manages a dictionary with:

        - key: an annotation
        - value: a list of strings

    """

    def __init__(self):
        """Create a sppasAnnSet instance."""
        super(sppasAnnSet, self).__init__()

    # -----------------------------------------------------------------------

    def copy(self):
        """Make a deep copy of self.

        Overridden to return a sppasAnnSet() instead of a sppasBaseSet().

        """
        d = sppasAnnSet()
        for data, value in self._data_set.items():
            d.append(data, value)

        return d

    # -----------------------------------------------------------------------

    def to_tier(self, name="AnnSet", annot_value=False):
        """Create a tier from the data set.

        :param name: (str) Name of the tier to be returned
        :param annot_value: (bool) format of the resulting annotation label. \
            By default, the label of the annotation is used. Instead, \
            its value in the data set is used.

        :returns: (sppasTier)

        """
        tier = sppasTier(name)
        for ann in self._data_set:

            # create the labels
            labels = list()
            if annot_value is True:
                for value in self._data_set[ann]:
                    labels.append(sppasLabel(sppasTag(value)))
            else:
                for l in ann.get_labels():
                    labels.append(l.copy())

            # create the annotation
            new_ann = tier.create_annotation(ann.get_location().copy(),
                                             labels)

            # Copy all metadata, except the 'id'.
            for key in ann.get_meta_keys():
                if key != 'id':
                    new_ann.set_meta(key, ann.get_meta(key))

        # we should create a new hierarchy link "TimeSubSet" to link the
        # original tier and the filtered one.

        return tier

    # -----------------------------------------------------------------------

    def __and__(self, other):
        """Implements the '&' operator between 2 data sets.

        Overridden to return a sppasAnnSet() instead of a sppasBaseSet().

        """
        d = sppasAnnSet()
        for data in self:
            if data in other:
                d.append(data, self.get_value(data))
                d.append(data, other.get_value(data))

        return d
