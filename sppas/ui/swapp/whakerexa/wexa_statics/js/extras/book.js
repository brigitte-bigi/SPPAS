/**
 :filename: wexa_statics/js/book.js
 :author: Brigitte Bigi
 :contributor: Florian Lopitaux
 :contact: contact@sppas.org
 :summary: A class to fill automatically the table of content.

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
export class Book {
    // FIELDS
    #tocElement;
    #headingsContainer;
    #htmlTags;
    #toggleButton;


    // CONSTRUCTOR
    /**
     * Instantiate the book class.
     *
     * @param id_headings {string} The id of the html element where searched all headings
     * @param id_toc {string} Optional parameter, the id of the html nav of our table of contents
     */
    constructor(id_headings, id_toc = "toc") {
        this.#tocElement = document.getElementById(id_toc);
        this.#headingsContainer = document.getElementById(id_headings);
        this.#htmlTags = "h1, h2, h3, h4";
        const container = this.#tocElement?.closest('nav, aside');
        if (container instanceof HTMLElement) {
            if (container.classList.contains('book-toc-aside')) {
                this.#setupAside(container);
            } else {
                container.setAttribute('tabindex', '-1');
            }
        }
    }


    // GETTERS
    /**
     * Get the table of contents html element.
     *
     * @returns {HTMLElement}
     */
    get domToc() {
        return this.#tocElement;
    }

    /**
     * Get the html element that contains all headings.
     *
     * @returns {HTMLElement}
     */
    get headings() {
        return this.#headingsContainer;
    }

    /**
     * Get the html tags takes in account by the Book to fill the table.
     *
     * @returns {string} the html tags (format: <tag1>, <tag2>, ...)
     */
    get htmlTags() {
        return this.#htmlTags;
    }


    // PUBLIC METHODS
    /**
     * Set the html element where searched all headings.
     *
     * @param id_headings {string} The id of the html element
     */
    setHeadings(id_headings) {
        this.#headingsContainer =  document.getElementById(id_headings);
    }

    /**
     * Set the html tags take in account by the class.
     * By default, the html tags are h1, h2, h3, h4.
     *
     * @param tags {string} (0, n) the html tags that the book has to detect
     */
    addHtmlTags(...tags) {
        tags.forEach(current => {
            this.#htmlTags += ", " + current
        });
    }

    /**
     * Delete given html tags.
     *
     * @param tags {string} (0, n) the html tags to delete
     */
    deleteHtmlTags(...tags) {
        tags.forEach(current => {
            this.#htmlTags = this.#htmlTags.replace(", " + current, "");
        });
    }


    /**
     * Fill the table with all headings.
     *
     * @param only_numerate_headings (bool) if we search only numerate headings or not, true by default.
     */
    fillTable(only_numerate_headings = true) {
        if (!(this.#tocElement instanceof HTMLElement)) return;
        const headings = this.#getHeadings(only_numerate_headings);

        headings.forEach((heading, index) => {
            /* Add the anchor right before the heading */
            let anchor = document.createElement('a');
            anchor.setAttribute("id", 'toc' + index);
            anchor.setAttribute("name", 'toc' + index);

            /* Add an entry into the table of content */
            let link = document.createElement('a');
            link.setAttribute('href', '#toc' + index);
            link.textContent = heading.textContent;

            let item = document.createElement('li');
            item.setAttribute('class', this.#classOf(heading));

            item.appendChild(link);
            this.#tocElement.appendChild(item);
            heading.parentNode.insertBefore(anchor, heading);
        });
    }


    // PRIVATE METHODS
    /**
     * Get the classes of an entry of the table of contents.
     *
     * The level of the heading tells how the entry is written and numbered,
     * and book.css does both. Whether the chapter it belongs to is numbered
     * is the one thing a stylesheet cannot see from the table of contents,
     * so it is written here.
     *
     * @param heading {HTMLElement} The heading the entry leads to.
     *
     * @returns {string} The classes of the entry.
     */
    #classOf(heading) {
        const level = heading.tagName.toLowerCase();

        if (heading.closest('.chapter.nonumber') === null) {
            return level;
        }

        return level + ' nonumber';
    }

    /**
     * Inject a toggle button and manage open/close state for aside.book-toc-aside.
     *
     * @param aside {HTMLElement} The aside.book-toc-aside element
     */
    #setupAside(aside) {
        if (!aside.id) aside.id = 'book-toc-aside';

        // A panel that is set aside is out of reach: 'inert' says it once, for
        // the keyboard as for a screen reader. 'aria-hidden' would say it to
        // the reader alone, and leave the links it holds declared as reachable.
        aside.inert = true;

        const titleEl = aside.querySelector('h1, h2');
        const label = titleEl?.textContent?.trim() || 'Table of contents';

        this.#toggleButton = document.createElement('button');
        this.#toggleButton.className = 'book-toc-toggle';
        this.#toggleButton.setAttribute('aria-controls', aside.id);
        this.#toggleButton.setAttribute('aria-expanded', 'false');
        this.#toggleButton.setAttribute('aria-label', label);
        this.#toggleButton.textContent = label;
        this.#toggleButton.addEventListener('click', () => {
            const isOpen = aside.classList.toggle('open');
            this.#toggleButton.setAttribute('aria-expanded', String(isOpen));
            aside.inert = !isOpen;
            if (isOpen) {
                aside.querySelector('a[href], button')?.focus();
            } else {
                this.#toggleButton.focus();
            }
        });

        this.#placeToggleButton();

        // Browsers do not honour page-break on <aside> elements when printing.
        // Inserting a <section class="blank-page"> immediately after the aside
        // acts as the page-break carrier (print.css targets .blank-page).
        // The empty <p> that follows prevents the section from being collapsed
        // by certain layout engines before the break is applied.
        const blankPage = document.createElement('section');
        blankPage.className = 'blank-page';
        aside.after(blankPage);

        const spacer = document.createElement('p');
        blankPage.after(spacer);
    }

    /**
     * Put the button where a reader reaches it first.
     *
     * The button navigates the document, so it stands with what navigates it:
     * last of the navigation bar. Beside the aside it commands, it came in the
     * tabbing order at the place of a table of contents, which a book writes
     * after its preface, while it is seen from the first second.
     *
     * Nothing of the framework is asked for: a nav, a header, a main and a body
     * are what HTML gives every document. A document without a nav keeps the
     * order all the same, end of the header, then start of the main, then start
     * of the body.
     *
     * @returns {void}
     */
    #placeToggleButton() {
        const bar = document.querySelector('nav');
        if (bar !== null) {
            bar.appendChild(this.#toggleButton);
            return;
        }

        const header = document.querySelector('header');
        if (header !== null) {
            header.appendChild(this.#toggleButton);
            return;
        }

        const main = document.querySelector('main');
        if (main !== null) {
            main.prepend(this.#toggleButton);
            return;
        }

        document.body.prepend(this.#toggleButton);
    }

    /**
     * Searched all headings linked with the table of contents.
     *
     * @param only_numerate_headings (bool) if we search only numerate headings or not.
     *
     * @returns {Array[HTMLElement]} the headings array
     */
    #getHeadings(only_numerate_headings) {
        if (!(this.#headingsContainer instanceof HTMLElement)) return [];
        const titles = Array.from(this.#headingsContainer.querySelectorAll(this.#htmlTags));
        let headings = [];

        titles.forEach(current => {
            if (only_numerate_headings) {
                // check if the heading begin by a number
                const c = window.getComputedStyle(current, '::before')['content'];
                if (c && c !== 'none' && c !== '""' && c !== "''") {
                    headings.push(current);
                }
            } else {
                headings.push(current);
            }
        });

        return headings;
    }
}
