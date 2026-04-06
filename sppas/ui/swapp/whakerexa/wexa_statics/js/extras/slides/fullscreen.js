/**
 :filename: statics.js.slides.fullscreen.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Fullscreen controller for slide presentation.

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
 * This controller encapsulates browser fullscreen requests so that the
 * presentation layer can toggle fullscreen without dealing with vendor
 * prefixes or browser differences.
 */
export default class SlidesFullscreenController {
    /**
     * @param {HTMLElement|null} [target=document.documentElement] - Target element for fullscreen.
     */
    constructor(target = null) {
        const defaultTarget = typeof document !== 'undefined'
            ? document.documentElement
            : null;

        this._target = target instanceof HTMLElement ? target : defaultTarget;
    }

    /**
     * Request fullscreen on the target element.
     *
     * @returns {void}
     */
    enter() {
        if (this._target === null) {
            return;
        }

        const request = this._target.requestFullscreen
            || this._target.requestFullScreen
            || this._target.mozRequestFullScreen
            || this._target.webkitRequestFullScreen
            || null;

        if (typeof request === 'function') {
            request.call(this._target);
        }
    }

    /**
     * Exit fullscreen if active.
     *
     * @returns {void}
     */
    exit() {
        if (typeof document === 'undefined') {
            return;
        }

        const exitMethod = document.exitFullscreen
            || document.cancelFullScreen
            || document.mozCancelFullScreen
            || document.webkitCancelFullScreen
            || null;

        if (typeof exitMethod === 'function') {
            exitMethod.call(document);
        }
    }

    /**
     * Toggle fullscreen mode depending on current state.
     *
     * @returns {void}
     */
    toggle() {
        if (typeof document === 'undefined') {
            return;
        }

        const activeElement = document.fullscreenElement
            || document.mozFullScreenElement
            || document.webkitFullscreenElement
            || null;

        if (activeElement === null) {
            this.enter();
        } else {
            this.exit();
        }
    }
}
