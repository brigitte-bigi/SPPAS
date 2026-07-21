/**
 :filename: statics.js.slides.note_view.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: DOM rendering for the note (memo) view mode.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa

 Copyright (C) 2023-2026 Brigitte Bigi, CNRS
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

'use strict';

/**
 * Wraps each slide + its associated <aside for="id"> into a .note-container
 * when entering note mode, and restores the original DOM on exit.
 *
 * HTML contract: <aside for="slide-id"> must be a sibling of <section id="slide-id">.
 */
export default class NoteView {

    /**
     * @param {HTMLElement[]} slides
     */
    constructor(slides) {
        this._slides     = Array.isArray(slides) ? slides : [];
        this._containers = [];
    }

    /**
     * @param {import('./slides_data.js').default} data
     */
    onModeChange(data) {
        if (data.mode === 'note') {
            this._build();
        } else {
            this._teardown();
        }
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    _build() {
        if (this._containers.length > 0) {
            return;
        }
        for (const slide of this._slides) {
            const aside = slide.id
                ? document.querySelector(`aside[for="${slide.id}"]`)
                : null;

            const container = document.createElement('div');
            container.className = 'note-container';

            slide.parentNode.insertBefore(container, slide);
            container.appendChild(slide);
            if (aside instanceof HTMLElement) {
                container.appendChild(aside);
            }

            this._containers.push(container);
        }
    }

    _teardown() {
        if (this._containers.length === 0) {
            return;
        }
        for (const container of this._containers) {
            const parent = container.parentNode;
            if (!(parent instanceof HTMLElement)) {
                continue;
            }
            while (container.firstChild) {
                parent.insertBefore(container.firstChild, container);
            }
            parent.removeChild(container);
        }
        this._containers = [];
    }
}
