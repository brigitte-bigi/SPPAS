/**
:filename: statics.js.progress.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: File that contains the function to update the html progress bar.

-------------------------------------------------------------------------

This file is part of Whakerexa: https://whakerexa.sf.net/

Copyright (C) 2023-2024 Brigitte Bigi, CNRS
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

*/

function update_bar(percent, text = "", header = "") {
    let p = document.getElementById("progress_text");
    if (p != null) {
        p.innerHTML = text;
    }

    let h3 = document.getElementById("progress_header");
    if (h3 != null) {
        h3.innerHTML = header;
    }

    let progress = document.getElementById("percent");
    progress.setAttribute("value", percent);
}
