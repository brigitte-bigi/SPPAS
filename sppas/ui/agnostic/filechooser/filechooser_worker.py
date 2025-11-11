"""
:filename: sppas.ui.agnostic.filechooser.filechooser_worker.py
:author: Brigitte Bigi
:contact: contact@sppas.org

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

import json
import argparse
from tkinter import Tk
from tkinter import filedialog
import gettext
import os

# Get the path of the 'locale' directory (adjust as needed)
LOCALE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "locale"))
gettext.bindtextdomain("ui", LOCALE_DIR)
gettext.textdomain("ui")
_ = gettext.gettext

# ---------------------------------------------------------------------------


MSG_DESCRIPTION = _("Native file chooser worker.")
MSG_SELECT_FILE = _("Select a file or directory")
MSG_ALLOW_MULTIPLE = _("Allow multiple selection")
MSG_DEFAULT_EXT = _("Default file extension (for savefile)")
MSG_WILDCARDS = _("JSON list of (label, pattern)")
MSG_TYPE = _("Dialog type")
MSG_ALL_FILES = _("All files")

# ---------------------------------------------------------------------------


def parse_args():
    """Argument parsing for the dialog options.

    :return: Parsed arguments

    """
    parser = argparse.ArgumentParser(description=MSG_DESCRIPTION)
    parser.add_argument("mode", choices=["openfile", "savefile", "directory"], help=MSG_TYPE)
    parser.add_argument("--title", type=str, default=MSG_SELECT_FILE)
    parser.add_argument("--multiple", action="store_true", help=MSG_ALLOW_MULTIPLE)
    parser.add_argument("--filetypes", type=str, help=MSG_WILDCARDS)
    parser.add_argument("--defaultext", type=str, help=MSG_DEFAULT_EXT)
    return parser.parse_args()

# ---------------------------------------------------------------------------
# Main execution logic: launches the appropriate native dialog
# according to the mode ('openfile', 'savefile', 'directory').
# Uses Tkinter without a mainloop and returns the result as JSON.
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    try:
        root = Tk()
        root.withdraw()

        filetypes = json.loads(args.filetypes) if args.filetypes else [(MSG_ALL_FILES, "*.*")]
        result = ""

        if args.mode == "openfile":
            if args.multiple:
                result = filedialog.askopenfilenames(title=args.title, filetypes=filetypes)
            else:
                result = filedialog.askopenfilename(title=args.title, filetypes=filetypes)

        elif args.mode == "savefile":
            result = filedialog.asksaveasfilename(title=args.title, defaultextension=args.defaultext, filetypes=filetypes)

        elif args.mode == "directory":
            result = filedialog.askdirectory(title=args.title)

        root.destroy()

        if isinstance(result, tuple) is True:
            # Result contains multiple paths (when --multiple is used)
            print(json.dumps({"paths": list(result)}))
        else:
            print(json.dumps({"path": result}))

    except Exception as e:
        # On error, return a JSON structure with the error as a path.
        print(json.dumps({"path": f"Error : {str(e)}"}))

# ---------------------------------------------------------------------------


if __name__ == "__main__":
    main()
