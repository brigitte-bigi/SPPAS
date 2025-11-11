# -*- coding : UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.media.mediaevents.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Events required to implement a media player.

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

import wx.lib.newevent


class MediaEvents(object):

    # -----------------------------------------------------------------------
    # Event to be used by a media to ask parent perform an action.

    MediaActionEvent, EVT_MEDIA_ACTION = wx.lib.newevent.NewEvent()
    MediaActionCommandEvent, EVT_MEDIA_ACTION_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # Event sent when the media is loaded, so when it's real size is known.
    # Not platform dependent: the event is sent whatever the backend used.
    MediaLoadedEvent, EVT_MEDIA_LOADED = wx.lib.newevent.NewEvent()
    MediaLoadedCommandEvent, EVT_MEDIA_LOADED_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # Event sent when the media failed to be loaded.
    # Not platform dependent: the event is sent whatever the backend used.
    MediaNotLoadedEvent, EVT_MEDIA_NOT_LOADED = wx.lib.newevent.NewEvent()
    MediaNotLoadedCommandEvent, EVT_MEDIA_NOT_LOADED_COMMAND = wx.lib.newevent.NewCommandEvent()

    # -----------------------------------------------------------------------
    # Event sent when the period on a media has changed.
    MediaPeriodEvent, EVT_MEDIA_PERIOD = wx.lib.newevent.NewEvent()
    MediaPeriodCommandEvent, EVT_MEDIA_PERIOD_COMMAND = wx.lib.newevent.NewCommandEvent()
