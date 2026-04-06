/**
 * :filename: wexa_statics.js.links.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Controls user interactions on clickable elements that open URLs.
 *
 *  -------------------------------------------------------------------------
 *
 *  This file is part of Whakerexa: https://whakerexa.sf.net/
 *
 *  Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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

/**
 * Class managing all clickable elements that open URLs on user action.
 *
 * This class attaches keyboard and mouse listeners to any element having
 * an `href` or `data-href` attribute. When activated (by click or Enter),
 * the associated URL is opened according to the declared `data-target`.
 *
 * Usage example::
 *
 *     import LinkController from './links.js';
 *     const linkManager = new LinkController();
 *     linkManager.handleLinks(['doc_btn', 'help_link', 'open_video']);
 *
 * Supported attributes::
 *   - `href`:      the main URL to open.
 *   - `data-href`: fallback URL if `href` is empty.
 *   - `data-target`:
 *       * `_blank` → open in new tab (default)
 *       * `_self`  → open in same page
 *       * any other value → treated as iframe id, URL assigned to iframe.src
 *
 * Accessibility::
 *   Both click and Enter key trigger the same action.
 *   Event propagation and default navigation are prevented.
 */
export class LinkController {

    /**
     * Initialize a LinkController instance.
     * This class is self-contained and does not listen automatically.
     */
    constructor() {
        // Nothing to initialize; listeners are attached explicitly via handleLinks().
    }

    // ----------------------------------------------------------------------

    /**
     * Attach event listeners to all elements whose ids are listed in `selectors`.
     *
     * Each valid element will respond to both mouse clicks and Enter key events,
     * invoking the internal `_handleActivation()` method.
     *
     * @param {string[]} selectors - List of element ids to be handled.
     * @returns {void}
     */
    handleLinks(selectors) {
        this._bindLinks(selectors, false);
    }

    /**
     * Attach event listeners to all elements whose ids are listed in `selectors`.
     *
     * Each valid element will respond to both mouse clicks and Enter key events,
     * invoking the internal `_handleActivation()` method.
     *
     * @param {string[]} selectors - List of element ids to be handled.
     * @returns {void}
     */
    handleLinksWithParameters(selectors) {
        this._bindLinks(selectors, true);
    }

    // ----------------------------------------------------------------------
    // Private
    // ----------------------------------------------------------------------

    /**
     * Attach event listeners to all elements whose ids are listed in `selectors`.
     *
     * Each valid element will respond to both mouse clicks and Enter key events,
     * invoking the internal `_handleActivation()` method.
     *
     * @param {string[]} selectors - List of element ids to be handled.
     * @returns {void}
     */
    _bindLinks(selectors, withParameters) {
        if (!Array.isArray(selectors)) {
            console.error('LinkController: Expected a list of element ids.');
            return;
        }

        for (const id of selectors) {
            const element = document.getElementById(id);
            if (element === null) {
                console.warn(`LinkController: No element found with id "${id}".`);
                continue;
            }

            // Avoid multiple bindings on the same element
            element.removeEventListener('click', this._handleActivation);
            element.removeEventListener('keydown', this._handleActivation);

            element.addEventListener('click', (event) => this._handleActivation(event, element, withParameters));
            element.addEventListener('keydown', (event) => this._handleActivation(event, element, withParameters));
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Handle a click or keydown (Enter) event and open the appropriate target.
     *
     * @param {Event} event - The event object.
     * @param {HTMLElement} element - The element that triggered the event.
     * @param {Boolean} withParameters - Preserve accessibility
     * @private
     */
    _handleActivation(event, element, withParameters) {
        const isClick = (event.type === 'click');
        const isEnter = (event.type === 'keydown' && event.key === 'Enter');

        if (isClick === false && isEnter === false) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const url = element.getAttribute('href') || element.dataset.href;
        if (!url) {
            console.warn(`LinkController: No URL defined for element id="${element.id}".`);
            return;
        }

        const target = element.dataset.target || '_blank';
        this._openUrl(url, target, withParameters);
    }

    // ----------------------------------------------------------------------

    /**
     * Open the given URL according to the specified target.
     *
     * @param {string} url - The URL to open.
     * @param {string} target - The target mode: `_blank`, `_self`, or iframe id.
     * @param {Boolean} withParameters - Preserve accessibility
     * @private
     */
    _openUrl(url, target, withParameters) {
        let finalUrl = url;

        if (withParameters === true) {
            const absoluteUrl = new URL(url, window.location.href).href;
            finalUrl = window.Wexa.accessibility.setUrlWithParameters(absoluteUrl);
        }

        if (target === '_blank' || target === '_self') {
            window.open(finalUrl, target, 'noopener');
            return;
        }

        const iframe = document.getElementById(target);
        if (iframe && iframe.tagName.toLowerCase() === 'iframe') {
            iframe.src = finalUrl;
        } else {
            console.warn(`LinkController: No iframe found with id="${target}". Opening in new tab.`);
            window.open(finalUrl, '_blank', 'noopener');
        }
    }
}
