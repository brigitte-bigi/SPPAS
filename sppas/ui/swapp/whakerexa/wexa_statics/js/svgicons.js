/**
 * :filename: wexa_statics.js.svgicons.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Centralised SVG icon loader for Whakerexa.
 *
 * -------------------------------------------------------------------------
 *
 * This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa
 *
 * Copyright (C) 2023-2026 Brigitte Bigi, CNRS
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

import { WexaLogger } from './logger.js';

/**
 * Centralised SVG icon loader for Whakerexa.
 *
 * This static class fetches SVG files from the `icons/mono-svg/` directory
 * and caches them in memory. Any code that needs an icon — buttons, navs,
 * dynamic components — calls `SVGIconsManager.get('name')` and receives the
 * raw SVG markup, ready to be set as `innerHTML`.
 *
 * Two usage modes are supported transparently:
 *  - **Module mode** (http/https): icons are fetched on demand via `fetch()`.
 *    Call `SVGIconsManager.init(import.meta.url)` once at init time to resolve
 *    the base path relative to this module.
 *  - **Bundle mode** (file://): icons are pre-registered at build time via
 *    `SVGIconsManager.register(name, svgContent)`. `get()` returns cached
 *    content immediately without any network request.
 *
 * @example
 * // Module mode — wexa.js calls init() once:
 * SVGIconsManager.init(import.meta.url);
 *
 * // Anywhere in the codebase:
 * const svg = await SVGIconsManager.get('contrast');
 * button.innerHTML = svg;
 *
 * @example
 * // Bundle mode — build script pre-registers icons:
 * SVGIconsManager.register('contrast', '<svg ...>...</svg>');
 * SVGIconsManager.register('color',    '<svg ...>...</svg>');
 */
export class SVGIconsManager {

    // -----------------------------------------------------------------------
    // PRIVATE FIELDS
    // -----------------------------------------------------------------------

    /** @type {Map<string, string>} In-memory cache: icon name → SVG markup. */
    static #cache = new Map();

    /** @type {string|null} Base URL for resolving icon file paths. */
    static #base = null;

    // -----------------------------------------------------------------------
    // PUBLIC STATIC METHODS
    // -----------------------------------------------------------------------

    /**
     * Set the base URL used to resolve icon paths.
     *
     * Must be called once in module mode, before the first `get()` call.
     * Pass `import.meta.url` from the calling module so the path to
     * `icons/mono-svg/` is resolved relative to this file's location.
     *
     * @param {string} metaUrl - The `import.meta.url` of the calling module.
     * @returns {void}
     */
    static init(metaUrl) {
        const base = metaUrl !== null ? metaUrl : (document.currentScript && document.currentScript.src);
        SVGIconsManager.#base = new URL('../icons/mono-svg/', base).href;
        WexaLogger.debug('SVGIconsManager: base URL set to ' + SVGIconsManager.#base);
    }

    // -----------------------------------------------------------------------

    /**
     * Pre-register an icon's SVG markup (bundle mode).
     *
     * Called by the build script to embed icons directly into the bundle.
     * A registered icon is returned immediately by `get()` without any fetch.
     *
     * @param {string} name       - Icon name, without path or extension.
     * @param {string} svgContent - Full SVG markup string.
     * @returns {void}
     */
    static register(name, svgContent) {
        SVGIconsManager.#cache.set(name, svgContent);
    }

    /**
     * Inject an icon into an element only if it does not already contain an SVG.
     *
     * @param {HTMLElement} element - Target element.
     * @param {string}      name    - Icon name passed to get().
     * @returns {Promise<void>}
     */
    static async inject(element, name) {
        if (element === null || element === undefined) {
            return;
        }
        if (element.querySelector('svg') !== null) {
            return;
        }
        element.insertAdjacentHTML('afterbegin', await SVGIconsManager.get(name));
    }

    // -----------------------------------------------------------------------

    /**
     * Return the SVG markup for the given icon name.
     *
     * Returns cached content immediately if the icon was already fetched or
     * pre-registered. Otherwise fetches `{base}{name}.svg`, caches the result,
     * and returns it. Returns an empty string on error.
     *
     * @async
     * @param {string} name - Icon name, without path or extension (e.g. `'contrast'`).
     * @returns {Promise<string>} SVG markup string, or `''` on failure.
     */
    static async get(name) {
        if (SVGIconsManager.#cache.has(name)) {
            return SVGIconsManager.#cache.get(name);
        }

        if (SVGIconsManager.#base === null) {
            WexaLogger.error('SVGIconsManager: call init() before get().');
            return '';
        }

        try {
            const response = await fetch(SVGIconsManager.#base + name + '.svg');
            if (response.ok === false) {
                WexaLogger.warn(`SVGIconsManager: icon "${name}" not found (HTTP ${response.status}).`);
                return '';
            }
            const content = await response.text();
            SVGIconsManager.#cache.set(name, content);
            return content;
        } catch (error) {
            WexaLogger.error(`SVGIconsManager: failed to fetch icon "${name}".`, error);
            return '';
        }
    }
}
