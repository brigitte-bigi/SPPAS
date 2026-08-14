/**
 :filename: statics.js.slides.slide_block.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: The smallest part of a slide that can be laid down on its own.

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
 * A part of a slide that is laid down whole.
 *
 * A block is a row of a table, an item of a list, or a child of the slide. What
 * it is exactly is decided by SlideBlockReader, and nowhere else: here, a block
 * is an element, a place in the order the content is written, and a height.
 *
 * The height is the only thing a block learns after it is built: it is not
 * known until something measures it, in the slide that holds it.
 */
export class SlideBlock {
    // FIELDS
    #element;
    #place;
    #height;


    // CONSTRUCTOR
    /**
     * Instantiate a block of a slide.
     *
     * @param element {HTMLElement} The element of the document.
     * @param place {number} Its place in the order the content is written, 1 or more.
     */
    constructor(element, place) {
        this.#element = element;
        this.#place = place;
        this.#height = 0;
    }


    // GETTERS
    /**
     * Get the element of the document.
     *
     * @returns {HTMLElement}
     */
    get element() {
        return this.#element;
    }

    /**
     * Get the place of the block in the order the content is written.
     *
     * @returns {number} 1 or more.
     */
    get place() {
        return this.#place;
    }

    /**
     * Get the height of the block.
     *
     * @returns {number} 0 as long as nothing has measured it.
     */
    get height() {
        return this.#height;
    }


    // SETTERS
    /**
     * Set the height of the block, as it was measured in its slide.
     *
     * Written by SlideMeasure, and by nobody else: a height measured anywhere
     * else is worth nothing.
     *
     * @param value {number} The measured height, 0 or more.
     */
    set height(value) {
        this.#height = value;
    }


    // PUBLIC METHODS
    /**
     * Say whether the block fits in what is left of a slide.
     *
     * It compares two numbers, and knows neither slide nor document.
     *
     * @param room {number} The height left, 0 or more.
     * @returns {boolean} True when the block does not exceed that height.
     */
    fitsIn(room) {
        return this.#height <= room;
    }
}
