# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.page_editor.datactrls.videoframe.py
:author:   Audric V., Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A video window with 1 or 3 frames of the video and a tier.

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

A video frame which shows info, previous, current and next images of a video
in a standard frame and the selected tier of annotations in the editor.

When collapsed, the collapsible panel shows only the file name and when
expanded, it shows all the info and the previous and next frames of the
frames currently played.

Previous and next frames and frame numbers should be only shown when using
frame-by-frame feature, in order to limit as much as possible performance
issues when playing videos.

"""

import logging
import os.path
import random
import wx
import wx.lib.newevent

from sppas.core.config import paths
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasTrsRW
from sppas.src.imgdata import sppasImage
from sppas.ui import _
from sppas.ui.wxapp.windows import sppasFrame
from sppas.ui.wxapp.windows import sppasImagePanel
from sppas.ui.wxapp.windows import sppasPanel
from sppas.ui.wxapp.windows import sppasStaticText
from sppas.ui.wxapp.windows import sppasToolbar
from sppas.ui.wxapp.windows import sppasImageRatioPanel

from ..media.tickslider import sppasTicksSlider

from .layerctrl import sppasTierWindow
from .layerctrl import TierEvent
from .layerctrl import EVT_TIER
from .filmctrl import FRAME_FILL_COLOUR
from .videodatavalues import VideoDataValues

# -----------------------------------------------------------------------
# Events
# -----------------------------------------------------------------------

VideoFrameEvent, EVT_VIDEO_FRAME = wx.lib.newevent.NewEvent()
AnnotationManagementEvent, EVT_ANN_MANAGEMENT = wx.lib.newevent.NewEvent()
_MV_POINT_START_0_FD_RADIUS = "efp_left_noradius"
_MV_POINT_START_1_FD_RADIUS = "efp_left_radius"
_MV_POINT_MID_HALF_FD_RADIUS = "efp_middle_noradius"
_MV_POINT_MID_1_AND_HALF_FD_RADIUS = "efp_middle_radius"
_MV_POINT_END_0_FD_RADIUS = "efp_right_noradius"
_MV_POINT_END_1_FD_RADIUS = "efp_right_radius"

# -----------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------

FRAME_BORDER = 2

# -----------------------------------------------------------------------
# Messages
# -----------------------------------------------------------------------

# Frames
LABEL_FRAME_NUMBER_TEXT = _("Frame no. {:s}")
LABEL_UNKNOWN_FRAME_NUMBER = _("unknown")

TOOLTIP_PREVIOUS_FRAME = _("Previous frame")
TOOLTIP_CURRENT_FRAME = _("Current frame")
TOOLTIP_NEXT_FRAME = _("Next frame")

# Video info
TOOLTIP_VIDEO_FILENAME = _("Video file path: {:s}")
TOOLTIP_VIDEO_RESOLUTION = _("Resolution (in pixels)")
TOOLTIP_VIDEO_FRAME_RATE = _("Frame rate (number of frames per second)")
TOOLTIP_VIDEO_DURATION = _("Duration (HH:MM:SS.ms)")

# Toolbar buttons
TOOLTIP_ZOOM_OUT = _("Decrease height of time ruler and annotations")
TOOLTIP_ZOOM_IN = _("Increase height of time ruler and annotations")
TOOLTIP_MV_POINT_START_0_FD_RADIUS = _(
    "Move the point to current frame's start and use no radius")
TOOLTIP_MV_POINT_START_1_FD_RADIUS = _(
    "Move the point to current frame's start and use the duration of a frame as radius")
TOOLTIP_MV_POINT_MIDDLE_HALF_FD_RADIUS = _(
    "Move the point to current frame's middle and use the duration of half a frame as radius")
TOOLTIP_MV_POINT_MIDDLE_1_AND_HALF_FD_RADIUS = _(
    "Move the point to current frame's middle and use the duration of one and a half frames as radius")
TOOLTIP_MV_POINT_END_0_FD_RADIUS = _(
    "Move the point to current frame's end and use no radius")
TOOLTIP_MV_POINT_END_1_FD_RADIUS = _(
    "Move the point to current frame's end and use the duration of a frame as radius")
TOOLTIP_PLAY_PREV_FRAME = _("Display backward three successive video frames")
TOOLTIP_PLAY_NEXT_FRAME = _("Display forward three successive video frames")

# -----------------------------------------------------------------------


class VideoAnnotationFrame(sppasFrame):
    """Display frames of a video and its corresponding annotations.

    Information on the video file displayed are its file name, resolution,
    framerate and duration.

    The following information of video frames are also shown: frame number,
    frame time range and frame position.

    """

    def __init__(self, *args, **kwargs):
        """Construct an instance.

        See the documentation of `sppasFrame` and its parent classes for more
        details about parameters.

        """
        super().__init__(*args, **kwargs)

        self._file_path = None
        self.__cur_frame_idx = -1
        self.__video_data = VideoDataValues()
        self.__period = (0., 0.)

        self._create_content()
        self._setup_events()

        self.SetMaxSize(wx.Display().GetClientArea().GetSize())
        if self.GetTopLevelParent() is not None:
            self.SetSize(width=-1, height=wx.GetTopLevelParent(self).GetSize()[1])
        self.Center()
        self.Fit()

    # -----------------------------------------------------------------------
    # Data setters and UI updates (public)
    # -----------------------------------------------------------------------

    def set_video_data(self, video_data: VideoDataValues) -> None:
        """Set the data of the video.

        The video data are storing the framerate, the duration, and the
        resolution of the video. The period of time stored in these data is
        the one of the timeline, not the one of this video frame.

        :param video_data: (VideoDataValues) All-in-one video data

        """
        self.__video_data = video_data

    # -----------------------------------------------------------------------

    def set_filename(self, file_path: str) -> None:
        """Set the file path of the video.

        The file name will be shown in the corresponding text and the full
        path when hovering this text.

        :param file_path: (str) the complete path to the file being played

        """
        self._file_path = file_path

    # -----------------------------------------------------------------------

    def UpdateVideoInfos(self) -> None:
        """Update the information about the video.

        """
        self._info_panel.UpdateVideoInfos(file_path=self._file_path, video_data=self.__video_data)

    # -----------------------------------------------------------------------

    def UpdateTier(self, tier: sppasTier, ann_idx: int, selected_point: sppasPoint = None) -> None:
        """Update the tier to be annotated.

        :param tier: (sppasTier or None) the tier to use
        :param ann_idx: (int) the index of the selected annotation in the tier
        :param selected_point: (sppasPoint or None) the selected point

        """
        self._tierann_panel.UpdateTier(tier=tier, ann_idx=ann_idx, selected_point=selected_point)

    # -----------------------------------------------------------------------

    def UpdateFrames(self,
                     current_image: sppasImage,
                     current_image_index: int,
                     previous_image: sppasImage = None,
                     next_image: sppasImage = None) -> None:
        """Update the video frame(s).

        :param current_image: (sppasImage) current image in the video
        :param current_image_index: (int) number of the current image
        :param previous_image: (sppasImage or None) previous image of the current one
        :param next_image: (sppasImage or None) next image of the current one

        """
        self.__cur_frame_idx = current_image_index
        if current_image is None:
            # Set a blank frame if no current image is passed
            cfp = self.FindWindow("current_frame_panel")
            cfp_size = cfp.GetSize()
            current_image = sppasImage(0).blank_image(w=cfp_size.GetWidth(), h=cfp_size.GetHeight())

        if previous_image is not None and next_image is not None:
            self._update_videoframes(prev_img=previous_image, cur_img=current_image, next_img=next_image)
            # everything is updated, the panel can be refreshed
            self.Refresh()
        else:
            self._update_playpanel(current_image)

    # -----------------------------------------------------------------------
    # Content construction (protected)
    # -----------------------------------------------------------------------

    def _create_content(self) -> None:
        """Create the whole content of the video frame. """
        sizer = wx.BoxSizer(wx.VERTICAL)
        border = self.fix_size(FRAME_BORDER)

        # information about the video
        info_panel = VideoInfosPanel(parent=self, name="vidinfos_panel")
        sizer.Add(window=info_panel,
                  proportion=0,
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                  border=border)
        info_panel.Show()

        # a single frame of the video
        videoplay_panel = sppasImageRatioPanel(parent=self, name="videoplay_panel")
        videoplay_panel.SetBackgroundColour(FRAME_FILL_COLOUR)
        sizer.Add(window=videoplay_panel,
                  proportion=1,
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
                  border=border)
        videoplay_panel.Show()

        # a sequence of 3 frames of the video
        # TODO: externalize into a standalone class
        videoframes_panel = self._create_videoframes_panel(parent=self, border=border)
        sizer.Add(window=videoframes_panel,
                  proportion=1,
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                  border=border)
        videoframes_panel.Hide()

        # a single tier displaying annotations of the frames' period
        tier_panel = TierAnnotationPanel(parent=self, name="tierann_panel")
        sizer.Add(window=tier_panel,
                  proportion=0,
                  flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                  border=border)
        tier_panel.Hide()

        self.SetSizer(sizer)

    # ----------------------------------------------------------------------

    def _create_videoframes_panel(self, parent: wx.Window, border: int) -> sppasPanel:
        """Return a panel to display a sequence of 3 frames.

        :param parent: (wx.Window) the parent of the video frames panel
        :param border: (int) the size of the border to apply between frames

        """
        _panel = sppasPanel(parent=parent, name="videoframes_panel")
        _sizer = wx.GridSizer(cols=3, vgap=10, hgap=0)

        previous_panel = self.__create_vidframe_panel(
            frame_panel_name="previous_frame_panel",
            frame_image_name="previous_frame_image_panel",
            frame_number_text_name="previous_frame_number_text",
            frame_number_text_tooltip=TOOLTIP_PREVIOUS_FRAME)

        current_panel = self.__create_vidframe_panel(
            frame_panel_name="current_frame_panel",
            frame_image_name="current_frame_image_panel",
            frame_number_text_name="current_frame_number_text",
            frame_number_text_tooltip=TOOLTIP_CURRENT_FRAME)

        next_panel = self.__create_vidframe_panel(
            frame_panel_name="next_frame_panel",
            frame_image_name="next_frame_image_panel",
            frame_number_text_name="next_frame_number_text",
            frame_number_text_tooltip=TOOLTIP_NEXT_FRAME)

        _sizer.Add(window=previous_panel, proportion=0, flag=wx.EXPAND | wx.RIGHT, border=border)
        _sizer.Add(window=current_panel, proportion=1, flag=wx.EXPAND, border=0)
        _sizer.Add(window=next_panel, proportion=0, flag=wx.EXPAND | wx.LEFT, border=border)
        _panel.SetSizerAndFit(_sizer)
        return _panel

    # ----------------------------------------------------------------------

    def __create_vidframe_panel(self,
                                frame_panel_name: str,
                                frame_image_name: str,
                                frame_number_text_name: str,
                                frame_number_text_tooltip: str) -> sppasPanel:
        # main frame panel & its sizer
        _panel = sppasPanel(parent=self._videoframes_panel, name=frame_panel_name)
        _width = self.__video_data.width
        _height = self.__video_data.height
        _border = self.fix_size(FRAME_BORDER)

        # frame's number text
        _text = sppasStaticText(parent=_panel,
                                name=frame_number_text_name,
                                label=LABEL_FRAME_NUMBER_TEXT.format(LABEL_UNKNOWN_FRAME_NUMBER),
                                style=wx.ALIGN_CENTRE_HORIZONTAL)
        _text.SetToolTip(frame_number_text_tooltip)

        # frame's image panel
        _image_panel = sppasImageRatioPanel(parent=_panel,
                                            size=wx.Size(width=_width, height=_height),
                                            name=frame_image_name,
                                            horizontal_alignment=wx.ALIGN_CENTER,
                                            vertical_alignment=wx.ALIGN_CENTER)
        _image_panel.SetBackgroundColour(FRAME_FILL_COLOUR)

        _sizer = wx.BoxSizer(wx.VERTICAL)
        _sizer.Add(window=_text, proportion=0, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=_border)
        _sizer.Add(window=_image_panel, proportion=1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM, border=_border)
        _panel.SetSizerAndFit(_sizer)
        return _panel

    # ----------------------------------------------------------------------
    # Access to some elements of the UI (protected)
    # ----------------------------------------------------------------------

    @property
    def _info_panel(self):
        return self.FindWindow("vidinfos_panel")

    @property
    def _videoframes_panel(self):
        return self.FindWindow("videoframes_panel")

    @property
    def _videoplay_panel(self):
        return self.FindWindow("videoplay_panel")

    @property
    def _tierann_panel(self):
        return self.FindWindow("tierann_panel")

    # -----------------------------------------------------------------------
    # Update video frames panel or play panel (protected and private)
    # ----------------------------------------------------------------------

    def _update_videoframes(self, prev_img: sppasImage, cur_img: sppasImage, next_img: sppasImage) -> None:
        """Update the video frames with the given 3 images.

        """
        previous_frame_index = self.__cur_frame_idx - 1 if self.__cur_frame_idx > 0 else -1
        self._set_frame(frame_index=previous_frame_index,
                        image_panel=self.FindWindow("previous_frame_image_panel"),
                        frame_number_text=self.FindWindow("previous_frame_number_text"),
                        image=prev_img)

        current_frame_index = self.__cur_frame_idx if self.__cur_frame_idx > 0 else -1
        self._set_frame(frame_index=current_frame_index,
                        image_panel=self.FindWindow("current_frame_image_panel"),
                        frame_number_text=self.FindWindow("current_frame_number_text"),
                        image=cur_img)

        next_frame_index = self.__cur_frame_idx + 1 if self.__cur_frame_idx > 0 else -1
        self._set_frame(frame_index=next_frame_index,
                        image_panel=self.FindWindow("next_frame_image_panel"),
                        frame_number_text=self.FindWindow("next_frame_number_text"),
                        image=next_img)

        # Show all the panels but the videoplay one.
        try:
            self._update_range_in_tieranns_panel()
        except Exception as e:
            wx.LogError(str(e))
            self._tierann_panel.Enable(False)

        # Show everything but the image panel for playback (if it's not already the case)
        self._update_frame_panels(False)

    # -----------------------------------------------------------------------

    def _update_playpanel(self, image: sppasImage) -> None:
        """Update the play panel with the given image.

        """
        vp = self._videoplay_panel
        self._set_frame_panel_image(image=image, image_panel=vp)

        # Show only the image panel for playback and hide the rest (if it's not already the case)
        self._update_frame_panels(True)
        vp.Refresh()

    # -----------------------------------------------------------------------

    def _update_frame_panels(self, video_frames_panel_shown_value: bool) -> None:
        """Update frame panels depending on video frames panel's visibility.

        :param video_frames_panel_shown_value: (bool) the visibility value of the video
        frames panel with which frame panels' visibility will be updated

        """
        video_frames_panel = self._videoframes_panel
        if video_frames_panel.IsShown() is video_frames_panel_shown_value:
            self._videoplay_panel.Show(video_frames_panel_shown_value)

            video_frames_panel.Show(not video_frames_panel_shown_value)
            self._tierann_panel.Show(not video_frames_panel_shown_value)
            self.FindWindow("previous_frame_panel").Show(not video_frames_panel_shown_value)
            self.FindWindow("next_frame_panel").Show(not video_frames_panel_shown_value)
            self.Layout()

    # -----------------------------------------------------------------------

    def _set_frame(self,
                   frame_index: int,
                   image_panel: sppasImageRatioPanel,
                   frame_number_text: sppasStaticText,
                   image: sppasImage = None) -> None:
        """Set the image of the given frame with its number in the video file.

        :param frame_index: (int) the index of the current frame
        :param image_panel: (sppasImageRatioPanel) the image panel to update
        :param frame_number_text: (sppasStaticText) the text UI element for the
        displayed frame number
        :param image: (sppasImage) the current image, which can be `None`

        """
        self._set_frame_panel_image(image=image, image_panel=image_panel)
        self._set_frame_number_label(text_element=frame_number_text, frame_index=frame_index)

    # ----------------------------------------------------------------------

    @staticmethod
    def _set_frame_number_label(text_element: sppasStaticText, frame_index: int) -> None:
        # display "-" for unknown frame numbers or invalid data provided
        # frame indexes start from 0, so we need to add 1 to get the frame number
        text_element.SetLabel(LABEL_FRAME_NUMBER_TEXT.format(str(frame_index + 1) if frame_index >= 0 else "-"))

    @staticmethod
    def _set_frame_panel_image(image: sppasImage, image_panel: sppasImagePanel) -> None:
        if wx.Platform == '__WXGTK__':
            # This is an attempt to support any version and to provide blinking
            image_panel.SetBackgroundImageArray(image.iresize(512, 0))
        else:
            image_panel.SetBackgroundImageArray(image)

    # ----------------------------------------------------------------------
    # Update tier's annotation panel (protected)
    # ----------------------------------------------------------------------

    def _update_range_in_tieranns_panel(self) -> None:
        """Update the tier and ruler with the current time interval.

        """
        frame_duration = 1. / self.__video_data.framerate
        cur_frame_time = self.__cur_frame_idx * frame_duration

        # Time interval for the ruler and the tier
        time_range_begin = cur_frame_time - frame_duration
        if time_range_begin < 0.:
            time_range_begin = 0.

        time_range_end = cur_frame_time + frame_duration * 2
        if time_range_end > self.__video_data.duration:
            time_range_end = self.__video_data.duration
        end_current_frame = cur_frame_time + frame_duration

        # Indicators for the ruler
        i1 = cur_frame_time
        i2 = end_current_frame
        if self.__video_data.duration is not None and end_current_frame > self.__video_data.duration:
            i2 = self.__video_data.duration

        # Update the panel
        self._tierann_panel.UpdateTimeRange(begin_time=time_range_begin,
                                            end_time=time_range_end,
                                            indicators=(i1, i2))
        # Inform parent
        self.notify(action="selected_time_range_update", value=(time_range_begin, time_range_end))

    # -----------------------------------------------------------------------
    # Event handling (public and protected)
    # -----------------------------------------------------------------------

    def _setup_events(self):
        """Bind events."""
        # Events related to the embedded tier window
        self.Bind(event=EVT_TIER, handler=self._process_tier_event)
        if wx.Platform == "__WXMSW__":
            # Do not penalize other OS because of M$ Windows issues
            # Allows to refresh properly when resizing the frame
            self.Bind(event=wx.EVT_SIZE, handler=self._on_size_under_windows)

    # -----------------------------------------------------------------------

    # noinspection PyUnusedLocal
    def _on_size_under_windows(self, event: wx.Event):
        self.Layout()
        self.Refresh()

    # -----------------------------------------------------------------------

    def notify(self, action: str, value: any) -> None:
        """The parent has to be informed that the current frame is required.

        :param action: (str) the action name
        :param value: (any) the event value

        """
        evt = VideoFrameEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(dest=self.GetParent(), event=evt)

    # -----------------------------------------------------------------------

    def _process_tier_event(self, event):
        """Process an event from the embedded tier.

        This is a solution to convert the EVT_TIER received from a
        sppasTierWindow into an EVT_VIDEOFRAME.

        :param event: (wx.Event)

        """
        if event.action == "tier_selected":
            # The event value is the name of the selected tier.
            # We have to send the index of the selected annotation instead.
            self.notify(action=event.action, value=self._tierann_panel.get_selected_ann())
        else:
            self.notify(action=event.action, value=event.value)

# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------


class VideoInfosPanel(sppasPanel):
    """Display metadata of a video.

    TODO: add test

    """

    def __init__(self, parent, name="vidinfos_panel"):
        super().__init__(parent=parent, name=name)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        border = self.fix_size(FRAME_BORDER)

        # file name
        self.filename_text = sppasStaticText(parent=self,
                                             name="filename_text",
                                             label="",
                                             style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(window=self.filename_text, proportion=2, flag=wx.ALL | wx.EXPAND, border=border)

        # frame rate
        frame_rate_text = sppasStaticText(parent=self,
                                          name="framerate_text",
                                          label="",
                                          style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(window=frame_rate_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=border)

        # duration
        duration_text = sppasStaticText(parent=self,
                                        name="duration_text",
                                        label="",
                                        style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(window=duration_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=border)

        # resolution
        resolution_text = sppasStaticText(parent=self,
                                          name="resolution_text",
                                          label="",
                                          style=wx.ALIGN_CENTRE_HORIZONTAL)
        sizer.Add(window=resolution_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=border)

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def UpdateVideoInfos(self, file_path: str, video_data: VideoDataValues) -> None:
        """Update the information about the video.

        :param file_path: (str) the absolute path to the file, which must not
        be `None`
        :param video_data (VideoDataValues) video data, which must not be
        `None`

        """
        filename_text = self.FindWindow("filename_text")
        filename_text.SetToolTip(TOOLTIP_VIDEO_FILENAME.format(file_path))
        filename_text.SetLabel(os.path.basename(file_path))

        framerate_text = self.FindWindow("framerate_text")
        framerate_text.SetToolTip(TOOLTIP_VIDEO_FRAME_RATE)
        framerate_text.SetLabel("{:.2f}".format(video_data.framerate))

        resolution_text = self.FindWindow("resolution_text")
        resolution_text.SetToolTip(TOOLTIP_VIDEO_RESOLUTION)
        resolution_text.SetLabel(
            "{:s}×{:s}".format(str(video_data.width), str(video_data.height)))

        duration_text = self.FindWindow("duration_text")
        duration_text.SetToolTip(TOOLTIP_VIDEO_DURATION)

        (hours, seconds) = divmod(video_data.duration, 3600)
        (minutes, seconds) = divmod(video_data.duration, 60)

        # use 2 as the format of hours and minutes, as we want to display two digits
        # use 6 as the format of seconds, as we want to display two digits, a dot and three digits
        formatted = f"{hours:02.0f}:{minutes:02.0f}:{seconds:06.3f}"

        duration_text.SetLabel("{:s}".format(formatted))

        self.Refresh()
        self.Layout()  # in case the file name has a different length

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


class AnnotationManagementToolbar(sppasToolbar):
    """A sppasToolbar managing annotations' points on the visible frames."""

    # -----------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------
    def __init__(self, *args, **kw):
        """Construct a `AnnotationManagementToolbar` instance.

        See the documentation of `sppasToolbar` and its parent classes for more
        details about parameters.

        """
        super().__init__(*args, **kw)
        self._create_content()

    # -----------------------------------------------------------------------

    def _create_content(self) -> None:
        self.AddButton(icon="zoom_up", tooltip=TOOLTIP_ZOOM_IN)
        self.AddButton(icon="zoom_down", tooltip=TOOLTIP_ZOOM_OUT)

        self.AddSpacer(1)

        self.AddButton(icon=_MV_POINT_START_0_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_START_0_FD_RADIUS)
        self.AddButton(icon=_MV_POINT_START_1_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_START_1_FD_RADIUS)
        self.AddButton(icon=_MV_POINT_MID_HALF_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_MIDDLE_HALF_FD_RADIUS)
        self.AddButton(icon=_MV_POINT_MID_1_AND_HALF_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_MIDDLE_1_AND_HALF_FD_RADIUS)
        self.AddButton(icon=_MV_POINT_END_1_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_END_1_FD_RADIUS)
        self.AddButton(icon=_MV_POINT_END_0_FD_RADIUS, tooltip=TOOLTIP_MV_POINT_END_0_FD_RADIUS)

        self.AddSpacer(1)

        self.AddButton(icon="media_play_prev_frame", tooltip=TOOLTIP_PLAY_PREV_FRAME)
        self.AddButton(icon="media_play_next_frame", tooltip=TOOLTIP_PLAY_NEXT_FRAME)

