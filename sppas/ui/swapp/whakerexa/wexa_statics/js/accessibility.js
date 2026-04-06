import { BaseManager } from './transport/base_manager.js';
import { OnLoadManager } from './dom-loader.js';

/**
:filename: statics.js.accessibility.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to manage the color and contrast scheme of the body.

-------------------------------------------------------------------------

This file is part of Whakerexa: https://whakerexa.sf.net/

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
 * Manage the color and contrast accessibility schemes of a web application.
 *
 * The AccessibilityManager controls two user interface properties:
 * color theme (e.g., light or dark) and contrast level (e.g., normal or high).
 * It applies the appropriate CSS classes to the <body> element, ensures that
 * all internal links maintain the selected scheme through URL parameters, and
 * synchronizes the current accessibility state with the server using POST events.
 *
 * The manager operates fully client-side but can inform the server of any
 * theme or contrast change through inherited BaseManager methods. It is designed
 * to remain lightweight, non-intrusive, and compatible with all Whakerexa modules.
 *
 * Typical interactions:
 * - Automatic setup on page load (reading URL parameters and applying classes).
 * - Real-time update when switching color or contrast schemes.
 * - Optional server synchronization via `postEvents()` for persistence across pages.
 *
 * @example
 * // Toggle dark mode
 * AccessibilityManager.switch_color_scheme();
 *
 * @example
 * // Activate high-contrast mode
 * AccessibilityManager.activate_contrast_scheme('contrast');
 *
 */
export class AccessibilityManager extends BaseManager {

    // -----------------------------------------------------------------------
    // FIELDS
    // -----------------------------------------------------------------------

    #colors;
    #activated_color;
    #contrasts;
    #activated_contrast;

    // -----------------------------------------------------------------------
    // CONSTRUCTOR
    // -----------------------------------------------------------------------

