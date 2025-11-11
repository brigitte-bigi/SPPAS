#!/usr/bin/env python
"""
:filename: sppas.__main__.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Entry point to launch the Graphical User Interface of SPPAS

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######  ########  ########     ###     ######
    ##    ## ##     ## ##     ##   ## ##   ##    ##     the automatic
    ##       ##     ## ##     ##  ##   ##  ##            annotation
     ######  ########  ########  ##     ##  ######        and
          ## ##        ##        #########       ##        analysis
    ##    ## ##        ##        ##     ## ##    ##         of speech
     ######  ##        ##        ##     ##  ######

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

In Python, '__main__' is the name of the scope in which top-level code
executes. Within SPPAS, it allows to launch the Graphical User Interface.

To launch the GUI, this main file allows the followings 3 solutions:

>>> py3=".sppaspyenv~/bin/python"
>>> py3 -m sppas
>>> py3 sppas/__main__.py
>>> py3 sppas  # possible, but not recommended

It is supposed that the 'py3' is a link to the python virtuel environment,
created during the setup, i.e. either .sppaspyenv/bin/python (Unix OS)
or .sppaspyenv/Scripts/python.exe (Windows).

In case of error, SPPAS creates a log file with the error message, and it
displays it in the web browser.

"""

# Import of python standard libraries then python version check.
from __future__ import annotations
import sys
import os
import webbrowser
import time
import logging
from argparse import ArgumentParser

sppas_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# package is not defined if the program is launched without the -m option
# but... => new with Python 3.12: DeprecationWarning: __package__ != __spec__.parent
# if __package__ is None or len(__package__) == 0:
#     sys.path.insert(0, sppas_dir)
#     __package__ = "sppas"

if '__package__' not in globals() or __package__ is None or len(__package__) == 0:
    sys.path.insert(0, sppas_dir)

    # Gestion de __spec__ pour éviter le warning
    if '__spec__' not in globals() or __spec__ is None:
        __package__ = "sppas"  # Définition manuelle de __package__
    else:
        __package__ = __spec__.parent

# ---------------------------------------------------------------------------


