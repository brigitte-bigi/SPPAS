/**
 :filename: statics.js.slides.touch.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Touch navigation controller for slides.

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
 * This controller handles swipe gestures only.
 * It never manipulates the DOM visually and never decides navigation rules.
 * It simply calls SlidesManager.next() or SlidesManager.prev().
 */
export default class SlidesTouchController {
    /**
     * @param {Object} slidesManager - SlidesManager instance.
     * @param {Object} [options] - Configuration.
     * @param {HTMLElement|null} [options.target] - Element receiving touch events.
     * @param {number} [options.threshold=100] - Minimum horizontal movement in px.
     */
    constructor(slidesManager, options = {}) {
        if (typeof slidesManager !== 'object' || slidesManager === null) {
            throw new Error('SlidesTouchController: "slidesManager" must be an object.');
        }

        this._manager = slidesManager;

        const target = options.target;
        this._target = target instanceof HTMLElement ? target : document.body;

        const threshold = options.threshold;
        this._threshold = typeof threshold === 'number' && threshold > 0 ? threshold : 100;

        this._tracking = false;
        this._originX = 0;

        this._onStart = this._touchStart.bind(this);
        this._onMove = this._touchMove.bind(this);
    }

    /**
     * Activate touch listeners.
     *
     * @returns {void}
     */
    init() {
        this._target.addEventListener('touchstart', this._onStart, { passive: false });
        this._target.addEventListener('touchmove', this._onMove, { passive: false });
    }

    /**
     * Remove all listeners (optional cleanup).
     *
     * @returns {void}
     */
    destroy() {
        this._target.removeEventListener('touchstart', this._onStart, false);
        this._target.removeEventListener('touchmove', this._onMove, false);
    }

    // ---------------------------------------------------------------------
    // Private methods
    // ---------------------------------------------------------------------

    /**
     * Start of gesture: record the X origin.
     *
     * @param {TouchEvent} event - Touch event.
     * @private
     * @returns {void}
     */
    _touchStart(event) {
        if (event.changedTouches.length === 0) {
            return;
        }

        event.preventDefault();

        this._tracking = true;
        this._originX = event.changedTouches[0].pageX;
    }

    /**
     * Movement: detect horizontal swipe.
     *
     * @param {TouchEvent} event - Touch event.
     * @private
     * @returns {void}
     */
    _touchMove(event) {
        if (this._tracking === false) {
            return;
        }
        if (event.changedTouches.length === 0) {
            return;
        }

        const newX = event.changedTouches[0].pageX;
        const delta = this._originX - newX;

        if (delta > this._threshold) {
            this._tracking = false;
            this._manager.next();
            return;
        }

        if (delta < -this._threshold) {
            this._tracking = false;
            this._manager.prev();
            return;
        }
    }
}
