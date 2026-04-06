# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.scoring.ubpa.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Estimates the Unit Boundary Positioning Accuracy and CI.

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

import sys


def _eval_index(step, value):
    m = (value % step)  # Estimate the rest
    d = (value-m)       # Make "d" an entire value
    index = d/step      # evaluate the index depending on step
    return int(index)


def _inc(vector, idx):
    if idx >= len(vector):
        toadd = idx - len(vector) + 1
        vector.extend([0]*toadd)
    vector[idx] += 1


def ubpa(vector, text, fp=sys.stdout, delta_max=0.04, step=0.01):
    """Estimate the Unit Boundary Positioning Accuracy.

    :param vector: contains the list of the delta values.
    :param text: one of "Duration", "Position Start", ...
    :param fp: a file pointer
    :param delta_max: Maximum delta duration to print result (default: 40ms)
    :param step: Delta time (default: 10ms)

    :returns: (tab_neg, tab_pos) with number of occurrences of each position

    """
    # Estimates the UBPA
    tab_neg = []
    tab_pos = []

    for delta in vector:
        if delta > 0.:
            idx = _eval_index(step, delta)
            _inc(tab_pos, idx)
        else:
            idx = _eval_index(step, delta*-1.)
            _inc(tab_neg, idx)

    # Print the result
    nb_values = len(vector)
    fp.write("|--------------------------------------------| \n")
    fp.write("|      Unit Boundary Positioning Accuracy    | \n")
    fp.write("|            Delta=T(hyp)-T(ref)             | \n")
    fp.write("|--------------------------------------------| \n")
    i = len(tab_neg)-1
    occ_success_sum = 0
    for value in reversed(tab_neg):
        if (i+1)*step <= delta_max:
            occ_success_sum += value
            percent = (value*100.) / nb_values
            fp.write("|  Delta-%s < -%.3f: %d (%.2f%%) \n" % (text, (i+1)*step, value, percent))
        i -= 1
    fp.write("|--------------------------------------------| \n")
    for i, value in enumerate(tab_pos):
        if (i+1)*step <= delta_max:
            occ_success_sum += value
            percent = round(((value*100.)/nb_values), 3)
            fp.write("|  Delta-%s < +%.3f: " % (text, ((i+1)*step)))
            fp.write("%d (%.2f%%)\n" % (value, percent))

    p = float(occ_success_sum) / float(nb_values)
    se = (p * (1 - p) / nb_values) ** 0.5  # standard error
    ci_low = p - 1.96 * se
    ci_high = p + 1.96 * se

    fp.write("|--------------------------------------------| \n")
    fp.write(f"| UBPA: {p * 100:.2f}% ({occ_success_sum}/{nb_values})                   |\n")
    fp.write(f"| 95% CI: [{ci_low * 100:.2f}%, {ci_high * 100:.2f}%]                   |\n")
    fp.write("|--------------------------------------------| \n")

