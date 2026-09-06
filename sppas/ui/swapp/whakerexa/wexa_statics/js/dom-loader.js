/**
 * :filename: statics.js.dom-loader.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: What a page runs once it is there.
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
 * What waits for the page, and is run when the page is there.
 *
 * A module says what it has to do once the document is loaded, and says it to
 * this one alone: the listener is registered on the first demand and not by
 * every module, so nothing depends on the order the scripts were written in.
 *
 * A demand made after the load has already happened is answered on the spot.
 * A module loaded on a promise is built after that event, and a listener added
 * then would wait for something that will not come again.
 *
 * Everything is static: a document is loaded once, and there is nothing here
 * a page would want two of.
 *
 * @example
 * OnLoadManager.addLoadFunction(() => console.log('The page is there.'));
 */
export class OnLoadManager {

    /** @type {Function[]} What waits for the load. */
    static #functions = [];

    /** @type {boolean} Whether the listener has been registered. */
    static #listening = false;

    // -----------------------------------------------------------------------

    /**
     * Hold a function until the page is loaded.
     *
     * @param {Function} func - What to run then.
     * @returns {void}
     */
    static addLoadFunction(func) {
        if (typeof func !== 'function') {
            return;
        }

        if (document.readyState === 'complete') {
            func();
            return;
        }

        OnLoadManager.#functions.push(func);
        OnLoadManager.#listen();
    }

    // -----------------------------------------------------------------------

    /**
     * Run what was held, in the order it was given.
     *
     * @returns {void}
     */
    static runLoadFunctions() {
        for (const func of OnLoadManager.#functions) {
            func();
        }
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Register the listener, once for all the modules that ask.
     *
     * @private
     * @returns {void}
     */
    static #listen() {
        if (OnLoadManager.#listening === true) {
            return;
        }

        OnLoadManager.#listening = true;
        window.addEventListener('load', OnLoadManager.runLoadFunctions);
    }
}
