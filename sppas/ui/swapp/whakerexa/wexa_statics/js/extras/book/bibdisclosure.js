/**
 :filename: wexa_statics/js/extras/book/bibdisclosure.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to open and close a content of a bibliography on demand.

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
 * Open and close a content of a bibliography on demand.
 *
 * There is one of these per content that opens: an abstract, a BibTeX source.
 * Each has its own state, which no other one knows. Several stay open at the
 * same time, and none closes on its own: closing what nobody asked to close
 * makes what is being read disappear.
 *
 * Whether it is open is read on the control, which already says it for the
 * screen reader. Keeping it a second time would make two truths possible.
 *
 * The element "details" was set aside: the browser closes the paragraph it
 * finds it in, so it cannot stand inside a sentence, which is where a citation
 * stands.
 */
export class ReferenceDisclosure {
    // CONSTANTS
    /**
     * What a control inside the content looks like, when there is one.
     */
    static CLOSING_CONTROL = '.bib-disclosure-close';


    // FIELDS
    #control;
    #content;


    // CONSTRUCTOR
    /**
     * Instantiate a content that opens on demand.
     *
     * The content is expected to follow the control in the order of the
     * document: the keyboard then reaches it by going on, and nothing has to
     * be moved when it opens.
     *
     * @param control {HTMLElement} The button that opens and closes.
     * @param content {HTMLElement} What is shown, hidden until it is asked for.
     */
    constructor(control, content) {
        this.#control = control;
        this.#content = content;

        this.#control.addEventListener('click', () => this.toggle());

        const closing = this.#content.querySelector(ReferenceDisclosure.CLOSING_CONTROL);
        if (closing !== null) {
            closing.addEventListener('click', () => this.close());
        }
    }


    // GETTERS
    /**
     * Get the control that opens and closes.
     *
     * It is also where the reading comes back to, at every closing.
     *
     * @returns {HTMLElement}
     */
    get control() {
        return this.#control;
    }

    /**
     * Get what is shown when it is open.
     *
     * @returns {HTMLElement}
     */
    get content() {
        return this.#content;
    }

    /**
     * Tell whether the content is open.
     *
     * The answer is read on the control, and nowhere else.
     *
     * @returns {boolean}
     */
    get isOpen() {
        return this.#control.getAttribute('aria-expanded') === 'true';
    }


    // PUBLIC METHODS
    /**
     * Show the content.
     *
     * The focus does not move: the content follows the control, so it is
     * reached by going on, and the page does not scroll. Opening what is
     * already open does nothing wrong.
     *
     * @returns {void}
     */
    open() {
        this.#control.setAttribute('aria-expanded', 'true');
        this.#content.hidden = false;
    }

    /**
     * Hide the content, and give the focus back to the control.
     *
     * Giving the focus back is what matters when the closing came from inside
     * the content: what held the focus has just been hidden, and a focus left
     * on a hidden element is a reader left nowhere.
     *
     * @returns {void}
     */
    close() {
        this.#control.setAttribute('aria-expanded', 'false');
        this.#content.hidden = true;
        this.#control.focus();
    }

    /**
     * Open what is closed, close what is open.
     *
     * @returns {void}
     */
    toggle() {
        if (this.isOpen === true) {
            this.close();
            return;
        }

        this.open();
    }
}
