import { WexaLogger } from '../logger.js';
import { DialogManager } from '../dialog.js';
import { RequestManager } from './request.js';
/**
_This file is part of Whakerexa: https://whakerexa.sourceforge.io

-------------------------------------------------------------------------


██╗    ██╗██╗  ██╗ █████╗ ██╗  ██╗███████╗██████╗ ███████╗██╗  ██╗ █████╗
██║    ██║██║  ██║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗
██║ █╗ ██║███████║███████║█████╔╝ █████╗  ██████╔╝█████╗   ╚███╔╝ ███████║
██║███╗██║██╔══██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██╗██╔══╝   ██╔██╗ ██╔══██║
╚███╔███╔╝██║  ██║██║  ██║██║  ██╗███████╗██║  ██║███████╗██╔╝ ██╗██║  ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝


-------------------------------------------------------------------------

Copyright (C) 2024-2025 Brigitte Bigi, CNRS
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

 --------------------------------------------------------------------------

 * BaseManager class serves as a foundation for managing HTTP requests
 * and handling responses. It encapsulates common functionality for derived
 * classes, including managing a request manager instance and URI extraction
 * from the current window location.
 *
 * This class provides methods to display action results and error messages
 * in a user-friendly way, either through a <dialog> element or a browser
 * alert, facilitating consistent error handling across different components
 * that extend this base class.
 *
 * Usage example:
 *  class DerivedManager extends BaseManager {
 *      ...
 *  }
 *  const manager = new DerivedManager();
 *
 */

'use strict';

export class BaseManager {

    // ----------------------------------------------------------------------
    // Private members shared by all classes
    // ----------------------------------------------------------------------

    // An instance of the RequestManager class responsible for managing HTTP requests.
    _requestManager;
    // A string representing the current URL path, extracted from the window location.
    _uri;

    // ----------------------------------------------------------------------
    // Constructor
    // ----------------------------------------------------------------------

    constructor() {
        this._requestManager = new RequestManager();
        let url = new URL(window.location.href);
        this._uri = url.pathname.substring(1);
        this._dialog = new DialogManager();
    }

    // ----------------------------------------------------------------------

    /**
     * Display an error or info message, and/or reloads the page.
     *
     * Handles the result of an action by checking the status of the request. If the
     * request was unsuccessful (status code not 200), an error message is displayed.
     * Otherwise, an optional info message is shown. If `reload` is set to true, the page
     * is reloaded after displaying the message.
     * The messages are displayed in a <dialog> element if available, or in an alert box otherwise.
     *
     * HTML Requirement:
     *  - A <dialog> element with id="error_dialog" to display error messages.
     *  - A <dialog> element with id="info_dialog" to display info messages.
     *
     * @param {string} [error="No details"] - The error message to display if a request fails.
     * @param {string} [info=""] - An optional info message to display upon success.
     * @param {boolean} [reload=true] - Whether to reload the page if no error occurred.
     *
     * @returns {void}
     *
     */
    _showActionResult(error = "", info = "", reload = true) {
        if (this._requestManager.status !== 200) {
            WexaLogger.error(`HTTP error ${this._requestManager.status}: ${error}`);
            this._showDialog('error_dialog', `Erreur ${this._requestManager.status} : ${error}`);
        } else {
            if (info) {
                WexaLogger.info(info);
                this._showDialog('info_dialog', info);
            }
            if (reload) {
                window.location.reload();
            }
        }
    }

    // ----------------------------------------------------------------------

    /**
    * Submit a temporary hidden form using HTTP POST.
    *
    * This method programmatically creates a `<form>` element containing a single
    * hidden `<input>` field, posts it to the current page URI, and relies on the
    * browser to handle the HTTP navigation and render the new page. It is mainly
    * used for actions that require a full page reload.
    *
    * @param {string} inputName - Name attribute of the hidden input field.
    * @param {string} inputValue - Value to assign to the hidden input field.
    * @returns {void}
    */
    submitForm(inputName, inputValue) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.style.display = 'none';

            const input = document.createElement('input');
            input.name = inputName;
            input.value = inputValue;
            input.type = 'hidden';
            form.appendChild(input);

            document.body.appendChild(form);
            form.submit();

            // Clean the DOM
            document.body.removeChild(form);
    }

    // ----------------------------------------------------------------------

    /**
    * Send an asynchronous POST request to the server and return its response.
    *
    * This method sends event data to the server using the internal
    * RequestManager instance. If the server returns an error, it displays
    * the corresponding message; otherwise, it returns the parsed response.
    *
    * @async
    * @param {Object} events - Key/value pairs describing the events to send.
    * @returns {Object|undefined} The server response if successful, or
    *                             undefined if an error occurred.
    */
    async postEvents(events) {
        let response;
        let respError= "";
        let respInfo = "";

        try {
            response = await this._requestManager.send_post_request(
                events,
                'application/json',
                this._uri
            );
            WexaLogger.debug(`HTTP status ${this._requestManager.status}`);
            // If there's a message in the response
            respError = response.error || "";
            respInfo = response.info || "";

        } catch (error) {
            // Do not handle any request or network error: it's probably a standard server, not a WhakerPy one!
            // respError = error.toString();
            // No backend available: ignore silently
            return;
        }

        // Server replied: process normally
        if (respError || respInfo) {
            this._showActionResult(respError, '', true);
            return;
        }

        // No server response: ignore silently
        if (!response) {
            return;
        }

        // Return the response if no message sent
        return response;
    }

    // ----------------------------------------------------------------------

    /**
     * Display a message in a <dialog> element if it exists, or falls back to an alert.
     *
     * This function searches for a <dialog> element by its ID. If found, it inserts the
     * provided message inside the dialog and opens it. If the dialog is not found, it
     * displays the message using a browser alert.
     *
     * @param {string} dialogId - The ID of the <dialog> element to display the message in.
     * @param {string} message - The message to display in the dialog or alert.
     *
     * @returns {void}
     *
     */
    _showDialog = (dialogId, message) => {
        let dlg = document.getElementById(dialogId);
        if (dlg != null) {
            dlg.innerHTML = `<p>${message}</p>`;
            this._dialog.open(dialogId);
        } else {
            alert(message);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Hide a <dialog> element if it exists.
     *
     * This function searches for a <dialog> element by its ID. If found, it deletes the
     * existing message inside the dialog and closes it.
     *
     * @param {string} dialogId - The ID of the <dialog> element to display the message in.
     *
     * @returns {void}
     *
     */
    _hideDialog = (dialogId) => {
        let dlg = document.getElementById(dialogId);
        if (dlg != null) {
            dlg.innerHTML = ``;
            this._dialog.close(dialogId);
        } else {
            WexaLogger.warn(`No such dialog ${dialogId}`);
        }
    }
}
