import { WexaLogger } from './logger.js';
import { BaseManager } from './transport/base_manager.js';
/**
 * :filename: wexa_statics.js.progressbar.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Generic progress bar class for Whakerexa applications.
 *
 * -------------------------------------------------------------------------
 *
 * This file is part of Whakerexa: https://whakerexa.sf.net/
 *
 * Copyright (C) 2023-2025 Brigitte Bigi, CNRS
 * Laboratoire Parole et Langage, Aix-en-Provence, France
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 * This banner notice must not be removed.
 *
 * -------------------------------------------------------------------------
 */

/**
 * Represent a generic, reusable progress bar component for Whakerexa.
 *
 * This class implements a visual progress bar that can operate in two modes:
 * 1. **Managed mode** – The application provides explicit callbacks for update
 *    and completion events. This mode is suitable for internal tasks where the
 *    progress values are computed locally.
 * 2. **Autonomous mode** – The component automatically polls a remote server
 *    through a provided `RequestManager` and `targetUrl`. It updates its display
 *    based on server responses until completion.
 *
 * The `ProgressBar` class is framework-agnostic. It handles DOM rendering,
 * timing, and error management but never embeds application-specific logic.
 * Each instance maintains its own update interval and target DOM elements,
 * allowing multiple progress bars to coexist within the same page.
 *
 * @example
 * // Managed mode
 * const bar = new ProgressBar({
 *   updateCallback: async () => ({ percent: 60, text: 'Processing...', header: 'Task running' }),
 *   completeCallback: () => console.log('Completed!')
 * });
 * bar.start();
 *
 * @example
 * // Autonomous mode
 * const bar = new ProgressBar({
 *   requestManager: req,
 *   targetUrl: '/setup.html',
 *   intervalMs: 1000
 * });
 * bar.start();
 *
 */

export class ProgressBar extends BaseManager {

    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------

    /**
     * Create a ProgressBar instance.
     *
     * @param {Object} [options] - Optional parameters.
     * @param {Function} [options.updateCallback] - Called at each refresh to fetch progress data.
     * @param {Function} [options.completeCallback] - Called when progress reaches 100%.
     * @param {Object} [options.requestManager] - Optional RequestManager instance.
     * @param {string} [options.targetUrl] - URL used when in autonomous mode.
     * @param {number} [options.intervalMs=1500] - Refresh interval in milliseconds.
     * @param {Object} [options.domIds] - Custom DOM element IDs.
     */
    constructor(options = {}) {
        super();
        this._updateCallback = options.updateCallback || null;
        this._completeCallback = options.completeCallback || null;
        this._requestManager = options.requestManager || null;
        this._targetUrl = options.targetUrl || '';
        this._intervalMs = options.intervalMs || 1500;
        this._domIds = { percent: '', text: '', header: '' };
        this._domIds = options.domIds || {
            percent: 'percent_progress',
            text: 'progress_text',
            header: 'progress_header'
        };
        this._intervalId = null;
        this._percent = 0;
        this._text = '';
        this._header = '';
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /**
    * Start the periodic update loop for the progress bar.
    *
    * This method clears any existing interval, then repeatedly fetches
    * progress data from the server using the defined RequestManager.
    * It updates the DOM until the installation is completed or an HTTP 200
    * status is received, in which case the completion handler is triggered.
    *
    * @returns {void}
    */
    start() {
        this.stop();
        WexaLogger.debug("Progress start:")

        this._intervalId = setInterval(async () => {
            const response = await this._fetchProgressData();
            if (response === null) {
                WexaLogger.warn(" == Empty response == ")
                await this._fetchComplete();
                return;
            }

            // Stop updates when installation is completed.
            if ((this._requestManager && this._requestManager.status === 200) || response.status === 200) {
                WexaLogger.debug(" == STATUS 200 RECEIVED ==")
                await this._fetchComplete();
                return
            }

            // The progress is updated
            this._updateDisplay(response.percent, response.text, response.header);
            if (this._percent >= 100) {
                WexaLogger.debug(" == PERCENT COMPLETED ==")
                await this._fetchComplete();
            }

        }, this._intervalMs);
    }

    // -----------------------------------------------------------------------

    /**
    * Stop the progress update loop.
    *
    * This method cancels the active interval used to fetch progress
    * updates and resets its identifier. It ensures that no further
    * requests are sent once the progress monitoring has ended.
    *
    * @returns {void}
    */
    stop() {
        WexaLogger.debug("Progress stop:")
        if (this._intervalId !== null) {
            clearInterval(this._intervalId);
            this._intervalId = null;
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Update displayed values manually (for managed mode).
     *
     * @param {number} percent - Progress percentage.
     * @param {string} text - Status message.
     * @param {string} header - Header message.
     */
    update(percent, text, header) {
        WexaLogger.debug("Progress update:")
        this._updateDisplay(percent, text, header);
    }

    // -----------------------------------------------------------------------

    /**
     * Assign or change the RequestManager used in autonomous mode.
     *
     * @param {Object} requestManager - Instance of RequestManager.
     * @param {string} targetUrl - Target URL for POST requests.
     */
    setRequestManager(requestManager, targetUrl) {
        this._requestManager = requestManager;
        this._targetUrl = targetUrl;
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    /**
    * Handle the completion of the installation process.
    *
    * This method stops the update loop and triggers either the registered
    * completion callback or, if none is defined, submits a 'complete' event
    * to the server to finalize the installation phase.
    *
    * @async
    * @returns {Promise<void>}
    */
    async _fetchComplete() {
        this.stop();
        if (this._completeCallback !== null) {
            this._completeCallback();
        } else {
            this.submitForm('event_bake', 'complete');
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Internal function to fetch progress data.
     *
     * It uses the updateCallback if defined (managed mode),
     * otherwise sends a POST request with event_name=update.
     *
     * @returns {Promise<Object|null>} Progress data or null if none available.
     * @private
     */
    async _fetchProgressData() {
        if (this._updateCallback !== null) {
            return await this._updateCallback();
        }
        if (this._requestManager === null || this._targetUrl === '') {
            WexaLogger.error('ProgressBar: No update callback or RequestManager available.');
            return null;
        }

        const response = await this.postEvents({event_name: 'update'});
        return response
    }

    // -----------------------------------------------------------------------

    /**
     * Internal function to update internal state and re-render DOM nodes.
     *
     * @param {number} percent - Progress percentage.
     * @param {string} text - Status message.
     * @param {string} header - Header message.
     * @private
     */
    _updateDisplay(percent, text, header) {
        if (typeof percent === 'number') {
            this._percent = percent;
        }
        if (typeof text === 'string') {
            this._text = text;
        }
        if (typeof header === 'string') {
            this._header = header;
        }
        this._render();
    }

    // -----------------------------------------------------------------------

    /**
    * Render the current progress state to the DOM.
    *
    * This method updates the visual elements of the progress bar
    * (`<progress>`, header, and text) according to the current values
    * of percent, text, and header stored in the instance.
    *
    * @returns {void}
    */
    _render() {
        const percentEl = document.getElementById(this._domIds.percent);
        const textEl = document.getElementById(this._domIds.text);
        const headerEl = document.getElementById(this._domIds.header);

        if (percentEl !== null) {
            percentEl.value = this._percent;
        }
        if (textEl !== null) {
            textEl.textContent = this._text;
        }
        if (headerEl !== null) {
            headerEl.textContent = this._header;
        }
    }
}
