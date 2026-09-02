/**
 * :filename: statics.js.customize.icon_placer.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Puts a content where it was asked for. The only one that writes.
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

import { IconForm } from './icon_set.js';
import { DemandKind } from './icon_demand.js';

/** What marks what this class wrote, and what it may take away again. */
const MARK = 'data-icon-placed';

/**
 * Puts a content where it was asked for.
 *
 * It is the only class that changes the document shown, and the only one that
 * knows a line drawing from an image, and a drawing from a ground.
 *
 * A line drawing is written into the element, so that it takes the color of
 * what surrounds it in every mode and every theme. An image is put in an
 * <img> that carries the room the place declared, so that nothing waits for
 * the file to know how much space it will take. A ground covers the surface
 * and is written nowhere: it stands for nothing.
 *
 * Nothing around a demand moves when a content arrives: the room was declared
 * before it was asked for.
 */
export class IconPlacer {

    /**
     * Put a content where the demand asks for it.
     *
     * @param {IconDemand} demand - What asks.
     * @param {IconContent} content - What answers.
     * @returns {void}
     */
    place(demand, content) {
        if (demand === null || content === null) {
            return;
        }

        this.clear(demand);

        if (demand.kind === DemandKind.SURFACE) {
            this.#cover(demand, content);
            return;
        }

        if (content.form === IconForm.LINE) {
            this.#writeIn(demand, content);
        } else {
            this.#putImageIn(demand, content);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Take away what was put, and leave the room where it was.
     *
     * @param {IconDemand} demand - What asks.
     * @returns {void}
     */
    clear(demand) {
        if (demand === null) {
            return;
        }

        const element = demand.element;
        if (demand.kind === DemandKind.SURFACE) {
            element.style.removeProperty('background-image');
            element.style.removeProperty('background-repeat');
            element.style.removeProperty('background-position');
            return;
        }

        const placed = element.querySelector('[' + MARK + ']');
        if (placed !== null) {
            placed.remove();
        }
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Write a line drawing into the element.
     *
     * @private
     * @param {IconDemand} demand
     * @param {IconContent} content
     * @returns {void}
     */
    #writeIn(demand, content) {
        const holder = document.createElement('span');
        holder.setAttribute(MARK, content.name);
        holder.setAttribute('aria-hidden', 'true');
        holder.innerHTML = content.source;

        const drawing = holder.querySelector('svg');
        if (drawing !== null) {
            drawing.setAttribute(MARK, content.name);
            drawing.setAttribute('aria-hidden', 'true');
            demand.element.insertAdjacentElement('afterbegin', drawing);
            return;
        }

        demand.element.insertAdjacentElement('afterbegin', holder);
    }

    // -----------------------------------------------------------------------

    /**
     * Put an image in the element, carrying the room the place declared.
     *
     * @private
     * @param {IconDemand} demand
     * @param {IconContent} content
     * @returns {void}
     */
    #putImageIn(demand, content) {
        const image = document.createElement('img');
        image.setAttribute(MARK, content.name);
        image.setAttribute('src', content.source);
        image.setAttribute('alt', '');
        image.setAttribute('loading', 'lazy');
        image.setAttribute('decoding', 'async');

        const room = this.#roomOf(demand.element);
        image.setAttribute('width', room.width);
        image.setAttribute('height', room.height);

        demand.element.insertAdjacentElement('afterbegin', image);
    }

    // -----------------------------------------------------------------------

    /**
     * Cover a surface with a ground.
     *
     * @private
     * @param {IconDemand} demand
     * @param {IconContent} content
     * @returns {void}
     */
    #cover(demand, content) {
        const element = demand.element;
        element.style.backgroundImage = 'url("' + content.source + '")';
        // A ground covers: it is laid from the corner and repeated. The
        // framework asks for no repetition on every element, which would leave
        // one drawing at the top of the surface.
        element.style.backgroundRepeat = 'repeat';
        element.style.backgroundPosition = '0 0';
    }

    // -----------------------------------------------------------------------

    /**
     * Give the room a place declared, in pixels.
     *
     * The two dimensions are declared by the place and not by the drawing:
     * were they to follow the drawing, changing the set in force would move
     * what surrounds it.
     *
     * @private
     * @param {HTMLElement} element
     * @returns {Object} Its width and its height, as whole numbers.
     */
    #roomOf(element) {
        const style = window.getComputedStyle(element);
        const width = parseInt(style.getPropertyValue('--icon-width'), 10);
        const height = parseInt(style.getPropertyValue('--icon-height'), 10);
        const size = parseInt(style.fontSize, 10) || 16;

        return {
            width: String(Number.isNaN(width) === true ? size : width),
            height: String(Number.isNaN(height) === true ? size : height)
        };
    }
}
