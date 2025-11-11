# -*- coding: UTF-8 -*-
"""
:filename: sppas.ui.swapp.app_dashboard.script_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Script for the Dashboard of webapp allowing user agreement.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from whakerpy.htmlmaker import HTMLScriptNode

SCRIPT = """

// Open the license agreement dialog alert, but not in modal mode. 
open_dialog('agreement_dlg', false);

// Inform server of acceptance and close the license agreement dialog alert.
async function close_agreement_dialog() {
    // Send a request to the server to inform the user agreed.
    let request = new RequestManager();
    const response = await request.send_post_request({
        licence_agreement: true
    });

    // Check the status of the request then close.
    if (request.status === 200) {
        close_dialog('agreement_dlg');
    }
    else {
        alert(request.status + " " + response.message);
    }
}

"""

# ---------------------------------------------------------------------------


class SwappScript(HTMLScriptNode):

    def __init__(self, parent_id: str):
        super(SwappScript, self).__init__(parent_id)
        self.set_attribute("id", "script-content")
        self.set_value(SCRIPT)
