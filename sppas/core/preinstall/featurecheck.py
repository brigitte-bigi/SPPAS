"""
:filename: sppas.src.coreutils.featurecheck.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Check if the required dependencies can be imported

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

import webbrowser

from sppas.core.config import sppasExecProcess
from sppas.core.coreutils.reports import sppasLogFile

# ---------------------------------------------------------------------------


class DepsFeatureChecker:
    """Check if the given python dependencies can be imported.

    """

    def __init__(self, values=None):
        """Create a module import checker.

        By default, the tested values are the required one, for core, i.e.:
        values = ((("whakerpy",), ("whakerkit",), ("audioopy",)), None)

        :param values: tuple (modules, commands) to check, where:
               - modules: tuple of tuples, each inner tuple is an OR group, AND between groups.
                 E.g. (('a', 'b'), ('c',)) means (a OR b) AND c
               - commands: tuple of commands to check (all must succeed).

        :example:
        >>> # Check core dependencies by default and create a report if error
        >>> core_checker = DepsFeatureChecker()
        >>> core_checker.check(do_report=True)
        >>> # The features needs a pip package but no command
        >>> wxpython_checker = DepsFeatureChecker(((("wx", ),), None))
        >>> wxpython_checker.check()
        >>> # The feature does not need a pip package but a command
        >>> julius_checker = DepsFeatureChecker((None, (("julius", ),)))
        >>> julius_checker.check()
        >>> # The features needs both pip packages and a command
        >>> stt_checker = DepsFeatureChecker(((("torch",), ("whisper",), ("transformers",)), ("ffmpeg -h",)))
        >>> stt_checker.check()

        """
        if values is None:
            values = ((("whakerpy",), ("whakerkit",), ("audioopy",)), None)
        self.__values = values

    # -----------------------------------------------------------------------

    def check(self, do_report=False):
        """Check if the defined dependencies can be imported or executed.

        :param do_report: whether to report errors or not in a file and in webbrowser
        :raises: ImportError: a module failed to be imported
        :raises: RuntimeError: a command failed to be executed

        """
        msg = list()
        try:
            test_modules, test_commands = self.__values
            if test_commands is not None:
                DepsFeatureChecker.check_commands(test_commands)
                msg.append(f"Successfully executed: '{test_commands}'.")
            if test_modules is not None:
                DepsFeatureChecker.check_modules(test_modules)
                msg.append(f"Successfully imported: '{test_modules}'.")
        except ImportError as e:
            if do_report is True:
                msg.append(str(e))
                self.report_message("\n".join(msg))
            raise
        except RuntimeError as e:
            if do_report is True:
                msg.append(str(e))
                self.report_message("\n".join(msg))
            raise

    # -----------------------------------------------------------------------

    @staticmethod
    def check_modules(test_modules):
        """Check if the defined module dependencies can be imported.

        :param test_modules: tuple of tuples (OR-groups in AND-chain), e.g. (('a', 'b'), ('c',))
        :raises ImportError: if any AND-group fails (i.e., no module in OR-group can be imported)

        """
        if test_modules is None:
            return

        # Robustness: handle str or single tuple directly
        if isinstance(test_modules, str):
            test_modules = ((test_modules,),)
        elif isinstance(test_modules, tuple) and all(isinstance(m, str) for m in test_modules):
            # legacy: ('wx',) → ((‘wx’,),)
            test_modules = (test_modules,)

        for or_group in test_modules:
            found = False
            for module_name in or_group:
                try:
                    __import__(module_name)
                    found = True
                    break  # One success in the OR-group is enough
                except ImportError:
                    continue
                except Exception as e:
                    raise ImportError(
                        f"Error while importing '{module_name}': {e}"
                    )
            if not found:
                raise ImportError(
                    f"None of the modules in {or_group} could be imported."
                )

    # -----------------------------------------------------------------------

    @staticmethod
    def check_commands(test_commands):
        """Check if the defined command dependencies can be executed.

        :param test_commands: (list) the commands to check
        :raises: RuntimeError: a command failed to be executed

        """
        if test_commands is None:
            return

        for command in test_commands:
            p = sppasExecProcess()
            success = p.test_command(command)
            if success is False:
                raise RuntimeError(f"Failed to execute the required command: {command}.")

    # -----------------------------------------------------------------------

    @staticmethod
    def report_message(message):
        """Create a report of the error and open it in the web browser.

        :param message: the error message to be displayed

        """
        report = sppasLogFile(pattern="setup")
        with open(report.get_filename(), "w") as f:
            f.write(report.get_header())
            f.write(message + "\n")
        webbrowser.open(url=report.get_filename())
