# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.TGA.timegroupanalysis.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  The time group analyzer partly re-implemented

.. _This file is part of SPPAS: <https://sppas.org/>
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

from sppas.src.calculus.stats import variability
from sppas.src.calculus.stats.linregress import tga_linear_regression
from sppas.src.calculus.stats.descriptivesstats import sppasDescriptiveStatistics

# ----------------------------------------------------------------------------


class TimeGroupAnalysis(sppasDescriptiveStatistics):
    u"""Time Group Analyzer estimator class.

    TGA: Time Group Analyzer is an online tool for speech annotation mining
    written by Dafydd Gibbon (Universität Bielefeld).

    See: <http://wwwhomes.uni-bielefeld.de/gibbon/TGA/>

    This class estimates TGA on a set of data values, stored in a dictionary:

        - key is the name of the time group;
        - value is the list of durations of each segments in the time group.

    >>> d = {'tg1':[1.0, 1.2, 3.2, 4.1] , 'tg2':[2.9, 3.3, 3.6, 5.8]}
    >>> tga = TimeGroupAnalysis(d)
    >>> total = tga.total()
    >>> intercept, slope = tga.intercept_slope()
    >>> print(slope['tg_1'])
    >>> print(slope['tg_2'])

    """

    def __init__(self, dict_items):
        """TGA - The Time Group Analyzer.

        :param dict_items: (dict) a dict of a list of durations.

        """
        super(TimeGroupAnalysis, self).__init__(dict_items)

    # -----------------------------------------------------------------------
    # Specific estimators for speech rythm analysis
    # -----------------------------------------------------------------------

    def rPVI(self):
        """Estimate the Raw Pairwise Variability Index of data values.

        :returns: (dict) a dictionary of (key, nPVI) of float values

        """
        return dict((key, variability.rPVI(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def nPVI(self):
        """Estimate the Normalized Pairwise Variability Index of data values.

        :returns: (dict) a dictionary of (key, nPVI) of float values

        """
        return dict((key, variability.nPVI(values))
                    for key, values in self._items.items())

    # -----------------------------------------------------------------------

    def intercept_slope_original(self):
        """Estimate the intercept like the original TGA of data values.

        Create the list of points (x,y) of each TG where:
            - x is the position
            - y is the duration

        :returns: (dict) a dict of (key, (intercept,slope)) of float values

        """
        lin_reg = list()
        for key, values in self._items.items():
            points = [(pos, dur) for pos, dur in enumerate(values)]
            lin_reg.append((key, (tga_linear_regression(points))))

        return dict(lin_reg)

    # -----------------------------------------------------------------------

    def intercept_slope(self):
        """Estimate the intercept like AnnotationPro of data values.

        Create the list of points (x,y) of each TG where:
            - x is the timestamps
            - y is the duration

        :returns: (dict) a dict of (key, (intercept, slope)) of float values

        """
        lin_reg = list()
        for key, values in self._items.items():
            points = list()
            timestamp = 0.
            for duration in values:
                points.append((timestamp, duration))
                timestamp += duration
            lin_reg.append((key, (tga_linear_regression(points))))

        return dict(lin_reg)
