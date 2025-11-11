GOTO EndHeader

:filename:     setup.bat
:author:       Brigitte Bigi
:contact:      contact@sppas.org
:summary:      Launch the setup of SPPAS for Windows.

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
title "SPPAS Setup"

set PYTHONIOENCODING=UTF-8
set PYENV=".sppaspyenv~"
set ACTIVATE=".sppaspyenv~\Scripts\activate.bat"
set PYTHON=".sppaspyenv~\Scripts\python.exe"

echo ----------------------------------------------------------------------------------
echo Welcome to SPPAS setup.
echo a program written by Brigitte Bigi, Researcher at
echo Laboratoire Parole et Langage, Aix-en-Provence, France.
echo ----------------------------------------------------------------------------------
echo This setup creates a Python Virtual Environment for SPPAS in %PYENV%
echo It will then install a few core programs and open a new tab in your web
echo browser in order to install some external programs to enable more features.
echo ----------------------------------------------------------------------------------

if not exist %PYENV% (
    echo Browse through all available python command
    for /f %%i in ('where python3*.exe 2^>nul') do (
        if not exist %PYENV% (
            echo Test %%i
            call %%i .\sppas\bin\checkpy.py
            if ERRORLEVEL 0 (
                echo valid
                color 1E
                echo Please wait while Python virtual environment is being created
                call %%i -m venv %PYENV%
                echo ... ok
                REM we need to wait for Windows to realize that the pyenv was created...
                timeout /t 3
            ) else (echo invalid)
        )
    )
)

REM Launch the setup within the python virtual environment
if exist %PYENV% (
    color F1
	echo Required dependencies installation:
    %PYTHON% -m pip install whakerpy==1.4 || %PYTHON% -m pip install sppas\dist\whakerpy-1.4-py3-none-any.whl
    %PYTHON% -m pip install WhakerKit==1.3 || %PYTHON% -m pip install sppas\dist\whakerkit-1.3-py3-none-any.whl
    %PYTHON% -m pip install AudiooPy==0.5 || %PYTHON% -m pip install sppas\dist\AudiooPy-0.5-py3-none-any.whl

    if ERRORLEVEL 0 (
        echo * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        echo * * *   Closing this windows will kill the application  * * *
        echo * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        echo Start application
        start "SPPAS Web-Setup" /b /high %PYTHON% .\sppas\ui\swapp\__main__.py --Setup
        REM ... /b Starts an application without opening a new Command Prompt window
        REM ... /high Starts an application in the specified priority class.  
  
    ) else (
        color 4E
        echo ********************************************************
        echo An error occurred when trying to install required python packages.
        echo Try manually in a PowerShell or Command application.
        echo ********************************************************
        timeout /t 120
    )
) else (
    color 4E
	echo ********************************************************
    echo      No valid python command was found or 
    echo      the virtual environment failed to be created.
    echo      Install Python 3 from the Windows Store,
	echo      and re-start this setup.
	echo ********************************************************
    timeout /t 120
)
