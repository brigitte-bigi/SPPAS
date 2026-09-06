/**
 * :filename: statics.js.customize.icon_sets.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: The declared sets of icons, and which one answers a name.
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

import { WexaLogger } from '../logger.js';

/**
 * The sets that were declared, and the one they fall back to.
 *
 * This class decides the whole of the fallback and reads nothing: a name is
 * answered by the set in force when that set carries it, by the reference set
 * when it does not, and by nothing when neither does. It is therefore the one
 * class of the icons that is tested without a document.
 *
 * The fallback is name by name, and not set by set: a set that carries three
 * drawings does not have to carry the others.
 *
 * A name goes down a chain of two: the set that answers for the others, which
 * the application names among its own, and then the reference set. An
 * application whose complete set is its own does not want the framework to
 * answer what one of its incomplete sets leaves out.
 */
export class IconSets {

    /** @type {Map<string, IconSet>} */
    #declared = new Map();

    /** @type {IconSet|null} */
    #reference = null;

    /** @type {string} The name of the set that answers for the others. */
    #fallback = '';

    // -----------------------------------------------------------------------

    /**
     * Hold a set under its name.
     *
     * A name declared twice keeps the first set: the second is said in the
     * console, for whoever wrote the page.
     *
     * @param {IconSet} set - The set to hold.
     * @returns {void}
     */
    declare(set) {
        if (set === null || set === undefined) {
            return;
        }

        if (this.#declared.has(set.name) === true) {
            WexaLogger.warn('IconSets: the set "' + set.name
                + '" is declared twice. The first one is kept.');
            return;
        }

        this.#declared.set(set.name, set);
    }

    // -----------------------------------------------------------------------

    /**
     * Hold the set a name falls back to.
     *
     * @param {IconSet} set - The set of the framework.
     * @returns {void}
     */
    reference(set) {
        if (set === null || set === undefined) {
            return;
        }
        this.#reference = set;
    }

    // -----------------------------------------------------------------------

    /**
     * Name the set that answers what the others leave unanswered.
     *
     * A name that was never declared leaves the chain as it was.
     *
     * @param {string} name - The name of one of the declared sets.
     * @returns {void}
     */
    fallback(name) {
        if (this.#declared.has(name) === false) {
            WexaLogger.warn('IconSets: the set "' + name
                + '" answers for the others, and was never declared.');
            return;
        }
        this.#fallback = name;
    }

    // -----------------------------------------------------------------------

    /**
     * Say which set answers a name.
     *
     * The chain is walked once, and has two links: the set that answers for
     * the others, then the reference set. A set that answers for itself is
     * therefore asked once and not twice.
     *
     * @param {string} name - The name asked for.
     * @param {string} inForce - The name of the set the document is shown with.
     * @returns {IconSet} The set that carries the name, or null when none does.
     */
    setFor(name, inForce) {
        const chosen = this.#declared.get(inForce);
        if (chosen !== undefined && chosen.carries(name) === true) {
            return chosen;
        }

        if (this.#fallback !== '' && this.#fallback !== inForce) {
            const answering = this.#declared.get(this.#fallback);
            if (answering !== undefined && answering.carries(name) === true) {
                return answering;
            }
        }

        if (this.#reference !== null && this.#reference.carries(name) === true) {
            return this.#reference;
        }

        return null;
    }

    // -----------------------------------------------------------------------

    /**
     * Say the names a document shows under a set.
     *
     * The same chain as setFor(), walked whole instead of being asked one
     * name: what the set in force carries, then what the set answering for
     * the others adds to it, then what the reference set adds to both. A name
     * carried twice is said once, by the first set of the chain that carries
     * it.
     *
     * @param {string} inForce - The name of the set the document is shown with.
     * @returns {string[]} The names, in the order the chain gives them.
     */
    namesFor(inForce) {
        const names = [];
        const chain = [
            this.#declared.get(inForce),
            this.#declared.get(this.#fallback),
            this.#reference
        ];

        for (const set of chain) {
            if (set === undefined || set === null) {
                continue;
            }
            for (const name of set.names) {
                if (names.includes(name) === false) {
                    names.push(name);
                }
            }
        }

        return names;
    }

    // -----------------------------------------------------------------------

    /**
     * Say the names of the sets, the reference one last.
     *
     * @returns {string[]} The names, in the order they were declared.
     */
    names() {
        const names = Array.from(this.#declared.keys());
        if (this.#reference !== null) {
            names.push(this.#reference.name);
        }
        return names;
    }
}
