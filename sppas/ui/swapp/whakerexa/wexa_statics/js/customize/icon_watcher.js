/**
 * :filename: statics.js.customize.icon_watcher.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Says when a demand comes into view. The only one that reads it.
 *
 *  -------------------------------------------------------------------------
 *
 *  This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa
 *
 *  Copyright (C) 2023-2026 Brigitte Bigi, CNRS
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

'use strict';

/**
 * Says when a demand comes into view.
 *
 * A content is loaded only when the reader is about to see it: a set of fifty
 * drawings costs the five that are on the screen. It is the only class that
 * reads the rendering, and it decides nothing.
 *
 * A browser that does not answer for what is in view is answered for: every
 * demand is announced at once, which loads more than needed and shows
 * everything, rather than showing nothing.
 */
export class IconWatcher {

    /** @type {IntersectionObserver|null} */
    #observer = null;

    /** @type {Map<HTMLElement, IconDemand>} */
    #watched = new Map();

    /** @type {function|null} */
    #onView = null;

    /**
     * Watch a set of demands.
     *
     * @param {IconDemand[]} demands - What to watch.
     * @param {function} onView - Called with a demand when it comes into view.
     * @returns {void}
     */
    watch(demands, onView) {
        this.#onView = typeof onView === 'function' ? onView : null;

        if (this.#onView === null || Array.isArray(demands) === false) {
            return;
        }

        if (typeof IntersectionObserver === 'undefined') {
            demands.forEach(demand => this.#onView(demand));
            return;
        }

        if (this.#observer === null) {
            this.#observer = new IntersectionObserver(
                entries => this.#seen(entries),
                { rootMargin: '200px' });
        }

        for (const demand of demands) {
            this.#watched.set(demand.element, demand);
            this.#observer.observe(demand.element);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Stop watching everything.
     *
     * @returns {void}
     */
    stop() {
        if (this.#observer !== null) {
            this.#observer.disconnect();
        }
        this.#watched.clear();
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Announce the demands that came into view, and stop watching them.
     *
     * @private
     * @param {IntersectionObserverEntry[]} entries
     * @returns {void}
     */
    #seen(entries) {
        for (const entry of entries) {
            if (entry.isIntersecting === false) {
                continue;
            }

            const demand = this.#watched.get(entry.target);
            if (demand === undefined) {
                continue;
            }

            this.#observer.unobserve(entry.target);
            this.#watched.delete(entry.target);
            this.#onView(demand);
        }
    }
}