# ---------------------------------------------------------------------------


class TierAnnotationPanel(sppasPanel):
    """Annotation on a single tier.

    Allows to perform segmentation on a tier with action buttons.
    Current version is not allowing to move boundaries with the mouse.

    """

    TIER_HEIGHT = 20
    ZOOMS = (25, 50, 75, 100, 150, 200, 300)

    # -----------------------------------------------------------------------

    def __init__(self, parent, name="tierann_panel"):
        super().__init__(parent=parent, name=name)
        self.__tier = None
        self.__ann_idx = -1
        self._zoom = 100
        self._create_content()
        # Events from the annotations toolbar
        self.Bind(event=wx.EVT_BUTTON, handler=self._process_toolbar_event)
        self.Bind(event=EVT_TIER, handler=self._process_tier_event)

    # -----------------------------------------------------------------------

    def get_selected_ann(self) -> int:
        return self._tier_window.get_selected_ann()

    # -----------------------------------------------------------------------

    def UpdateTier(self, tier: sppasTier, ann_idx: int, selected_point: sppasPoint = None) -> None:
        """Set the tier for which its annotations will be shown.

        After the tier and its annotation index are set, the frame annotations
        are refreshed.

        :param tier: (sppasTier or None) the tier to use
        :param ann_idx: (int) the index of the selected annotation in the tier
        :param selected_point: (sppasPoint or None) the selected point

        """
        self.__tier = tier
        self.__ann_idx = ann_idx

        tw = self._tier_window
        tw.set_tier(tier)
        tw.set_selected_point(selected_point)
        tw.set_selected_ann(ann_idx)

        if tier is not None:
            tw.Enable(True)
            at = self._ann_toolbar
            at.Enable(self.__tier.is_interval() and tw.get_visible_period() != (0., 0.))
            at.Refresh()
        else:
            tw.Enable(False)

        tw.Refresh()

    # ----------------------------------------------------------------------

    def UpdateTimeRange(self, begin_time: float, end_time: float, indicators=()) -> None:
        """Update the tier and ruler to display the given time interval.

        :param begin_time: (float) Start time value
        :param end_time: (float) End time value
        :param indicators: (list) Time values to be inserted in the ruler

        """
        tw = self._tier_window
        tw.set_visible_period(begin=begin_time, end=end_time)
        tw.Refresh()

        fr = self._frames_ruler
        fr.set_range(start=begin_time, end=end_time)
        fr.reset_indicators()

        for value in indicators:
            fr.add_indicator(value)

        fr.Refresh()

        if self.__tier is not None:
            at = self._ann_toolbar
            at.Enable(self.__tier.is_interval() and tw.get_visible_period() != (0., 0.))
            at.Refresh()
        else:
            self._ann_toolbar.Enable(False)

    # ----------------------------------------------------------------------

    def InvalidateTimeRange(self) -> None:
        """Reset the displayed time range."""
        self.UpdateTimeRange(begin_time=0., end_time=0.)

    # -----------------------------------------------------------------------
    # Construct the panel
    # -----------------------------------------------------------------------

    def get_tier_height(self) -> int:
        """Return the height required to draw the film."""
        try:
            h = int(sppasPanel.fix_size(self.TIER_HEIGHT) * self._zoom // 100)
        except AttributeError:
            h = int(self.TIER_HEIGHT * self._zoom // 100)
        return h

    # -----------------------------------------------------------------------

    def _create_content(self) -> None:
        """Create the content of the tier annotation panel."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Time ruler with ticks and indicators
        ruler = sppasTicksSlider(parent=self, name="frames_ruler")
        ruler.show_startend(True)
        ruler.set_allows_changes(False)
        ruler.SetSize(wx.Size(width=-1, height=int(0.75 * float(self.get_tier_height()))))
        sizer.Add(window=ruler, proportion=1, flag=wx.EXPAND, border=0)

        # Tier content on a given range
        tier_window = sppasTierWindow(parent=self, name="tier_window")
        tier_window.show_infos(False)
        tier_window.Enable(False)
        tier_window.SetSize(wx.Size(width=-1, height=self.get_tier_height()))
        sizer.Add(window=tier_window, proportion=1, flag=wx.EXPAND, border=0)

        # Toolbar for actions on annotation boundaries
        tb = AnnotationManagementToolbar(parent=self, name="ann_toolbar")
        tb.Enable(False)
        sizer.Add(window=tb, proportion=0, flag=wx.TOP | wx.ALIGN_CENTER, border=0)

        # sizer setting
        self.SetSizer(sizer)

    # -----------------------------------------------------------------------
    # Access to some elements of the UI (protected)
    # -----------------------------------------------------------------------

    @property
    def _ann_toolbar(self):
        return self.FindWindow("ann_toolbar")

    @property
    def _frames_ruler(self):
        return self.FindWindow("frames_ruler")

    @property
    def _tier_window(self):
        return self.FindWindow("tier_window")

    # -----------------------------------------------------------------------
    # Events (public and protected)
    # -----------------------------------------------------------------------

    def notify(self, action: str, value: any) -> None:
        """The parent has to be informed that the current frame is required.

        :param action: (str) the action name
        :param value: (any) the event value

        """
        evt = TierEvent(action=action, value=value)
        evt.SetEventObject(self)
        wx.PostEvent(dest=self.GetParent(), event=evt)

    # -----------------------------------------------------------------------

    def _process_tier_event(self, event: TierEvent) -> None:
        wx.PostEvent(dest=self.GetParent(), event=event)

    # -----------------------------------------------------------------------

    def _process_toolbar_event(self, event: wx.Event) -> None:
        """Process an action from a button of the toolbar.

        """
        event_name = event.GetEventObject().GetName()
        fr = self._frames_ruler
        tw = self._tier_window

        if "zoom" in event_name:
            if "up" in event_name:
                next_cur_zoom_idx = self.ZOOMS.index(self._zoom) + 1

                if next_cur_zoom_idx < len(self.ZOOMS):
                    self._zoom = self.ZOOMS[next_cur_zoom_idx]
            elif "down" in event_name:
                prev_cur_zoom_idx = self.ZOOMS.index(self._zoom) - 1

                if prev_cur_zoom_idx > 0:
                    self._zoom = self.ZOOMS[prev_cur_zoom_idx]

            fr.SetMinSize(wx.Size(width=-1, height=int(0.75 * float(self.get_tier_height()))))
            tw.SetMinSize(wx.Size(width=-1, height=int(self.get_tier_height())))

            self.Layout()
            self.GetParent().SendSizeEvent()

        elif "media_play" in event_name:
            # Send to the parent to decide the action to perform.
            event.Skip()

        else:
            # ensure we have data
            if self.__tier is None:
                return

            indicators = fr.get_indicator_times()
            if len(indicators) != 2:
                return

            # get the reference point. It's the one the event action will be performed.
            ref_point = self.get_reference_point()
            if ref_point is None:
                logging.warning("No point was selected in the period.")
                return

            # perform the requested action
            new_point = self._create_point(action=event_name, indicators=indicators)
            if new_point is not None:
                tw.move_midpoint(old_time_value=ref_point.get_midpoint(),
                                 time_value=new_point.get_midpoint())
                tw.set_radius(midpoint=new_point.get_midpoint(),
                              new_radius=new_point.get_radius())
            else:
                logging.warning("No point can be moved in the displayed period of time.")
                return

    # -----------------------------------------------------------------------

    def get_reference_point(self):
        """Return the point to be modified by an action in the toolbar.

        :return: Either the currently selected point, or the only visible one or None

        """
        tw = self._tier_window
        start_time, end_time = tw.get_visible_period()
        ref_point = tw.get_selected_point()

        # If no point is selected in the visible period
        if ref_point is None or ref_point < start_time or ref_point > end_time:
            # get all the annotations in the current time interval
            period_ann_idxs = self.__tier.find(begin=sppasPoint(start_time),
                                               end=sppasPoint(end_time),
                                               indexes=True,
                                               radius_overlaps=True)

            if len(period_ann_idxs) == 0:
                return None

            # get all the points in the current time interval
            period_points = self._get_period_points(ann_idxs=period_ann_idxs,
                                                    period_start=start_time,
                                                    period_end=end_time)

            if len(period_points) == 0:
                return None

            if len(period_points) == 1:
                ref_midpoint = period_points[0]
                # Turn this point into the selected one in the tier window
                tw.update_select_annotation(time_value=ref_midpoint)
                self.notify(action="tier_selected", value=self.__tier.get_name())
                # a little bit of precaution
                ref_point = tw.get_selected_point()
                assert ref_midpoint == ref_midpoint  # equal midpoint values

        return ref_point

    # -----------------------------------------------------------------------

    def _get_period_points(self, 
                           ann_idxs: list[int],
                           period_start: float,
                           period_end: float) -> list[sppasPoint]:
        """Return the points of the given annotations in the given period of time."""
        midpoints = list()
        for i in range(0, len(ann_idxs)):
            ann_index = ann_idxs[i]
            ann = self.__tier[ann_index]

            start_point = ann.get_lowest_localization()
            end_point = ann.get_highest_localization()
            if period_start <= start_point <= period_end:
                # tuple structure: annotation index, point, is a start point
                midpoints.append(round(start_point.get_midpoint(), 2))
            if period_start <= end_point <= period_end:
                # tuple structure: annotation index, point, is a start point
                midpoints.append(round(end_point.get_midpoint(), 2))

        return list(set(midpoints))

    # -----------------------------------------------------------------------

    def _create_point(self, action: str, indicators: list[float]) -> sppasPoint:
        """Return the point corresponding to the requested action.
        
        :param action: (str) name of an action
        :param indicators: (list of float) two accepted time values to fix
        midpoint and radius
        :return: sppasPoint
        
        """
        new_point = None
        delta = indicators[1] - indicators[0]
        if action == _MV_POINT_START_0_FD_RADIUS:
            new_point = self._build_point(midpoint=indicators[0])

        elif action == _MV_POINT_START_1_FD_RADIUS:
            new_point = self._build_point(midpoint=indicators[0], radius=delta)

        elif action == _MV_POINT_MID_HALF_FD_RADIUS:
            new_point = self._build_point(midpoint=(indicators[0] + indicators[1]) / 2.,
                                          radius=delta / 2.)

        elif action == _MV_POINT_MID_1_AND_HALF_FD_RADIUS:
            new_point = self._build_point(midpoint=(indicators[0] + indicators[1]) / 2.,
                                          radius=delta * 1.5)

        elif action == _MV_POINT_END_0_FD_RADIUS:
            new_point = self._build_point(midpoint=indicators[1])

        elif action == _MV_POINT_END_1_FD_RADIUS:
            new_point = self._build_point(midpoint=indicators[1], radius=delta)

        return new_point

    # -----------------------------------------------------------------------

    @staticmethod
    def _build_point(midpoint: float, radius: float = None) -> sppasPoint:
        # do we really need the following 2 lines?
        # if midpoint > self.__video_data.duration:
        #     return sppasPoint(midpoint=self.__video_data.duration, radius=radius)
        return sppasPoint(midpoint=max(midpoint, 0.), radius=radius)

# ---------------------------------------------------------------------------


class TestPanel(wx.Panel):
    """Test panel for `ExtendedFramePlayer`."""

    img1 = os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png")
    img2 = os.path.join(paths.samples, "faces", "BrigitteBigiSlovenie2016.jpg")
    img3 = os.path.join(paths.samples, "faces", "BrigitteBigi2020.png")
    imgs = [img1, img2, img3]

    def __init__(self, parent):
        super(TestPanel, self).__init__(parent=parent, name="Video frame")
        filename = os.path.join(paths.samples, "annotation-results", "samples-fra", "F_F_B003-P8-palign.xra")
        parser = sppasTrsRW(filename)
        self.trs = parser.read()

        s = wx.BoxSizer(wx.VERTICAL)
        button = wx.Button(parent=self,
                           pos=(10, 10),
                           size=(180, 70),
                           label="Open video frame",
                           name="frame_player_btn")
        button.Bind(event=wx.EVT_BUTTON, handler=self.process_event)
        s.Add(window=button, proportion=0)

        # Empty panel: no tier, no time range, no indicators
        p0 = TierAnnotationPanel(parent=self)
        s.Add(window=p0, proportion=0, flag=wx.EXPAND)

        # A tier but no time range, no indicators
        p1 = TierAnnotationPanel(parent=self)
        p1.UpdateTier(tier=self.trs[0], ann_idx=-1)
        s.Add(window=p1, proportion=0, flag=wx.EXPAND)

        # A tier with a time range but no indicators
        p2 = TierAnnotationPanel(parent=self)
        p2.UpdateTier(tier=self.trs[0], ann_idx=-1)
        p2.UpdateTimeRange(begin_time=0.5, end_time=3.5)
        s.Add(window=p2, proportion=0, flag=wx.EXPAND)

        # A tier with a time range and indicators
        p3 = TierAnnotationPanel(parent=self)
        p3.UpdateTier(tier=self.trs[0], ann_idx=-1)
        p3.UpdateTimeRange(0.5, 3.5, indicators=(1.5, 2.5))
        s.Add(window=p3, proportion=0, flag=wx.EXPAND)

        self.SetSizer(s)

    # ----------------------------------------------------------------------

    def process_event(self, event: wx.Event) -> None:
        """Process any kind of events.

        TODO: Add a "play" button to refresh images ONCE.

        :param event: (wx.Event) a wx event

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "frame_player_btn":
            video_frame = VideoAnnotationFrame(
                parent=self,
                style=wx.CAPTION | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.DIALOG_NO_PARENT
                | wx.CLOSE_BOX)
            vd = VideoDataValues()
            vd.set_video_data(framerate=30.0, duration=85.65, width=1280, height=720)
            video_frame.set_filename("No filename -- Video frame test")
            video_frame.set_video_data(vd)
            video_frame.Show()

            video_frame.current_image_index = None
            video_frame.UpdateTier(tier=self.trs[1], ann_idx=5)
            video_frame.second = 0

            # noinspection PyUnusedLocal
            def refresh_images(evt: wx.TimerEvent) -> None:
                random.shuffle(TestPanel.imgs)
                video_frame.UpdateFrames(
                    previous_image=sppasImage(filename=TestPanel.imgs[0]).ito_rgb(),
                    current_image=sppasImage(filename=TestPanel.imgs[1]).ito_rgb(),
                    current_image_index=85,
                    next_image=sppasImage(filename=TestPanel.imgs[2]).ito_rgb())

            video_frame.refresh_images = refresh_images

            video_frame.timer = wx.Timer(owner=video_frame)
            video_frame.Bind(event=wx.EVT_TIMER, handler=video_frame.refresh_images, source=video_frame.timer)

            # noinspection PyUnusedLocal
            def stop_timer(evt: wx.CloseEvent) -> None:
                video_frame.timer.Stop()
                video_frame.Destroy()

            video_frame.stop_timer = stop_timer

            video_frame.Bind(event=wx.EVT_CLOSE, handler=video_frame.stop_timer)

            video_frame.timer.Start(milliseconds=5000)
