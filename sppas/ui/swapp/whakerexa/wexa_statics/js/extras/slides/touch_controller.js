/**
 :filename: statics.js.slides.touch_controller.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Touch/swipe input controller for the Slides module.

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
 * Detects horizontal swipe gestures and dispatches slides:navigate events.
 * No reference to logic modules or views.
 *
 * CustomEvents dispatched on document:
 *   slides:navigate → { action: 'next' | 'prev' }
 */
export default class TouchController {

    /**
     * @param {Object} [options]
     * @param {HTMLElement|null} [options.target] - Element to listen on (default: document.body).
     * @param {number} [options.threshold=100] - Minimum swipe distance in px.
     */
    constructor(options = {}) {
        const target = options.target;
        this._target = target instanceof HTMLElement ? target : document.body;

        const threshold = options.threshold;
        this._threshold = typeof threshold === 'number' && threshold > 0 ? threshold : 100;

        this._tracking = false;
        this._originX  = 0;

        this._onStart = this._touchStart.bind(this);
        this._onMove  = this._touchMove.bind(this);
    }

    /** Attach touch listeners. */
    init() {
        this._target.addEventListener('touchstart', this._onStart, { passive: false });
        this._target.addEventListener('touchmove',  this._onMove,  { passive: false });
    }

    /** Remove touch listeners. */
    destroy() {
        this._target.removeEventListener('touchstart', this._onStart, false);
        this._target.removeEventListener('touchmove',  this._onMove,  false);
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    _touchStart(event) {
        if (event.changedTouches.length === 0) {
            return;
        }
        event.preventDefault();
        this._tracking = true;
        this._originX  = event.changedTouches[0].pageX;
    }

    _touchMove(event) {
        if (!this._tracking || event.changedTouches.length === 0) {
            return;
        }

        const delta = this._originX - event.changedTouches[0].pageX;

        if (delta > this._threshold) {
            this._tracking = false;
            document.dispatchEvent(new CustomEvent('slides:navigate', {
                detail: { action: 'next' }
            }));
        } else if (delta < -this._threshold) {
            this._tracking = false;
            document.dispatchEvent(new CustomEvent('slides:navigate', {
                detail: { action: 'prev' }
            }));
        }
    }
}
