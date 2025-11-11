/**
:filename: statics.js.book.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to filled the table of content.

-------------------------------------------------------------------------

This file is part of Whakerexa: https://whakerexa.sf.net/

Copyright (C) 2023-2024 Brigitte Bigi, CNRS
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


class Book {
    // FIELDS
    #toc_element;
    #headings_container;
    #html_tags;


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
            item.setAttribute('class', heading.tagName.toLowerCase());

            item.appendChild(link);
            this.#toc_element.appendChild(item);
            heading.parentNode.insertBefore(anchor, heading);
        });
    }


    // PRIVATE METHODS
    /**
     * Searched all headings linked with the table of contents.
     *
     * @param only_numerate_headings (bool) if we search only numerate headings or not.
     *
     * @returns {Array[HTMLElement]} the headings array
     */
    #get_headings(only_numerate_headings) {
        let titles = [].slice.call(this.#headings_container.querySelectorAll(this.#html_tags));
        let headings = [];

        titles.forEach(current => {
            if (only_numerate_headings) {
                // check if the heading begin by a number
                let before = window.getComputedStyle(current,'::before');

                if (before['content'].includes("counter(")) {
                    headings.push(current);
                }
            } else {
                headings.push(current);
            }
        });

        return headings;
    }
}
