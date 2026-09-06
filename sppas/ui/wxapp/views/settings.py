# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.views.settings.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  A custom settings dialog.

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

import copy
import wx

from sppas.ui import _
from ..imgtools import sppasImagesAccess
from ..events import sb
from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import BitmapButton
from ..windows import sppasStaticText
from ..windows.book import sppasNotebook

# ---------------------------------------------------------------------------
# Messages used in this view
# ---------------------------------------------------------------------------

MSG_HEADER_SETTINGS = _("Settings")
MSG_FONT = _("Font")
MSG_BG = _("Background color")
MSG_FG = _("Foreground color")
MSG_FONT_COLORS = _("Fonts and Colors")
MSG_HEADER = _("Top panel")
MSG_CONTENT = _("Main panel")
MSG_ACTIONS = _("Bottom panel")
MSG_SPLASH = _("Duration of the splash window, in seconds: ")

# ----------------------------------------------------------------------------


class sppasSettingsDialog(sppasDialog):
    """Settings dialog view.

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """

    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)

        """
        super(sppasSettingsDialog, self).__init__(
            parent=parent,
            title="Settings",
            style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.STAY_ON_TOP)

        self._back_up = dict()
        self._backup_settings()

        self.CreateHeader(MSG_HEADER_SETTINGS, "settings")
        self._create_content()
        self.CreateActions([wx.ID_CANCEL, wx.ID_OK])

        # Bind events
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.LayoutComponents()
        self.GetSizer().Fit(self)
        self.FadeIn()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def _backup_settings(self):
        """Back-up the settings."""
        settings = wx.GetApp().settings
        for k in settings.__dict__:
            try:
                self._back_up[k] = copy.deepcopy(getattr(settings, k))
            except:
                # deepcopy is using 'pickle' which can't copy some class instances
                self._back_up[k] = getattr(settings, k)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        s = sppasPanel.fix_size(16)
        
        # Make the notebook and an image list
        notebook = sppasNotebook(self, name="content")
        il = wx.ImageList(s, s)
        ftc = sppasImagesAccess().get_bmp_image("font_color", height=s)
        idx1 = il.Add(ftc)
        notebook.AssignImageList(il)

        page1 = FontAndColorsPanel(notebook)
        notebook.AddPage(page1, MSG_FONT_COLORS)
        notebook.SetPageImage(0, idx1)

        self.SetContent(notebook)

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_id = event_obj.GetId()

        if event_id == wx.ID_CANCEL:
            self.on_cancel(event)

        elif event_id == wx.ID_OK:
            self.EndModal(wx.ID_OK)

        else:
            self.UpdateUI()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        settings = wx.GetApp().settings
        for k in self._back_up:
            settings.set(k, self._back_up[k])

        # close the dialog with a wx.ID_CANCEL response
        self.EndModal(wx.ID_CANCEL)

# ----------------------------------------------------------------------------


class FontAndColorsPanel(sppasPanel):
    """Settings for background, foreground and font.

    """

    def __init__(self, parent):
        super(FontAndColorsPanel, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE
        )
        self._create_content()
        self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Colors&Fonts of the header panel
        p1 = sppasColoursFontPickerPanel(
             parent=self,
             style=wx.BORDER_SUNKEN,
             name="colors_font_header",
             title=MSG_HEADER)
        sizer.Add(p1, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(4))

        # Colors&Fonts of the main panel
        p2 = sppasColoursFontPickerPanel(
             parent=self,
             style=wx.BORDER_SUNKEN,
             name="colors_font_content",
             title=MSG_CONTENT)
        sizer.Add(p2, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(4))

        # Colors&Fonts of the actions panel
        p3 = sppasColoursFontPickerPanel(
             parent=self,
             style=wx.BORDER_SUNKEN,
             name="colors_font_actions",
             title=MSG_ACTIONS)
        sizer.Add(p3, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(4))

        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if "color" in event_name:
            self.on_color_dialog(event)
            event.Skip()

        elif "font" in event_name:
            self.on_select_font(event)
            event.Skip()

    # -----------------------------------------------------------------------
    # Callbacks to event
    # -----------------------------------------------------------------------

    def GetColour(self):
        """Return the color the user choose.

        :param parent: (wx.Window)
        :return: (wx.Colour) or None if no color was defined

        """
        # open the dialog
        dlg = wx.ColourDialog(self)

        # Ensure the full colour dialog is displayed,
        # not the abbreviated version.
        dlg.GetColourData().SetChooseFull(True)

        c = None
        if dlg.ShowModal() == wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            r = color.Red()
            g = color.Green()
            b = color.Blue()
            c = wx.Colour(r, g, b)
        dlg.Destroy()

        # Either return None or the wx.Colour(r,g,b)
        return c

    # -----------------------------------------------------------------------

    def on_color_dialog(self, event):
        """Open a dialog to choose a color, then fix it.

        :param event: (wx.Event)

        """
        color = self.GetColour()
        if color is not None:

            # get the button that was clicked on
            button = event.GetEventObject()
            name = button.GetName()

            # new value in the settings for which panel?
            if "content" in button.GetParent().GetName():
                wx.GetApp().settings.set(name, color)

            elif "header" in button.GetParent().GetName():
                wx.GetApp().settings.set("header_"+name, color)

            elif "action" in button.GetParent().GetName():
                wx.GetApp().settings.set("action_"+name, color)

    # -----------------------------------------------------------------------

    def on_select_font(self, event):
        """Open a dialog to choose a font, then fix it.

        :param event: (wx.Event)

        """
        button = event.GetEventObject()

        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.GetApp().settings.fg_color)
        data.SetInitialFont(wx.GetApp().settings.text_font)

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()

            if "content" in button.GetParent().GetName():
                wx.GetApp().settings.set('text_font', font)

            elif "header" in button.GetParent().GetName():
                wx.GetApp().settings.set('header_text_font', font)

            elif "action" in button.GetParent().GetName():
                wx.GetApp().settings.set('action_text_font', font)

        dlg.Destroy()

# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------


class sppasColoursFontPickerPanel(sppasPanel):
    """Panel to propose the change of colors and font.

    """

    def __init__(self, parent,
                 id=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL,
                 name=wx.PanelNameStr,
                 title=""):
        super(sppasColoursFontPickerPanel, self).__init__(parent, id, pos, size, style, name)

        b = sppasPanel.fix_size(5)
        flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL
        gbs = wx.GridBagSizer(hgap=b, vgap=b)

        # ---------- Title

        txt = wx.StaticText(self, -1, title, name="title")
        gbs.Add(txt, (0, 0), flag=flag, border=b)

        # ---------- Background color

        txt_bg = wx.StaticText(self, -1, MSG_BG)
        gbs.Add(txt_bg, (1, 0), flag=flag, border=b)

        btn_color_bg = self.create_button("bg_color")
        gbs.Add(btn_color_bg, (1, 1), flag=flag, border=b)

        # ---------- Foreground color

        txt_fg = wx.StaticText(self, -1, MSG_FG)
        gbs.Add(txt_fg, (2, 0), flag=flag, border=b)

        btn_color_fg = self.create_button(name="fg_color")
        gbs.Add(btn_color_fg, (2, 1), flag=flag, border=b)

        # ---------- Font

        txt_font = wx.StaticText(self, -1, MSG_FONT)
        gbs.Add(txt_font, (3, 0), flag=flag, border=b)

        btn_font = self.create_button(name="font")
        gbs.Add(btn_font, (3, 1), flag=flag, border=b)

        gbs.AddGrowableCol(1)
        self.SetSizer(gbs)
        self.SetMinSize(wx.Size(sppasPanel.fix_size(150),
                                sppasPanel.fix_size(150)))

    # -----------------------------------------------------------------------

    def create_button(self, name):
        btn = BitmapButton(parent=self, name=name)
        btn.SetBorderWidth(1)
        btn.SetFocusWidth(0)
        btn.SetMinSize(wx.Size(sppasPanel.fix_size(20),
                               sppasPanel.fix_size(20)))
        btn.SetSize((wx.GetApp().settings.action_height,
                     wx.GetApp().settings.action_height))
        btn.Bind(sb.EVT_WINDOW_SELECTED, self._on_selected)
        btn.Bind(sb.EVT_WINDOW_FOCUSED, self._on_focused)

        return btn

    # -----------------------------------------------------------------------

    def _on_selected(self, event):
        pass

    # -----------------------------------------------------------------------

    def _on_focused(self, event):
        pass

    # -----------------------------------------------------------------------

    def SetFont(self, font):
        """Override."""
        sppasPanel.SetFont(self, font)
        current = wx.GetApp().settings.text_font
        f = wx.Font(int(current.GetPointSize() * 1.2),
                    wx.FONTFAMILY_SWISS,   # family,
                    wx.FONTSTYLE_NORMAL,   # style,
                    wx.FONTWEIGHT_BOLD,    # weight,
                    underline=False,
                    faceName=current.GetFaceName(),
                    encoding=wx.FONTENCODING_SYSTEM)
        self.FindWindow("title").SetFont(f)

# ---------------------------------------------------------------------------


def Settings(parent):
    """Display a dialog to fix new settings.

    :param parent: (wx.Window)
    :returns: the response

    Returns wx.ID_CANCEL if the dialog is destroyed or wx.ID_OK if some
    settings changed.

    """
    dialog = sppasSettingsDialog(parent)
    response = dialog.ShowModal()
    dialog.DestroyFadeOut()
    return response
