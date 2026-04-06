# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.config.process.py
:author: Brigitte Bigi
:contributor: Florian Hocquet
:contact: contact@sppas.org
:summary: Execute a subprocess and get results.

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

"""

import os
import shlex
import logging
import signal
import subprocess
import platform

# ------------------------------------------------------------------------


class sppasExecProcess(object):
    """A convenient class to execute a subprocess.

    A sppasExecProcess is a wrapper of 'subprocess.Popen' command.
    The sppasExecProcess class is a convenient wrapper for executing
    subprocesses in Python. It provides methods for running a command,
    getting the stdout and stderr of the command, stopping a running
    command, and checking the status of the command.

    The main functionalities of the sppasExecProcess class are:

    - Running a command using 'subprocess.Popen' or 'subprocess.run'
    - Getting the stdout and stderr of the executed command
    - Stopping a running command
    - Checking the status of the executed command

    :example:
    >>> # Launch a command:
    >>> p = sppasExecProcess()
    >>> p.run_popen("ls -l")
    >>> # Get the stdout of the command:
    >>> p.out()
    >>> # Get the stderr of the command:
    >>> p.error()
    >>> # Stop a command:
    >>> p.stop()
    >>> # Get the state of the command:
    >>> p.is_running()

    """

    def __init__(self):
        """Create a new instance."""
        self.__process = None

    # ------------------------------------------------------------------------

    @staticmethod
    def test_command(command):
        """Return True if command exists.

        Test only the main command: the first string without its arguments.

        :param command: (str) a system command possibly with args.
        :return: (bool) True if the given command can be executed.

        """
        command_args = shlex.split(command)
        test_command = command_args[0]
        logging.debug("Test of the command: {:s}".format(test_command))

        fd_null = open(os.path.devnull, 'w')
        try:
            p = subprocess.Popen([test_command], shell=False, stdout=fd_null, stderr=fd_null)
        except OSError:
            fd_null.close()
            return False

        # Get the process id & try to terminate it gracefully
        pid = p.pid
        p.terminate()

        # Check if the process has really terminated & force kill if not.
        try:
            os.kill(pid, signal.SIGINT)
            p.kill()
        except OSError:
            pass
        fd_null.close()
        return True

    # ------------------------------------------------------------------------

    def run_popen(self, command):
        """Execute the given command with 'subprocess.Popen'.

        Deprecated, use run() instead.

        :param command: (str) The command to be executed

        """
        logging.info("Process command: {}".format(command))
        command = command.strip()
        command_args = shlex.split(command)
        pipe = subprocess.PIPE
        self.__process = subprocess.Popen(command_args, stdout=pipe, stderr=pipe)  # text=True)
        self.__process.wait()

    # ------------------------------------------------------------------------

    def run(self, command, timeout=300):
        """Execute command with 'subprocess.run'.

        :param command: (str) The command to execute.
        :param timeout: (int) Time in seconds before the command times out.
        :raises: ValueError: Empty command
        :raises: subprocess.TimeoutExpired: If the command exceeds the timeout.
        :raises: subprocess.SubprocessError: For any other execution error.

        """
        logging.info("Process command: {}".format(command))
        command = command.strip()
        if len(command) == 0:
            raise ValueError("Empty command.")
        command_args = shlex.split(command)

        # Define subprocess arguments for cross-platform consistency
        subprocess_args = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": False,                # Explicitly False for security
            "cwd": None,                   # Current working directory
            "timeout": timeout,            # Time limit for command execution
            "check": False,                # Do not raise an exception for non-zero exit code
            "encoding": None,              # Use system default encoding
            "errors": None,                # Default error handling for encoding
            "env": None,                   # Inherit the parent environment
            "universal_newlines": True     # Ensure text output (compatibility with Python <3.7)
        }

        # Adjust for platform-specific requirements
        if platform.system() != "Windows":
            # Use shell=True on non-Windows systems
            subprocess_args["shell"] = True

        try:
            self.__process = subprocess.run(
                command_args if not subprocess_args["shell"] else command,
                **subprocess_args
            )
        except AttributeError:
            return_code = subprocess.call(command_args, stdin=None,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=False)
            # Simulate a CompletedProcess object for uniform handling
            self.__process = self._create_legacy_process(command_args, return_code)

    # ------------------------------------------------------------------------

    @staticmethod
    def _create_legacy_process(args, return_code):
        """Simulate a CompletedProcess object for Python < 3.5."""
        return subprocess.CompletedProcess(
            args=args,
            returncode=return_code,
            stdout=None,
            stderr=None
        )

    # ------------------------------------------------------------------------

    def out(self):
        """Return the standard output of the processed command.

        :return: (str) output message

        """
        if self.__process is None:
            return ""
        out = self.__process.stdout
        out = str(out)
        return out

    # ------------------------------------------------------------------------

    def error(self):
        """Return the error output of the processed command.

        :return: (str) error message

        """
        if self.__process is None:
            return ""
        error = self.__process.stderr
        error = str(error)
        return error

    # ------------------------------------------------------------------------

    def stop(self):
        """Terminate the current command if it is running."""
        if self.is_running() is True:
            self.__process.terminate()

    # ------------------------------------------------------------------------

    def status(self):
        """Return the status of the command if the process is completed.

        :return: (int) -2 means no process or process returned code

        """
        if self.__process is None:
            return -2
        return self.__process.returncode

    # ------------------------------------------------------------------------

    def is_running(self):
        """Return True if the process is still running.

        :return: (bool)

        """
        if self.__process is None:
            return False
        return self.__process.poll() is None
