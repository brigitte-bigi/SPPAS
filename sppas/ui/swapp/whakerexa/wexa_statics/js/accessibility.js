/**
:filename: statics.js.accessibility.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to manage the color and contrast scheme of the body.

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


class AccessibilityScheme {

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
     * Instantiate all properties with default color and contrast scheme.
     * Also add onload events to set the body classes and custom the 'a link'.
     */
    constructor() {
        this.#colors = ["dark"];
        this.#activated_color = "";
        this.#contrasts = ["contrast"];
        this.#activated_contrast = "";

        // add onload events
        OnLoadManager.addLoadFunction(this.#load_body_classes.bind(this));
        OnLoadManager.addLoadFunction(this.#set_all_links_custom.bind(this));
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
    get color_schemes() {
        return this.#colors;
    }

    // -----------------------------------------------------------------------

    /**
     * Get the current color scheme activated.
     * If this value is an empty string, then it's the default (light) mode which is activated.
     *
     * @returns {string}
     */
    get activated_color_scheme() {
        return this.#activated_color;
    }

    // -----------------------------------------------------------------------

    /**
     * Get all contrast schemes register in the class.
     * By default, contains only 'contrast'.
     *
     * @returns {Array[string]}
     */
    get contrast_schemes() {
        return this.#contrasts;
    }

    // -----------------------------------------------------------------------

    /**
     * Get the current contrast scheme activated.
     * If this value is an empty string, then it's the default (no-contrast) mode which is activated.
     *
     * @returns {string}
     */
    get activated_contrast_scheme() {
        return this.#activated_contrast;
    }


    // -----------------------------------------------------------------------
    // SETTERS
    // -----------------------------------------------------------------------

    /**
     * Append a new color scheme in the list.
     * Use this method if you build a custom color scheme, and you want to use it in your webapp.
     * The color scheme has to have a css class on the same name which override color css variables that the body can use.
     *
     * @param color_scheme The name of the new color scheme (css class name)
     */
    add_color_scheme(color_scheme) {
        if (typeof color_scheme === "string") {
            this.#colors.push(color_scheme);
        } else {
            console.log("The 'color_scheme' parameter has to be a string and not a : " + typeof color_scheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Remove a color scheme presents in the list.
     *
     * @param color_scheme The name of the color scheme to delete
     */
    remove_color_scheme(color_scheme) {
        if (typeof color_scheme !== "string") {
            console.log("The 'color_scheme' parameter has to be a string and not a : " + typeof color_scheme);
        }

        // get the index of the element to delete
        const color_index = this.#colors.indexOf(color_scheme);

        // check if the element was found
        if (color_index === -1) {
            console.log("The color scheme : '" + color_scheme + "' doesn't exist !");
        } else {
            this.#colors.splice(color_index, 1);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Append a new contrast scheme in the list.
     * Use this method if you build a custom contrast scheme, and you want to use it in your webapp.
     * The contrast scheme has to have a css class on the same name which override contrast css variable that the body can use.
     *
     * @param contrast_scheme The name of the contrast scheme
     */
    add_contrast_scheme(contrast_scheme) {
        if (typeof contrast_scheme === "string") {
            this.#contrasts.push(contrast_scheme);
        } else {
            console.log("The 'contrast_scheme' parameter has to be a string and not a : " + typeof contrast_scheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Remove a contrast scheme presents in the list.
     *
     * @param contrast_scheme The name of the contrast scheme to delete
     */
    remove_contrast_scheme(contrast_scheme) {
        if (typeof contrast_scheme !== "string") {
            console.log("The 'contrast_scheme' parameter has to be a string and not a : " + typeof contrast_scheme);
        }

        // get the index of the element to delete
        const contrast_index = this.#contrasts.indexOf(contrast_scheme);

        // check if the element was found
        if (contrast_index === -1) {
            console.log("The contrast scheme : '" + contrast_scheme + "' doesn't exist !");
        } else {
            this.#contrasts.splice(contrast_index, 1);
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
     * Switch the color scheme from nothing (light) to color scheme and unversed.
     * You can only call this method if you have one color scheme set (only the dark scheme or custom scheme, and you remove the dark scheme).
     * Otherwise, use the activate_color_scheme() method to set a specific color scheme.
     */
    switch_color_scheme() {
        if (this.#colors.length > 1) {
            console.log("Impossible to switch color scheme because multiple color schemes has set !" +
                "You have to use the activate_color_scheme() method !");
        }

        if (this.#activated_color === "") {
            this.#activated_color = this.#colors[0];
            document.body.classList.add(this.#colors[0]);

        } else {
            this.#activated_color = "";
            document.body.classList.remove(this.#colors[0]);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Set the current color scheme that the client has to use.
     *
     * @param color_scheme The name of the color scheme
     */
    activate_color_scheme(color_scheme) {
        if (color_scheme === "" || this.#colors.includes(color_scheme)) {
            if (this.#activated_color !== "") {
                document.body.classList.remove(this.#activated_color);
            }

            if (color_scheme !== "") {
                document.body.classList.add(color_scheme);
            }

            this.#activated_color = color_scheme;
        } else {
            console.log("Unknown given color scheme : " + color_scheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Switch the contrast scheme from nothing (no-contrast) to contrast scheme and unversed.
     * You can only call this method if you have one contrast scheme set (only the contrast scheme or custom scheme, and you remove the contrast scheme).
     * Otherwise, use the activate_contrast_scheme() method to set a specific contrast scheme.
     */
    switch_contrast_scheme() {
        if (this.#contrasts.length > 1) {
            console.log("Impossible to switch contrast scheme because multiple contrast schemes has set !" +
                "You have to use the activate_contrast_scheme() method !");
        }

        if (this.#activated_contrast === "") {
            this.#activated_contrast = this.#contrasts[0];
            document.body.classList.add(this.#contrasts[0]);

        } else {
            this.#activated_contrast = "";
            document.body.classList.remove(this.#contrasts[0]);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Set the current contrast scheme that the client has to use.
     *
     * @param contrast_scheme The name of the contrast scheme
     */
    activate_contrast_scheme(contrast_scheme) {
        if (contrast_scheme === "" || this.#contrasts.includes(contrast_scheme)) {
            if (this.#activated_contrast !== "") {
                document.body.classList.remove(this.#activated_contrast);
            }

            if (contrast_scheme !== "") {
                document.body.classList.add(contrast_scheme);
            }

            this.#activated_contrast = contrast_scheme;
        } else {
            console.log("Unknown given contrast scheme : " + contrast_scheme);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Customs the link before redirect the client.
     *
     * If the link target an external server, nothing changes.
     * If the link target a page of our server, apply get parameters for the color and contrast scheme.
     *
     * @param element The 'a' html element which contains the url to custom
     */
    go_to_link(element) {
        // check if it's an external link to another server
        if (element.host !== window.location.host) {
            document.location.href = element.href;
            return;
        }

        // set the new url to redirect the client
        document.location.href = this.set_url_with_parameters(element.href);
    }

    // -----------------------------------------------------------------------

    set_url_with_parameters(url) {
        let custom_url = new URL(url);

        // it's an internal link, we add get parameters for the color and contrast scheme
        if (this.#activated_color !== "") {
            custom_url.searchParams.set(AccessibilityScheme.COLOR_PARAMETER_NAME, this.#activated_color);
        } else {
            custom_url.searchParams.delete(AccessibilityScheme.COLOR_PARAMETER_NAME);
        }

        if (this.#activated_contrast !== "") {
            custom_url.searchParams.set(AccessibilityScheme.CONTRAST_PARAMETER_NAME, this.#activated_contrast);
        } else {
            custom_url.searchParams.delete(AccessibilityScheme.CONTRAST_PARAMETER_NAME);
        }

        return custom_url.href;
    }


    // -----------------------------------------------------------------------
    // PRIVATE METHODS
    // -----------------------------------------------------------------------

    /**
     * Loads body css classes to set the color and contrast scheme of the webapp.
     * This function has to be called in the 'onload' property of the body element.
     *
     * By default, the body doesn't have special classes added (equivalent of 'light scheme' and 'no contrast')
     */
    #load_body_classes() {
        const params = new URLSearchParams(window.location.search);

        // manage color scheme
        if (params.has(AccessibilityScheme.COLOR_PARAMETER_NAME)) {
            const color_parameter = params.get(AccessibilityScheme.COLOR_PARAMETER_NAME).toLowerCase();

            if (this.#colors.includes(color_parameter)) {
                this.#activated_color = color_parameter;
                document.body.classList.add(color_parameter);

            } else {
                console.log(AccessibilityScheme.COLOR_PARAMETER_NAME + " get parameter unknown : " + color_parameter);
            }
        }

        // manage contrast scheme
        if (params.has(AccessibilityScheme.CONTRAST_PARAMETER_NAME)) {
            const contrast_param = params.get(AccessibilityScheme.CONTRAST_PARAMETER_NAME).toLowerCase();

            if (this.#contrasts.includes(contrast_param)) {
                this.#activated_contrast = contrast_param;
                document.body.classList.add(contrast_param);

            } else {
                console.log(AccessibilityScheme.CONTRAST_PARAMETER_NAME + " get parameter unknown : " + contrast_param);
            }
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Custom the click event of all 'a' html element to call the goToLink function.
     */
    #set_all_links_custom() {
        let link_elements = Array.from(document.querySelectorAll("a"));

        link_elements.forEach(element => {
            element.addEventListener("click", event => {
                event.preventDefault();
                this.go_to_link(element);
            });
        });
    }
}



// -----------------------------------------------------------------------

// instantiate the AccessibilityScheme to set properties and use it after in other scripts
let accessibility_manager = new AccessibilityScheme();
