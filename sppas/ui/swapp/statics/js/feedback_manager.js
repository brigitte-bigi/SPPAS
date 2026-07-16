const wexa_statics_js = window.WEXA_JS_PATH;
const wexa_log_level = window.WEXA_LOG_LEVEL;
const { WexaLogger } = await import(`${wexa_statics_js}/logger.js`);
WexaLogger.setLogLevel(wexa_log_level);

/**
 * :filename: sppas.ui.swapp.statics.js.feedback_manager.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: JS for the Feedback page
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
// Class: FeedbackManager. Controls the page feedback.html
// --------------------------------------------------------------------------

/**
 * This class orchestrates user interactions within *feedback.html*.
 *
 * The message never leaves the application by itself: the send button
 * copies the whole message (user text and technical information) into the
 * clipboard, then opens the default e-mail client with the recipient and
 * the subject. The user pastes the message and sends it from there.
 *
 * All displayed texts come from the page itself (data attributes), so the
 * internationalization stays on the server side. The messages are shown
 * in line, in the status area of the page: never in a dialog.
 *
 * handleFeedbackManagerOnLoad() has to be invoked **after** the DOM is loaded.
 *
 */
export default class FeedbackManager {

    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------

    constructor() {
        this.sendButton = null;
        this.messageInput = null;
        this.systemInfoBlock = null;
        this.statusParagraph = null;
    }

    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------

    /**
     * Register event listeners once the DOM content is loaded.
     *
     * This method must be called after the page structure is available.
     *
     * @returns {void}
     */
    handleFeedbackManagerOnLoad() {
        WexaLogger.debug('Attach Feedback listeners');
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.attachFeedbackListeners());
        } else {
            this.attachFeedbackListeners();
        }
    }

    // ------------------------------------------------------------------------

    /**
     * Find the elements of the feedback form and attach the send action.
     *
     * @returns {void}
     */
    attachFeedbackListeners() {
        this.sendButton = document.getElementById('feedback_send_button');
        this.messageInput = document.getElementById('feedback_message');
        this.systemInfoBlock = document.getElementById('feedback_sysinfo');
        this.statusParagraph = document.getElementById('feedback_status');

        if (this.sendButton === null || this.messageInput === null ||
                this.systemInfoBlock === null || this.statusParagraph === null) {
            console.error('FeedbackManager: an element of the feedback form was not found.');
            return;
        }

        this.sendButton.addEventListener('click', () => this.#onSendActivated());
    }

    // ------------------------------------------------------------------------
    // Private
    // ------------------------------------------------------------------------

    /**
     * Copy the whole message into the clipboard, then open the e-mail client.
     *
     * The mailto URL carries the recipient and the subject only: the body
     * (user text and technical information) travels in the clipboard, so
     * pasting it never duplicates anything.
     *
     * @returns {Promise<void>}
     */
    async #onSendActivated() {
        const userText = this.messageInput.value.trim();
        if (userText.length === 0) {
            this.statusParagraph.textContent = this.sendButton.getAttribute('data-msg-empty');
            return;
        }

        const systemInfo = this.systemInfoBlock.textContent;
        const wholeMessage = userText + '\n\n' + systemInfo;

        try {
            await navigator.clipboard.writeText(wholeMessage);
            this.statusParagraph.textContent = this.sendButton.getAttribute('data-msg-copied');
        } catch (error) {
            console.error('FeedbackManager: the clipboard is not available.', error);
            this.statusParagraph.textContent = this.sendButton.getAttribute('data-msg-error');
            return;
        }

        const to = this.sendButton.getAttribute('data-to');
        const subject = this.sendButton.getAttribute('data-subject');
        window.location.href = 'mailto:' + to +
            '?subject=' + encodeURIComponent(subject);
    }
}
