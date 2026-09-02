/**
 :filename: statics.js.keyboard.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to answer keys pressed on a page, without taking them from
           whoever is typing.

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
 * Answer the keys a page declares, and no other.
 *
 * A page says which keys it answers and what they do; everything else is
 * given back to the browser. One listener stands on the body, whatever the
 * number of shortcuts, and it is silent as soon as the focus is on something
 * a key belongs to -- a field being typed in, a control being operated. That
 * guard is the reason this class exists: written again in each component, it
 * is written differently in each, and a document ends up stealing the letters
 * of whoever writes in it.
 *
 * Enter and space are never answered: they operate whatever holds the focus,
 * and no page is entitled to take them.
 *
 * @example
 * const keyboard = new KeyboardController();
 * keyboard.register({keys: ['h', 'H', '?'], action: () => help.click()});
 * keyboard.register({keys: ['ArrowRight'], action: 'page:next', preventsDefault: true});
 * keyboard.init();
 */
export class KeyboardController {

    // CONSTANTS
    /**
     * The keys that operate what holds the focus, and are never answered.
     */
    static RESERVED_KEYS = ['Enter', ' '];

    /**
     * What a key must not be taken from: a field, a control, a link, a media
     * with its own commands, and anything a page made reachable by the tab key.
     */
    static INTERACTIVE_TAGS = ['input', 'select', 'textarea', 'button', 'summary'];


    // FIELDS
    #shortcuts;
    #boundHandler;
    #listening;


    // CONSTRUCTOR
    /**
     * Instantiate a controller that answers nothing yet.
     *
     * @constructor
     * @returns {KeyboardController}
     */
    constructor() {
        this.#shortcuts = new Map();
        this.#boundHandler = this.#onKeyDown.bind(this);
        this.#listening = false;
    }


    // GETTERS
    /**
     * Get what the page answers, in the order it was declared.
     *
     * A help dialog is written from this: it says the keys and what they are
     * for, and it says nothing the controller does not answer.
     *
     * @returns {Array} One entry per shortcut, with its keys and its label.
     */
    get shortcuts() {
        const said = [];

        this.#shortcuts.forEach(shortcut => {
            if (said.includes(shortcut) === false) {
                said.push(shortcut);
            }
        });

        return said.map(shortcut => ({keys: [...shortcut.keys], label: shortcut.label}));
    }


    // PUBLIC METHODS
    /**
     * Declare the keys the page answers, and what they do.
     *
     * What is done is either a function, called with the event, or the name of
     * a CustomEvent dispatched on the document. The second is what a component
     * made of several parts uses: the keys are read in one place, and answered
     * wherever the work is done.
     *
     * A key already declared is answered by the last declaration, and the
     * console says so: two answers to one key is a mistake of the page, not a
     * choice to be silently kept.
     *
     * @param {Object} shortcut - What is declared.
     * @param {string[]} shortcut.keys - The keys, as KeyboardEvent.key writes them.
     * @param {Function|string} shortcut.action - What they do, or the name of the event to dispatch.
     * @param {Object} [shortcut.detail] - What the dispatched event carries.
     * @param {string} [shortcut.label] - What the keys are for, for a help dialog.
     * @param {boolean} [shortcut.preventsDefault] - Whether the browser is kept from acting, a key that scrolls asking for it.
     * @returns {void}
     */
    register({keys, action, detail = {}, label = '', preventsDefault = false}) {
        if (Array.isArray(keys) === false || keys.length === 0) {
            console.warn('KeyboardController: a shortcut without a key is not declared.');
            return;
        }
        if (typeof action !== 'function' && typeof action !== 'string') {
            console.warn(`KeyboardController: the keys "${keys.join(', ')}" do nothing, and are not declared.`);
            return;
        }

        const answered = keys.filter(key => KeyboardController.RESERVED_KEYS.includes(key) === false);
        if (answered.length !== keys.length) {
            console.warn('KeyboardController: Enter and space operate what holds the focus, and are not declared.');
        }
        if (answered.length === 0) {
            return;
        }

        const shortcut = {keys: answered, action: action, detail: detail,
                          label: label, preventsDefault: preventsDefault};

        answered.forEach(key => {
            if (this.#shortcuts.has(key) === true) {
                console.warn(`KeyboardController: the key "${key}" was already answered, and its answer is replaced.`);
            }
            this.#shortcuts.set(key, shortcut);
        });
    }

    // -----------------------------------------------------------------------

    /**
     * Stop answering the keys of a shortcut.
     *
     * @param {string[]} keys - The keys to give back to the browser.
     * @returns {void}
     */
    forget(keys) {
        keys.forEach(key => this.#shortcuts.delete(key));
    }

    // -----------------------------------------------------------------------

    /**
     * Start answering.
     *
     * Called twice, it listens once: a page that sets its shortcuts up again
     * does not answer each key twice.
     *
     * @returns {void}
     */
    init() {
        if (this.#listening === true) {
            return;
        }
        document.body.addEventListener('keydown', this.#boundHandler, false);
        this.#listening = true;
    }

    // -----------------------------------------------------------------------

    /**
     * Stop answering, and give every key back to the browser.
     *
     * @returns {void}
     */
    destroy() {
        document.body.removeEventListener('keydown', this.#boundHandler, false);
        this.#listening = false;
    }

    // -----------------------------------------------------------------------

    /**
     * Tell whether a key must be given back to whatever holds the focus.
     *
     * Held here so that a component never writes it again: what is typed in a
     * field, what operates a control, and what a page made reachable by the
     * tab key all belong to the element, not to the page.
     *
     * @param {EventTarget} target - What the event was aimed at.
     * @returns {boolean} True when the key belongs to the target.
     */
    static isInteractiveTarget(target) {
        if (target instanceof HTMLElement === false) {
            return true;
        }

        const tag = target.tagName.toLowerCase();

        if (KeyboardController.INTERACTIVE_TAGS.includes(tag) === true) {
            return true;
        }

        if (tag === 'a' && target.hasAttribute('href') === true) {
            return true;
        }

        if ((tag === 'video' || tag === 'audio') && target.hasAttribute('controls') === true) {
            return true;
        }

        if (target.isContentEditable === true) {
            return true;
        }

        const reachable = target.getAttribute('tabindex');
        if (reachable !== null) {
            const rank = parseInt(reachable, 10);
            if (Number.isNaN(rank) === false && rank >= 0) {
                return true;
            }
        }

        return false;
    }


    // PRIVATE METHODS
    /**
     * Answer one key, or give it back.
     *
     * @param {KeyboardEvent} event - What was pressed.
     * @returns {void}
     */
    #onKeyDown(event) {
        const shortcut = this.#shortcuts.get(event.key);
        if (shortcut === undefined) {
            return;
        }
        if (KeyboardController.isInteractiveTarget(event.target) === true) {
            return;
        }

        if (shortcut.preventsDefault === true) {
            event.preventDefault();
        }

        if (typeof shortcut.action === 'function') {
            shortcut.action(event);
            return;
        }

        document.dispatchEvent(new CustomEvent(shortcut.action, {detail: shortcut.detail}));
    }
}
