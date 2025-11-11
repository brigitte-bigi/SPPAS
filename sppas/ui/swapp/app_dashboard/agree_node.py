"""
:filename: sppas.ui.swapp.app_dashboard.agree_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: The agreement dialog of the SPPAS Dashboard Application.

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

from sppas.ui import _

# ---------------------------------------------------------------------------


MSG_INFO = _("By using SPPAS, you are encouraged to mention it in your publications or products, in accordance with the best practices of the AGPL license.")
# En utilisant SPPAS, vous êtes invité à le mentionner dans vos publications ou produits, conformément aux bonnes pratiques de la licence AGPL.
MSG_AGREE = _("I agree")

# ---------------------------------------------------------------------------


class AgreementNode(HTMLNode):
    """A dialog for the user to accept the license requirements.

    """

    def __init__(self, parent_id):
        super(AgreementNode, self).__init__(parent_id, "dashboard_agreement_sec", "section")

        dlg_node = HTMLNode(self.identifier, "agreement_dlg", "dialog") #, value=MSG_INFO)
        dlg_node.add_attribute("id", "agreement_dlg")
        dlg_node.add_attribute("role", "alertdialog")
        dlg_node.add_attribute("class", "info hidden-alert")
        self.append_child(dlg_node)

        agree_p = HTMLNode(dlg_node.identifier, "agree_p", "p", value=MSG_INFO)
        dlg_node.append_child(agree_p)

        agree_btn = HTMLNode(dlg_node.identifier, "agree_btn", "button", value=MSG_AGREE)
        agree_btn.add_attribute("id", "agree_btn")
        agree_btn.add_attribute("onclick", "close_agreement_dialog();")
        agree_btn.add_attribute("onkeydown", "close_agreement_dialog();")
        dlg_node.append_child(agree_btn)
