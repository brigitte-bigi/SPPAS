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
    #toc_element;
    #headings_container;
    #html_tags;
    #toggle_button;


    // CONSTRUCTOR
    /**
     * Instantiate the book class.
     *
     * @param id_headings {string} The id of the html element where searched all headings
     * @param id_toc {string} Optional parameter, the id of the html nav of our table of contents
     */
    constructor(id_headings, id_toc = "toc") {
        this.#toc_element = document.getElementById(id_toc);
        this.#headings_container = document.getElementById(id_headings);
        this.#html_tags = "h1, h2, h3, h4";
        const container = this.#toc_element?.closest('nav, aside');
        if (container instanceof HTMLElement) {
            if (container.classList.contains('book-toc-aside')) {
                this.#setup_aside(container);
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
    get dom_toc() {
        return this.#toc_element;
    }

    /**
     * Get the html element that contains all headings.
     *
     * @returns {HTMLElement}
     */
    get headings() {
        return this.#headings_container;
    }

    /**
     * Get the html tags takes in account by the Book to fill the table.
     *
     * @returns {string} the html tags (format: <tag1>, <tag2>, ...)
     */
    get html_tags() {
        return this.#html_tags;
    }


    // PUBLIC METHODS
    /**
     * Set the html element where searched all headings.
     *
     * @param id_headings {string} The id of the html element
     */
    set_headings(id_headings) {
        this.#headings_container =  document.getElementById(id_headings);
    }

    /**
     * Set the html tags take in account by the class.
     * By default, the html tags are h1, h2, h3, h4.
     *
     * @param tags {string} (0, n) the html tags that the book has to detect
     */
    add_html_tags(...tags) {
        tags.forEach(current => {
            this.#html_tags += ", " + current
        });
    }

    /**
     * Delete given html tags.
     *
     * @param tags {string} (0, n) the html tags to delete
     */
    delete_html_tags(...tags) {
        tags.forEach(current => {
            this.#html_tags = this.#html_tags.replace(", " + current, "");
        });
    }


    /**
     * Fill the table with all headings.
     *
     * @param only_numerate_headings (bool) if we search only numerate headings or not, true by default.
     */
    fill_table(only_numerate_headings = true) {
        if (!(this.#toc_element instanceof HTMLElement)) return;
        const headings = this.#get_headings(only_numerate_headings);

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
            item.setAttribute('class', this.#class_of(heading));

            item.appendChild(link);
            this.#toc_element.appendChild(item);
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
    #class_of(heading) {
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
    #setup_aside(aside) {
        if (!aside.id) aside.id = 'book-toc-aside';
        aside.setAttribute('aria-hidden', 'true');

        const titleEl = aside.querySelector('h1, h2');
        const label = titleEl?.textContent?.trim() || 'Table of contents';

        this.#toggle_button = document.createElement('button');
        this.#toggle_button.className = 'book-toc-toggle';
        this.#toggle_button.setAttribute('aria-controls', aside.id);
        this.#toggle_button.setAttribute('aria-expanded', 'false');
        this.#toggle_button.setAttribute('aria-label', label);
        this.#toggle_button.textContent = label;
        this.#toggle_button.addEventListener('click', () => {
            const isOpen = aside.classList.toggle('open');
            this.#toggle_button.setAttribute('aria-expanded', String(isOpen));
            aside.setAttribute('aria-hidden', String(!isOpen));
            if (isOpen) {
                aside.querySelector('a[href], button')?.focus();
            } else {
                this.#toggle_button.focus();
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
            bar.appendChild(this.#toggle_button);
            return;
        }

        const header = document.querySelector('header');
        if (header !== null) {
            header.appendChild(this.#toggle_button);
            return;
        }

        const main = document.querySelector('main');
        if (main !== null) {
            main.prepend(this.#toggle_button);
            return;
        }

        document.body.prepend(this.#toggle_button);
    }

    /**
     * Searched all headings linked with the table of contents.
     *
     * @param only_numerate_headings (bool) if we search only numerate headings or not.
     *
     * @returns {Array[HTMLElement]} the headings array
     */
    #get_headings(only_numerate_headings) {
        if (!(this.#headings_container instanceof HTMLElement)) return [];
        const titles = Array.from(this.#headings_container.querySelectorAll(this.#html_tags));
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
