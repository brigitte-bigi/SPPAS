GOTO EndHeader

:filename: dashboard.bat
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Launch the setup of SPPAS for Windows.

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
title "SPPAS Dashboard"

set PYTHONIOENCODING=UTF-8
set PYENV=.sppaspyenv~
set ACTIVATE=".sppaspyenv~\Scripts\activate.bat"
set PYTHON=".sppaspyenv~\Scripts\python.exe"

echo ----------------------------------------------------------------------------------
echo Welcome to SPPAS Dashboard,
echo a program written by Brigitte Bigi, Researcher at CNRS,
echo Laboratoire Parole et Langage, Aix-en-Provence, France.
echo ----------------------------------------------------------------------------------

setlocal enabledelayedexpansion
if not exist "%PYENV%" (
    set "SCRIPT_DIR=%~dp0"

    echo A Python Virtual Environment for SPPAS is being created in %PYENV%.
    echo It will then install a few core programs.
    echo ----------------------------------------------------------------------------------

    echo Browse through all available python command
    for /f "delims=" %%i in ('where python.exe python3*.exe 2^>nul') do (
        echo Test "%%i"
        call "%%i" "%SCRIPT_DIR%sppas\bin\runtime_initializer.py"
        echo Exit code: !ERRORLEVEL!
        if !ERRORLEVEL! == 0 (
            echo Environment is ready.
            timeout /t 3 >nul
            goto :venv_ok
        ) else (
            echo invalid
            rem Cleanup if runtime_initializer.py created a partial venv
            if exist "%PYENV%" (
                echo Removing incomplete virtual environment...
                rmdir /s /q "%PYENV%"
            )
        )
    )
)

:venv_ok
endlocal


REM Launch the setup within the python virtual environment
if exist %PYENV% (

    echo SPPAS Dashboard application starts...
    echo ----------------------------------------------------------------------------------
    echo * * *   Closing this windows will kill the application  * * *
    echo ----------------------------------------------------------------------------------

    start "SPPAS Dashboard" /b /high %PYTHON% .\sppas\ui\swapp\__main__.py
    REM ... /b Starts an application without opening a new Command Prompt window
    REM ... /high Starts an application in the specified priority class.
  
) else (
    color 4E
	echo ********************************************************
    echo      No valid python command was found or 
    echo      the virtual environment failed to be created.
    echo      Install Python >= 3.9 from the Windows Store,
	echo      and re-start this setup.
	echo ********************************************************
    timeout /t 120
)
