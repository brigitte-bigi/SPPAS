/**
 :filename: statics.js.slides.slides_pagination.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Lay every written slide on as many slides as it takes.

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

import { SlideBlockReader } from './slide_block_reader.js';
import { SlideMeasure } from './slide_measure.js';
import { SlidePaginator } from './slide_paginator.js';
import { SlideComposer } from './slide_composer.js';
import { PaginationError } from './slide_errors.js';

/**
 * Lay every written slide on as many slides as it takes.
 *
 * This class is the one that knows in which order the work is done, and it is
 * the only one that catches an error. Whatever happens, run() never raises: a
 * presentation whose slide cannot be laid out is still a presentation.
 *
 * Nobody runs anything: the author writes one slide, and the work happens in
 * the browser of whoever opens the page. Nothing is kept, and the document the
 * author wrote is not modified.
 */
export class SlidesPagination {
    // CONSTANTS
    /**
     * What a slide written by the author is.
     */
    static SLIDES = 'section.slide';


    // FIELDS
    #reader;
    #measure;
    #paginator;
    #composer;


    // CONSTRUCTOR
    /**
     * Instantiate the layout of the slides of a document.
     */
    constructor() {
        this.#reader = new SlideBlockReader();
        this.#measure = new SlideMeasure();
        this.#paginator = new SlidePaginator();
        this.#composer = new SlideComposer();
    }


    // PUBLIC METHODS
    /**
     * Do the whole work, and never raise.
     *
     * The promise is what the assembly waits for: the slides are counted and
     * the overview is built once every slide is laid down, and counting before
     * would give wrong numbers.
     *
     * @returns {Promise<void>} Kept once everything is laid down, or once it cannot be.
     */
    async run() {
        try {
            const written = Array.from(document.querySelectorAll(SlidesPagination.SLIDES));

            written.forEach(slide => this.#layOut(slide));

        } catch (error) {
            if (error instanceof PaginationError) {
                console.error('SlidesPagination: ' + error.message);
                return;
            }

            throw error;
        }
    }


    // PRIVATE METHODS
    /**
     * Lay one written slide out.
     *
     * A slide holding nothing but its title is left alone: there is nothing to
     * measure, and nothing to lay out.
     *
     * @param slide {HTMLElement} A slide written by the author.
     * @returns {void}
     */
    #layOut(slide) {
        const blocks = this.#reader.blocks(slide);

        if (blocks.length === 0) {
            return;
        }

        this.#measure.measure(blocks, slide);
        const room = this.#measure.room(slide, blocks);

        const layout = this.#paginator.paginate(blocks, room);

        this.#report(layout.oversized(room));

        if (layout.count() === 1) {
            return;
        }

        // The blocks are laid down once, in the order they were written. What
        // was measured is what is shown, so what was decided holds: laying a
        // slide out a second time would cut again on a difference of a pixel,
        // and leave a slide holding one block.
        this.#composer.compose(slide, layout);
    }

    /**
     * Say in the console what could not be laid down.
     *
     * A block taller than a slide on its own stays whole, and overflows: the
     * program does not cut inside a block, and the author is the one who can.
     *
     * @param blocks {SlideBlock[]} The blocks that exceed a slide on their own.
     * @returns {void}
     */
    #report(blocks) {
        blocks.forEach(block => {
            console.warn('SlidesPagination: a block is taller than the slide, and overflows.',
                block.element);
        });
    }
}
