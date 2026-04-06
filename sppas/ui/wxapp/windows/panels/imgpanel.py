"""
:filename: sppas.ui.wxapp.windows.panels.imgpanel.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A panel is a window on which controls are placed.

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

Panels of SPPAS allow to propagate properly fonts and colors defined in the
settings. An ImagePanel is designing an image instead of the background.

Avoiding flickering under Windows:
----------------------------------
R. Dunn: "On OSX and GTK3 the system does double-buffering internally,
so there really isn’t much reason to do it yourself. If you’re on Windows
then flicker is still an issue that needs to be considered, but you can
tell the system to double-buffer a window by calling SetDoubleBuffered."
(https://discuss.wxpython.org/t/how-to-eliminate-flicker/34596)
Setting the Double Buffering, and adding the parameter "useMask=True" when
setting a Bitmap to True is then required under Windows.

"""

import wx
import wx.lib.scrolledpanel as sc
import os

from sppas.core.config import paths

from .panel import sppasPanel

# ---------------------------------------------------------------------------


class sppasImagePanel(sppasPanel):
    """Create a panel with an optional image as background.

    """

    def __init__(self, parent, id=wx.ID_ANY, image=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="imgbg_panel"):
        self._image = None
        super(sppasImagePanel, self).__init__(parent, id, pos, size, style, name)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(384),
                                sppasPanel.fix_size(128)))
        if image is not None:
            self.SetBackgroundImage(image)

        self.SetDoubleBuffered(True)
        # Bind the events related to our window
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    # -----------------------------------------------------------------------

    def SetBackgroundImage(self, img_filename=None):
        """Set the image filename but do not refresh.

        :param img_filename: (str) None to disable the BG image

        """
        self._image = None
        if img_filename is not None and os.path.exists(img_filename) is True:
            try:
                self._image = wx.Image(img_filename, wx.BITMAP_TYPE_ANY)
                return True
            except:
                pass

        return False

    # -----------------------------------------------------------------------

    def SetBackgroundImageArray(self, img):
        """Set the image from a numpy array but do not refresh.

        :param img: (sppasImage) Numpy array of the image

        """
        try:
            width = img.shape[1]
            height = img.shape[0]
            self._image = wx.Image(width, height)
            self._image.SetData(img.tostring())
            return True
        except:
            pass
        self._image = None
        return False

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        # the image is covering the whole area.
        return

    # -----------------------------------------------------------------------

    def OnEraseBackground(self, evt):
        """Trap the erase event to draw the image as background.

        :param evt: wx.EVT_ERASE_BACKGROUND

        """
        if isinstance(self._image, wx.Image) is True:
            dc = evt.GetDC()
            if not dc:
                dc = wx.ClientDC(self)
            self._draw_background(dc, clear=True)

    # -----------------------------------------------------------------------

    def OnPaint(self, event):
        """Handle paint request and draw hatched lines onto the window"""
        dc = wx.PaintDC(self)
        self._draw_background(dc, clear=True)

    # -----------------------------------------------------------------------

    def _draw_background(self, dc, clear=True):
        w, h = self.GetClientSize()
        if w*h > 0:
            if clear is True:
                dc.Clear()
            if self._image is not None:
                img = self._image.Copy()
                img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.Bitmap(img)
                # useMask has to be true to avoid flickering under Windows.
                dc.DrawBitmap(bmp, x=0, y=0, useMask=True)

# ---------------------------------------------------------------------------


