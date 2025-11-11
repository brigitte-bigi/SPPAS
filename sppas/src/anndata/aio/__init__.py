# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.anndata.aio.__init__.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Readers and writers of annotated data.

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

from .annotationpro import sppasANT
from .annotationpro import sppasANTX
from .anvil import sppasAnvil
from .audacity import sppasAudacity
from .elan import sppasEAF
from .htk import sppasLab
from .phonedit import sppasMRK
from .phonedit import sppasSignaix
from .praat import sppasTextGrid
from .praat import sppasIntensityTier
from .praat import sppasPitchTier
from .sclite import sppasCTM
from .sclite import sppasSTM
from .subtitle import sppasSubRip
from .subtitle import sppasSubViewer
from .subtitle import sppasWebVTT
from .text import sppasRawText
from .text import sppasCSV
from .table import sppasARFF
from .table import sppasXRFF
from .table import sppasTRA
from .xtrans import sppasTDF
from .xra import sppasXRA

from .aioutils import serialize_label
from .aioutils import serialize_labels
from .aioutils import format_label
from .aioutils import format_labels

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------

# The use of these variables is DEPRECATED:
# Now: get extension of each format from the sppasRW() parser

ext_sppas = ['.xra', '.[Xx][Rr][Aa]']
ext_praat = ['.TextGrid', '.PitchTier', '.[Tt][eE][xX][tT][Gg][Rr][Ii][dD]','.[Pp][Ii][tT][cC][hH][Tt][Ii][Ee][rR]']
ext_transcriber = ['.trs', '.[tT][rR][sS]']
ext_elan = ['.eaf', '[eE][aA][fF]']
ext_ascii = ['.txt', '.csv', '.[cC][sS][vV]', '.[tT][xX][Tt]', '.info']
ext_phonedit = ['.mrk', '.[mM][rR][kK]']
ext_signaix = ['.hz', '.[Hh][zZ]']
ext_sclite = ['.stm', '.ctm', '.[sScC][tT][mM]']
ext_htk = ['.lab', '.mlf']
ext_subtitles = ['.sub', '.srt', '.[sS][uU][bB]', '.[sS][rR][tT]']
ext_anvil = ['.anvil', '.[aA][aN][vV][iI][lL]']
ext_annotationpro = ['.antx', '.[aA][aN][tT][xX]']
ext_xtrans = ['.tdf', '.[tT][dD][fF]']
ext_audacity = ['.aup']
ext_table = ['.tra', '.arff', '.xrff']

primary_in = ['.hz', '.PitchTier']
annotations_in = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.anvil', '.aup', '.trs', '.tdf']

extensions = ['.xra', '.textgrid', '.pitchtier', '.hz', '.eaf', '.trs', '.csv', '.mrk', '.txt', '.mrk', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', 'anvil', '.antx', '.tdf', '.arff', '.xrff']
extensionsul = ext_sppas + ext_praat + ext_transcriber + ext_elan + ext_ascii + ext_phonedit + ext_signaix + ext_sclite + ext_htk + ext_subtitles + ext_anvil + ext_annotationpro + ext_xtrans + ext_audacity + ext_table
extensions_in = primary_in + annotations_in
extensions_out = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.txt', '.stm', '.ctm', '.lab', '.mlf', '.sub', '.srt', '.antx', '.arff', '.xrff']
extensions_out_multitiers = ['.xra', '.TextGrid', '.eaf', '.csv', '.mrk', '.antx', '.arff', '.xrff']

# ----------------------------------------------------------------------------


__all__ = (
    "sppasANT",
    "sppasANTX",
    "sppasAnvil",
    "sppasAudacity",
    "sppasEAF",
    "sppasLab",
    "sppasMRK",
    "sppasSignaix",
    "sppasTextGrid",
    "sppasIntensityTier",
    "sppasPitchTier",
    "sppasCTM",
    "sppasSTM",
    "sppasSubRip",
    "sppasSubViewer",
    "sppasWebVTT",
    "sppasRawText",
    "sppasCSV",
    "sppasTDF",
    "sppasTRA",
    "sppasARFF",
    "sppasXRFF",
    "sppasXRA",
    "extensions",
    "extensions_in",
    "extensions_out",
    "serialize_label",
    "serialize_labels",
    "format_label",
    "format_labels"
)