    /**
    * Create a new AccessibilityManager instance.
    *
    * This constructor initializes default color and contrast schemes,
    * sets their active values to empty (light and no-contrast by default),
    * and registers two onload functions:
    * 1. `#load_body_classes()` – applies color and contrast settings from URL parameters.
    * 2. `#set_all_links_custom()` – ensures internal links preserve accessibility parameters.
    *
    * @constructor
    * @returns {AccessibilityManager} A new accessibility manager instance.
    */
    constructor() {
        super();
        this.#colors = ["dark"];
        this.#activated_color = "";
        this.#contrasts = ["contrast"];
        this.#activated_contrast = "";

        // add onload events
        OnLoadManager.addLoadFunction(this.#loadBodyClasses.bind(this));
        OnLoadManager.addLoadFunction(this.#setAllLinksCustom.bind(this));
        OnLoadManager.addLoadFunction(this.#setSubmitCustom.bind(this));
    }

    // -----------------------------------------------------------------------
    // GETTERS
    // -----------------------------------------------------------------------

    /**
     * Get all color schemes register in the class.
     * By default, contains only 'dark' (the 'light' mode is the default scheme when no scheme is set).
     *
     * @returns {Array[string]}
     */
    get colorSchemes() {
        return this.#colors;
    }

    // -----------------------------------------------------------------------

    /**
     * Get the current color scheme activated.
     * If this value is an empty string, then it's the default (light) mode which is activated.
     *
     * @returns {string}
     */
    get activatedColorScheme() {
        return this.#activated_color;
    }

    // -----------------------------------------------------------------------

    /**
     * Get all contrast schemes register in the class.
     * By default, contains only 'contrast'.
     *
     * @returns {Array[string]}
     */
    get contrastSchemes() {
        return this.#contrasts;
    }

    // -----------------------------------------------------------------------

    /**
     * Get the current contrast scheme activated.
     * If this value is an empty string, then it's the default (no-contrast) mode which is activated.
     *
     * @returns {string}
     */
    get activatedContrastScheme() {
        return this.#activated_contrast;
    }

    // -----------------------------------------------------------------------
    // SETTERS
    // -----------------------------------------------------------------------

    /**
     * Add a new color scheme to the registered list.
     *
     * This method registers a custom color scheme that can later be applied
     * through `activateColorScheme()`. The provided name must correspond to a
     * CSS class that overrides the color variables used by the `<body>` element.
     *
     * @param {string} colorScheme - The name of the new color scheme (CSS class name).
     * @returns {void}
     */
    addColorScheme(colorScheme) {
        if (typeof colorScheme === 'string') {
            this.#colors.push(colorScheme);
        } else {
            console.log("The 'colorScheme' parameter must be a string, not a: " + typeof colorScheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Remove a color scheme from the registered list.
     *
     * This method deletes a specific color scheme name from the internal list
     * if it exists. If the provided name is invalid or not found, a warning
     * message is logged.
     *
     * @param {string} colorScheme - The name of the color scheme to remove.
     * @returns {void}
     */
    removeColorScheme(colorScheme) {
        if (typeof colorScheme !== 'string') {
            console.log("The 'colorScheme' parameter must be a string, not a: " + typeof colorScheme);
        }

        const colorIndex = this.#colors.indexOf(colorScheme);

        if (colorIndex === -1) {
            console.log("The color scheme '" + colorScheme + "' does not exist!");
        } else {
            this.#colors.splice(colorIndex, 1);
        }
    }


    // -----------------------------------------------------------------------

    /**
     * Add a new contrast scheme to the registered list.
     *
     * This method registers a custom contrast scheme that can later be applied
     * through `activateContrastScheme()`. The given name must correspond to a CSS
     * class defining the contrast variables usable by the `<body>` element.
     *
     * @param {string} contrastScheme - The name of the contrast scheme to add.
     * @returns {void}
     */
    addContrastScheme(contrastScheme) {
        if (typeof contrastScheme === 'string') {
            this.#contrasts.push(contrastScheme);
        } else {
            console.log("The 'contrastScheme' parameter must be a string, not a: " + typeof contrastScheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Remove a contrast scheme from the registered list.
     *
     * This method deletes a specific contrast scheme name from the internal list
     * if it exists. If the provided name is invalid or unknown, a warning message
     * is logged.
     *
     * @param {string} contrastScheme - The name of the contrast scheme to remove.
     * @returns {void}
     */
    removeContrastScheme(contrastScheme) {
        if (typeof contrastScheme !== 'string') {
            console.log("The 'contrastScheme' parameter must be a string, not a: " + typeof contrastScheme);
        }

        const contrastIndex = this.#contrasts.indexOf(contrastScheme);

        if (contrastIndex === -1) {
            console.log("The contrast scheme '" + contrastScheme + "' does not exist!");
        } else {
            this.#contrasts.splice(contrastIndex, 1);
        }
    }

    // -----------------------------------------------------------------------
    // PUBLIC STATIC METHODS
    // -----------------------------------------------------------------------

    static get COLOR_PARAMETER_NAME() {
        return "wexa_color";
    }

    static get CONTRAST_PARAMETER_NAME() {
        return "wexa_contrast";
    }

    // -----------------------------------------------------------------------
    // PUBLIC METHODS
    // -----------------------------------------------------------------------

    /**
     * DEPRECATED.
     * @returns {Promise<void>}
     */
    async switch_color_scheme() {
        await this.switchColorScheme();
    }

    /**
    * Toggle between the default (light) and the configured color scheme.
    *
    * This method switches the color mode when only one color scheme is registered.
    * If multiple color schemes exist, it logs a warning and requires using
    * `activate_color_scheme()` instead. The method updates the `<body>` element’s
    * CSS class, refreshes the visual state of the theme button, and informs the
    * server of the current color scheme through a POST event.
    *
    * @async
    * @returns {Promise<void>}
    */
    async switchColorScheme() {
        if (this.#colors.length > 1) {
            console.log("Impossible to switch color scheme because multiple color schemes has set !" +
                "You have to use the activate_color_scheme() method!");
        }

        if (this.#activated_color === "") {
            this.#activated_color = this.#colors[0];
            document.body.classList.add(this.#colors[0]);

        } else {
            this.#activated_color = "";
            document.body.classList.remove(this.#colors[0]);
        }

        // Update state of the theme button
        this.#updateButtonState('btn-theme');
        await this.postEvents({"accessibility_color": this.#activated_color});
    }

    // -----------------------------------------------------------------------

    /**
    * DEPRECATED.
    * @param {string} color_scheme - Name of the color scheme to activate.
    * @returns {Promise<void>}
    */
    async activate_color_scheme(color_scheme) {
        await this.activateColorScheme(color_scheme);
    }

    /**
    * Activate a specific color scheme on the current page.
    *
    * This method applies the selected color theme by updating the `<body>` class
    * and removing any previously active color. It synchronizes the chosen scheme
    * with the server using a POST event, ensuring that both client and server
    * maintain a consistent accessibility state.
    *
    * @async
    * @param {string} colorScheme - The name of the color scheme to apply
    *                               (e.g., 'dark', 'light', or custom name).
    * @returns {Promise<void>}
    */
    async activateColorScheme(colorScheme) {
        if (colorScheme === "" || this.#colors.includes(colorScheme)) {
            if (this.#activated_color !== "") {
                document.body.classList.remove(this.#activated_color);
            }

            if (colorScheme !== "") {
                document.body.classList.add(colorScheme);
            }

            this.#activated_color = colorScheme;
            await this.postEvents({"accessibility_color": this.#activated_color});
        } else {
            console.log("Unknown given color scheme: " + colorScheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * DEPRECATED.
     * @returns {Promise<void>}
     */
    async switch_contrast_scheme() {
        await this.switchContrastScheme();
    }

    /**
     * Toggle between the default (no-contrast) and the configured contrast scheme.
     *
     * This method switches the contrast mode when only one contrast scheme is registered.
     * If multiple contrast schemes exist, it logs a warning and requires using
     * `activateContrastScheme()` instead. The method updates the `<body>` element’s
     * CSS class, refreshes the visual state of the contrast button, and notifies
     * the server of the current contrast mode via a POST event.
     *
     * @async
     * @returns {Promise<void>}
     */
    async switchContrastScheme() {
        if (this.#contrasts.length > 1) {
            console.log('Impossible to switch contrast scheme because multiple contrast schemes are set! ' +
                'Use activateContrastScheme() instead.');
        }

        if (this.#activated_contrast === '') {
            this.#activated_contrast = this.#contrasts[0];
            document.body.classList.add(this.#contrasts[0]);
        } else {
            this.#activated_contrast = '';
            document.body.classList.remove(this.#contrasts[0]);
        }

        this.#updateButtonState('btn-contrast');
        await this.postEvents({accessibility_contrast: this.#activated_contrast});
    }

    // -----------------------------------------------------------------------

    /**
     * DEPRECATED.
     * @param {string} contrast_scheme - Name of the contrast scheme to activate.
     * @returns {Promise<void>}
     */
    async activate_contrast_scheme(contrast_scheme) {
        await this.activateContrastScheme(contrast_scheme);
    }

    /**
     * Activate a specific contrast scheme on the current page.
     *
     * This method applies or removes the given contrast mode by updating the `<body>`
     * element’s class and synchronizes the resulting accessibility state with the
     * server through a POST event. If the provided scheme is unknown, a warning is logged.
     *
     * @async
     * @param {string} contrastScheme - The name of the contrast scheme to apply.
     *                                  An empty value disables contrast mode.
     * @returns {Promise<void>}
     */
    async activateContrastScheme(contrastScheme) {
        if (contrastScheme === '' || this.#contrasts.includes(contrastScheme)) {
            if (this.#activated_contrast !== '') {
                document.body.classList.remove(this.#activated_contrast);
            }

            if (contrastScheme !== '') {
                document.body.classList.add(contrastScheme);
            }

            this.#activated_contrast = contrastScheme;
            const response = await this.postEvents({accessibility_contrast: this.#activated_contrast});
        } else {
            console.log('Unknown given contrast scheme: ' + contrastScheme);
        }
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
     * @param {boolean} openInNewTab - True to open the destination in a new tab. False to navigate in place.
     * @returns {void}
     */
    goToLink(element, openInNewTab = false) {
        const rawHref = element.getAttribute('href');
        if (rawHref === null || rawHref === '') {
            return;
        }
        const url = new URL(element.href, window.location.href);

        // Determine whether accessibility parameters must be propagated.
        // They are added when:
        //   - running from localhost (development server), or
        //   - navigating within the same host.
        let targetUrl;

        if (window.location.protocol !== 'file:' && (window.location.hostname === 'localhost' || url.host === window.location.host)) {
            targetUrl = this.setUrlWithParameters(url.href);
        } else {
            targetUrl = url.href;
        }

        // Open either in a new tab or in the current page.
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
     * This method constructs a new URL that includes GET parameters reflecting
     * the current accessibility state. If a parameter is inactive (empty), it is
     * removed from the query string. External links should not be processed by
     * this method.
     *
     * @param {string} url - The URL to modify.
     * @returns {string} The updated URL containing accessibility parameters.
     */
    setUrlWithParameters(url) {
        if (url === null || url === '') {
            return '';
        }
        const customUrl = new URL(url, window.location.origin);

        if (this.#activated_color !== '') {
            customUrl.searchParams.set(AccessibilityManager.COLOR_PARAMETER_NAME, this.#activated_color);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.COLOR_PARAMETER_NAME);
        }

        if (this.#activated_contrast !== '') {
            customUrl.searchParams.set(AccessibilityManager.CONTRAST_PARAMETER_NAME, this.#activated_contrast);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.CONTRAST_PARAMETER_NAME);
        }

        return customUrl.href;
    }

    // -----------------------------------------------------------------------
    // PRIVATE METHODS
    // -----------------------------------------------------------------------

    /**
     * Load and apply accessibility classes from the current URL.
     *
     * This private asynchronous method reads `wexa_color` and `wexa_contrast`
     * parameters from the query string and applies the corresponding CSS classes
     * to the `<body>` element. It updates the internal state of the manager and,
     * if valid parameters were found, sends a single POST event to the server to
     * synchronize accessibility settings (color and contrast).
     *
     * This function is automatically executed on page load to restore the user's
     * accessibility preferences and ensure visual consistency across sessions.
     *
     * @private
     * @async
     * @returns {Promise<void>}
     */
    async #loadBodyClasses() {
        const params = new URLSearchParams(window.location.search);
        const events = {};

        // manage color scheme
        if (params.has(AccessibilityManager.COLOR_PARAMETER_NAME)) {
            const color_parameter = params.get(AccessibilityManager.COLOR_PARAMETER_NAME).toLowerCase();

            if (this.#colors.includes(color_parameter)) {
                this.#activated_color = color_parameter;
                document.body.classList.add(color_parameter);
                events.accessibility_color = this.#activated_color
            } else {
                console.log(AccessibilityManager.COLOR_PARAMETER_NAME + " get parameter unknown : " + color_parameter);
            }
        }

        // manage contrast scheme
        if (params.has(AccessibilityManager.CONTRAST_PARAMETER_NAME)) {
            const contrast_param = params.get(AccessibilityManager.CONTRAST_PARAMETER_NAME).toLowerCase();

            if (this.#contrasts.includes(contrast_param)) {
                this.#activated_contrast = contrast_param;
                document.body.classList.add(contrast_param);
                events.accessibility_contrast = this.#activated_contrast
            } else {
                console.log(AccessibilityManager.CONTRAST_PARAMETER_NAME + " get parameter unknown : " + contrast_param);
            }
        }

        // Inform the server in case of change
        if (Object.keys(events).length > 0) {
            await this.postEvents(events);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Custom the click event of all 'a' html element to call the goToLink function.
     */
    #setAllLinksCustom() {
        let link_elements = Array.from(document.querySelectorAll("a"));
        link_elements = link_elements.filter(el => el.href !== null && el.href !== '');

        link_elements.forEach(element => {
            element.addEventListener("click", event => {
                event.preventDefault();
                this.goToLink(element, element.target === '_blank');
            });
        });
    }

    // -----------------------------------------------------------------------

    /**
     * Customize the main form submission to preserve accessibility parameters.
     *
     * This private method attaches a click listener to the first submit button
     * found in the document. When triggered, it rewrites the form’s `action`
     * attribute using `setUrlWithParameters()` so that the current color and
     * contrast schemes remain applied after submission.
     *
     * This behavior ensures continuity of the accessibility context between pages
     * without requiring any manual script injection.
     *
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
     * Update the visual pressed state of a specific accessibility button.
     * @private
     * @param {string} buttonId - 'btn-contrast' or 'btn-theme'.
     */
    #updateButtonState(buttonId) {
        const btn = document.getElementById(buttonId);
        if (btn === null) { console.error(`Button not found: ${buttonId}.`); return; }

        let pressed = false;
        if (buttonId === 'btn-contrast') { pressed = this.#activated_contrast !== ''; }
        else if (buttonId === 'btn-theme') { pressed = this.#activated_color !== ''; }
        else { console.error(`Unknown button id: ${buttonId}.`); return; }

        btn.setAttribute('aria-pressed', String(pressed));
    }

}
