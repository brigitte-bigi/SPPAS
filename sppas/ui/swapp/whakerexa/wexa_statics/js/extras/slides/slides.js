import SlidesApp from './slides_app.js';

/**
 :filename: statics.js.slides.slides.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Public facade for the Slides module.

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

export default class Slides {

    /**
     * @param {Object} config - User configuration.
     * @param {NodeList|HTMLElement[]|Array} config.slides - Slide elements.
     * @param {HTMLElement|null} config.progressBar - Progress bar element.
     * @param {HTMLElement|null} config.controls - Slides controls element.
     * @param {HTMLElement|null} config.controlsView - Slides controls view element.
     * @param {HTMLElement|null} config.overviewContainer - Slides overview container.
     * @param {...any} others - Other configuration options.
     */
    constructor(config = {}) {

        // --- Normalize configuration -----------------------------------------
        // We guarantee that "slides" is ALWAYS a true Array.
        // If user gives a NodeList, we convert it.
        // If user gives null/undefined, we use an empty Array.
        // Internal classes never need to question it.
        // ---------------------------------------------------------------------

        let slidesArray = [];

        if (Array.isArray(config.slides)) {
            slidesArray = config.slides;

        } else if (config.slides && typeof config.slides.length === 'number') {
            // NodeList or HTMLCollection
            slidesArray = Array.from(config.slides);

        } else {
            console.error('Slides: "slides" was not a valid list. Using [].');
            slidesArray = [];
        }

        const cleanedConfig = {
            ...config,
            slides: slidesArray
        };

        // --- Instantiate the internal application -----------------------------

        this._app = new SlidesApp(cleanedConfig);
    }

    /**
     * Initialize all components.
     * @returns {void}
     */
    init() {
        this._app.init();
    }

    /**
     * Expose SlidesManager to the outside.
     * @returns {SlidesManager}
     */
    get manager() {
        return this._app.manager;
    }

    /**
     * Expose Fullscreen controller to the outside.
     * @returns {SlidesFullscreenController}
     */
    get fullscreen() {
        return this._app.fullscreen;
    }
}

