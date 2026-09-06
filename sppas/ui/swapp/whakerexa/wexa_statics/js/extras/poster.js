/**
 :filename: statics.js.extras.poster.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: The accessibility controls of a poster, and the key that shows them.

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

import { KeyboardController } from '../keyboard.js';
import { AccessibilityNav } from '../accessibility_nav.js';

/**
 * A poster is read on a wall, by someone standing in front of it.
 *
 * A poster is one page and stays one page: it has no slide to move to, no
 * mode to switch to, and nothing to navigate. What it owes whoever stands
 * in front of it is the means to read it -- another theme, the contrast
 * mode, the light or dark mode -- without those controls taking, at all
 * times, the room the poster was drawn to fill.
 *
 * So the controls are built once, kept out of sight, and shown by a key.
 * The bar itself is the one of the framework, AccessibilityNav: the poster
 * says which of the three buttons it wants, and nothing more.
 *
 * @example
 *     // All three buttons, shown and hidden by the "a" key
 *     const poster = new Poster();
 *     poster.init();
 *
 * @example
 *     // A poster whose theme is chosen by whoever wrote it
 *     const poster = new Poster({theme: false, contrast: true, color: true});
 *     poster.init();
 */
export class Poster {

    // CONSTANTS
    /**
     * The keys the poster answers.
     *
     * "a" is the key the slides answer for the same bar. A poster and a
     * presentation are read in the same room, by the same person, and what
     * shows the controls is the same gesture in both.
     */
    static SHORTCUT_KEYS = ['a', 'A'];

    /**
     * The class that keeps the bar out of sight, painted in poster.css.
     */
    static HIDDEN_CLASS = 'controls-hidden';


    // FIELDS
    #shown;
    #nav;
    #keyboard;


    // CONSTRUCTOR
    /**
     * Say which of the three buttons the poster carries.
     *
     * A button is carried unless it is asked not to be: a poster that says
     * nothing gets the three of them.
     *
     * @constructor
     * @param {Object} [shown] - Which buttons the bar carries.
     * @param {boolean} [shown.theme] - Whether the theme is changed.
     * @param {boolean} [shown.contrast] - Whether the contrast mode is entered.
     * @param {boolean} [shown.color] - Whether the light or dark mode is chosen.
     * @returns {Poster}
     */
    constructor(shown = {}) {
        this.#shown = {
            theme: shown.theme !== false,
            contrast: shown.contrast !== false,
            color: shown.color !== false
        };
        this.#nav = null;
        this.#keyboard = null;
    }


    // GETTERS
    /**
     * Give the bar of controls, once it is built.
     *
     * @returns {HTMLElement|null} The bar, or null before init() is called.
     */
    get nav() {
        return this.#nav;
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether the controls are in sight.
     *
     * @returns {boolean} Whether the bar is shown.
     */
    get visible() {
        if (this.#nav === null) {
            return false;
        }
        return this.#nav.classList.contains(Poster.HIDDEN_CLASS) === false;
    }


    // PUBLIC METHODS
    /**
     * Build the bar, put it at the top of the page, and answer the key.
     *
     * The bar is built out of sight: a poster is looked at before it is
     * operated. Nothing is built if the page already carries a bar under
     * this name, a page that wrote its own controls keeping them.
     *
     * @param {Object} [options] - How the bar is named.
     * @param {string} [options.id] - The name the page and the CSS call it by.
     * @param {string} [options.className] - The classes it carries.
     * @param {string} [options.label] - What a screen reader says of it.
     * @returns {Promise<HTMLElement|null>} The bar, or null if the page had one.
     */
    async init(options = {}) {
        const id = options.id || 'accessibility-controls';
        if (document.getElementById(id) !== null) {
            return null;
        }

        const bar = new AccessibilityNav(this.#shown);
        this.#nav = await bar.build({
            id: id,
            className: options.className || `nav-wexa ${Poster.HIDDEN_CLASS}`,
            label: options.label || 'Accessibility controls'
        });

        document.body.prepend(this.#nav);
        this.#answerKey();

        return this.#nav;
    }

    // -----------------------------------------------------------------------

    /**
     * Bring the controls in sight.
     *
     * @returns {void}
     */
    show() {
        if (this.#nav !== null) {
            this.#nav.classList.remove(Poster.HIDDEN_CLASS);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Put the controls back out of sight.
     *
     * @returns {void}
     */
    hide() {
        if (this.#nav !== null) {
            this.#nav.classList.add(Poster.HIDDEN_CLASS);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Show the controls if they are hidden, hide them if they are shown.
     *
     * @returns {void}
     */
    toggle() {
        if (this.visible === true) {
            this.hide();
            return;
        }
        this.show();
    }

    // -----------------------------------------------------------------------

    /**
     * Stop answering the key, and give it back to the browser.
     *
     * @returns {void}
     */
    destroy() {
        if (this.#keyboard !== null) {
            this.#keyboard.destroy();
            this.#keyboard = null;
        }
    }


    // PRIVATE METHODS
    /**
     * Declare the key that shows the controls.
     *
     * The keyboard of the framework is what listens: it stands back when the
     * focus is on something a key belongs to, and that guard is not written
     * again here.
     *
     * @returns {void}
     */
    #answerKey() {
        this.#keyboard = new KeyboardController();
        this.#keyboard.register({
            keys: Poster.SHORTCUT_KEYS,
            action: () => this.toggle(),
            label: 'Accessibility controls'
        });
        this.#keyboard.init();
    }
}
