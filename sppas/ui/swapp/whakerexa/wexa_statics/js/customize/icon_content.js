/**
 * :filename: statics.js.customize.icon_content.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: What answers a name: a line drawing, or an image.
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
 * What answers a name, once it is known.
 *
 * A line drawing carries its markup, which is written into the page and takes
 * the color of what surrounds it. An image carries its address, and nothing of
 * it is read: it is the page that goes and gets it, once, where it is shown.
 *
 * The fields are set at construction and do not change afterwards.
 */
export class IconContent {

    /** @type {string} */
    #name;

    /** @type {string} */
    #form;

    /** @type {string} */
    #source;

    /**
     * @param {string} name - The name it answers to.
     * @param {string} form - One of IconForm: a line, or an image.
     * @param {string} source - The markup of a line, the address of an image.
     */
    constructor(name, form, source) {
        this.#name = name;
        this.#form = form;
        this.#source = source;
    }

    /** @returns {string} The name it answers to. */
    get name() {
        return this.#name;
    }

    /** @returns {string} How it is painted: a line, or an image. */
    get form() {
        return this.#form;
    }

    /** @returns {string} The markup of a line, or the address of an image. */
    get source() {
        return this.#source;
    }
}
