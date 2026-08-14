/**
 :filename: wexa_statics/js/extras/book/bibcitedref.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to hold what a reference owes to the text that cites it.

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
 * What a reference owes to the text that cites it.
 *
 * A number and the places it is cited at are neither in the BibTeX data nor in
 * the bibliography: they come from the text, and only exist once the text has
 * been read. They travel together, in one object, so that the bibliography
 * never has to ask the citations anything: the two are independent, and a page
 * without any citation gets its bibliography all the same.
 */
export class CitedReference {
    // FIELDS
    #number;
    #places;


    // CONSTRUCTOR
    /**
     * Instantiate what a reference owes to the text.
     *
     * @param number {number} The number given the first time it was cited.
     * @param places {HTMLElement[]} Where it is cited, in the order of the text.
     */
    constructor(number, places) {
        this.#number = number;
        this.#places = [...places];
    }


    // GETTERS
    /**
     * Get the number given the first time the reference was cited.
     *
     * @returns {number}
     */
    get number() {
        return this.#number;
    }

    /**
     * Get the places of the text where the reference is cited.
     *
     * @returns {HTMLElement[]} A copy, in the order of the text.
     */
    get places() {
        return [...this.#places];
    }
}
