const wexa_statics_js = window.WEXA_JS_PATH;
const wexa_log_level = window.WEXA_LOG_LEVEL;
const { WexaLogger } = await import(`${wexa_statics_js}/logger.js`);
WexaLogger.setLogLevel(wexa_log_level);
const { RequestManager } = await import(`${wexa_statics_js}/transport/request.js`);

/**
 * :filename: sppas.ui.swapp.statics.js.trace_manager.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: JS for the page journal.html
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
// Class: TraceManager. Controls the page journal.html
// --------------------------------------------------------------------------

/**
 * This class sends the heartbeat of *journal.html*.
 *
 * The page is the single tab displaying the traces: a periodic POST tells
 * the server that this tab is open. When the heartbeat stops, the server
 * knows the tab was closed and the Dashboard invites the user to re-open
 * it. A failed request is only logged: the server may simply be shutting
 * down.
 *
 * handleTraceManagerOnLoad() has to be invoked **after** the DOM is loaded.
 *
 */
export default class TraceManager {

    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------

    constructor() {
        // Milliseconds between two heartbeats.
        this.heartbeatInterval = 15000;
        this.requestManager = new RequestManager();
    }

    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------

    /**
     * Start the heartbeat once the DOM content is loaded.
     *
     * This method must be called after the page structure is available.
     *
     * @returns {void}
     */
    handleTraceManagerOnLoad() {
        WexaLogger.debug('Start the trace heartbeat');
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.startHeartbeat());
        } else {
            this.startHeartbeat();
        }
    }

    // ------------------------------------------------------------------------

    /**
     * Send an immediate heartbeat, then one every heartbeatInterval.
     *
     * @returns {void}
     */
    startHeartbeat() {
        this.sendHeartbeat();
        setInterval(() => this.sendHeartbeat(), this.heartbeatInterval);
    }

    // ------------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------------

    /**
     * Send one heartbeat to the server.
     *
     * @private
     * @async
     * @returns {Promise<void>} Resolves when the heartbeat has been sent,
     * or when its failure has been logged.
     */
    async sendHeartbeat() {
        const pageUri = window.location.pathname.substring(1);
        try {
            await this.requestManager.send_post_request(
                {trace_heartbeat: true}, "application/json", pageUri);
        } catch (error) {
            WexaLogger.debug(`TraceManager: heartbeat not sent: ${error}`);
        }
    }
}
