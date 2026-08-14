/**
 :filename: wexa_statics/js/extras/book/bibsource.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to take the BibTeX data, wherever the document keeps them.

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

import { RequestManager } from '../../transport/request.js';
import { MissingBibtexData } from './biberrors.js';

/**
 * Take the BibTeX data, wherever the document keeps them.
 *
 * This class is the only one that knows where the data come from, and no other
 * one needs to. They are written in the page, which is what works everywhere,
 * or kept in a file next to it, which is what a long bibliography deserves.
 *
 * Nothing is ever asked of the internet: a document reads its own data, and
 * well kept data need nothing else.
 */
export class BibtexSource {
    // FIELDS
    #element;
    #address;


    // CONSTRUCTOR
    /**
     * Instantiate the reader of the BibTeX data.
     *
     * @param elementId {string} The id of the element the data are written in.
     * @param address {string} The address of the file holding them, when there is one.
     */
    constructor(elementId, address = '') {
        this.#element = document.getElementById(elementId);
        this.#address = address;
    }


    // GETTERS
    /**
     * Get the element the data are written in.
     *
     * @returns {HTMLElement} The element, or null when the page has none.
     */
    get element() {
        return this.#element;
    }

    /**
     * Get the address of the file holding the data.
     *
     * @returns {string} The address, or an empty string.
     */
    get address() {
        return this.#address;
    }


    // PUBLIC METHODS
    /**
     * Read the BibTeX data.
     *
     * The page comes first: data written where they are read cost nothing and
     * never fail. The file is only asked for when the page holds nothing.
     *
     * @returns {Promise<string>} The BibTeX data, which are never empty.
     * @throws {MissingBibtexData} When neither the page nor the file gives anything.
     */
    async read() {
        const written = this.#readFromPage();

        if (written.trim().length > 0) {
            return written;
        }

        const fetched = await this.#readFromAddress();

        if (fetched.trim().length > 0) {
            return fetched;
        }

        throw new MissingBibtexData('No BibTeX data, neither in the page nor at an address.');
    }


    // PRIVATE METHODS
    /**
     * Read the data written in the page.
     *
     * @returns {string} What the element holds, or an empty string when there is none.
     */
    #readFromPage() {
        if (this.#element === null) {
            return '';
        }

        return this.#element.textContent;
    }

    /**
     * Ask for the file holding the data.
     *
     * The address is the one a link would use, relative to the page. It is
     * turned into what the request manager expects, which is relative to the
     * server. An address that leads to another server is refused: a document
     * reads its own data.
     *
     * @returns {Promise<string>} The BibTeX data, or an empty string when the file cannot be read.
     */
    async #readFromAddress() {
        if (this.#address.length === 0) {
            return '';
        }

        const wanted = new URL(this.#address, window.location.href);

        if (wanted.origin !== window.location.origin) {
            console.error(`BibtexSource: "${this.#address}" is on another server, it is not read.`);
            return '';
        }

        const manager = new RequestManager();
        const answer = await manager.send_get_request(wanted.pathname.substring(1) + wanted.search);

        if (manager.status !== 200) {
            console.error(`BibtexSource: "${this.#address}" answered ${manager.status}.`);
            return '';
        }

        return answer;
    }
}
