/**
 :filename: statics.js.slides.overview.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Build and control the overview panel.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://whakerexa.sf.net/

 Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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
 * The overview displays a list of slide copies.
 * Each item contains: <header> number, <main> clone, <footer> GoTo button.
 *
 * SlidesOverview builds and displays the overview mode, a panel of cloned
 * slides, each with:
 * - <header> : slide number
 * - <main>   : full clone of the slide content
 * - <footer> : GoTo button
 *
 * SlidesOverview has its own isolated copy of the slide list to ensure
 * full separation between visual modes (presentation vs overview).
 */
export default class SlidesOverview {
    /**
     * @constructor
     * Create an Overview view.
     *
     * @param {HTMLElement[]} slides - The list of slides managed by the module.
     * @param {HTMLElement} panelElement - The <section> used as overview panel.
     * @param {function(number):void} onSelectSlide - Callback invoked on GoTo.
     */
    constructor(slides, panelElement, onSelectSlide) {
        this._slides = Array.isArray(slides) ? slides : [];

        this._panel = panelElement instanceof HTMLElement ? panelElement : null;

        this._onSelectSlide = (typeof onSelectSlide === 'function') ? onSelectSlide : null;

        if (this._panel !== null) {
            this._panel.style.display = 'none'; // hidden by default
        }
    }

    // -------------------------------------------------------------------------
    //  Public API
    // -------------------------------------------------------------------------

    /**
     * Build the overview panel.
     *
     * @returns {void}
     */
    build() {
        if (this._panel === null) {
            return;
        }

        this._panel.innerHTML = '';

        const total = this._slides.length;

        for (let i = 0; i < total; i++) {
            const slide = this._slides[i];
            const index = i + 1;

            // Create the <article> container.
            const article = document.createElement('article');
            article.className = 'overview-item';

            // Header: slide number.
            const header = document.createElement('header');
            header.textContent = String(index);
            article.appendChild(header);

            // Main: clone of the slide.
            const main = document.createElement('main');
            // only the content, not the section container
            const fragment = document.createRange().createContextualFragment(slide.innerHTML);
            main.appendChild(fragment);
            article.appendChild(main);

            // Footer: GoTo button.
            const footer = document.createElement('footer');
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = 'GoTo';

            btn.addEventListener('click', () => {
                if (typeof this._onSelectSlide === 'function') {
                    this._onSelectSlide(index);
                }
                this.hide();
            });

            footer.appendChild(btn);
            article.appendChild(footer);

            this._panel.appendChild(article);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Show the overview panel.
     *
     * @returns {void}
     */
    show() {
        if (this._panel !== null) {
            this._panel.style.display = 'block';
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Hide the overview panel.
     *
     * @returns {void}
     */
    hide() {
        if (this._panel !== null) {
            this._panel.style.display = 'none';
        }
    }

}
