# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.annotations.__init__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The automatic annotations of SPPAS.

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
annotations: automatic annotations.
*****************************************************************************

This package includes all the automatic annotations, each one in a package
and the classes to manage the data to be annotated and the resulting
annotated data.

Requires the following other packages:

* config
* utils
* exc
* structs
* wkps
* resources
* anndata
* imgdata    -- if "video" feature enabled
* videodata  -- if "video" feature enabled

"""

from .FaceSights import ImageFaceLandmark

from .imports import *
from .autils import sppasFiles
from .baseannot import sppasBaseAnnotation
from .diagnosis import sppasDiagnosis
from .infotier import sppasMetaInfoTier
from .report import sppasAnnReport
from .searchtier import sppasFindTier
from .param import sppasParam
from .manager import sppasAnnotationsManager

# ---------------------------------------------------------------------------


__all__ = (
    'sppasFindTier',
    'sppasParam',
    'sppasFiles',
    'sppasBaseAnnotation',
    'sppasDiagnosis',
    'sppasAnnReport',
    'sppasMomel',
    'sppasIntsint',
    'sppasFillIPUs',
    'sppasSearchIPUs',
    'sppasTextNorm',
    'sppasPhon',
    'sppasAlign',
    'sppasSyll',
    'sppasTGA',
    'sppasIVA',
    'sppasSelfRepet',
    'sppasActivity',
    'sppasRMS',
    'sppasFormants',
    'sppasOtherRepet',
    "sppasOverActivity",
    'StopWords',
    'sppasStopWords',
    'sppasLexMetric',
    'sppasReOcc',
    'sppasAnnotationsManager',
    'sppasLexRep',
    'sppasHandPose',
    'sppasFaceDetection',
    'sppasFaceSights',
    "ImageFaceLandmark"
)
