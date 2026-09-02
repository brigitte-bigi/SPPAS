/**
 * :filename: statics.js.customize.icon_demand.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: An element of the document that asks for a name.
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

/** What a demand asks for: a drawing at a place, a ground on a surface. */
export const DemandKind = {
    PLACE: 'place',
    SURFACE: 'surface'
};

/** What an element writes to ask for one or the other. */
const ATTRIBUTE = {
    place: 'data-icon',
    surface: 'data-ground'
};

/**
 * An element that asks for a name.
 *
 * The attribute is written on the element that already carries the meaning —
 * a button with its label, a link with its text — and never on an element
 * added for the icon: what the icon stands for is said by that element, and a
 * drawing put in an element of its own would name nothing.
 */
export class IconDemand {

    /** @type {HTMLElement} */
    #element;

    /** @type {string} */
    #name;

    /** @type {string} */
    #kind;

    /**
     * @param {HTMLElement} element - What asks.
     * @param {string} name - The name it asks for.
     * @param {string} kind - One of DemandKind.
     */
    constructor(element, name, kind) {
        this.#element = element;
        this.#name = name;
        this.#kind = kind;
    }

    // -----------------------------------------------------------------------

    /**
     * Give the demand an element carries, when it carries one.
     *
     * @param {HTMLElement} element - Any element of the document.
     * @returns {IconDemand} The demand, or null when it asks for nothing.
     */
    static of(element) {
        if (element === null || element === undefined) {
            return null;
        }

        for (const kind of Object.keys(ATTRIBUTE)) {
            const name = element.getAttribute(ATTRIBUTE[kind]);
            if (name !== null && name !== '') {
                return new IconDemand(element, name, kind);
            }
        }

        return null;
    }

    // -----------------------------------------------------------------------

    /**
     * Give the selector every demand of a document answers to.
     *
     * @returns {string}
     */
    static get SELECTOR() {
        return '[' + ATTRIBUTE.place + '], [' + ATTRIBUTE.surface + ']';
    }

    // -----------------------------------------------------------------------

    /** @returns {HTMLElement} The element itself: it is what is written into. */
    get element() {
        return this.#element;
    }

    /** @returns {string} The name it asks for. */
    get name() {
        return this.#name;
    }

    /** @returns {string} One of DemandKind. */
    get kind() {
        return this.#kind;
    }
}
