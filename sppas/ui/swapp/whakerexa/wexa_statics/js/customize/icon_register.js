/**
 * :filename: statics.js.customize.icon_register.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Holds what was answered, so that a change of set asks again.
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
 * Holds the demands that were answered.
 *
 * A change of the set in force asks again for what it holds, and for nothing
 * else: what was never answered is answered when it comes into view, under the
 * set that is in force then.
 *
 * A demand whose element left the document is forgotten: it is not there to be
 * answered again.
 */
export class IconRegister {

    /** @type {Set<IconDemand>} */
    #held = new Set();

    /**
     * Hold a demand that was answered.
     *
     * @param {IconDemand} demand - What was answered.
     * @returns {void}
     */
    hold(demand) {
        if (demand === null || demand === undefined) {
            return;
        }
        this.#held.add(demand);
    }

    // -----------------------------------------------------------------------

    /**
     * Give back the demands that are still in the document.
     *
     * @returns {IconDemand[]} Those that were answered and are still there.
     */
    held() {
        const standing = [];

        for (const demand of this.#held) {
            if (demand.element.isConnected === true) {
                standing.push(demand);
            } else {
                this.#held.delete(demand);
            }
        }

        return standing;
    }

    // -----------------------------------------------------------------------

    /**
     * Forget everything.
     *
     * @returns {void}
     */
    clear() {
        this.#held.clear();
    }
}
