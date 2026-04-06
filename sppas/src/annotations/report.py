"""
:filename: sppas.src.annotations.log.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The Procedure Outcome Report of automatic annotations of SPPAS.

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

import codecs
import logging

from sppas.core.config import sg
from sppas.core.config import annots
from sppas.core.coreutils import info
from sppas.core.coreutils import u
from sppas.src.utils import sppasTime

# ---------------------------------------------------------------------------


class sppasAnnReport(object):
    """A log file utility class dedicated to automatic annotations.

    Class to manage the SPPAS automatic annotations log file, which is also
    called the "Procedure Outcome Report".

    """

    STR_INDENT = " ... "
    STR_ITEM = "  - "
    MAX_INDENT = 10

    # -----------------------------------------------------------------------

    def __init__(self, parameters=None):
        """Create a sppasLog instance and open an output stream to NULL.

        :param parameters: (sppasParam)

        """
        self.parameters = parameters
        self.logfp = None  # codecs.open(os.devnull, 'w', sg.__encoding__)

    # -----------------------------------------------------------------------
    # File management
    # -----------------------------------------------------------------------

    def create(self, filename):
        """Create and open a new output stream.

        :param filename: (str) Output filename

        """
        if self.logfp is not None:
            self.close()

        self.logfp = codecs.open(filename, 'w', sg.__encoding__)

    # -----------------------------------------------------------------------

    def open(self, filename):
        """Open an existing file and set the output stream.

        :param filename: (str) Output filename

        """
        if self.logfp is not None:
            self.close()

        self.logfp = codecs.open(filename, 'a+', sg.__encoding__)

    # -----------------------------------------------------------------------

    def close(self):
        """Close the current output stream."""
        if self.logfp is not None:
            self.logfp.close()
        self.logfp = None

    # -----------------------------------------------------------------------
    # Write data
    # -----------------------------------------------------------------------

    def print_step(self, step_number):
        """Print a step name in the output stream from its number.

        :param step_number: (1..N) Number of an annotation defined in a
        sppasParam instance.

        """
        if self.parameters is not None:
            message = self.parameters.get_step_name(step_number)
        else:
            message = "Annotation step " + str(step_number)

        if self.logfp is not None:
            # force to write at the end of the file
            self.logfp.seek(0, 2)
            self.print_separator()
            # try to write at center
            self.logfp.write(' '*24 + message)
            self.print_newline()
            self.print_separator()
        else:
            logging.info(" * * * " + message + " * * * ")

    # -----------------------------------------------------------------------

    def print_message(self, message, indent=0, status=None):
        """Print a message at the end of the current output stream.

        :param message: (str) The message to communicate
        :param indent: (int) Shift the message with indents
        :param status: (int) A status identifier

        0 means OK,
        1 means WARNING,
        2 means IGNORED,
        3 means INFO,
        -1 means ERROR.

        """
        message = u(message)
        if len(message) == 0:
            return
        str_indent = sppasAnnReport.get_indent_text(indent)

        if self.logfp is not None:
            self.logfp.seek(0, 2)
            status_text = sppasAnnReport.get_status_text(status)
            self.logfp.write(str_indent + status_text + message)
            self.print_newline()

        else:
            if status is None:
                logging.info(str_indent + message)
            else:
                if status == annots.info:
                    logging.info(str_indent + message)

                elif status == annots.warning:
                    logging.warning(str_indent + message)

                elif status == annots.error:
                    logging.error(str_indent + message)

                elif status == annots.ok:
                    logging.info(str_indent + message)

                else:
                    logging.debug(message)

    # -----------------------------------------------------------------------

    def print_raw_text(self, text):
        """Print a text at the end of the output stream.

        :param text: (str) text to print

        """
        if self.logfp is not None:
            self.logfp.seek(0, 2)  # write at the end of the file
            self.logfp.write(text)
        else:
            logging.info(text)

    # -----------------------------------------------------------------------

    def print_newline(self):
        """Print a CR in the output file stream, do nothing if logging."""
        if self.logfp is not None:
            self.logfp.write('\n')

    # -----------------------------------------------------------------------

    def print_separator(self):
        """Print a line in the output file stream, do nothing if logging."""
        if self.logfp is not None:
            self.logfp.write('-'*78)
            self.print_newline()

    # -----------------------------------------------------------------------

    def print_stats(self, stats):
        """Print the statistics values in the output stream for a given step.

        Do not print anything if no parameters were given.

        :param stats: List of values (one for each annotation)

        """
        if self.parameters is None:
            return

        if len(stats) != self.parameters.get_step_numbers():
            return

        self.print_separator()
        self.print_message('Result statistics:')
        self.print_separator()
        for i in range(len(stats)):
            self.print_stat_item(i, str(stats[i]))
        self.print_separator()

    # -----------------------------------------------------------------------

    def print_stat_item(self, step_number, value=None):
        """Print a statistic value in the output stream for a given step.

        Do not print anything if no parameters were given.

        :param step_number: (1..N)
        :param value: (str) A statistic value.
        Instead, print the status (enabled or disabled).

        """
        if self.parameters is None:
            return

        if value is None:
            if self.parameters.get_step_status(step_number):
                value = info(1030, "annotations")
            else:
                value = info(1031, "annotations")

        self.print_item(self.parameters.get_step_name(step_number),
                        str(value))

    # ----------------------------------------------------------------------

    def print_item(self, main_info, second_info=None):
        """Print an item in the output stream.

        :param main_info: (str) Main information to print
        :param second_info: (str) A secondary info to print

        """
        message = sppasAnnReport.STR_ITEM + main_info
        if second_info is not None:
            message += ': ' + second_info

        if self.logfp is not None:
            self.logfp.seek(0, 2)
            self.logfp.write(message)
            self.print_newline()
        else:
            logging.info(message)

    # ----------------------------------------------------------------------

    def print_header(self):
        """Print the parameters information in the output file stream."""

        sppas_name = sg.__name__ + ' ' + info(1032, "annotations") \
                     + ' ' + sg.__version__
        sppas_copy = sg.__copyright__
        sppas_url = info(1033, "annotations") + ': ' + sg.__url__
        sppas_contact = info(1034, "annotations") + ': ' + \
                        sg.__author__ + " (" + sg.__contact__ + ")"

        if self.logfp is not None:
            self.logfp.seek(0, 2)

            self.print_separator()
            self.print_newline()
            self.print_message(' ' * 24 + info(1054, "annotations"))
            self.print_newline()
            self.print_message(' ' * 24 + info(1035, "annotations"))
            self.print_newline()
            self.print_separator()
            self.print_newline()

            self.print_message(sppas_name)
            self.print_message(sppas_copy)
            self.print_message(sppas_url)
            self.print_message(sppas_contact)
            self.print_newline()
            self.print_separator()
        else:

            logging.info(sppas_name)
            logging.info(sppas_copy)
            logging.info(sppas_url)
            logging.info(sppas_contact)

    # ----------------------------------------------------------------------

    def print_annotations_header(self):
        """Print the parameters information in the output stream.

        Do not print anything if no parameters were given.

        """
        if self.parameters is None:
            return

        self.print_message(info(1036, "annotations") + ': ' + sppasTime().now)
        self.print_message(info(1037, "annotations") + ': ')
        for i in range(self.parameters.get_step_numbers()):
            if self.parameters.get_lang(i) is not None:
                self.print_item(self.parameters.get_step_name(i),
                                self.parameters.get_lang(i))
            else:
                self.print_item(self.parameters.get_step_name(i), "---")
        self.print_newline()

        self.print_message(info(1038, "annotations") + ': ')
        for sinput in self.parameters.get_checked_roots():
            self.print_item(sinput)
        self.print_newline()

        self.print_message(info(1039, "annotations") + ': ')
        for i in range(self.parameters.get_step_numbers()):
            self.print_stat_item(i)
        self.print_newline()

    # ----------------------------------------------------------------------

    @staticmethod
    def get_status_text(status_id):
        """Return a status text from a status identifier.

        :param status_id: (int)

        """
        if status_id is None:
            return ""

        status_id = int(status_id)

        if status_id == annots.ok:
            return info(1041, "annotations")

        if status_id == annots.warning:
            return info(1043, "annotations")

        if status_id == annots.ignore:
            return info(1044, "annotations")

        if status_id == annots.info:
            return info(1042, "annotations")

        if status_id == annots.error:
            return info(1045, "annotations")

        return ""

    # ----------------------------------------------------------------------

    @staticmethod
    def get_indent_text(number):
        """Return a string representing some indentation.

        :param number: (int) A positive integer.

        """
        number = int(number)

        if number > sppasAnnReport.MAX_INDENT:
            number = sppasAnnReport.MAX_INDENT

        if number < 0:
            number = 0

        return sppasAnnReport.STR_INDENT * number