class sppasImageRatioPanel(sppasImagePanel):
    """Create a panel with an optional fitted image as background.

    A panel with an optional background image respecting image's aspect
    ratio while fitting the panel size.

    """

    class AlignmentVertical(object):
        """Represent a subset of wx.Alignment for vertical way only."""

        def __init__(self):
            """Create the dictionary."""
            self.__dict__ = dict(
                TOP=wx.ALIGN_TOP,
                CENTER=wx.ALIGN_CENTER,
                BOTTOM=wx.ALIGN_BOTTOM
            )

        # -----------------------------------------------------------------------

        def __enter__(self):
            return self

        # -----------------------------------------------------------------------

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    # -----------------------------------------------------------------------

    class AlignmentHorizontal(object):
        """Represent a subset of wx.Alignment for horizontal way only."""

        def __init__(self):
            """Create the dictionary."""
            self.__dict__ = dict(
                LEFT=wx.ALIGN_LEFT,
                CENTER=wx.ALIGN_CENTER,
                RIGHT=wx.ALIGN_RIGHT
            )

        # -----------------------------------------------------------------------

        def __enter__(self):
            return self

        # -----------------------------------------------------------------------

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    # -----------------------------------------------------------------------

    def __init__(self, parent, id=wx.ID_ANY, image=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="imgbg_ratio_panel",
                 horizontal_alignment=wx.LEFT,
                 vertical_alignment=wx.TOP):

        super().__init__(parent, id=id, image=image, pos=pos, size=size, style=style, name=name)
        self._align_horiz = horizontal_alignment
        self._align_vert = vertical_alignment

        try:
            s = wx.GetApp().settings
            self.SetBackgroundColour(s.bg_color)
            self.SetForegroundColour(s.fg_color)
            self.SetFont(s.text_font)
        except AttributeError:
            self.InheritAttributes()

    # -----------------------------------------------------------------------

    def SetBackgroundColour(self, colour):
        """Override."""
        wx.Panel.SetBackgroundColour(self, colour)
        for c in self.GetChildren():
            c.SetBackgroundColour(colour)

    # -----------------------------------------------------------------------

    def _draw_background(self, dc: wx.PaintDC, clear: bool = True) -> None:
        """Draw the background image by keeping its aspect retio.

        """
        w, h = self.GetClientSize()
        if w*h > 0:
            if clear is True:
                dc.Clear()

            if self._image is not None:
                panel_width, panel_height = self.GetClientSize()
                image_width, image_height = self._image.GetSize()
                image = self._image.Copy()

                # Find the scale allowing the largest image
                x_scale = float(panel_width) / float(image_width)
                y_scale = float(panel_height) / float(image_height)
                scale = x_scale if (x_scale < y_scale) else y_scale

                # Apply scale to the image size
                new_width = int(float(image_width) * scale)
                new_height = int(float(image_height) * scale)
                image.Rescale(new_width, new_height, quality=wx.IMAGE_QUALITY_HIGH)

                # Apply alignments to shift the position either for x or y
                position_x = 0
                position_y = 0
                if scale == y_scale:
                    if self._align_horiz == self.AlignmentHorizontal().RIGHT:
                        position_x = panel_width - new_width
                    elif self._align_horiz != self.AlignmentHorizontal().LEFT:
                        remaining_width = panel_width - new_width
                        position_x = abs(remaining_width // 2)
                else:
                    if self._align_vert == self.AlignmentVertical().BOTTOM:
                        position_y = panel_height - new_height
                    elif self._align_vert != self.AlignmentVertical().TOP:
                        remaining_height = panel_height - new_height
                        position_y = abs(remaining_height // 2)

                dc.DrawBitmap(wx.Bitmap(image), x=position_x, y=position_y, useMask=True)

# ---------------------------------------------------------------------------
# Panel to test
# ---------------------------------------------------------------------------


class TestPanel(sc.ScrolledPanel):

    # horizontal
    img1 = os.path.join(paths.samples, "faces", "BrigitteBigi_Aix2020.png")
    # vertical
    img2 = os.path.join(paths.samples, "faces", "BrigitteBigi2020.png")

    def __init__(self, parent):
        super(TestPanel, self).__init__(
            parent,
            style=wx.BORDER_NONE | wx.WANTS_CHARS | wx.HSCROLL | wx.VSCROLL,
            name="Test Image Panels")

        # No image defined. It's the default background.
        p5 = sppasImagePanel(self)
        self.MakePanelContent(p5)
        p5.SetBackgroundColour(wx.WHITE)
        # bg transparent image defined.
        p6 = sppasImagePanel(self, image=TestPanel.img2)
        self.MakePanelContent(p6)
        # A bg image defined.
        p7 = sppasImagePanel(self, image=TestPanel.img1)
        self.MakePanelContent(p7)
        p5.SetBackgroundColour(wx.WHITE)

        # Vertical image -- Horizontal panel
        # A bg ratio image defined.
        p8 = sppasImageRatioPanel(self, image=TestPanel.img2, horizontal_alignment=wx.ALIGN_LEFT)
        self.MakePanelContent(p8)
        # A bg ratio image defined.
        p9 = sppasImageRatioPanel(self, image=TestPanel.img2, horizontal_alignment=wx.ALIGN_CENTER)
        self.MakePanelContent(p9)
        p9.SetBackgroundColour(wx.RED)
        # A bg ratio image defined.
        p10 = sppasImageRatioPanel(self, image=TestPanel.img2, horizontal_alignment=wx.ALIGN_RIGHT)
        self.MakePanelContent(p10)

        # Vertical image
        p = wx.Panel(self)
        sv = wx.GridSizer(cols=3, vgap=10, hgap=0)
        # A bg ratio image defined.
        p18 = sppasImageRatioPanel(p, image=TestPanel.img1, vertical_alignment=wx.ALIGN_TOP)
        # A bg ratio image defined.
        p19 = sppasImageRatioPanel(p, image=TestPanel.img1, vertical_alignment=wx.ALIGN_CENTER)
        p19.SetBackgroundColour(wx.RED)
        # A bg ratio image defined.
        p20 = sppasImageRatioPanel(p, image=TestPanel.img1, vertical_alignment=wx.ALIGN_BOTTOM)
        sv.Add(p18, 0, wx.EXPAND | wx.ALL, border=10)
        sv.Add(p19, 0, wx.EXPAND | wx.ALL, border=10)
        sv.Add(p20, 0, wx.EXPAND | wx.ALL, border=10)
        p.SetSizer(sv)
        p.SetMaxSize(wx.Size(1024, -1))
        p.SetBackgroundColour(wx.BLACK)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(p5, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p6, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p7, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p8, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p9, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p10, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.Add(p, 0, wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(sizer)
        self.SetMaxSize(wx.Size(1024, -1))
        self.Layout()
        self.SetupScrolling(scroll_x=True, scroll_y=True)
        self.SetAutoLayout(True)
        self.Refresh()

        self.Bind(wx.EVT_SIZE, self.OnSize)

    def MakePanelContent(self, pane):
        """Just make a few controls to put on the collapsible pane."""
        nameLbl = wx.StaticText(pane, -1, "Name:")
        name = wx.TextCtrl(pane, -1, "")

        addrLbl = wx.StaticText(pane, -1, "Address:")
        addr1 = wx.TextCtrl(pane, -1, "")
        addr2 = wx.TextCtrl(pane, -1, "")

        cstLbl = wx.StaticText(pane, -1, "City, State, Zip:")
        city = wx.TextCtrl(pane, -1, "", size=(150, -1))
        state = wx.TextCtrl(pane, -1, "", size=(50, -1))
        zip = wx.TextCtrl(pane, -1, "", size=(70, -1))

        addrSizer = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        addrSizer.AddGrowableCol(1)
        addrSizer.Add(nameLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(name, 0, wx.EXPAND)
        addrSizer.Add(addrLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        addrSizer.Add(addr1, 0, wx.EXPAND)
        addrSizer.Add((5, 5))
        addrSizer.Add(addr2, 0, wx.EXPAND)

        addrSizer.Add(cstLbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        cstSizer = wx.BoxSizer(wx.HORIZONTAL)
        cstSizer.Add(city, 1)
        cstSizer.Add(state, 0, wx.LEFT | wx.RIGHT, 5)
        cstSizer.Add(zip)
        addrSizer.Add(cstSizer, 0, wx.EXPAND)

        border = wx.BoxSizer()
        border.Add(addrSizer, 1, wx.EXPAND | wx.ALL, 5)
        pane.SetSizer(border)
        pane.SetMaxSize(wx.Size(1024, -1))
        pane.Layout()

    def OnSize(self, evt):
        self.Layout()
