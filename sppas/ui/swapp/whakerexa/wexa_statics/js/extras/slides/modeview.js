/**
 :filename: statics.js.slides.modeview.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Central manager for the current Slides view mode.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://whakerexa.sf.net/

 Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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
 * This manager provides a single authoritative entry point for switching
 * between presentation / overview modes. It notifies both the SlidesView and
 * the ControlsController to keep the UI perfectly synchronized.
 */
export default class SlidesViewModeManager {

    /**
     * @param {Object} slidesView - Instance of SlidesView.
     * @param {Object} controlsController - Instance of SlidesControlsController.
     */
    constructor(slidesView, controlsController) {

        if (typeof slidesView === 'object' && slidesView !== null) {
            this._slidesView = slidesView;
        } else {
            this._slidesView = null;
        }

        if (typeof controlsController === 'object' && controlsController !== null) {
            this._controlsController = controlsController;
        } else {
            this._controlsController = null;
        }

        this._mode = null;
    }

    /**
     * Set the global view mode.
     *
     * @param {string} mode - A SlidesView.MODES.* value.
     * @returns {void}
     */
    set(mode) {
        this._mode = mode;

        if (this._slidesView !== null &&
            typeof this._slidesView.setMode === 'function') {
            this._slidesView.setMode(mode);
        }

        if (this._controlsController !== null &&
            typeof this._controlsController.updateViewButtons === 'function') {
            this._controlsController.updateViewButtons(mode);
        }
    }

    /**
     * @returns {string|null}
     */
    get() {
        return this._mode;
    }
}
