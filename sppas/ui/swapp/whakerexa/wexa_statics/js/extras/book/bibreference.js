/**
 :filename: wexa_statics/js/extras/book/bibreference.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to represent one bibliographic reference.

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
 * One bibliographic reference, as one BibTeX entry describes it.
 *
 * A reference is known by its key, and keeps its type as it was written:
 * BibTeX is written by hand, and "@Article" and "@article" are the same type
 * seen twice. Whoever needs to compare types lowers their case.
 *
 * Nothing modifies a reference once it is built. What it gives out is either a
 * string or a copy, so that no one can change from the outside what the BibTeX
 * data says.
 */
export class Reference {
    // FIELDS
    #key;
    #type;
    #fields;
    #authors;
    #links;
    #source;


    // CONSTRUCTOR
    /**
     * Instantiate a reference.
     *
     * Field names are lowered once and for all, because BibTeX writes ABSTRACT
     * as willingly as abstract, and nothing downstream should have to know.
     *
     * @param key {string} The BibTeX key, which tells this reference apart.
     * @param type {string} The entry type, as written.
     * @param fields {Map} The fields, their LaTeX notations already converted.
     * @param authors {Author[]} The signatories, in the order they sign.
     * @param links {Link[]} The addresses where the publication can be reached.
     * @param source {string} The BibTeX entry, as written in the data.
     */
    constructor(key, type, fields, authors, links, source) {
        this.#key = key;
        this.#type = type;
        this.#fields = new Map();
        this.#authors = [...authors];
        this.#links = [...links];
        this.#source = source;

        fields.forEach((value, name) => {
            this.#fields.set(name.toLowerCase(), value);
        });
    }


    // GETTERS
    /**
     * Get the BibTeX key.
     *
     * @returns {string}
     */
    get key() {
        return this.#key;
    }

    /**
     * Get the entry type, as it was written.
     *
     * @returns {string}
     */
    get type() {
        return this.#type;
    }

    /**
     * Get the signatories, in the order they sign.
     *
     * @returns {Author[]} A copy, possibly empty.
     */
    get authors() {
        return [...this.#authors];
    }

    /**
     * Get the addresses where the publication can be reached.
     *
     * @returns {Link[]} A copy, possibly empty.
     */
    get links() {
        return [...this.#links];
    }

    /**
     * Get the BibTeX entry, as written in the data.
     *
     * It is kept word for word, because a reader may want to copy it into
     * their own bibliography.
     *
     * @returns {string}
     */
    get source() {
        return this.#source;
    }

    /**
     * Get the BibTeX entry without its abstract.
     *
     * The abstract is shown on its own, and a reader who asks for the BibTeX
     * source asks for what they would paste into their own bibliography: the
     * abstract there is a wall of text between them and the fields.
     *
     * @returns {string} The entry, its abstract field taken out.
     */
    get sourceWithoutAbstract() {
        return Reference.#withoutField(this.#source, 'abstract');
    }

    /**
     * Get the abstract.
     *
     * @returns {string} An empty string when the entry has none.
     */
    get abstract() {
        return this.field('abstract');
    }


    // PUBLIC METHODS
    /**
     * Get the value of a field.
     *
     * An absent field gives an empty string rather than nothing at all: what
     * displays a reference then has no existence to test, and a field that is
     * missing is shown as missing instead of being silently dropped.
     *
     * @param name {string} The name of the field, whatever its case.
     * @returns {string} The value, or an empty string.
     */
    field(name) {
        const wanted = name.toLowerCase();

        if (this.#fields.has(wanted) === false) {
            return '';
        }

        return this.#fields.get(wanted);
    }


    // PRIVATE STATIC METHODS
    /**
     * Take one field out of a BibTeX entry, leaving the rest as it was.
     *
     * The value is followed brace by brace, or quote by quote, because a
     * value holds anything: braces, commas, equal signs.
     *
     * @param source {string} The entry, as written in the data.
     * @param name {string} The name of the field to take out.
     * @returns {string} The entry without that field.
     */
    static #withoutField(source, name) {
        const start = source.search(new RegExp('[,{]\\s*' + name + '\\s*=', 'i'));

        if (start === -1) {
            return source;
        }

        // The comma or brace that opens the field is kept: it belongs to what
        // comes before, and taking it away would join two fields into one.
        let position = source.indexOf('=', start) + 1;
        while (position < source.length && /\s/.test(source[position]) === true) {
            position++;
        }

        const end = Reference.#endOfValue(source, position);
        const before = source.substring(0, start + 1);
        const after = source.substring(end);

        // A field written last leaves the comma of the one before it hanging
        // in front of the brace that closes the entry.
        if (after.trim().startsWith('}') === true && before.trimEnd().endsWith(',') === true) {
            return before.trimEnd().slice(0, -1) + after;
        }

        return before + after;
    }

    /**
     * Find where the value of a field ends.
     *
     * @param source {string} The entry, as written in the data.
     * @param start {number} Where the value begins.
     * @returns {number} Where it ends, its trailing comma included.
     */
    static #endOfValue(source, start) {
        const opening = source[start];
        let position = start;
        let depth = 0;

        while (position < source.length) {
            const character = source[position];

            if (character === '{') {
                depth++;
            } else if (character === '}') {
                depth--;
                if (depth === 0) {
                    position++;
                    break;
                }
            } else if (character === '"' && opening === '"' && position > start) {
                position++;
                break;
            }
            position++;
        }

        // The comma that follows goes too: the field before it already has one.
        while (position < source.length && /[\s,]/.test(source[position]) === true) {
            position++;
        }

        return position;
    }
}
