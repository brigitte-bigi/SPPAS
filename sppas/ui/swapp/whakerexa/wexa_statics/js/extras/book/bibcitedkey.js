/**
 :filename: wexa_statics/js/extras/book/bibcitedkey.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to represent one key written in a citation.

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
 * One key written in a citation.
 *
 * A cited key only exists as part of a citation, and its place in that
 * citation is what tells it apart from the others.
 *
 * The reference it names is looked for before the cited key is built, and
 * never put in afterwards. It may name nothing at all: a key that no entry
 * defines is kept as it was written, so that the citation can say that its
 * reference is missing rather than disappear.
 */
export class CitedKey {
    // FIELDS
    #place;
    #writtenKey;
    #reference;
    #targetPage;


    // CONSTRUCTOR
    /**
     * Instantiate a key written in a citation.
     *
     * @param place {number} The place in the citation, starting at 1.
     * @param writtenKey {string} The key, as it is written in the document.
     * @param reference {Reference} The reference bearing that key, or null.
     * @param targetPage {string} The page or the chapter aimed at, or an empty string.
     */
    constructor(place, writtenKey, reference, targetPage) {
        this.#place = place;
        this.#writtenKey = writtenKey;
        this.#reference = reference;
        this.#targetPage = targetPage;
    }


    // GETTERS
    /**
     * Get the place in the citation.
     *
     * @returns {number}
     */
    get place() {
        return this.#place;
    }

    /**
     * Get the key, as it is written in the document.
     *
     * @returns {string}
     */
    get writtenKey() {
        return this.#writtenKey;
    }

    /**
     * Get the reference bearing that key.
     *
     * @returns {Reference} Null when no entry defines it.
     */
    get reference() {
        return this.#reference;
    }

    /**
     * Get the page or the chapter aimed at.
     *
     * @returns {string} An empty string when the citation aims at the whole work.
     */
    get targetPage() {
        return this.#targetPage;
    }
}
