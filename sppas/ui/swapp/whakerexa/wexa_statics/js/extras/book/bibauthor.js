/**
 :filename: wexa_statics/js/extras/book/bibauthor.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to represent one signatory of a bibliographic reference.

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
 * One signatory of a bibliographic reference.
 *
 * An author only exists as part of a reference, and its place in the list of
 * signatories is what tells it apart from the others: two people may share
 * every part of their name.
 *
 * BibTeX splits a name into four parts. They are all kept apart rather than
 * assembled once, because the order they are written in depends on what the
 * name is used for: reading it, or sorting on it.
 *
 * An author never changes once it is built.
 */
export class Author {
    // FIELDS
    #place;
    #firstName;
    #particle;
    #lastName;
    #suffix;


    // CONSTRUCTOR
    /**
     * Instantiate an author.
     *
     * Any part of the name may be empty, and an author reduced to a last name
     * is the usual case for an institution. No part is ever null: the parser
     * gives an empty string for what BibTeX does not provide.
     *
     * @param place {number} The place in the list of signatories, starting at 1.
     * @param firstName {string} The given name.
     * @param particle {string} The particle, "van" or "de La" for instance.
     * @param lastName {string} The family name.
     * @param suffix {string} The suffix, "Jr" for instance.
     */
    constructor(place, firstName, particle, lastName, suffix) {
        this.#place = place;
        this.#firstName = firstName;
        this.#particle = particle;
        this.#lastName = lastName;
        this.#suffix = suffix;
    }


    // GETTERS
    /**
     * Get the place in the list of signatories.
     *
     * @returns {number}
     */
    get place() {
        return this.#place;
    }

    /**
     * Get the given name.
     *
     * @returns {string}
     */
    get firstName() {
        return this.#firstName;
    }

    /**
     * Get the particle.
     *
     * @returns {string}
     */
    get particle() {
        return this.#particle;
    }

    /**
     * Get the family name.
     *
     * @returns {string}
     */
    get lastName() {
        return this.#lastName;
    }

    /**
     * Get the suffix.
     *
     * @returns {string}
     */
    get suffix() {
        return this.#suffix;
    }


    // PUBLIC METHODS
    /**
     * Get the whole name, written the way it is signed.
     *
     * Parts that are empty leave no trace, so that a name never carries a
     * double space nor a leading one.
     *
     * @returns {string} The name to display, possibly empty.
     */
    text() {
        const parts = [this.#firstName, this.#particle, this.#lastName, this.#suffix];
        const written = parts.filter(part => part.length > 0);

        return written.join(' ');
    }

    /**
     * Get the value to sort on, family name first.
     *
     * Sorting on the displayed name would sort on given names, which is not
     * how a bibliography is read. An author without a family name falls back
     * on what it has, so that it still takes a place in the order.
     *
     * @returns {string} The value to sort on, possibly empty.
     */
    sortValue() {
        if (this.#lastName.length === 0) {
            return this.text();
        }

        const parts = [this.#firstName, this.#particle];
        const given = parts.filter(part => part.length > 0);

        if (given.length === 0) {
            return this.#lastName;
        }

        return this.#lastName + ', ' + given.join(' ');
    }
}
