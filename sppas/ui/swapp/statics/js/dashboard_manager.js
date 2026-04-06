const wexa_statics_js = window.WEXA_JS_PATH;
const wexa_log_level = window.WEXA_LOG_LEVEL;
const { WexaLogger } = await import(`${wexa_statics_js}/logger.js`);
WexaLogger.setLogLevel(wexa_log_level);
const { BaseManager } = await import(`${wexa_statics_js}/transport/base_manager.js`);

/**
 * :filename: sppas.ui.swapp.statics.js.dashboard_manager.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: JS for the Dashboard application
 *
 * .. _This file is part of SPPAS: https://sppas.org/
 * ..
 *     -------------------------------------------------------------------------
 *
 *      ######   ########   ########      ###      ######
 *     ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
 *     ##        ##     ##  ##     ##   ##   ##   ##            annotation
 *      ######   ########   ########   ##     ##   ######        and
 *           ##  ##         ##         #########        ##        analysis
 *     ##    ##  ##         ##         ##     ##  ##    ##         of speech
 *      ######   ##         ##         ##     ##   ######
 *
 *     Copyright (C) 2011-2026  Brigitte Bigi, CNRS
 *     Laboratoire Parole et Langage, Aix-en-Provence, France
 *
 *     This program is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU Affero General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU Affero General Public License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *     This banner notice must not be removed.
 *
 *     -------------------------------------------------------------------------
 */

'use strict';

// --------------------------------------------------------------------------
// Class: DashboardManager. Controls the page index.html
// --------------------------------------------------------------------------

/**
 * This class orchestrates user interactions within *index.html*. It attaches event
 * listeners to the buttons of the main container, sends corresponding asynchronous
 * requests to the server, and updates the DOM in response. It relies on BaseManager
 * for communication logic and form submission, and on WexaLogger for debug output.
 *
 * handleDashboardManagerOnLoad() has to be invoked **after** the DOM is loaded.
 *
 */
export default class DashboardManager extends BaseManager {

    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------

    constructor() {
        super();
    }

    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------

    /**
     * Register event listeners once the DOM content is loaded.
     *
     * This method must be called after the page structure is available.
     * It attaches listeners to all buttons within the main container.
     *
     * @returns {void}
     */
    handleDashboardManagerOnLoad() {
        WexaLogger.debug("Attach Dashboard listeners")
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.attachDashboardListeners());
        } else {
            this.attachDashboardListeners();
        }
    }

    // ------------------------------------------------------------------------

    /**
     * Attach click listeners to every button in the dashboard container.
     *
     * @returns {void}
     */
    attachDashboardListeners() {
        const container = document.getElementById('main-content');
        if (!container) return;

        // Redirections in any button -- with data-href
        const redirectButtons = container.querySelectorAll('#apps_section button.app-button[data-href]');
        for (const redirectButton of redirectButtons) {
            if (!(redirectButton instanceof HTMLButtonElement)) {
                continue;
            }
            redirectButton.addEventListener('click', (event) => this.#onRedirectButtonClick(event));
            redirectButton.addEventListener('keydown', (event) => this.#onRedirectButtonKeydown(event));
        }

        // Action of any button -- without data-href
        const buttons = container.querySelectorAll('button:not([data-href])');
        buttons.forEach((btn) => {
            btn.addEventListener('click', (e) => this.#handleButtonClick(e.currentTarget));
        });

        // Attach the Exit button of the menu
        const exitBtn = document.getElementById('exit-menu');
        if (exitBtn) {
            exitBtn.addEventListener('click', (e) => this.#handleButtonClick(e.currentTarget));
        }
    }

   // ----------------------------------------------------------------------

    /**
     * Open data-href (Enter/Space support) while preserving accessibility parameters.
     *
     * @param {KeyboardEvent} event
     * @returns {void}
     */
    #onRedirectButtonKeydown(event) {
        if (event.key !== 'Enter' && event.key !== ' ') {
            return;
        }
        event.preventDefault();
        this.#openRedirectFromEventTarget(event);
    }

   // ----------------------------------------------------------------------

    /**
     * Open data-href while preserving accessibility parameters.
     *
     * @param {MouseEvent} event
     * @returns {void}
     */
    #onRedirectButtonClick(event) {
        event.preventDefault();
        this.#openRedirectFromEventTarget(event);
    }

    // ----------------------------------------------------------------------

    /**
     * Extract data-href from the event target and open it in a new tab.
     *
     * @param {Event} event
     * @returns {void}
     */
    #openRedirectFromEventTarget(event) {
        const button = event.currentTarget;
        if (!(button instanceof HTMLButtonElement)) {
            return;
        }

        const href = button.getAttribute('data-href');
        if (typeof href !== 'string' || href.trim().length === 0) {
            return;
        }

        const absolute = new URL(href, window.location.href).href;
        const target = window.Wexa.accessibility.setUrlWithParameters(absolute);
        window.location.href = target;
    }

    // ----------------------------------------------------------------------
    // Buttons event dispatch
    // ----------------------------------------------------------------------

    /**
     * Central handler for all dashboard buttons.
     *
     * @param {HTMLElement} btn - The clicked button element.
     * @returns {void}
     */
    #handleButtonClick(btn) {
        switch (btn.id) {
            case 'agree_button':
                this.#sendAgreement();
                break;
            case 'sppas_button':
                this.#sendSPPASLaunch(btn);
                break;
            case 'exit-menu':
                this.#submitExitForm()
                break;
            default:
                WexaLogger.debug(`Unhandled button: ${btn.id}`);
        }
    }

    // ----------------------------------------------------------------------
    // Actions
    // ----------------------------------------------------------------------

    /**
    * Send the licence agreement event to the server and close the dialog.
    *
    * This method sends an event notifying the server that the user has accepted
    * the licence agreement. If the server responds successfully, the associated
    * dialog is visually hidden and closed using the DialogManager API to ensure
    * proper cleanup of accessibility states and focus handling. If the dialog
    * element is not found or the server does not respond, a warning or info
    * message is logged for debugging purposes.
    *
    * @private
    * @async
    * @returns {Promise<void>} Resolves when the event has been sent and the
    * dialog is closed or when an error has been logged.
    */
    async #sendAgreement() {
        const events = {'event_bake': 'handle_licence_agreement'};
        const response = await this.postEvents(events);
        if (response) {
            let dlg = document.getElementById('agreement_dialog');
            if (dlg != null) {
                dlg.classList.add("hidden-alert");
                DialogManager.close('agreement_dialog');
            } else {
                WexaLogger.warn("No such dialog with ID 'agreement_dialog'.");
            }
        } else {
            WexaLogger.info("Can't close dialog: No server response. ")
        }
    }

    // ----------------------------------------------------------------------

    async #sendSPPASLaunch(btn) {
        // Disable the button so that SPPAS can be launched only once.
        btn.setAttribute("disabled", "")
        // Send the event to the server so that it can launch the app.
        const events = {'event_bake': 'handle_start_sppas'};
        // The response is arriving when the SPPAS process ended
        const response = await this.postEvents(events);
        // Restore enabling button
        btn.removeAttribute("disabled")
        if (response) {
            WexaLogger.info("Launched & terminated SPPAS app...")
        } else {
            WexaLogger.info("Can't launch SPPAS: No server response. ")
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Trigger a clean exit by submitting a hidden POST form.
     *
     * This method allows the browser to perform a full HTTP POST navigation
     * handled entirely by the server before it stops.
     *
     * @returns {void}
     */
    #submitExitForm() {
        this.submitForm('event_bake', 'close');
    }

}
