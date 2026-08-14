/**
 :filename: statics.js.slides.navigation_logic.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Navigation logic for the Slides module.

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
 * Handles all navigation state transitions on SlidesData.
 *
 * Rules:
 * - Reads and writes SlidesData. Never touches the DOM.
 * - Calls onNavigate(data) after every state change.
 * - updateFromHash does NOT update window.location.hash.
 * - next/prev/goTo/goStart/goEnd DO update window.location.hash.
 */
export default class NavigationLogic {

    /**
     * @param {import('./slides_data.js').default} data
     */
    constructor(data) {
        this._data = data;
        this._onNavigate = null;
    }

    /** @param {function(SlidesData):void} fn */
    set onNavigate(fn) {
        this._onNavigate = typeof fn === 'function' ? fn : null;
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    next() {
        const { currentIndex, currentStep } = this._data;
        const maxStep = this._incrementalCount(currentIndex);

        if (currentIndex === this._data.count && currentStep >= maxStep) {
            return;
        }

        if (currentStep >= maxStep) {
            this._navigateTo(currentIndex + 1, 0);
        } else {
            this._navigateTo(currentIndex, currentStep + 1);
        }
    }

    prev() {
        const { currentIndex, currentStep } = this._data;
        if (currentIndex === 1 && currentStep === 0) {
            return;
        }

        if (currentStep === 0) {
            const prevIdx = currentIndex - 1;
            this._navigateTo(prevIdx, this._incrementalCount(prevIdx));
        } else {
            this._navigateTo(currentIndex, currentStep - 1);
        }
    }

    /** @param {number} index @param {number} [step=0] */
    goTo(index, step = 0) {
        this._navigateTo(index, step);
    }

    goStart() {
        this._navigateTo(1, 0);
    }

    goEnd() {
        const last = this._data.count;
        this._navigateTo(last, this._incrementalCount(last));
    }

    toggleContent() {
        const slide = this._data.slides[this._data.currentIndex - 1];
        if (!(slide instanceof HTMLElement)) {
            return;
        }
        const video = slide.querySelector('video');
        if (!(video instanceof HTMLVideoElement)) {
            return;
        }
        if (video.paused || video.ended) {
            video.play();
        } else {
            video.pause();
        }
    }

    /**
     * Apply position from hash string.
     * Does NOT write back to window.location.hash.
     *
     * @param {string} hash - e.g. '#3.1'
     */
    updateFromHash(hash) {
        if (typeof hash !== 'string' || hash === '' || hash[0] !== '#') {
            this._setPosition(1, 0);
            return;
        }

        const parts = hash.substring(1).split('.');
        const idx = parseInt(parts[0], 10);
        const stp = parts.length > 1 ? parseInt(parts[1], 10) : 0;

        // The address holds the reading and nothing else. A fragment that is
        // not a position names a place in the document: it is an entry of the
        // treatment that reaches a place, and the reading does not move for it.
        if (Number.isNaN(idx) === true) {
            return;
        }

        this._setPosition(idx, Number.isNaN(stp) ? 0 : stp);
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    /**
     * Navigate to index/step, then update window.location.hash.
     * @private
     */
    _navigateTo(index, step) {
        const changed = this._setPosition(index, step);
        if (changed) {
            window.location.hash = `#${this._data.currentIndex}.${this._data.currentStep}`;
        }
    }

    /**
     * Apply clamped position on data and fire onNavigate.
     * Skips if nothing changed, except on first call (previousIndex === 0).
     *
     * @private
     * @returns {boolean} true if state changed
     */
    _setPosition(index, step) {
        const clamped = this._clampIndex(index);
        const clampedStep = this._clampStep(clamped, step);

        const isInitial = this._data.previousIndex === 0;
        const unchanged = clamped === this._data.currentIndex
                       && clampedStep === this._data.currentStep;

        if (!isInitial && unchanged) {
            return false;
        }

        // Pause video on the slide we're leaving
        const prevSlide = this._data.slides[this._data.currentIndex - 1];
        if (prevSlide instanceof HTMLElement) {
            const v = prevSlide.querySelector('video');
            if (v instanceof HTMLVideoElement) {
                v.pause();
            }
        }

        this._data.previousIndex = this._data.currentIndex;
        this._data.currentIndex  = clamped;
        this._data.currentStep   = clampedStep;

        // Autoplay video on the slide we're entering
        if (this._data.autoPlay) {
            const currSlide = this._data.slides[clamped - 1];
            if (currSlide instanceof HTMLElement) {
                const v = currSlide.querySelector('video');
                if (v instanceof HTMLVideoElement) {
                    v.play();
                }
            }
        }

        if (this._onNavigate !== null) {
            this._onNavigate(this._data);
        }

        return true;
    }

    /**
     * @private
     * @param {number} index - 1-based
     * @returns {number}
     */
    _incrementalCount(index) {
        const slide = this._data.slides[this._clampIndex(index) - 1];
        if (!(slide instanceof HTMLElement)) {
            return 0;
        }
        return slide.querySelectorAll('.incremental > *').length;
    }

    /** @private */
    _clampIndex(index) {
        const n = this._data.count;
        if (n === 0) {
            return 1;
        }
        return Math.max(1, Math.min(index, n));
    }

    /** @private */
    _clampStep(index, step) {
        return Math.max(0, Math.min(step, this._incrementalCount(index)));
    }
}
