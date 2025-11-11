GOTO EndHeader

:filename:     sppas.bat
:author:       Brigitte Bigi
:contact:      contact@sppas.org
:summary:      Launch the GUI of SPPAS for Windows.

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

:EndHeader

@echo off
color 0F

SET PYTHONIOENCODING=UTF-8
SET PYENV=".sppaspyenv~"
SET PYTHON=".sppaspyenv~\Scripts\python.exe"

if exist %PYENV% (

    start "" %PYTHON% -m sppas

) else (

    color 4E
    echo Python virtual environment for SPPAS does not exist.
    echo ... did you forgot to read the installation instructions?
    timeout /t 120

)
