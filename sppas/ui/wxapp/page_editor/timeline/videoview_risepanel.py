# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.timeline.videoview_risepanel.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A rise-panel embedding a video viewer.

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

    Copyright (C) 2011-2023  Brigitte Bigi, CNRS
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
from sppas.ui.wxapp.windows import sppasScrolledPanel
from sppas.ui.wxapp.windows.panels import sppasBaseRisePanel

from ..datactrls.videoframe import EVT_VIDEO_FRAME
from ..datactrls.videoframe import VideoAnnotationFrame
from ..datactrls.videoframe import VideoFrameEvent
from ..datactrls.videodatavalues import VideoDataValues

from .timedatatype import TimelineType
from .baseview_risepanel import sppasFileViewPanel
from .videovista import sppasVideoVista

# ---------------------------------------------------------------------------


class VideoViewPanel(sppasFileViewPanel):
    """A panel to display the content of a video.

    Two objects are embedded in this class, a `sppasVideoVista` to show video
    info in the editor and an `ExtendedFramePlayer to show the video.

    Events emitted by this class is EVT_TIME_VIEW:

        - action="close" to ask for closing the panel

    """

    def __init__(self, parent, filename, name="videoview_risepanel"):
        """Create an VideoViewPanel.

        :param parent: (wx.Window) Parent window must NOT be none
        :param filename: (str) The name of the file of the media
        :param name: (str) the widget name.

        """
        super(VideoViewPanel, self).__init__(parent, filename=filename, name=name)

        self.video_frame = VideoAnnotationFrame(self,
                                                title=self._filename,
                                                style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT,
                                                name="video_frame")

        # The information we need about the video, no more!
        self.__video_data = VideoDataValues()
        self._ft = TimelineType().video
        self._filename = filename
        self.Expand()

        # A random light green between rgb1 and rgb2
        self._rgb1 = (210, 245, 200)
        self._rgb2 = (240, 255, 220)
        self.SetRandomColours()

    # -----------------------------------------------------------------------

    def set_visible_period(self, start, end):
        """Override. Fix the period of time to display (seconds).

        :param start: (int)
        :param end: (int) Time in seconds

        """
        self.__video_data.set_period(start, end)
        self.GetPane().set_visible_period(start, end)
        self.video_frame.set_video_data(self.__video_data)
        self.video_frame.Refresh()

    # -----------------------------------------------------------------------

    def set_video_data(self, framerate=None, duration=None, width=None, height=None) -> None:
        """Set all or any of the data we need about the video."""
        if framerate is not None:
            self.__video_data.framerate = float(framerate)
        if duration is not None:
            self.__video_data.duration = float(duration)
        if width is not None:
            self.__video_data.width = int(width)
        if height is not None:
            self.__video_data.height = int(height)

        self.GetPane().UpdateVideoInfos(self.__video_data)
        self.video_frame.set_video_data(self.__video_data)
        self.video_frame.UpdateVideoInfos()

    # -----------------------------------------------------------------------

    def invalidate_selected_frames(self):
        """Invalidate the visible selected frames in the film view."""
        self.GetPane().set_sel_frames_period(-1., -1.)

    # -----------------------------------------------------------------------

    def update_ann_in_video_frame(self, tier, ann_idx, selected_point=None):
        """Update the tier content of the video frame.

        :param tier: (sppasTier) the tier that is selected in the timeline panel
        :param ann_idx: (int) the index of the selected annotation in the given tier
        :param selected_point: (sppasPoint) the point selected in the tier

        """
        self.video_frame.UpdateTier(tier, ann_idx, selected_point)

    # -----------------------------------------------------------------------

    def show_film(self, value):
        """Enable or disable the view of the sequence of frames.

        If the film view is enabled, the infos are automatically disabled.

        """
        self.GetPane().show_film(value)
        # Automatically enable infos if nothing else is enabled
        if value is False:
            if self.GetPane().infos_shown() is False:
                self.GetPane().show_infos(True)
        # and automatically disable infos if something else is enabled
        else:
            if self.GetPane().infos_shown() is True:
                self.GetPane().show_infos(False)

    # -----------------------------------------------------------------------
    # Construct the GUI
    # -----------------------------------------------------------------------

    def _create_content(self):
        """Override. Create the content of the panel."""
        mc = sppasVideoVista(self)
        mc.show_infos(True)
        mc.show_film(False)
        self.SetPane(mc)

    # -----------------------------------------------------------------------
    # Events management
    # -----------------------------------------------------------------------

    def _setup_events(self) -> None:
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        self.Bind(EVT_VIDEO_FRAME, self.__process_frame_event)

    # -----------------------------------------------------------------------

    def __process_frame_event(self, event: VideoFrameEvent) -> None:
        """Handle `EVT_EXTENDED_FRAME_PLAYER` events from player UI.

        :param event: (ExtendedFramePlayerEvent) an event object from an
        `EVT_EXTENDED_FRAME_PLAYER` event

        """
        if event.action == "selected_time_range_update":
            try:
                time_range = event.value
                self.GetPane().set_sel_frames_period(start=time_range[0], end=time_range[1])
            except (AttributeError, IndexError):
                pass

        else:
            self.notify(action=event.action, value=event.value)

    # -----------------------------------------------------------------------

    def Collapse(self, collapse: bool = True) -> None:
        """Override to show or hide player when collapsing or not the panel.
        
        :param collapse: (bool) whether to collapse the panel and hide or show
        the player interface

        """
        sppasBaseRisePanel.Collapse(self, collapse)
        try:
            # Hide the interface when collapsing the panel and
            # Show the interface when expanding the panel.
            self.video_frame.Show(not collapse)
        except (RuntimeError, AttributeError):
            # if a window is closed even if flags to not allow window closing
            # are set, a RuntimeError would be thrown by wx.
            pass

# ---------------------------------------------------------------------------


class TestPanel(sppasScrolledPanel):

    vid1 = os.path.join(paths.samples, "faces", "video_sample.mp4")
    vid2 = os.path.join(paths.basedir, "demo", "demo.mp4")

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent, name="VideoView RisePanel")

        p1 = VideoViewPanel(self, filename=TestPanel.vid1)
        p2 = VideoViewPanel(self, filename=TestPanel.vid2)
        self._zoom = 100
        self._show_film = True

        s = wx.BoxSizer(wx.VERTICAL)
        btn1 = wx.Button(self, size=wx.Size(100, 40), label="Show info/film")
        btn1.Bind(wx.EVT_BUTTON, self._switch_view)
        s.Add(btn1, 0, wx.EXPAND)
        s.Add(p1, 0, wx.EXPAND | wx.TOP, 2)
        s.Add(p2, 0, wx.EXPAND | wx.TOP, 2)
        self.SetSizer(s)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    # -----------------------------------------------------------------------

    def _switch_view(self, event):
        self._show_film = not self._show_film
        for child in self.GetChildren():
            if isinstance(child, VideoViewPanel):
                child.show_film(self._show_film)
        self.Layout()
