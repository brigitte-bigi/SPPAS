/**
 :filename: wexa_statics/js/extras/book/labels.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to write what a program says in the language of the document.

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
 * Write what a program says in the language of the document.
 *
 * Everything a bibliography writes by itself follows the language of the
 * document: the headers of a table, what is said after a search, the name a
 * screen reader reads. The language is read on the element, and is never
 * written in the code.
 *
 * A language nobody wrote labels for falls back on English, and what is
 * written then says which language it is in, as WCAG 3.1.2 asks.
 */
export class Labels {
    // CONSTANTS
    /**
     * The language written when the one of the document is unknown.
     */
    static FALLBACK = 'en';


    // FIELDS
    #labels;


    // CONSTRUCTOR
    /**
     * Instantiate the labels of one part of the bibliography.
     *
     * @param labels {Map} What to write, by language, then by name.
     */
    constructor(labels) {
        this.#labels = labels;
    }


    // GETTERS
    /**
     * Get the language the labels are written in.
     *
     * @returns {string} The language of the document, or the fallback one.
     */
    get language() {
        const declared = document.documentElement.getAttribute('lang');

        if (declared === null) {
            return Labels.FALLBACK;
        }

        const spoken = declared.split('-')[0].toLowerCase();

        if (this.#labels.has(spoken) === false) {
            return Labels.FALLBACK;
        }

        return spoken;
    }

    /**
     * Tell whether the document is written in a language the labels know.
     *
     * @returns {boolean}
     */
    get isKnown() {
        const declared = document.documentElement.getAttribute('lang');

        if (declared === null) {
            return false;
        }

        return this.#labels.has(declared.split('-')[0].toLowerCase());
    }


    // PUBLIC METHODS
    /**
     * Get one label.
     *
     * @param name {string} The name of the label.
     * @returns {string} What to write.
     */
    text(name) {
        return this.#labels.get(this.language)[name];
    }

    /**
     * Write one label in an element.
     *
     * When the document speaks a language the labels do not know, the element
     * says which language it is written in: a screen reader then reads it with
     * the right voice instead of stumbling through it.
     *
     * @param element {HTMLElement} What receives the label.
     * @param name {string} The name of the label.
     * @returns {void}
     */
    write(element, name) {
        element.textContent = this.text(name);
        this.declare(element);
    }

    /**
     * Say in which language an element is written, when it cannot follow the
     * language of the document.
     *
     * @param element {HTMLElement} What was just written.
     * @returns {void}
     */
    declare(element) {
        if (this.isKnown === false) {
            element.setAttribute('lang', Labels.FALLBACK);
        }
    }
}
