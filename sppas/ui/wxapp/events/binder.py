# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.events.binder.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Custom binder for wx custom events.

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

    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
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

import wx


# ---------------------------------------------------------------------------
# List of event binders
# Because the type of an enumeration member is the enumeration, it can't be
# used to define our custom list of wx.PyEventBinder instances.
# ---------------------------------------------------------------------------


class sppasEventBinder(object):
    """A dictionnary of custom wx.PyEventBinder, with new event types.

    :Example of use:

        >>>with sppasEventBinder() as b:
        >>>    self.Bind(b.EVT_WINDOW_SELECTED, self._on_selected)
        >>>    type(b.EVT_WINDOW_SELECTED)
        >>>    ...<class 'wx.core.PyEventBinder'>

    This class mimics an 'Enum' and compatible with all python versions,
    AND the type of the defined entries is preserved.

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            EVT_LOGGING=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_DATA_CHANGED=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_ACTION=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_ACTION_FILE=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_WINDOW_SELECTED=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_WINDOW_FOCUSED=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_WINDOW_MOVED=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_WINDOW_RESIZED=wx.PyEventBinder(wx.NewEventType(), 1),
            EVT_BUTTON_PRESSED=wx.PyEventBinder(wx.NewEventType(), 1),
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------
# Create an instance in order to use the same one into the whole App(),
# for convenience reasons...


sb = sppasEventBinder()