class SPPASLauncher:
    """A launcher to handle the initialization and execution of the SPPAS application.

    It ensures compatibility with the required Python version, handles imports of
    necessary dependencies, manages error reporting, and launches the main GUI
    application.

    """

    def __init__(self):
        """Create a SPPASLauncher instance."""
        # Python requirements
        self.__min_py = (3, 7)
        self.__recommended_py = (3, 9)

        # The application to launch
        self.__app = None
        # The list of possible exceptions raised by the app
        self.__exc = tuple()
        # Exit infos: status code, error message and report filename
        self.__report = None
        self.__log = None
        self.__status = 1
        self.__error_message = "Unknown error."

    # ---------------------------------------------------------------------------

    def get_status(self) -> int:
        """Return the exit status code of the launcher."""
        return self.__status

    status = property(get_status, None, None)

    def get_report_filename(self) -> str:
        """Return the name of the report file, used in case of error."""
        if self.__report is None:
            return ""
        return self.__report.get_filename()
    
    report_filename = property(get_report_filename, None, None)

    def get_error_message(self) -> str:
        """Return the error message of the launcher, filled in case of error."""
        return self.__error_message

    error_message = property(get_error_message, None, None)

    # ---------------------------------------------------------------------------

    def check_python_version(self) -> str:
        """Check Python version compatibility and print diagnosis on stdout.

        :return: (str) A message if Python is not the expected one

        """
        if sys.version_info < self.__min_py:
            return ("[ WARNING ] You need to update Python version to launch the application. "
                    "The GUI of SPPAS requires version {:s}"
                    "".format(".".join([str(i) for i in self.__min_py])))

        if sys.version_info < self.__recommended_py:
            return ("[ INFO ] You should consider updating Python to {:s}+."
                    "".format(".".join([str(i) for i in self.__recommended_py])))

        return ""

    # ---------------------------------------------------------------------------

    def set_sppas_language(self, lang: str):
        sys.path.insert(0, os.path.join(sppas_dir, "config"))
        try:
            from config import set_language
            set_language(lang)
        except Exception as e:
            # Handle import errors and display a helpful message.
            self.__error_message = traceback.format_exc()
            try:
                self.__status = e.status
            except AttributeError:
                self.__status = 1

    # ---------------------------------------------------------------------------

    def import_dependencies(self):
        """Attempt to import all required dependencies for the application.

        :raises: Exception: If any of the required modules cannot be imported.

        """
        try:
            from sppas.core.coreutils import sppasLogFile
            from sppas.core.coreutils import sppasEnableFeatureError
            from sppas.core.coreutils import sppasPackageFeatureError
            from sppas.core.coreutils import sppasPackageUpdateFeatureError
            from sppas.ui.wxapp import sppasApp
            self.__status = 0
            self.__error_message = ""
            self.__report = sppasLogFile(pattern="run")
            self.__app = sppasApp()
            self.__exc = (sppasEnableFeatureError, sppasPackageFeatureError, sppasPackageUpdateFeatureError)
        except Exception as e:
            import traceback
            # Handle import errors and display a helpful message.
            self.__error_message = traceback.format_exc()
            try:
                self.__status = e.status
            except AttributeError:
                self.__status = 1

    # ---------------------------------------------------------------------------

    def run_wx_application(self):
        """Run the main application and handle runtime errors.

        """
        if self.__status != 0:
            raise Exception("The import of SPPAS modules wasn't done or failed")
        try:
            self.__status = self.__app.run()
        except self.__exc as e:
            self.__status = e.status
            self.__error_message = traceback.format_exc()
        except:
            self.__status = 1
            self.__error_message = traceback.format_exc()

    # ---------------------------------------------------------------------------

    def write_error_report(self):
        """Write an error report to a log file and open it in a browser.

        """
        with open(self.__report.get_filename(), "w") as f:
            f.write(self.__report.get_header())
            f.write(self.__error_message + "\n")
            f.write(f"\nSPPAS application exited with error status: {self.status}.\n")
        webbrowser.open(url=self.__report.get_filename())

# ---------------------------------------------------------------------------


def handle_error(launcher: SPPASLauncher):
    """Handle and report an error, then exit the application.

    - Prints the error message to the console.
    - Opens a web page with error documentation for the user.
    - Waits before exiting the program.

    """
    try:
        print(launcher.error_message)
        print(f"* * * * *  SPPAS exited with error number: {launcher.status:04d}  * * * * * ")
        url = f"https://sppas.org/book_08_annexes.html#error-{launcher.status:04d}"
        if not webbrowser.open(url):
            print(f"Visit the following URL for error details: {url}")
    except Exception as e:
        print(f"Error while reporting: {e}")
    finally:
        time.sleep(10)

# ---------------------------------------------------------------------------


def main(lang: str):
    """The main function to execute the SPPAS application.

    - Checks Python version compatibility.
    - Imports required dependencies.
    - Runs the application and handles any errors encountered.

    Exits the program with the appropriate status code.

    """
    launcher = SPPASLauncher()

    # Print information if Python version is not like expected
    msg = launcher.check_python_version()
    if len(msg):
        print(msg)

    # Fix SPPAS language
    if lang is not None:
        launcher.set_sppas_language(lang)

    # Import required SPPAS modules
    launcher.import_dependencies()
    if launcher.status != 0:
        handle_error(launcher)

    # Launch the 'wx' application
    launcher.run_wx_application()
    if launcher.status != 0:
        launcher.write_error_report()
        handle_error(launcher)

    sys.exit(launcher.status)

# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # create a parser for the command-line arguments
    parser = ArgumentParser(
        usage="SPPAS [-l lang]".format(os.path.basename(__file__)))

    # add arguments here
    parser.add_argument("-l", "--lang",
                        required=False,
                        type=str,
                        help='Language to be used for messages')

    # Parse arguments of the command line, and turn them into a dict
    args = parser.parse_args()

    lang = args.lang if args.lang else None
    if lang is not None:
        logging.debug("Requested language is {lang}")
    else:
        logging.debug("No language specified, using system default.")

    main(lang)
