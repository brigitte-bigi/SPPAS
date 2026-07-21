/**
 :filename: statics.js.slides.slides_data.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Pure state container for the Slides module.

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
 * Pure state container. No logic, no DOM access, no side effects.
 * Logic modules read and write this object. Views read it to render.
 */
export default class SlidesData {

    /**
     * @param {HTMLElement[]} slides
     */
    constructor(slides) {
        this.slides = Array.isArray(slides) ? slides : [];
        this.currentIndex = 1;   // 1-based
        this.currentStep  = 0;
        this.previousIndex = 0;  // 0 = no previous (initial state)
        this.mode = 'presentation';
        this.autoPlay = false;
    }

    /** @returns {number} */
    get count() {
        return this.slides.length;
    }
}
