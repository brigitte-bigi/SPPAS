# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.SpeechSeg.segtojson.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Speech segmentation output formatter to json.

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

    Copyright (C) 2011-2023 Brigitte Bigi
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

from sppas.src.annotations.Align.models.tiermapping import sppasMappingTier
from sppas.src.anndata.aio.aioutils import serialize_labels

# ---------------------------------------------------------------------------


class FormatTrsSeg(object):
    """Format speech segmentation output.

    """

    def __init__(self, map_table=None):
        self.data = {
            'phonemes': {},
            'silence': {},
            'words': {},
            'expressions': {}}

        # Base energy value
        self.base_energy = 0.75

        # Energy modulation coeff from SPPAS intensity coeff
        self.mod_energy = 0.20

        # Mapping table of phonemes
        self.__mapping = sppasMappingTier(map_table)
        self.__mapping.set_keep_miss(True)  # keep unknown entries as given
        self.__mapping.set_miss_symbol("")  # not used!
        self.__mapping.set_delimiters([])   # will use longest matching

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the data."""
        self.data = {
            'phonemes': {},
            'silence': {},
            'words': {},
            'expressions': {}}

    # -----------------------------------------------------------------------

    def trs_phn_to_map(self, trs):
        """Map the phonemes of the phonemes tier of the given trs.

        :param trs: (sppasTranscription)

        """
        # Map the phonemes of the tier "PhonAlign"
        tier_phon = trs.find("PhonAlign")
        new_tier = self.__mapping.map_tier(tier_phon)
        new_tier.set_name(tier_phon.get_name())

        # Replace the current phon tier by the mapped one
        trs.pop(trs.get_tier_index_id(tier_phon.get_id()))
        trs.append(new_tier)

    # -----------------------------------------------------------------------

    def trs_to_data_norm(self, trs):
        """Fill in the data normalized structure from the given trs.

        :param trs: (sppasTranscription)

        """
        tier_rms = trs.find("Intensity")
        tier_phon = trs.find("PhonAlign")
        tier_tok = trs.find("TokensAlign")
        for a in tier_phon:
            start = round(a.get_location().get_best().get_begin().get_midpoint(), 3)
            end = round(a.get_location().get_best().get_end().get_midpoint(), 3)
            phn = serialize_labels(a.get_labels(), " ")
            energy = -1
            if tier_rms is not None:
                ra = tier_rms.find(start, end, overlaps=False)
                if ra is not None:
                    value = ra[0].get_labels()[0].get_best().get_typed_content()
                    if value == 0:
                        energy = 0
                    else:
                        energy = self.base_energy + ((value-2) * self.mod_energy)
                else:
                    energy = self.base_energy
            # ok. set to the dict.
            self.data['phonemes'][start] = (phn, start, end, energy)

        for a in tier_tok:
            start = round(a.get_location().get_best().get_begin().get_midpoint(), 3)
            end = round(a.get_location().get_best().get_end().get_midpoint(), 3)
            tok_tag = a.get_best_tag(0)
            if tok_tag.is_silence() or tok_tag.is_pause():
                self.data['silence'][start] = (start, end, end-start)
            else:
                self.data['words'][start] = (tok_tag.get_content(), start, end)
