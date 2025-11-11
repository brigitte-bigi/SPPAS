#!/usr/bin python
"""

:author:       Brigitte Bigi
:date:         2018-07-09
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2018 Brigitte Bigi, Laboratoire Parole et Langage

:summary:      Open an annotated file and filter to answer the following request:
               get tokens preceded by AND followed by a silence.

Use of this software is governed by the GNU Public License, version 3.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this script. If not, see <https://www.gnu.org/licenses/>.

"""

import sys
import os.path
sys.path.append(os.path.join("../../documentation", ".."))

from sppas.src.anndata import sppasTrsRW
from sppas.src.analysis import sppasTierFilters
from sppas.core.coreutils import u

# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


def get_tier(filename, tier_name, verbose=True):
    """ Get a tier from a file.

    :param filename: (str) Name of the annotated file.
    :param tier_name: (str) Name of the tier
    :param verbose: (bool) Print message
    :returns: (Tier)

    """
    # Read an annotated file.
    if verbose:
        print("Read file: {:s}".format(filename))
    parser = sppasTrsRW(filename)
    trs = parser.read()
    if verbose:
        print(" ... [  OK  ] ")

    # Get the expected tier
    if verbose:
        print("Get tier {:s}".format(tier_name))

    tier = trs.find(tier_name, case_sensitive=False)
    if tier is None:
        print("Tier not found.")
        sys.exit(1)
    if verbose:
        print(" ... [  OK  ] ")

    return tier

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

filename = 'F_F_B003-P9-merge.TextGrid'

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

# Read an annotated file.
tier = get_tier(filename, "TokensAlign")
tier.set_radius(0.005)
f = sppasTierFilters(tier)

# get tokens, except silences
annset_not_sil = f.tag(not_exact=u("#"))
tier_tokens = annset_not_sil.to_tier('Tokens')

# get silences
annset_sil = f.tag(exact=u("#"))
tier_silences = annset_sil.to_tier('Silences')

# Apply separately the relations and combine results
fr = sppasTierFilters(tier_tokens)
ann_set = fr.rel(tier_silences, 'meets') & fr.rel(tier_silences, 'metby')

for ann in ann_set:
    print(' - {}'.format(ann))
