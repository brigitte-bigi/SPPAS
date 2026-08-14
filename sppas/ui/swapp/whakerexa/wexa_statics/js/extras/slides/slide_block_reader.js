/**
 :filename: statics.js.slides.slide_block_reader.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Read a written slide and give its blocks, in order.

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

import { SlideBlock } from './slide_block.js';

/**
 * Read a written slide and give its blocks, in the order of the document.
 *
 * This class is the only one that knows what the smallest part is: a row for a
 * table, an item for a list, a child otherwise. Everywhere else, a block is a
 * block.
 *
 * Two things a slide holds are never blocks. Its title, because every slide
 * that is engendered carries it, and the notes written for it, because they
 * stay with the slide they were written for.
 */
export class SlideBlockReader {
    // CONSTANTS
    /**
     * What a slide holds that is never laid out.
     */
    static KEPT_APART = 'h1, h2, h3, h4, h5, h6, [role="note"]';

    /**
     * What is read row by row.
     */
    static READ_AS_ROWS = 'TABLE';

    /**
     * What is read item by item.
     */
    static READ_AS_ITEMS = ['UL', 'OL'];


    // PUBLIC METHODS
    /**
     * Get the blocks of a slide, in the order they are written.
     *
     * @param slide {HTMLElement} The slide written by the author.
     * @returns {SlideBlock[]} Empty when the slide holds nothing but its title.
     */
    blocks(slide) {
        const found = [];

        Array.from(slide.children).forEach(child => {
            this.#readChild(child).forEach(element => {
                found.push(new SlideBlock(element, found.length + 1));
            });
        });

        return found;
    }


    // PRIVATE METHODS
    /**
     * Get the elements a child of the slide is laid down as.
     *
     * A container that holds a table or a list is read through: what makes it
     * tall is inside it, and a bibliography written in a slide is exactly
     * that, a container holding a table. A container that holds neither stays
     * whole: what was written side by side is not taken apart.
     *
     * @param child {HTMLElement} A child of the slide.
     * @returns {HTMLElement[]} The child itself, or the parts it is made of.
     */
    #readChild(child) {
        if (child.matches(SlideBlockReader.KEPT_APART) === true) {
            return [];
        }

        if (child.tagName === SlideBlockReader.READ_AS_ROWS) {
            return this.#rowsOf(child);
        }

        if (SlideBlockReader.READ_AS_ITEMS.includes(child.tagName) === true) {
            return Array.from(child.children);
        }

        if (this.#holdsParts(child) === true) {
            const parts = [];

            Array.from(child.children).forEach(held => {
                this.#readChild(held).forEach(element => parts.push(element));
            });

            return parts;
        }

        return [child];
    }

    /**
     * Say whether a container holds a table or a list of its own.
     *
     * @param child {HTMLElement} A child of the slide.
     * @returns {boolean} True when it is worth reading through.
     */
    #holdsParts(child) {
        return Array.from(child.children).some(held => {
            return held.tagName === SlideBlockReader.READ_AS_ROWS
                || SlideBlockReader.READ_AS_ITEMS.includes(held.tagName) === true;
        });
    }

    /**
     * Get the rows of a table, its head left apart.
     *
     * The head is repeated on every slide the table is laid on, so it is not
     * one of the parts to distribute.
     *
     * @param table {HTMLTableElement} A table written in the slide.
     * @returns {HTMLElement[]} The rows of its body, in the order they are written.
     */
    #rowsOf(table) {
        const bodies = Array.from(table.tBodies);

        if (bodies.length === 0) {
            return Array.from(table.rows);
        }

        const rows = [];

        bodies.forEach(body => {
            Array.from(body.rows).forEach(row => rows.push(row));
        });

        return rows;
    }
}
