"""
:filename: sppas.ui.agnostic.appcom_notify.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Notify the application events to subscribed observers.

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

    Copyright (C) 2011-2026  Brigitte Bigi, CNRS
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

# ---------------------------------------------------------------------------


class sppasCommNotifier:
    """Notify the application events to the subscribed observers.

    The contract of the observers is the one of the message envelope: a
    callable receiving the (key, value) of each event. The notifier is
    transport-agnostic: it does not know what an observer does with an
    event -- send it on a socket, post it to a UI event loop, log it...
    When nobody subscribed, notify() does nothing.

    """

    def __init__(self):
        """Create the notifier, without any observer."""
        self.__observers = list()

    # -----------------------------------------------------------------------

    def subscribe(self, observer) -> None:
        """Add an observer to notify.

        An already subscribed observer is not added twice.

        :param observer: (callable) Called with the (key, value) of each event.
        :raises: TypeError: The observer is not callable.

        """
        if callable(observer) is False:
            raise TypeError("observer must be a callable")
        if observer not in self.__observers:
            self.__observers.append(observer)

    # -----------------------------------------------------------------------

    def unsubscribe(self, observer) -> None:
        """Remove an observer.

        An unknown observer is ignored.

        :param observer: (callable) A previously subscribed observer.

        """
        if observer in self.__observers:
            self.__observers.remove(observer)

    # -----------------------------------------------------------------------

    def notify(self, key: int, value) -> None:
        """Notify all the observers of an event.

        :param key: (int) One of the sppasCommKeys constants
        :param value: (any) A JSON-serializable object
        :raises: TypeError: Invalid key type

        """
        if isinstance(key, int) is False:
            raise TypeError("event key must be an integer")

        for observer in self.__observers:
            observer(key, value)
