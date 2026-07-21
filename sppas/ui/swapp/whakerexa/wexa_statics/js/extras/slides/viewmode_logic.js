/**
 :filename: statics.js.slides.viewmode_logic.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: View-mode logic for the Slides module.

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
 * Manages the active view mode in SlidesData.
 * Calls onModeChange(data) after every mode transition.
 *
 * No DOM access. No view imports. No controller imports.
 */
export default class ViewModeLogic {

    static MODES = {
        PRESENTATION: 'presentation',
        OVERVIEW:     'overview',
        HANDOUT:      'handout',
        NOTE:         'note',
    };

    static DEFAULT = 'presentation';

    /**
     * @param {import('./slides_data.js').default} data
     */
    constructor(data) {
        this._data = data;
        this._onModeChange = null;
    }

    /** @param {function(SlidesData):void} fn */
    set onModeChange(fn) {
        this._onModeChange = typeof fn === 'function' ? fn : null;
    }

    /** @returns {string} */
    get current() {
        return this._data.mode;
    }

    /**
     * Switch to a new mode.
     * @param {string} mode - One of ViewModeLogic.MODES.*
     */
    set(mode) {
        const valid = Object.values(ViewModeLogic.MODES);
        if (!valid.includes(mode)) {
            return;
        }
        this._data.mode = mode;
        if (this._onModeChange !== null) {
            this._onModeChange(this._data);
        }
    }

    /**
     * Toggle between presentation and a target mode.
     * @param {string} [mode] - Target mode; defaults to overview.
     */
    toggle(mode = ViewModeLogic.MODES.OVERVIEW) {
        const next = this._data.mode === mode
            ? ViewModeLogic.MODES.PRESENTATION
            : mode;
        this._data.mode = next;
        if (this._onModeChange !== null) {
            this._onModeChange(this._data);
        }
    }
}
