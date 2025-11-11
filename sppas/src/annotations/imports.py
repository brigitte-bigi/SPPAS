"""
:filename: sppas.src.annotations.imports.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Import of all automatic annotations.

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

    ---------------------------------------------------------------------

"""

# STANDALONE
from .Activity import sppasActivity
from .Align import sppasAlign
from .FillIPUs import sppasFillIPUs
from .Intsint import sppasIntsint
from .LexMetric import sppasLexMetric
from .Momel import sppasMomel
from .Phon import sppasPhon
from .RMS import sppasRMS
from .Formants import sppasFormants
from .SearchIPUs import sppasSearchIPUs
from .SelfRepet import sppasSelfRepet
from .StopWords import sppasStopWords
from .Syll import sppasSyll
from .TextNorm import sppasTextNorm
from .TGA import sppasTGA
from .IVA import sppasIVA
from .Anonym import sppasAnonym
from .SpeechToText import sppasSpeechToText

# INTERACTIONS
from .OtherRepet import sppasOtherRepet
from .ReOccurrences import sppasReOcc
from .Overlaps import sppasOverActivity

# SPEAKER
from .SpkLexRep import sppasLexRep

# Annotations on either an image or a video:
from .FaceDetection import sppasFaceDetection
from .FaceSights import sppasFaceSights
from .HandPose import sppasHandPose

# Annotations on a video:
from .FaceIdentity import sppasFaceIdentifier

# Spin-offs: Annotations which are developed elsewhere and can be installed
from .spinoff import *
