# -*- coding: UTF-8 -*-
"""
:filename: sppas.coreutils.messages.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Functions for messages translations.

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

from sppas.core.config.sppaslang import translator

# ----------------------------------------------------------------------------


def info(msg_id, domain=None):
    """Return the info message from gettext.

    :param msg_id: (str or int) Info id
    :param domain: (str) Name of the domain
    :return: (str) Translated message or message

    """
    # Format the input message
    if isinstance(msg_id, int) is True:
        _msg = "{:04d}".format(msg_id)
    else:
        _msg = str(msg_id)
    _msg = ":INFO " + _msg + ": "

    if domain is not None and translator is not None:
        try:
            return translator.gettext(_msg, domain)
        except:
            pass
        try:
            return translator.gettext(_msg, domain)
        except Exception as e:
            import logging
            logging.debug(str(e))
            pass

    return _msg

# ---------------------------------------------------------------------------


def error(msg_id, domain=None):
    """Return the error message from gettext.

    :param msg_id: (str or int) Error id
    :param domain: (str) Name of the domain
    :return: (str) Translated message or message

    """
    # Format the input message
    if isinstance(msg_id, int) is True:
        _msg = "{:04d}".format(msg_id)
    else:
        _msg = str(msg_id)
    _msg = ":ERROR " + _msg + ": "

    if domain is not None and translator is not None:
        try:
            return translator.gettext(_msg, domain)
        except:
            pass

    return _msg

# ---------------------------------------------------------------------------


def msg(message, domain=None):
    """Return the message from gettext.

    :param message: (str) Message
    :param domain: (str) Name of the domain
    :return: (str) Translated message or message

    """
    if domain is not None and translator is not None:
        try:
            return translator.gettext(message, domain)
        except:
            pass

    return message
