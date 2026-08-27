"""
:filename: sppas.ui.swapp.wappsg.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary: This is the SPPAS Web-based application global' variables.

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

    Copyright (C) 2011-2026 Brigitte Bigi
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

from sppas.src.wkps.appwkpm import sppasWkpsManager
from sppas.src.wkps.wio import sppasWJSON

from sppas.ui.agnostic import sppasCommKeys
from sppas.ui.agnostic import sppasCommNotifier
from sppas.ui.swapp.main_settings import sppasWebAppSettings
from sppas.ui.swapp.main_trace_store import swappTraceStore

# -----------------------------------------------------------------------


# Instantiate the application settings
wapp_settings = sppasWebAppSettings()

# Instantiate the workspaces manager
wapp_wkps = sppasWkpsManager()

# Instantiate the application events notifier
wapp_notify = sppasCommNotifier()

# Instantiate the shared store of the trace/info records: the swapp server
# is the collector of the traces of all the SPPAS components.
wapp_trace = swappTraceStore()

# -----------------------------------------------------------------------


class sppasWxAppState:
    """Shared state reported by the wx interface interlocutor.

    The state is updated by the communication server, from the messages of
    the wxapp interlocutor: "running" from its HELLO to its BYE, allowing
    any web application to know whether the wx interface is running;
    "workspace_name" from its WKP_CHANGED messages, the display name of its
    current workspace at the time it was sent.

    The name is not an identifier: a workspace is renamed by moving its
    file, and swapp does not track the same workspace across a rename by
    matching names -- it only displays the last one wx reported.

    """

    def __init__(self):
        self.running = False
        self.workspace_name = ""


# Instantiate the shared state of the wx interface
wapp_wxstate = sppasWxAppState()

# -----------------------------------------------------------------------


def notify_wkp_changed() -> None:
    """Notify the observers that the shared workspace changed.

    The workspace of the manager is serialized and published with the
    WKP_CHANGED event key. Without any observer -- no local server, or
    no other UI -- nothing happens.

    """
    wjson = sppasWJSON()
    wjson.set(wapp_wkps.data)
    wapp_notify.notify(sppasCommKeys.WKP_CHANGED, wjson.serialize())

# -----------------------------------------------------------------------


def notify_show_page(page_name: str) -> None:
    """Ask the other UI to show one of its pages.

    The page is named with the vocabulary of the wx interface -- the names
    of its book: "page_files", "page_annotate", "page_analyze",
    "page_editor", "page_convert", "page_plugins". Without any observer --
    no local server, or no other UI -- nothing happens: it is up to the
    caller to launch the interface instead.

    :param page_name: (str) The name of the page to show

    """
    wapp_notify.notify(sppasCommKeys.SHOW_PAGE, page_name)
