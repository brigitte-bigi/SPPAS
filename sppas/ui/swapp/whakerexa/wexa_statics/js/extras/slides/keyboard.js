import SlidesView from './slides_view.js';

/**
 :filename: statics.js.slides.keyboard.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Keyboard and button navigation controller for slides.

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
 * Keyboard events listener.
 *
 * This listener is *pure input* and must never interfere with the
 * browser’s native accessibility behaviors. It implements a strict rule:
 *
 *     > The browser must always receive Enter, Space, and all navigation
 *     > keys whenever the focused element is interactive.
 *
 * As a consequence, this listener:
 * - Only listens for a restricted list of “slide keys”.
 * - Never handles Enter or Space.
 * - Never handles arrow keys, PageUp/PageDown, or Home/End if the
 *   focus is inside an interactive element (input, button, select…).
 *
 * This approach is unusual in slide frameworks, but it is the correct
 * design for accessibility. Screen readers, keyboard-only users, and
 * browser native controls must always retain full priority.
 *
 */
export default class SlidesKeyboardController {

    /**
     * The definitive list of keys supported by the Slides UI.
     * No other keys must ever be handled by this controller.
     */
    static SLIDE_KEYS = new Set([
        'Escape',  // Switch to Presentation mode
        'o', 'O',  // Switch to Overview mode
        's', 'S',  // Switch to Presentation mode
        'f', 'F',  // Enable/Disable Fullscreen
        'n', 'N',  // Show/Hide controls
        'b', 'B',  // Show/Hide progress bar
        'l', 'L',  // Show/Hide logo
        'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',  // Browse slides
        'PageUp', 'PageDown',
        'Home', 'End'
    ]);

    // ----------------------------------------------------------------------
    // CONSTRUCTOR
    // ----------------------------------------------------------------------

    /**
     * @param {Object} slidesManager - Instance of SlidesManager.
     * @param {Object} [options]
     * @param {HTMLElement|null} [options.nextButton]
     * @param {HTMLElement|null} [options.prevButton]
     * @param {HTMLElement|null} [options.backButton]
     */
    constructor(slidesManager, options = {}) {
        if (typeof slidesManager !== 'object' || slidesManager === null) {
            throw new Error('SlidesKeyboardController: "slidesManager" must be an object.');
        }
        this._manager = slidesManager;

        this._boundKeyHandler = this._onKeyDown.bind(this);
    }

    // ----------------------------------------------------------------------
    // INITIALIZATION
    // ----------------------------------------------------------------------

    /**
     * Activate listeners.
     *
     * @returns {void}
     */
    init() {
        document.body.addEventListener('keydown', this._boundKeyHandler, false);
    }

    /**
     * Remove listeners (optional cleanup).
     *
     * @returns {void}
     */
    destroy() {
        document.body.removeEventListener('keydown', this._boundKeyHandler, false);
    }

    // ---------------------------------------------------------------------
    // PRIVATE — ACCESSIBILITY-FIRST KEYBOARD HANDLING
    // ---------------------------------------------------------------------

    /**
     * Master keyboard handler.
     * Accessibility rules:
     *  1. If the key is not a slide key → ignore.
     *  2. Enter and Space → ALWAYS ignored (browser must handle them).
     *  3. If the target is interactive → ignore all slide keys.
     *
     * @param {KeyboardEvent} event
     * @private
     */
    _onKeyDown(event) {
        const key = event.key;

        // --- RULE 1: Ignore all keys not part of the Slides UI ----------------
        if (!SlidesKeyboardController.SLIDE_KEYS.has(key)) {
            return;
        }

        // --- RULE 2: Never handle Enter or Space ------------------------------
        // Space is " " (U+0020)
        if (key === 'Enter' || key === ' ') {
            return;
        }

        // --- RULE 3: If focus is on an interactive element → browser priority -
        if (this._isInteractiveTarget(event.target)) {
            return;
        }

        // ----------------------------------------------------------------------
        // From here, we know safely:
        //  - The key is a slide key
        //  - It is not Enter/Space
        //  - The focused element is *not* interactive
        // ----------------------------------------------------------------------

        switch (key) {

            case 'Escape':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.DEFAULT_MODE);
                }
                return;

            case 'o': case 'O':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.MODES.OVERVIEW);
                }
                return;

            case 's': case 'S':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.MODES.PRESENTATION);
                }
                return;

            case 'f': case 'F':
                this._manager.toggleFullscreen?.();
                return;

            case 'n': case 'N':
                if (this._manager.visibilityManager !== null) {
                    this._manager.visibilityManager.toggle('controls');
                }
                return;

            case 'l': case 'L':
                if (this._manager.visibilityManager !== null) {
                    //this._manager.visibilityManager.toggle('logo');
                }
                return;

            case 'b': case 'B':
                if (this._manager.visibilityManager !== null) {
                    //this._manager.visibilityManager.toggle('progress');
                }
                return;

            // Navigation backward
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
                event.preventDefault();
                this._manager.prev();
                return;

            // Navigation forward
            case 'ArrowRight':
            case 'ArrowDown':
            case 'PageDown':
                event.preventDefault();
                this._manager.next();
                return;

            case 'Home':
                event.preventDefault();
                this._manager.goStart();
                return;

            case 'End':
                event.preventDefault();
                this._manager.goEnd();
                return;

            default:
                return;
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Detect whether event.target is an interactive element.
     *
     * This method is intentionally very liberal: anything that a browser
     * would treat as focusable or clickable must return true.
     *
     * @param {HTMLElement} target
     * @returns {boolean}
     * @private
     */
    _isInteractiveTarget(target) {
        if (!(target instanceof HTMLElement)) {
            return true;
        }

        const tag = target.tagName.toLowerCase();

        // Native interactive elements
        if (tag === 'input' ||
            tag === 'select' ||
            tag === 'textarea' ||
            tag === 'button' ||
            tag === 'summary') {
            return true;
        }

        // Links
        if (tag === 'a' && target.hasAttribute('href')) {
            return true;
        }

        // Media controls
        if ((tag === 'video' || tag === 'audio') && target.hasAttribute('controls')) {
            return true;
        }

        // Any element with tabindex >= 0 is interactive
        const tab = target.getAttribute('tabindex');
        if (tab !== null) {
            const n = parseInt(tab, 10);
            if (!Number.isNaN(n) && n >= 0) {
                return true;
            }
        }

        return false;
    }

    // ---------------------------------------------------------------------
    // Utils
    // ---------------------------------------------------------------------

    /**
     * @param {*} element
     * @private
     * @returns {HTMLElement|null}
     */
    _elementOrNull(element) {
        return element instanceof HTMLElement ? element : null;
    }
}

