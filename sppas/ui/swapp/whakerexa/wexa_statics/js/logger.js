/**
 *  :filename: wexa_statics.js.logger.js
 *  :author: Brigitte Bigi
 *  :contact: contact@sppas.org
 *  :summary: A unified logging utility for all Whakerexa modules.
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

/**
 * Manage centralized logging for Whakerexa modules.
 *
 * This static class provides consistent, prefixed log messages across the
 * framework. It mimics Python's logging system with numeric levels from
 * 0 (silent) to 50 (critical). Only messages with a severity less than or
 * equal to the current `logLevel` are displayed.
 *
 * Levels:
 *  - 10 → Debug
 *  - 20 → Info
 *  - 30 → Warning
 *  - 40 → Error
 *  - 50 → Critical
 *
 * @example
 * WexaLogger.setLogLevel(20);
 * WexaLogger.info('Initialization complete.');
 * WexaLogger.error('Unhandled exception.', err);
 */
export class WexaLogger {

    static #logLevel = 20;

    /**
     * Get the current log level.
     *
     * @returns {number} The current log level (0–50).
     */
    static getLogLevel() {
        return this.#logLevel;
    }

    /**
     * Set the global log level for Whakerexa logging.
     *
     * @param {number} level - A value between 0 and 50.
     * @returns {void}
     */
    static setLogLevel(level) {
        if (typeof level !== 'number' || level < 0 || level > 50) {
            console.warn('[WexaWarning] Invalid log level. Must be between 0 and 50.');
            return;
        }
        this.#logLevel = level;
    }

    /**
     * Log a debug message if level <= 10.>
     *
     * @param {string} msg - Message to display.
     * @returns {void}
     */
    static debug(msg) {
        if (this.#logLevel <= 10) console.info(`[WexaDebug] ${msg}`);
    }

    /**
     * Log an informational message if level <= 20.>
     *
     * @param {string} msg - Message to display.
     * @returns {void}
     */
    static info(msg) {
        if (this.#logLevel <= 20) console.info(`[WexaInfo] ${msg}`);
    }

    /**
     * Log a warning message if level <= 30.
     *
     * @param {string} msg - Message to display.
     * @returns {void}
     */
    static warn(msg) {
        if (this.#logLevel <= 30) console.warn(`[WexaWarning] ${msg}`);
    }

    /**
     * Log an error message if level <= 40.
     *
     * @param {string} msg - Message to display.
     * @param {Error|string} [err] - Optional associated error.
     * @returns {void}
     */
    static error(msg, err) {
        if (this.#logLevel <= 40) console.error(`[WexaError] ${msg}`, err || '');
    }

    /**
     * Log a critical message whatever the level.
     *
     * @param {string} msg - Message to display.
     * @param {Error|string} [err] - Optional associated error.
     * @returns {void}
     */
    static critical(msg, err) {
        console.error(`[WexaCritical] ${msg}`, err || '');
    }
}
