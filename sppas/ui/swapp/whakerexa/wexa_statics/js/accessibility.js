import { BaseManager } from './transport/base_manager.js';
import { OnLoadManager } from './dom-loader.js';
import { SVGIconsManager } from './svgicons.js';

/**
:filename: statics.js.accessibility.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to manage the color and contrast modes of the body.

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

/**
 * Manage the color and contrast accessibility modes of a web application.
 *
 * The AccessibilityManager controls two orthogonal binary modes:
 *   - color mode: light (default) or dark, toggled with switchColorScheme().
 *   - contrast mode: normal (default) or high-contrast, toggled with switchContrastScheme().
 *
 * CSS themes (wexa_theme_*.css) are loaded statically and are not managed here.
 * This class only applies the two mode classes to <body>, propagates them via
 * URL parameters across pages, and synchronizes state with the server.
 *
 * @example
 * Wexa.accessibility.switchColorScheme();    // toggle dark mode
 * Wexa.accessibility.switchContrastScheme(); // toggle contrast mode
 */
export class AccessibilityManager extends BaseManager {

    // -----------------------------------------------------------------------
    // FIELDS
    // -----------------------------------------------------------------------

    #activatedColor;
    #activatedContrast;

    // -----------------------------------------------------------------------
    // CONSTRUCTOR
    // -----------------------------------------------------------------------

