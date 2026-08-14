/**
 :filename: wexa_statics/js/extras/book/bibcitation.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to represent one place of a text where references are cited.

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

import { Labels } from './labels.js';

/**
 * One place of a text where references are cited.
 *
 * A citation is written between two words of a sentence, and shows nothing but
 * its number. What the document holds inside it is what a reader gets when
 * JavaScript does not run; as soon as it does, the number takes its place.
 *
 * The brackets are seen and never spoken: a screen reader says "Reference"
 * and the number, which is what a reader would say aloud.
 */
export class Citation {
    // CONSTANTS
    /**
     * What starts the identifier of a citation, so that its reference in the
     * bibliography can lead back to it.
     */
    static ID_PREFIX = 'cite-';

    /**
     * What surrounds the number, seen and never spoken.
     */
    static OPENING = '[';
    static CLOSING = ']';

    /**
     * What is shown when the key names nothing.
     */
    static UNKNOWN = '?';

    /**
     * The space that keeps the number with the word before it.
     */
    static UNBREAKABLE_SPACE = '\u00A0';

    /**
     * What ends the identifier of what a citation opens.
     */
    static CONTENT_SUFFIX = '-reference';

    /**
     * What the program says, in the languages it knows.
     */
    static LABELS = new Map([
        ['en', {reference: 'Reference', missing: 'missing reference'}],
        ['fr', {reference: 'Référence', missing: 'référence absente'}]
    ]);


    // FIELDS
    #element;
    #place;
    #citedKeys;
    #texts;


    // CONSTRUCTOR
    /**
     * Instantiate a citation.
     *
     * @param element {HTMLElement} What is written in the paragraph.
     * @param place {number} Its place in the order the citations appear, starting at 1.
     * @param citedKeys {CitedKey[]} The keys it bears, at least one.
     */
    constructor(element, place, citedKeys) {
        this.#element = element;
        this.#place = place;
        this.#citedKeys = [...citedKeys];
        this.#texts = new Labels(Citation.LABELS);
    }


    // GETTERS
    /**
     * Get what is written in the paragraph.
     *
     * @returns {HTMLElement}
     */
    get element() {
        return this.#element;
    }

    /**
     * Get its place in the order the citations appear.
     *
     * @returns {number}
     */
    get place() {
        return this.#place;
    }

    /**
     * Get the keys it bears.
     *
     * @returns {CitedKey[]} A copy, in the order they are written.
     */
    get citedKeys() {
        return [...this.#citedKeys];
    }


    // PUBLIC METHODS
    /**
     * Show the number the reference was given.
     *
     * @param number {number} The number of the reference, 1 or more.
     * @returns {void}
     */
    showNumber(number) {
        this.#show(Citation.OPENING + String(number) + Citation.CLOSING,
            this.#texts.text('reference') + ' ' + String(number));
    }

    /**
     * Show the number, and let the reference be read without leaving the
     * sentence.
     *
     * The number becomes a button, and what it opens is written right after
     * it, in the same paragraph: a reader consults a reference and goes on
     * reading, without the page moving under them.
     *
     * @param number {number} The number of the reference, 1 or more.
     * @param content {DocumentFragment} The reference, its addresses and what it says.
     * @param target {string} The identifier of its row in the bibliography.
     * @returns {HTMLElement} What opens, so that whoever opens it can be tied to it.
     */
    showReference(number, content, target) {
        this.showNumber(number);

        const control = document.createElement('button');
        control.type = 'button';
        control.className = 'bib-disclosure-control bib-citation-control';
        control.setAttribute('aria-expanded', 'false');
        control.setAttribute('aria-controls', this.#element.id + Citation.CONTENT_SUFFIX);
        control.setAttribute('aria-label', this.#element.getAttribute('aria-label'));
        control.textContent = this.#element.textContent;
        this.#texts.declare(control);

        // On paper nothing opens, and a button is neither a link nor
        // clickable in a PDF. The same number is written a second time, as a
        // link to the bibliography, and each of the two shows where it serves.
        const anchor = document.createElement('a');
        anchor.className = 'bib-citation-anchor';
        anchor.setAttribute('href', '#' + target);
        anchor.textContent = control.textContent;
        anchor.setAttribute('aria-label', control.getAttribute('aria-label'));
        this.#texts.declare(anchor);

        this.#element.textContent = '';
        this.#element.removeAttribute('aria-label');
        this.#element.appendChild(control);
        this.#element.appendChild(anchor);

        const opened = document.createElement('span');
        opened.className = 'bib-citation-content';
        opened.id = this.#element.id + Citation.CONTENT_SUFFIX;
        opened.hidden = true;
        opened.appendChild(content);
        this.#element.after(opened);

        return opened;
    }

    /**
     * Show that the key names no reference at all.
     *
     * No number is given: numbers belong to references, and there is none
     * here. The citation stays where it is, so that whoever wrote the document
     * sees what is missing, and so does whoever reads it.
     *
     * @returns {void}
     */
    showMissing() {
        this.#show(Citation.OPENING + Citation.UNKNOWN + Citation.CLOSING,
            this.#texts.text('missing'));
    }


    // PRIVATE METHODS
    /**
     * Write what is seen and what is spoken.
     *
     * @param seen {string} What takes the place of the text written in the document.
     * @param spoken {string} What a screen reader says instead.
     * @returns {void}
     */
    #show(seen, spoken) {
        if (this.#element.id === '') {
            this.#element.id = Citation.ID_PREFIX + String(this.#place);
        }

        this.#element.textContent = seen;
        this.#element.setAttribute('aria-label', spoken);
        this.#texts.declare(this.#element);

        this.#keepWithPreviousWord();
    }

    /**
     * Keep the citation with the word that comes before it.
     *
     * A number alone at the beginning of a line is a number nobody attaches to
     * anything. The space before the citation is what would break, so it
     * becomes an unbreakable one.
     *
     * @returns {void}
     */
    #keepWithPreviousWord() {
        const before = this.#element.previousSibling;

        if (before === null || before.nodeType !== Node.TEXT_NODE) {
            return;
        }

        before.textContent = before.textContent.replace(/\s+$/, Citation.UNBREAKABLE_SPACE);
    }
}
