/**
 :filename: statics.js.slides.visibility.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Generic controller to toggle visibility of a single DOM element.

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
 * This controller contains no business logic. It only shows, hides,
 * or toggles a specific HTMLElement, without modifying styles unrelated
 * to display management.
 *
 * Usage:
 *   const vc = new VisibilityController(element);
 *   vc.show();
 *   vc.hide();
 *   vc.toggle();
 */
export default class SlidesVisibilityController {

    /**
     * @param {HTMLElement|null} element - Target element to control.
     */
    constructor(element) {
        this._element = element instanceof HTMLElement ? element : null;
    }

    /**
     * Show the element.
     * @returns {void}
     */
    isVisible() {
        if (!(this._element instanceof HTMLElement)) {
            return false;
        }
        return window.getComputedStyle(this._element).display !== 'none';
    }

    show() {
        if (this._element instanceof HTMLElement) {
            this._element.classList.remove('controls-hidden');
            this._element.style.display = '';
        }
    }

    /**
     * Hide the element.
     * @returns {void}
     */
    hide() {
        if (this._element instanceof HTMLElement) {
            this._element.style.display = 'none';
        }
    }

    /**
     * Toggle visibility.
     * @returns {void}
     */
    toggle() {
        if (!(this._element instanceof HTMLElement)) {
            return;
        }

        // Use getComputedStyle to handle elements visible via CSS rules (not inline style).
        const computed = window.getComputedStyle(this._element).display;
        if (computed === 'none') {
            this.show();
        } else {
            this.hide();
        }
    }
}