    /**
    * Create a new AccessibilityManager instance.
    *
    * Initializes both modes to their default (inactive) state and registers
    * three onload functions: class restoration from URL, link customization,
    * and form submit customization.
    *
    * @constructor
    * @returns {AccessibilityManager}
    */
    constructor() {
        super();
        this.#activatedColor = "";
        this.#activatedContrast = "";

        OnLoadManager.addLoadFunction(this.#loadBodyClasses.bind(this));
        OnLoadManager.addLoadFunction(this.#setAllLinksCustom.bind(this));
        OnLoadManager.addLoadFunction(this.#setSubmitCustom.bind(this));
        OnLoadManager.addLoadFunction(this.#injectButtonIcons.bind(this));
    }

    // -----------------------------------------------------------------------
    // STATIC CONSTANTS
    // -----------------------------------------------------------------------

    static get COLOR_MODE()              { return "dark"; }
    static get CONTRAST_MODE()           { return "contrast"; }
    static get COLOR_PARAMETER_NAME()    { return "wexa_color"; }
    static get CONTRAST_PARAMETER_NAME() { return "wexa_contrast"; }

    // -----------------------------------------------------------------------
    // GETTERS
    // -----------------------------------------------------------------------

    /**
     * The currently active color mode class, or "" when light (default).
     * @returns {string}
     */
    get activatedColorMode() {
        return this.#activatedColor;
    }

    // -----------------------------------------------------------------------

    /**
     * The currently active contrast mode class, or "" when normal (default).
     * @returns {string}
     */
    get activatedContrastMode() {
        return this.#activatedContrast;
    }

    // -----------------------------------------------------------------------
    // PUBLIC METHODS
    // -----------------------------------------------------------------------

    /**
    * Toggle between light (default) and dark color mode.
    *
    * Adds or removes the "dark" class on <body>, updates the color mode
    * button state, and notifies the server via a POST event.
    *
    * @async
    * @returns {Promise<void>}
    */
    async switchColorScheme() {
        if (this.#activatedColor === "") {
            this.#activatedColor = AccessibilityManager.COLOR_MODE;
            document.documentElement.classList.add(AccessibilityManager.COLOR_MODE);
        } else {
            this.#activatedColor = "";
            document.documentElement.classList.remove(AccessibilityManager.COLOR_MODE);
        }

        this.#updateButtonState('btn-color');
        this.#updateUrl();
        await this.postEvents({"accessibility_color": this.#activatedColor});
    }

    // -----------------------------------------------------------------------

    /**
     * Toggle between normal (default) and high-contrast mode.
     *
     * Adds or removes the "contrast" class on <body>, updates the contrast
     * button state, and notifies the server via a POST event.
     *
     * @async
     * @returns {Promise<void>}
     */
    async switchContrastScheme() {
        if (this.#activatedContrast === "") {
            this.#activatedContrast = AccessibilityManager.CONTRAST_MODE;
            document.documentElement.classList.add(AccessibilityManager.CONTRAST_MODE);
        } else {
            this.#activatedContrast = "";
            document.documentElement.classList.remove(AccessibilityManager.CONTRAST_MODE);
        }

        this.#updateButtonState('btn-contrast');
        this.#updateUrl();
        await this.postEvents({"accessibility_contrast": this.#activatedContrast});
    }

    // -----------------------------------------------------------------------

    /**
     * Redirect the client while preserving accessibility parameters.
     *
     * Accessibility parameters are appended when navigating within the same
     * host or when the current page is served from localhost (development mode).
     * External domains are left unchanged unless the current host is localhost.
     *
     * @param {HTMLAnchorElement} element - The <a> element providing the target URL.
     * @param {boolean} openInNewTab - True to open the destination in a new tab.
     * @returns {void}
     */
    goToLink(element, openInNewTab = false) {
        const rawHref = element.getAttribute('href');
        if (rawHref === null || rawHref === '') {
            return;
        }
        const url = new URL(element.href, window.location.href);

        let targetUrl;
        if (window.location.protocol !== 'file:' && (window.location.hostname === 'localhost' || url.host === window.location.host)) {
            targetUrl = this.setUrlWithParameters(url.href);
        } else {
            targetUrl = url.href;
        }

        if (openInNewTab === true) {
            window.open(targetUrl, '_blank', 'noopener');
            return;
        }

        document.location.href = targetUrl;
    }

    // -----------------------------------------------------------------------

    /**
     * Append accessibility parameters (color and contrast) to a given URL.
     *
     * All parameters present in the current page URL are forwarded first, so
     * that parameters owned by other managers (e.g. wexa_theme from ThemeManager)
     * are preserved during navigation. Accessibility parameters are then set or
     * removed on top of those forwarded values.
     *
     * @param {string} url - The URL to modify.
     * @returns {string} The updated URL with accessibility parameters.
     */
    setUrlWithParameters(url) {
        if (url === null || url === '') {
            return '';
        }
        const customUrl = new URL(url, window.location.href);

        // Forward all parameters from the current URL so that params owned by
        // other managers (e.g. wexa_theme) survive cross-page navigation.
        const currentParams = new URLSearchParams(window.location.search);
        for (const [key, value] of currentParams) {
            customUrl.searchParams.set(key, value);
        }

        if (this.#activatedColor !== '') {
            customUrl.searchParams.set(AccessibilityManager.COLOR_PARAMETER_NAME, this.#activatedColor);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.COLOR_PARAMETER_NAME);
        }

        if (this.#activatedContrast !== '') {
            customUrl.searchParams.set(AccessibilityManager.CONTRAST_PARAMETER_NAME, this.#activatedContrast);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.CONTRAST_PARAMETER_NAME);
        }

        return customUrl.href;
    }

    // -----------------------------------------------------------------------
    // PRIVATE METHODS
    // -----------------------------------------------------------------------

    /**
     * Restore color and contrast modes from URL parameters on page load.
     * @private
     * @async
     * @returns {Promise<void>}
     */
    async #loadBodyClasses() {
        const params = new URLSearchParams(window.location.search);
        const events = {};

        if (params.has(AccessibilityManager.COLOR_PARAMETER_NAME)) {
            const colorParam = params.get(AccessibilityManager.COLOR_PARAMETER_NAME).toLowerCase();
            if (colorParam === AccessibilityManager.COLOR_MODE) {
                this.#activatedColor = colorParam;
                document.documentElement.classList.add(colorParam);
                events.accessibility_color = this.#activatedColor;
            } else {
                console.log(AccessibilityManager.COLOR_PARAMETER_NAME + " unknown value: " + colorParam);
            }
        }

        if (params.has(AccessibilityManager.CONTRAST_PARAMETER_NAME)) {
            const contrastParam = params.get(AccessibilityManager.CONTRAST_PARAMETER_NAME).toLowerCase();
            if (contrastParam === AccessibilityManager.CONTRAST_MODE) {
                this.#activatedContrast = contrastParam;
                document.documentElement.classList.add(contrastParam);
                events.accessibility_contrast = this.#activatedContrast;
            } else {
                console.log(AccessibilityManager.CONTRAST_PARAMETER_NAME + " unknown value: " + contrastParam);
            }
        }

        if (Object.keys(events).length > 0) {
            await this.postEvents(events);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Customize the click event of all 'a' elements to call goToLink().
     * @private
     */
    #setAllLinksCustom() {
        let linkElements = Array.from(document.querySelectorAll("a"));
        linkElements = linkElements.filter(el => el.href !== null && el.href !== '');

        linkElements.forEach(element => {
            element.addEventListener("click", event => {
                event.preventDefault();
                this.goToLink(element, element.target === '_blank');
            });
        });
    }

    // -----------------------------------------------------------------------

    /**
     * Rewrite the form action on submit to preserve accessibility parameters.
     * @private
     * @returns {void}
     */
    #setSubmitCustom() {
        const submitButton = document.querySelector('button[type="submit"]');
        if (!submitButton) return;

        submitButton.addEventListener('click', () => {
            const form = document.querySelector('form');
            if (form) {
                form.action = this.setUrlWithParameters(form.action);
            }
        });
    }

    // -----------------------------------------------------------------------

    /**
     * Inject inline SVG icons into btn-contrast and btn-color if they are empty.
     * Inline SVG is required so that stroke/fill currentColor inherits from CSS color.
     *
     * @async
     * @private
     * @returns {Promise<void>}
     */
    async #injectButtonIcons() {
        await SVGIconsManager.inject(document.getElementById('btn-contrast'), 'contrast');
        await SVGIconsManager.inject(document.getElementById('btn-color'), 'color');
    }

    // -----------------------------------------------------------------------

    /**
     * Reflect the current accessibility state in the browser URL without reloading.
     * Ensures that a page reload restores both color and contrast modes.
     * @private
     */
    #updateUrl() {
        history.replaceState(null, '', this.setUrlWithParameters(window.location.href));
    }

    // -----------------------------------------------------------------------

    /**
     * Update the aria-pressed state of a mode toggle button.
     * @private
     * @param {string} buttonId - 'btn-contrast' or 'btn-color'.
     */
    #updateButtonState(buttonId) {
        const btn = document.getElementById(buttonId);
        if (btn === null) { console.error(`Button not found: ${buttonId}.`); return; }

        let pressed = false;
        if (buttonId === 'btn-contrast') { pressed = this.#activatedContrast !== ''; }
        else if (buttonId === 'btn-color') { pressed = this.#activatedColor !== ''; }
        else { console.error(`Unknown button id: ${buttonId}.`); return; }

        btn.setAttribute('aria-pressed', String(pressed));
    }

}
