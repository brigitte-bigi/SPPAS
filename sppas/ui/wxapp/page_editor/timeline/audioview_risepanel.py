# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.timeline.audioview_risepanel.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  View panel for an audio file.

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

import os
import wx
import wx.lib

from sppas.core.config import paths
from audioopy.aio import open as audio_open

from sppas.ui.wxapp.windows import sppasScrolledPanel

from ..datactrls.audiodatavalues import AudioDataValues

from .timedatatype import TimelineType
from .baseview_risepanel import sppasFileViewPanel
from .audiovista import sppasAudioVista
from .timeevents import EVT_TIMELINE_VIEW

# ---------------------------------------------------------------------------


class AudioViewPanel(sppasFileViewPanel):
    """A panel to display the content of an audio.

    The object embedded in this class is a sppasAudioVista.

    Events emitted by this class is EVT_TIME_VIEW:
        - action="close" to ask for closing the panel
        - action="media_loaded", value=boolean to inform the file was
        successfully or un-successfully loaded.

    """

    def __init__(self, parent, filename, name="audioview_risepanel"):
        """Create an AudioViewPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param filename: (str) The name of the file of the media
        :param name: (str) the widget name.

        """
        super(AudioViewPanel, self).__init__(parent, filename=filename, name=name)

        # The information we need about the audio, no more!
        self.__audio_data = AudioDataValues()
        self._ft = TimelineType().audio
        self.Collapse()

        self._rgb1 = (220, 225, 250)
        self._rgb2 = (230, 240, 255)
        self.SetRandomColours()

    # -----------------------------------------------------------------------

    def set_visible_period(self, start, end):
        """Set a period in time to draw some of the views.

        :param start: (float) Start time in seconds.
        :param end: (float) End time in seconds.

        """
        self.__audio_data.set_period(start, end)
        self.GetPane().UpdateAudioInfos(self.__audio_data)

    # -----------------------------------------------------------------------
    
    def set_audio_data(self, nchannels=None, sampwidth=None, framerate=None, duration=None, frames=None):
        self.__audio_data.set_audio_data(nchannels, sampwidth, framerate, duration, frames)
        self.GetPane().UpdateAudioInfos(self.__audio_data)

    # -----------------------------------------------------------------------

    def show_waveform(self, value):
        """Enable or disable the waveform.

        If the waveform is enabled, the infos are automatically disabled.

        """
        self.GetPane().show_waveform(value)
        # Automatically enable infos if nothing else is enabled
        if value is False:
            if self.GetPane().infos_shown() is False:
                self.GetPane().show_infos(True)
        # and automatically disable infos if something else is enabled
        else:
            if self.GetPane().infos_shown() is True:
                self.GetPane().show_infos(False)

        # Send the audio data to be displayed
        self.GetPane().UpdateAudioInfos(self.__audio_data)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        mc = sppasAudioVista(self)
        mc.SetBackgroundColour(self.GetBackgroundColour())
        mc.SetForegroundColour(self.GetForegroundColour())
        mc.show_infos(True)
        mc.show_waveform(False)
        self.SetPane(mc)

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="AudioView RisePanel")
        self._zoom = 100
        self._show_waveform = True

        s = wx.BoxSizer(wx.VERTICAL)
        btn1 = wx.Button(self, size=wx.Size(100, 40), label="Show info/waveform")
        btn1.Bind(wx.EVT_BUTTON, self._switch_view)
        btn2 = wx.Button(self, size=wx.Size(50, 40), label="Zoom UP")
        btn2.Bind(wx.EVT_BUTTON, self._zoom_up)
        btn3 = wx.Button(self, size=wx.Size(50, 40), label="Zoom DOWN")
        btn3.Bind(wx.EVT_BUTTON, self._zoom_down)
        s.Add(btn1, 0, wx.EXPAND)
        s.Add(btn2, 0, wx.EXPAND)
        s.Add(btn3, 0, wx.EXPAND)

        samples = [
            os.path.join(paths.samples, "samples-fra", "F_F_B003_P8.wav"),
            os.path.join(paths.samples, "samples-eng", "oriana1.wav"),
            os.path.join(paths.samples, "samples-eng", "oriana3.wave")
        ]

        for filename in samples:
            panel = AudioViewPanel(self, filename=filename)

            audio = audio_open(filename)
            panel.set_audio_data(
                nchannels=audio.get_nchannels(),
                sampwidth=audio.get_sampwidth(),
                framerate=audio.get_framerate(),
                duration=audio.get_duration(),
                frames=audio.read_frames(audio.get_nframes()))
            panel.set_visible_period(0., audio.get_duration())
            panel.show_waveform(self._show_waveform)
            panel.Expand()
            s.Add(panel, 0, wx.EXPAND | wx.TOP, 2)

        self.Bind(EVT_TIMELINE_VIEW, self._process_timeview)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    # -----------------------------------------------------------------------

    def _switch_view(self, event):
        self._show_waveform = not self._show_waveform
        for child in self.GetChildren():
            if isinstance(child, AudioViewPanel):
                child.show_waveform(self._show_waveform)

    # -----------------------------------------------------------------------

    def _process_timeview(self, event):
        obj = event.GetEventObject()
        if event.action == "zoom_up":
            obj.ZoomUp()
        elif event.action == "zoom_down":
            obj.ZoomDown()

    # -----------------------------------------------------------------------

    def _zoom_up(self, event):
        for child in self.GetChildren():
            if isinstance(child, AudioViewPanel):
                child.ZoomUp()

    # -----------------------------------------------------------------------

    def _zoom_down(self, event):
        for child in self.GetChildren():
            if isinstance(child, AudioViewPanel):
                child.ZoomDown()
