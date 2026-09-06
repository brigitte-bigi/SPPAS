/**
 * :filename: statics.js.accessibility_nav.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: The bar that switches the theme, the contrast and the color mode.
 *
 *  -------------------------------------------------------------------------
 *
 *  This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa
 *
 *  Copyright (C) 2023-2026 Brigitte Bigi, CNRS
 *  Laboratoire Parole et Langage, Aix-en-Provence, France
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *  This banner notice must not be removed.
 *
 *  -------------------------------------------------------------------------
 */

'use strict';

import { icons } from './customize/icons.js';

/**
 * What each button is called when the document says nothing.
 *
 * A document that knows better says so: the wording is proposed here, and
 * never imposed on the page that shows the bar.
 *
 * @type {Object}
 */
export const NAV_WORDING = {
    theme: { label: 'Switch theme', title: 'Switch theme' },
    contrast: { label: 'Switch contrast', title: 'Switch contrast' },
    color: { label: 'Switch light and dark', title: 'Switch light and dark' }
};

/**
 * The bar a document shows to whoever reads it, and what it switches.
 *
 * It holds three buttons and nothing else: the theme, the contrast and the
 * color mode. A document says which of the three it offers — a document with
 * one theme has nothing to switch, and says so — and the bar is built with
 * those alone.
 *
 * It belongs here and not to a presentation: what it commands is the
 * accessibility of a document, whatever the shape that document takes. A
 * presentation asks for it, a poster asks for it, a page asks for it.
 *
 * @example
 * const nav = new AccessibilityNav({ theme: true, contrast: true, color: true });
 * document.body.appendChild(await nav.build());
 */
export class AccessibilityNav {

    /** @type {Object} */
    #shown;

    /**
     * @param {Object} [shown] - Which buttons the bar holds. Each one is on
     *                           unless it is said to be off.
     * @param {boolean} [shown.theme] - The button that cycles the themes.
     * @param {boolean} [shown.contrast] - The one that switches the contrast.
     * @param {boolean} [shown.color] - The one that switches light and dark.
     */
    constructor(shown = {}) {
        this.#shown = {
            theme: shown.theme !== false,
            contrast: shown.contrast !== false,
            color: shown.color !== false
        };
    }

    // -----------------------------------------------------------------------

    /**
     * Build the bar.
     *
     * @param {Object} [options] - How the bar is written in the document.
     * @param {string} [options.id] - The identifier it carries.
     * @param {string} [options.className] - The classes it carries.
     * @param {string} [options.label] - What it is called for a screen reader.
     * @param {Object} [options.wording] - What each button is called: an entry
     *                 'theme', 'contrast' or 'color', each one taking a label
     *                 and a title. What is left out keeps NAV_WORDING.
     * @returns {Promise<HTMLElement>} The nav, to be added where it belongs.
     */
    async build(options = {}) {
        const nav = document.createElement('nav');
        nav.id = options.id !== undefined ? options.id : 'accessibility-controls';
        nav.className = options.className !== undefined
            ? options.className
            : 'nav-wexa';
        nav.setAttribute('aria-label', options.label !== undefined
            ? options.label
            : 'Accessibility controls');

        if (this.#shown.theme === true) {
            const wording = this.#wordingOf(options, 'theme');
            nav.appendChild(await this.#button(
                'btn-css-theme', 'menuitem', 'theme', wording.label,
                () => {
                    if (window.themes !== null && window.themes !== undefined) {
                        window.themes.next();
                    }
                },
                { title: wording.title }));
        }

        if (this.#shown.contrast === true) {
            const wording = this.#wordingOf(options, 'contrast');
            nav.appendChild(await this.#button(
                'btn-contrast', 'menuitem accessibility', 'contrast', wording.label,
                () => this.#accessibility('switchContrastScheme'),
                { ariaPressed: 'false', title: wording.title }));
        }

        if (this.#shown.color === true) {
            const wording = this.#wordingOf(options, 'color');
            nav.appendChild(await this.#button(
                'btn-color', 'menuitem accessibility', 'color', wording.label,
                () => this.#accessibility('switchColorScheme'),
                { ariaPressed: 'false', title: wording.title }));
        }

        return nav;
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Say how one button is called.
     *
     * What the document gives is taken, what it leaves out keeps the wording
     * the bar proposes: a page names the buttons in its own language without
     * having to name all three.
     *
     * @private
     * @param {Object} options - What build() was given.
     * @param {string} which - 'theme', 'contrast' or 'color'.
     * @returns {Object} The label and the title to write.
     */
    #wordingOf(options, which) {
        const proposed = NAV_WORDING[which];
        const said = options.wording !== undefined ? options.wording[which] : undefined;

        if (said === undefined || said === null) {
            return { label: proposed.label, title: proposed.title };
        }

        const label = said.label !== undefined ? said.label : proposed.label;
        const title = said.title !== undefined ? said.title : proposed.title;
        return { label: label, title: title };
    }

    // -----------------------------------------------------------------------

    /**
     * Build one button of the bar.
     *
     * @private
     * @param {string} id - What it is named.
     * @param {string} className - What it wears.
     * @param {string} iconName - The icon it shows.
     * @param {string} ariaLabel - What it stands for.
     * @param {Function} onClick - What it does.
     * @param {Object} [extras] - ariaPressed, title.
     * @returns {Promise<HTMLButtonElement>}
     */
    async #button(id, className, iconName, ariaLabel, onClick, extras = {}) {
        const button = document.createElement('button');
        button.type = 'button';
        button.id = id;
        button.className = className;
        button.setAttribute('aria-label', ariaLabel);

        if (extras.ariaPressed !== undefined) {
            button.setAttribute('aria-pressed', extras.ariaPressed);
        }
        if (extras.title !== undefined) {
            button.title = extras.title;
        }

        button.innerHTML = await icons.get(iconName);
        button.addEventListener('click', onClick);
        return button;
    }

    // -----------------------------------------------------------------------

    /**
     * Ask the accessibility manager for one of its two switches.
     *
     * @private
     * @param {string} what - The name of the switch.
     * @returns {void}
     */
    #accessibility(what) {
        const manager = window.Wexa !== undefined && window.Wexa !== null
            ? window.Wexa.accessibility
            : null;

        if (manager !== null && manager !== undefined) {
            manager[what]();
        }
    }
}
