# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swpapp.htmltags.hbutton.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: A button node with easy access to icons.

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

from whakerpy.htmlmaker import HTMLButtonNode
from sppas.ui.swapp.wapputils import sppasImagesAccess

# ---------------------------------------------------------------------------


class sppasHTMLButton(HTMLButtonNode):
    """Represent a button element.

    Overridden for an easier icon access and CSS properties added:
    "sp-button-text" and "sp-button-icon".

    """

    def __init__(self, parent, identifier, attributes=dict()):
        """Create an input node. Default type is 'text'.

        """
        super(sppasHTMLButton, self).__init__(parent, identifier, attributes=attributes)
        self.add_attribute("class", "action-button")

    # -----------------------------------------------------------------------

    def set_icon(self, icon_name, attributes=dict()):
        """Override. Set an icon to the button from its name in the app.

        Class sp-button-icon is added.

        :param icon_name: (str) Name of an icon in the app.
        :param attributes: (dict).

        """
        icon = sppasImagesAccess.get_image_filename(name=icon_name)
        node = HTMLButtonNode.set_icon(self, icon, attributes)
        return node
