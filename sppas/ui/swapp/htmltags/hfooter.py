# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.htmltags.hfooter.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Default footer node for any SPPAS Web APPlication.

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

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLFooterNode

from sppas.core.config import sg
from sppas.ui.swapp.wappsg import wapp_settings

# -----------------------------------------------------------------------


class SwappFooter(HTMLFooterNode):

    def __init__(self, parent_id: str):
        super(SwappFooter, self).__init__(parent_id)
        self.set_attribute("class", "center")

        self.__create_content()

    # -----------------------------------------------------------------------

    def __create_content(self) -> None:

        # SPPAS splash
        img_splash = HTMLNode(self.identifier, None, "img")
        img_splash.add_attribute("src", f"{wapp_settings.images}/splash-v5-bleu-transparent.png")
        img_splash.add_attribute("class", "")
        img_splash.add_attribute("alt", "")
        self.append_child(img_splash)

        # The copyright
        p_copy = HTMLNode(self.identifier, None, "p",
                          value=sg.__copyright__)
        p_copy.add_attribute("class", "copyright")
        self.append_child(p_copy)

        back_top = HTMLNode(self.identifier, None, "a")
        back_top.add_attribute("href", "#header-content")
        back_top.add_attribute("role", "button")
        back_top.add_attribute("class", "action-button")
        self.append_child(back_top)
        img_top = HTMLNode(back_top.identifier, None, "img")
        img_top.add_attribute("src", f"{wapp_settings.icons}Refine/scroll-up.png")
        img_top.add_attribute("class", "small-logo")
        img_top.add_attribute("alt", "Scoll Up")
        back_top.append_child(img_top)
