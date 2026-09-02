/**
 * :filename: statics.js.customize.icon_set.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: One set of icons: what it carries, and where its contents stand.
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

/** The two forms a content takes, read in the file it stands in. */
export const IconForm = {
    LINE: 'line',
    IMAGE: 'image'
};

/**
 * One set of icons.
 *
 * A set says what it carries, and never goes and looks: a name it does not
 * declare is a name it does not carry, whether a file stands behind it or not.
 * That is what lets a name fall back to another set with no request at all —
 * where nothing serves the document a request is never answered, and where
 * something does it would cost a round trip for every name a set leaves out.
 *
 * A set is not held to one format: an author brings the files he has, and one
 * set carries a line drawing beside an image. The form is read in the file and
 * nowhere else.
 *
 * The fields are set at construction and do not change afterwards.
 */
export class IconSet {

    /** @type {string} */
    #name;

    /** @type {string} */
    #base;

    /** @type {Map<string, string>} Icon name → the file that answers it. */
    #files = new Map();

    /**
     * Create a set.
     *
     * @param {string} name - How the set is named, and what a reader chooses.
     * @param {string} base - Where its contents stand, with its last separator.
     * @param {string[]} files - The files it carries. Each one answers to the
     *                           name it bears without its extension.
     */
    constructor(name, base, files) {
        this.#name = name;
        this.#base = base;

        const given = Array.isArray(files) === true ? files : [];
        for (const file of given) {
            this.#files.set(IconSet.nameOf(file), file);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Give the name a file answers to.
     *
     * @param {string} file - A file, with its extension.
     * @returns {string} What it bears before its last dot.
     */
    static nameOf(file) {
        const dot = file.lastIndexOf('.');
        return dot === -1 ? file : file.substring(0, dot);
    }

    // -----------------------------------------------------------------------

    /** @returns {string} The name the set was declared under. */
    get name() {
        return this.#name;
    }

    /** @returns {string} Where its contents stand. */
    get base() {
        return this.#base;
    }

    /** @returns {string[]} The names it carries, in the order they were given. */
    get names() {
        return Array.from(this.#files.keys());
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether the set carries a name.
     *
     * Answers from what was declared, and reads nothing.
     *
     * @param {string} name - The name asked for.
     * @returns {boolean} True when the set declared that name.
     */
    carries(name) {
        if (typeof name !== 'string' || name === '') {
            return false;
        }
        return this.#files.has(name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say where the content of a name stands.
     *
     * @param {string} name - A name the set carries.
     * @returns {string} The address, from the base of the set.
     */
    addressOf(name) {
        return this.#base + this.#files.get(name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say how the content of a name is painted.
     *
     * An SVG is written into the page and takes the color of what surrounds
     * it. Anything else is an image, and keeps the colors it was drawn with.
     *
     * @param {string} name - A name the set carries.
     * @returns {string} One of IconForm.
     */
    formOf(name) {
        const file = this.#files.get(name);
        if (file === undefined) {
            return IconForm.IMAGE;
        }
        return file.toLowerCase().endsWith('.svg') === true
            ? IconForm.LINE
            : IconForm.IMAGE;
    }
}
