/**
 :filename: statics.js.slides.slide_layout.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Which blocks go on which slide.

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
 * The result of a distribution: the blocks of each slide, in order.
 *
 * It says nothing of the document. What is here is what SlidePaginator decided,
 * and what SlideComposer will lay down. A layout that asks for one slide asks
 * for nothing to be engendered: the slide the author wrote is enough.
 */
export class SlideLayout {
    // FIELDS
    #parts;


    // CONSTRUCTOR
    /**
     * Instantiate a distribution.
     *
     * A part is empty only when it is the only one: a slide holding nothing but
     * its title has nothing to lay out, and still takes one slide.
     *
     * @param parts {SlideBlock[][]} The blocks of each slide, in the order the content is written.
     */
    constructor(parts) {
        this.#parts = parts.map(part => [...part]);
    }


    // GETTERS
    /**
     * Get the blocks of each slide.
     *
     * @returns {SlideBlock[][]} A copy, in the order the content is written.
     */
    get parts() {
        return this.#parts.map(part => [...part]);
    }


    // PUBLIC METHODS
    /**
     * Get how many slides the distribution asks for.
     *
     * @returns {number} 1 or more. 1 means nothing is to be engendered.
     */
    count() {
        return this.#parts.length;
    }

    /**
     * Get the blocks that exceed a slide on their own.
     *
     * They are laid down whole all the same, and the console says so: the
     * program does not cut inside a block, and an overflow is seen.
     *
     * @param room {number} The height a slide leaves to its content.
     * @returns {SlideBlock[]} May be empty.
     */
    oversized(room) {
        const found = [];

        this.#parts.forEach(part => {
            part.forEach(block => {
                if (block.fitsIn(room) === false) {
                    found.push(block);
                }
            });
        });

        return found;
    }
}
