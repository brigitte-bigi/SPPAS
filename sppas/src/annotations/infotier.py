"""
:filename: sppas.src.annotations.infotier.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Tier with meta information about SPPAS.

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

from sppas.src.anndata import sppasMetaData
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLabel, sppasTag
from sppas.src.anndata import sppasLocation, sppasPoint, sppasInterval
from sppas.src.structs import sppasMetaInfo
from sppas.src.utils import sppasTime

# ---------------------------------------------------------------------------


class sppasMetaInfoTier(sppasMetaInfo):
    """Meta information manager about SPPAS.

    Manager of meta information about SPPAS.
    Allows to create a tier with activated meta-information.

    """

    def __init__(self, meta_object=None):
        """Create a new sppasMetaInfoTier instance.

        Add and activate all known information about SPPAS.

        :param meta_object: (sppasMetadata) where to get meta infos.

        """
        super(sppasMetaInfoTier, self).__init__()

        if meta_object is None:
            m = sppasMetaData()
            m.add_software_metadata()

            for key in m.get_meta_keys():
                self.add_metainfo(key, m.get_meta(key))
            self.add_metainfo('date', sppasTime().now)

        else:

            for key in meta_object.get_meta_keys():
                self.add_metainfo(key, meta_object.get_meta(key))

    # ------------------------------------------------------------------------

    def create_time_tier(self, begin, end, tier_name="MetaInformation"):
        """Create a tier with activated information as annotations.

        :param begin: (float) Begin midpoint value
        :param end: (float) End midpoint value
        :param tier_name: (str) Name of the tier to create
        :returns: sppasTier

        """
        active_keys = self.keys_enabled()
        if len(active_keys) == 0:
            return None

        tier_dur = float(end) - float(begin)
        ann_dur = round(tier_dur / float(len(active_keys)), 3)

        tier = sppasTier(tier_name)
        ann_begin = round(begin, 3)
        ann_end = begin + ann_dur
        for key in active_keys:
            value = self.get_metainfo(key)
            tag = sppasTag(key + "=" + value)

            tier.create_annotation(
                sppasLocation(
                    sppasInterval(sppasPoint(ann_begin),
                                  sppasPoint(ann_end))),
                sppasLabel(tag))
            ann_begin = ann_end
            ann_end = ann_begin + ann_dur

        tier[-1].get_location().get_best().set_end(sppasPoint(end))
        return tier
