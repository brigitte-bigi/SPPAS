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

import os
import copy
import logging
import wx

from sppas.core.config import paths

from sppas.ui import _
from ..imgtools import sppasImagesAccess
from ..events import sb
from ..windows import sppasDialog
from ..windows import sppasPanel
from ..windows import BitmapButton
from ..windows import sppasStaticText
from ..windows import sppasStaticLine
from ..windows.book import sppasNotebook
from ..windows import sppasRadioBoxPanel

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
MSG_THEME = _("Icons")
MSG_FADE_IN = _("Fade in dialog windows delta value: ")
MSG_FADE_OUT = _("Fade out dialog windows delta value: ")
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
        fti = sppasImagesAccess().get_bmp_image("iconset", height=s)
        idx1 = il.Add(ftc)
        idx2 = il.Add(fti)
        notebook.AssignImageList(il)

        page1 = FontAndColorsPanel(notebook)
        notebook.AddPage(page1, MSG_FONT_COLORS)
        notebook.SetPageImage(0, idx1)

        page2 = ThemePanel(notebook)
        notebook.AddPage(page2, MSG_THEME)
        notebook.SetPageImage(1, idx2)

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


class ThemePanel(sppasPanel):
    """Settings for icons theme.

    """

    def __init__(self, parent):
        super(ThemePanel, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE
        )
        self._themes = self.list_of_themes()
        current_theme = wx.GetApp().settings.icons_theme
        if current_theme not in self._themes:
            wx.GetApp().settings.icons_theme = self._themes[0]

        logging.debug("List of available icon themes: {}".format(self._themes))
        self._create_content()
        # self.Bind(wx.EVT_BUTTON, self._process_event)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # At left, the list of icons themes
        rb = sppasRadioBoxPanel(self,
            choices=self._themes,
            style=wx.RA_SPECIFY_COLS)
        current_theme = wx.GetApp().settings.icons_theme
        if current_theme not in self._themes:
            current_theme = self._themes[0]
        rb.SetSelection(self._themes.index(current_theme))
        self.Bind(wx.EVT_RADIOBOX, self._process_rb_event, rb)

        # At right, the fade in and fade out values, the splash delay
        fp = sppasPanel(self)
        s = wx.BoxSizer(wx.VERTICAL)
        fade_in = self.__create_spin_panel(fp, 3, 85, wx.GetApp().settings.fade_in_delta, "fade_in_delta", MSG_FADE_IN)
        fade_out = self.__create_spin_panel(fp, -85, -3, wx.GetApp().settings.fade_out_delta,"fade_out_delta", MSG_FADE_OUT)
        splash = self.__create_spin_panel(fp, 1, 10, wx.GetApp().settings.splash_delay,"splash_delay", MSG_SPLASH)
        self.Bind(wx.EVT_SPINCTRL, self._process_spin_event)
        s.Add(fade_in, 1, wx.EXPAND)
        s.Add(fade_out, 1, wx.EXPAND)
        s.Add(splash, 1, wx.EXPAND)
        fp.SetSizer(s)

        sizer.Add(rb, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(2))
        sizer.Add(self.VertLine(), 0, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(2))
        sizer.Add(fp, 1, wx.EXPAND | wx.ALL, border=sppasPanel.fix_size(2))
        self.SetSizerAndFit(sizer)

    # -----------------------------------------------------------------------

    def __create_spin_panel(self, parent, min_value, max_value, init_value, spin_name, msg):
        p = sppasPanel(parent)
        s = wx.BoxSizer(wx.HORIZONTAL)
        text = sppasStaticText(p, label=msg)
        spin = wx.SpinCtrl(p, value="",
                           min=min_value, max=max_value, initial=init_value,
                           style=wx.SP_BORDER | wx.SP_ARROW_KEYS | wx.ALIGN_RIGHT,
                           name=spin_name)
        s.Add(text, 1, wx.EXPAND)
        s.Add(spin, 0, wx.ALL, p.fix_size(4))
        p.SetSizer(s)
        return p

    # ------------------------------------------------------------------------

    def VertLine(self):
        """Return a vertical static line."""
        line = sppasStaticLine(self, orient=wx.LI_VERTICAL)
        line.SetMinSize(wx.Size(1, -1))
        line.SetSize(wx.Size(1, -1))
        line.SetPenStyle(wx.PENSTYLE_SOLID)
        line.SetDepth(1)
        return line

    # -----------------------------------------------------------------------

    def list_of_themes(self):
        """Return the theme names from the icons' folder of the package."""
        themes = list()
        for f in os.listdir(paths.icons):
            if os.path.isdir(os.path.join(paths.icons, f)) is True:
                themes.append(f)
        return themes

    # -----------------------------------------------------------------------

    def _process_rb_event(self, event):
        """Set the icons theme to match the checked radiobox."""
        cur_idx = event.GetEventObject().GetSelection()
        wx.GetApp().settings.icons_theme = self._themes[cur_idx]
        logging.debug("Icons theme set to: {:s}".format(wx.GetApp().settings.icons_theme))

    # -----------------------------------------------------------------------

    def _process_spin_event(self, event):
        """Set the fade in or fade out value."""
        spinstrl = event.GetEventObject()
        name = spinstrl.GetName()
        wx.GetApp().settings.set(name, spinstrl.GetValue())

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
