# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.wxapp.main_settings.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The main settings of the SPPAS wx Application.

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

import os
import json
import logging
import wx

# ---------------------------------------------------------------------------


class WxAppSettings(object):
    """Manage the application global settings for look&feel.

    """

    def __init__(self):
        """Create or load the dictionary of settings for the application."""
        # Ensure all members will be set.
        self.reset()
        # Load the existing stored members.
        self.load()

        fh = self.get_font_height()
        self.size_coeff = float(fh) / 10.

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()

    # -----------------------------------------------------------------------

    def GetDefaultIconsTheme(self):
        """The full theme: the one with all icons used to fall back."""
        return "Refine"

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a dump file.

        """
        # Messages are sent to the python logging and not the wx one because
        # our setup_logging occurs after the settings are loaded...
        if os.path.exists(self.__filename):
            try:
                with open(self.__filename, "r") as fd:
                    d = json.load(fd)
                    self.__parse(d)
                    logging.info("Settings loaded from {:s}"
                                 "".format(self.__filename))
            except Exception as e:
                self.reset()
                logging.error("Settings not loaded: {:s}. Reset to default."
                              "".format(str(e)))
        else:
            logging.info("No settings defined. Set to default.")
            self.reset()

    # -----------------------------------------------------------------------

    def save(self):
        """Save the dictionary of settings in a file.

        """
        try:
            with open(self.__filename, 'w') as fd:
                json.dump(self.__serialize(), fd, indent=4, separators=(',', ': '))
            logging.info("Settings saved successfully in file {:s}".format(self.__filename))
        except Exception as e:
            logging.error("Settings not saved: {:s}.".format(str(e)))

    # -----------------------------------------------------------------------

    def set(self, key, value):
        """Set a new value to a key."""
        setattr(self, key, value)

    # -----------------------------------------------------------------------

    def reset(self):
        """Fill the dictionary with the default values."""
        font_height = self.get_font_height()
        self.size_coeff = float(font_height) / 10.

        self.__dict__ = dict(
            # Delay of the splash displayed before the main window, in seconds
            splash_delay=2,

            # Initial properties of the main window
            frame_size=self.__frame_size(),
            frame_pos=wx.Point(10, 10),

            # The current theme of icons -- a folder name of etc/icons
            icons_theme="Refine",

            # Foreground colors
            fg_color=wx.Colour(20, 20, 20),
            # header_fg_color=wx.Colour(240, 240, 230),
            header_fg_color=wx.Colour(0, 0, 0),
            action_fg_color=wx.Colour(230, 230, 225),

            # Background colors
            bg_color=wx.Colour(240, 240, 235, alpha=wx.ALPHA_OPAQUE),
            # header_bg_color=wx.Colour(22, 22, 47, alpha=wx.ALPHA_OPAQUE),
            header_bg_color=wx.Colour(87, 117, 176, alpha=wx.ALPHA_OPAQUE),
            # action_bg_color=wx.Colour(42, 42, 87, alpha=wx.ALPHA_OPAQUE),
            action_bg_color=wx.Colour(66, 82, 98, alpha=wx.ALPHA_OPAQUE),

            # Fonts
            text_font=self.__text_font(),
            header_text_font=self.__header_font(),
            action_text_font=self.__action_font(),
            mono_text_font=self.__mono_font(),

            # header and action panels height
            header_height=font_height * 5,
            action_height=font_height * 3,

            # Value to apply to the opacity when starting/closing dialogs
            fade_in_delta=5,
            fade_out_delta=-5,

            # Editor
            editor_timeline_zoom=100,
            editor_nb_prev_play_frames=3,
            editor_nb_next_play_frames=5
        )

        # Fix the name of the file with the stored settings [can't be changed]
        phoenix_app_dir = os.path.dirname(os.path.abspath(__file__))
        self.__filename = os.path.join(phoenix_app_dir, ".wxapp")

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def get_font_height(self):
        """Return the default font height provided by the system.

        :return: (int) Nb of pixels

        """
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        return font.GetPixelSize()[1]

    # -----------------------------------------------------------------------

    def __get_font_pointsize(self):
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        return font.GetPointSize()

    # -----------------------------------------------------------------------

    def __get_font_pixelsize(self):
        # No font defined? So use the default GUI font provided by the system
        try:  # wx4
            font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        except AttributeError:  # wx3
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

        return font.GetPixelSize()

    # -----------------------------------------------------------------------

    def __text_font(self):
        # pixelSize, family, flags=FONTFLAG_DEFAULT, faceName=””, encoding=FONTENCODING_DEFAULT
        s = self.__get_font_pointsize()
        text_font = wx.Font(s,
                            wx.FONTFAMILY_DEFAULT,
                            wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_NORMAL,
                            underline=False,
                            faceName="Lucida sans",
                            encoding=wx.FONTENCODING_SYSTEM)
        return text_font
        # flags=wx.FONTFLAG_ANTIALIASED

    # -----------------------------------------------------------------------

    def __header_font(self):
        s = self.__get_font_pointsize()
        title_font = wx.Font(int(float(s)*1.5),      # point size
                             wx.FONTFAMILY_DEFAULT,  # family,
                             wx.FONTSTYLE_NORMAL,    # style,
                             wx.FONTWEIGHT_BOLD,     # weight,
                             underline=False,
                             faceName="Lucida sans",
                             encoding=wx.FONTENCODING_SYSTEM)
        return title_font

    # -----------------------------------------------------------------------

    def __action_font(self):
        s = self.__get_font_pointsize()
        button_font = wx.Font(s,                      # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Lucida sans",
                              encoding=wx.FONTENCODING_SYSTEM)
        return button_font

    # -----------------------------------------------------------------------

    def __mono_font(self):
        s = self.__get_font_pointsize()
        mono_font = wx.Font(s,    # point size
                            wx.FONTFAMILY_TELETYPE,   # family,
                            wx.FONTSTYLE_NORMAL,    # style,
                            wx.FONTWEIGHT_NORMAL,   # weight,
                            underline=False,
                            encoding=wx.FONTENCODING_SYSTEM)
        return mono_font

    # -----------------------------------------------------------------------

    def __frame_size(self):
        (w, h) = wx.GetDisplaySize()
        w = float(w)
        h = float(h)
        ratio = h / w
        w = min(0.9 * w, w * 0.6 * self.size_coeff)
        h = min(0.9 * h, w * ratio)
        return wx.Size(max(int(w), 520), max(int(h), 480))

    # -----------------------------------------------------------------------

    def __serialize(self):
        """Convert this setting dictionary into a serializable data structure.

        :returns: (dict) a dictionary that can be serialized (without classes).

        """
        d = dict()
        for k in self.__dict__:
            # save only members of the dict in reset,
            # but do not save added members.
            if k.startswith("_" + self.__class__.__name__) is True:
                continue

            v = self.__dict__[k]
            if isinstance(v, wx.Font):
                d[k] = list()
                d[k].append("font")
                d[k].append(v.GetPointSize())
                d[k].append(v.GetFamily())
                d[k].append(v.GetStyle())
                d[k].append(v.GetWeight())
                d[k].append(v.GetFaceName())
            elif isinstance(v, wx.Colour):
                d[k] = list()
                d[k].append("color")
                d[k].append(v.Red())
                d[k].append(v.Green())
                d[k].append(v.Blue())
                d[k].append(v.Alpha())
            elif isinstance(v, wx.Size):
                d[k] = list()
                d[k].append("size")
                d[k].append(v[0])
                d[k].append(v[1])
            elif isinstance(v, wx.Point):
                d[k] = list()
                d[k].append("pos")
                d[k].append(v[0])
                d[k].append(v[1])
            else:
                d[k] = v

        return d

    # -----------------------------------------------------------------------

    def __parse(self, d):
        """Fill in the internal dictionary with data in the given dict.

        :param d: (dict) a dictionary that can be serialized (without classes).

        """
        self.reset()
        for k in d:
            v = d[k]
            if isinstance(v, list):
                if v[0] == "font":
                    typed_v = wx.Font(*(v[1:5]), faceName=v[5])
                    setattr(self, k, typed_v)
                elif v[0] == "color":
                    typed_v = wx.Colour(*(v[1:]))
                    setattr(self, k, typed_v)
                elif v[0] == "size":
                    typed_v = wx.Size(*(v[1:]))
                    setattr(self, k, typed_v)
                elif v[0] == "pos":
                    typed_v = wx.Point(*(v[1:]))
                    setattr(self, k, typed_v)
            else:
                setattr(self, k, v)
