# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.calculus.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Package for the calculus of SPPAS.

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

*****************************************************************************
calculus: proposes some math on data.
*****************************************************************************

This package includes mathematical functions to estimate descriptive
statistics, for the scoring or in the domain of the information theory.

No required other package. This package is compatible with all versions of
Python (from 2.7 to 3.9).

"""

from .stats.descriptivesstats import sppasDescriptiveStatistics
from .scoring.kappa import sppasKappa
from .scoring.ubpa import ubpa

from .geometry.circle import observed_angle
from .geometry.distances import squared_euclidian, euclidian, manathan, minkowski, chi_squared
from .geometry.linear_fct import linear_fct, ylinear_fct, linear_values, slope, intercept, slope_intercept
from .stats.central import fsum, fmult, fmin, fmax, fmean, fmedian, fgeometricmean, fharmonicmean
from .stats.frequency import freq, percent, percentile, quantile
from .stats.linregress import tga_linear_regression, tansey_linear_regression
from .stats.linregress import gradient_descent, gradient_descent_linear_regression, compute_error_for_line_given_points
from .stats.moment import lmoment, lvariation, lskew, lkurtosis
from .stats.variability import lvariance, lstdev, lz, rPVI, nPVI
from .infotheory import sppasKullbackLeibler
from .infotheory import sppasEntropy
from .infotheory import find_ngrams
from .infotheory import symbols_to_items

__all__ = (
    "sppasDescriptiveStatistics",
    "sppasKappa",
    "squared_euclidian",
    "euclidian",
    "manathan",
    "minkowski",
    "chi_squared",
    "linear_fct",
    "ylinear_fct",
    "linear_values",
    "slope",
    "intercept",
    "slope_intercept",
    "fsum",
    "fmult",
    "fmin",
    "fmax",
    "fmean",
    "fmedian",
    "fgeometricmean",
    "fharmonicmean",
    "freq",
    "percent",
    "percentile",
    "quantile",
    "tga_linear_regression",
    "tansey_linear_regression",
    "gradient_descent",
    "gradient_descent_linear_regression",
    "compute_error_for_line_given_points",
    "lmoment",
    "lvariation",
    "lskew",
    "lkurtosis",
    "lvariance",
    "lstdev",
    "lz",
    "rPVI",
    "nPVI",
    "ubpa",
    "sppasKullbackLeibler",
    "sppasEntropy",
    "find_ngrams",
    "symbols_to_items",
    "observed_angle"
)
