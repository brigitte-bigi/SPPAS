/**
 :filename: statics.js.slides.slide_measure.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Measure a slide, and what it holds.

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

import { MissingSlide, UnmeasurableSlide } from './slide_errors.js';

/**
 * Measure a slide, and the blocks it holds.
 *
 * This is the only class that reads the rendering, and it decides nothing. A
 * height is measured in the slide itself, at its width and its font sizes: the
 * font sizes of a slide are not those of a page, and a height measured
 * elsewhere is worth nothing.
 */
export class SlideMeasure {
    // CONSTANTS
    /**
     * What a slide holds that its content does not have to make room for.
     */
    static TITLE = 'h1, h2, h3, h4, h5, h6';

    /**
     * What tells a slide from any other element.
     */
    static SLIDE = 'section.slide';


    // PUBLIC METHODS
    /**
     * Get the height a slide leaves to its blocks.
     *
     * What surrounds the blocks is deducted, because it is on every slide the
     * content is laid on: the title, the head of a table, the margins and the
     * paddings of what holds them, and the line where the page counter is
     * written. It is measured, not listed: whatever a slide holds that is not
     * a block takes the room it takes.
     *
     * @param slide {HTMLElement} A slide of the document.
     * @param blocks {SlideBlock[]} Its blocks, already measured.
     * @returns {number} The height left to the blocks.
     * @throws {MissingSlide} The element is not a slide.
     * @throws {UnmeasurableSlide} The slide is not rendered.
     */
    room(slide, blocks) {
        if (slide === null || slide === undefined || typeof slide.matches !== 'function') {
            throw new MissingSlide('The element to measure is not an element of the document.');
        }

        if (slide.matches(SlideMeasure.SLIDE) === false) {
            throw new MissingSlide('The element to measure is not a slide.');
        }

        const box = slide.getBoundingClientRect();

        if (box.height === 0) {
            throw new UnmeasurableSlide('The slide has no height: it is not rendered.');
        }

        const style = window.getComputedStyle(slide);
        const inside = box.height
            - parseFloat(style.paddingTop)
            - parseFloat(style.paddingBottom)
            - parseFloat(style.borderTopWidth)
            - parseFloat(style.borderBottomWidth);

        return inside - this.#counterHeight(slide) - this.#aroundHeight(slide, blocks);
    }

    /**
     * Give each block the height it takes in its slide.
     *
     * @param blocks {SlideBlock[]} The blocks of that slide.
     * @param slide {HTMLElement} The slide they are written in.
     * @returns {void}
     */
    measure(blocks, slide) {
        blocks.forEach(block => {
            block.height = this.#heightOf(block.element);
        });
    }


    // PRIVATE METHODS
    /**
     * Get the height of everything a slide holds that is not a block.
     *
     * What a slide holds is measured, and the blocks are taken out of it: what
     * is left is the title, the head of a table, and the margins and paddings
     * of what holds the blocks. All of it is written again on every slide the
     * content is laid on, so none of it is room for a block.
     *
     * @param slide {HTMLElement} A slide of the document.
     * @param blocks {SlideBlock[]} Its blocks, already measured.
     * @returns {number} 0 or more.
     */
    #aroundHeight(slide, blocks) {
        let held = 0;

        Array.from(slide.children).forEach(child => {
            held = held + this.#heightOf(child);
        });

        let laid = 0;

        blocks.forEach(block => {
            laid = laid + block.height;
        });

        return Math.max(0, held - laid);
    }

    /**
     * Get the height of the line where the page counter is written.
     *
     * It stands at the bottom of every slide, and a block written under it is
     * a block nobody reads.
     *
     * @param slide {HTMLElement} A slide of the document.
     * @returns {number} 0 when nothing is written there.
     */
    #counterHeight(slide) {
        const counter = window.getComputedStyle(slide, ':before');
        const height = parseFloat(counter.height);

        if (isNaN(height) === true) {
            return 0;
        }

        return height;
    }

    /**
     * Get the height an element takes, its margins included.
     *
     * Margins are counted: two blocks laid one after the other are as far apart
     * as their margins say, and a height that leaves them out fills a slide
     * with more than it holds.
     *
     * @param element {HTMLElement} An element of the document.
     * @returns {number} Its height, 0 or more.
     */
    #heightOf(element) {
        const box = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);

        return box.height + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
    }
}
