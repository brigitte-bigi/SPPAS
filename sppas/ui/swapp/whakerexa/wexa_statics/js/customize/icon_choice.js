/**
 * :filename: statics.js.customize.icon_choice.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: The set of icons a document is shown with.
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

/**
 * Which set of icons a document is shown with.
 *
 * There is one at a time, for the whole document. It is read in the address
 * first, so that a choice holds from one page to the next, then in what the
 * page names, and it falls back on the reference set when neither names one
 * that was declared.
 *
 * This class decides nothing about the drawings: it holds a name, and says
 * when that name changes.
 */
export class IconChoice {

    /** @returns {string} The parameter the choice travels in. */
    static get PARAMETER_NAME() {
        return 'wexa_icons';
    }

    /** @type {IconSets} */
    #sets;

    /** @type {string} */
    #inForce;

    /**
     * Hold the set in force.
     *
     * @param {IconSets} sets - The sets that were declared.
     * @param {string} [named] - The set the page names, if any.
     * @param {string} [search] - The query of the address. Read from the
     *                            document when it is not given.
     */
    constructor(sets, named = '', search = null) {
        this.#sets = sets;
        this.#inForce = this.#firstDeclared([
            this.#inAddress(search),
            named
        ]);
    }

    // -----------------------------------------------------------------------

    /** @returns {string} The name of the set the document is shown with. */
    inForce() {
        return this.#inForce;
    }

    // -----------------------------------------------------------------------

    /**
     * Show the document with another set.
     *
     * A set that was never declared changes nothing.
     *
     * @param {string} name - The name of the set to put in force.
     * @returns {boolean} True when the set in force changed.
     */
    put(name) {
        if (this.#isDeclared(name) === false) {
            return false;
        }
        if (name === this.#inForce) {
            return false;
        }

        this.#inForce = name;
        this.#sayInAddress(name);
        return true;
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Say whether a name is one of the sets that were declared.
     *
     * @private
     * @param {string} name
     * @returns {boolean}
     */
    #isDeclared(name) {
        if (typeof name !== 'string' || name === '') {
            return false;
        }
        return this.#sets.names().includes(name);
    }

    // -----------------------------------------------------------------------

    /**
     * Give the first of the given names that was declared.
     *
     * The reference set answers when none of them was.
     *
     * @private
     * @param {string[]} names
     * @returns {string}
     */
    #firstDeclared(names) {
        for (const name of names) {
            if (this.#isDeclared(name) === true) {
                return name;
            }
        }

        const declared = this.#sets.names();
        return declared.length === 0 ? '' : declared[declared.length - 1];
    }

    // -----------------------------------------------------------------------

    /**
     * Read the set named in the address.
     *
     * @private
     * @param {string} search - The query, or null to read the document.
     * @returns {string} The name, or an empty string.
     */
    #inAddress(search) {
        const query = search !== null ? search : window.location.search;
        const asked = new URLSearchParams(query.substring(query.indexOf('?') + 1));
        return asked.get(IconChoice.PARAMETER_NAME) || '';
    }

    // -----------------------------------------------------------------------

    /**
     * Write the set in force in the address, without loading the page again.
     *
     * @private
     * @param {string} name
     * @returns {void}
     */
    #sayInAddress(name) {
        if (typeof window === 'undefined' || window.history === undefined) {
            return;
        }

        const address = new URL(window.location.href);
        address.searchParams.set(IconChoice.PARAMETER_NAME, name);
        window.history.replaceState(null, '', address.href);
    }
}
