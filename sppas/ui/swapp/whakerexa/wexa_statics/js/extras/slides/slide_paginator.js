/**
 :filename: statics.js.slides.slide_paginator.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Lay blocks out on as many slides as it takes.

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

import { SlideLayout } from './slide_layout.js';

/**
 * Lay blocks out on as many slides as it takes.
 *
 * This class knows neither the document nor the browser: it receives heights
 * and gives a distribution back. That is what makes it the one that can be
 * tested without opening anything, and it is where the rule of the whole work
 * is written: the cut is made between blocks, never inside one.
 *
 * A block that exceeds a slide on its own is laid down whole, alone on its
 * slide, and overflows. Cutting inside it would decide in the author's place.
 */
export class SlidePaginator {

    // PUBLIC METHODS
    /**
     * Lay the blocks out, in the order the content is written.
     *
     * A slide is filled as long as the next block fits. As soon as it does not,
     * the block opens the next slide. Nothing is dropped, and nothing is placed
     * twice.
     *
     * @param blocks {SlideBlock[]} The blocks, each carrying its height, in the order they are written.
     * @param room {number} The height a slide leaves to its content, more than 0.
     * @returns {SlideLayout} One part per slide. A single empty part when there is no block.
     */
    paginate(blocks, room) {
        if (blocks.length === 0) {
            return new SlideLayout([[]]);
        }

        const parts = [];
        let current = [];
        let left = room;

        blocks.forEach(block => {
            const opensASlide = (current.length > 0 && block.fitsIn(left) === false);

            if (opensASlide === true) {
                parts.push(current);
                current = [];
                left = room;
            }

            current.push(block);
            left = left - block.height;
        });

        parts.push(current);

        return new SlideLayout(parts);
    }
}
