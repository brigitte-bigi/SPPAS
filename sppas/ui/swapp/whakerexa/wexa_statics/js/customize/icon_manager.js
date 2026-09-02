/**
 * :filename: statics.js.customize.icon_manager.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Calls the others in order. The only one that catches an error.
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
import { IconSets } from './icon_sets.js';
import { IconChoice } from './icon_choice.js';
import { IconReader } from './icon_reader.js';
import { IconPlacer } from './icon_placer.js';
import { IconWatcher } from './icon_watcher.js';
import { IconRegister } from './icon_register.js';
import { IconDemand, DemandKind } from './icon_demand.js';
import { IconError } from './icon_errors.js';

/**
 * Answers the demands of a document.
 *
 * It calls the others in order and holds nothing of its own: the sets say
 * which one answers a name, the choice says which is in force, the watcher
 * says when a demand is about to be seen, the reader goes and gets what
 * answers, and the placer puts it where it was asked for.
 *
 * It is the only class that writes a try. A name no set carries draws nothing,
 * keeps its room, is said in the console, and breaks no page: an error must
 * never do worse than the absence of the program.
 */
export class IconManager {

    /** @type {IconSets} */
    #sets;

    /** @type {IconChoice} */
    #choice;

    /** @type {IconReader} */
    #reader = new IconReader();

    /** @type {IconPlacer} */
    #placer = new IconPlacer();

    /** @type {IconWatcher} */
    #watcher;

    /** @type {IconRegister} */
    #register = new IconRegister();

    /**
     * @param {IconSets} sets - The sets that were declared.
     * @param {string} [named] - The set the page names, if any.
     * @param {IconWatcher} [watcher] - What says when a demand is about to be
     *                                  seen. One is made when none is given;
     *                                  another one is given by a test, which
     *                                  cannot wait for a rendering.
     */
    constructor(sets, named = '', watcher = null) {
        this.#sets = sets;
        this.#choice = new IconChoice(sets, named);
        this.#watcher = watcher !== null ? watcher : new IconWatcher();
    }

    // -----------------------------------------------------------------------

    /** @returns {string} The name of the set the document is shown with. */
    inForce() {
        return this.#choice.inForce();
    }

    /** @returns {string[]} The names of the sets, the reference one last. */
    names() {
        return this.#sets.names();
    }

    // -----------------------------------------------------------------------

    /**
     * Hold a set the page brings.
     *
     * @param {IconSet} set - The set to hold.
     * @returns {void}
     */
    declare(set) {
        this.#sets.declare(set);
    }

    /**
     * Hold the markup of a drawing, read from nowhere.
     *
     * What gathers the drawings into a document calls this, so that a document
     * read where nothing serves it answers without reading anything.
     *
     * @param {string} setName - The name of the set that carries it.
     * @param {string} name - The name it answers to.
     * @param {string} markup - The markup of the drawing.
     * @returns {void}
     */
    gather(setName, name, markup) {
        this.#reader.gather(setName, name, markup);
    }

    // -----------------------------------------------------------------------

    /**
     * Hold the set a name falls back to last.
     *
     * @param {IconSet} set - The set of the framework.
     * @returns {void}
     */
    reference(set) {
        this.#sets.reference(set);
    }

    /**
     * Name the set that answers what the others leave unanswered.
     *
     * @param {string} name - The name of one of the declared sets.
     * @returns {void}
     */
    fallback(name) {
        this.#sets.fallback(name);
    }

    // -----------------------------------------------------------------------

    /**
     * Give what answers a name, for whoever writes it themselves.
     *
     * A component of the framework asks for an icon by its name and puts it
     * where it wants: it does not write an attribute in a document it does not
     * own.
     *
     * @param {string} name - The name asked for.
     * @returns {Promise<string>} The markup of a line drawing, the address of
     *                            an image, or an empty string.
     */
    async get(name) {
        const set = this.#sets.setFor(name, this.#choice.inForce());
        if (set === null) {
            WexaLogger.warn('IconManager: no set carries the name "' + name + '".');
            return '';
        }

        try {
            const content = await this.#reader.read(set, name);
            return content.source;
        } catch (error) {
            this.#say(error);
            return '';
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Put an icon in an element, unless it already holds one.
     *
     * @param {HTMLElement} element - What receives it.
     * @param {string} name - The name asked for.
     * @returns {Promise<void>} Never raises.
     */
    async inject(element, name) {
        if (element === null || element === undefined) {
            return;
        }
        if (element.querySelector('svg') !== null) {
            return;
        }

        const markup = await this.get(name);
        if (markup === '') {
            return;
        }

        element.insertAdjacentHTML('afterbegin', markup);
    }

    // -----------------------------------------------------------------------

    /**
     * Watch the demands of the document, and answer them as they are seen.
     *
     * @param {HTMLElement} [root] - What holds the demands.
     * @returns {Promise<void>} Never raises.
     */
    async run(root = document) {
        try {
            const demands = [];
            for (const element of root.querySelectorAll(IconDemand.SELECTOR)) {
                const demand = IconDemand.of(element);
                if (demand !== null) {
                    demands.push(demand);
                }
            }

            this.#watcher.watch(demands, demand => this.#answer(demand));

        } catch (error) {
            this.#say(error);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Show the document with another set.
     *
     * What is held is answered again, and nothing else: what is not seen is
     * answered when it is seen, under the set in force then.
     *
     * @param {string} name - The name of the set to put in force.
     * @returns {Promise<void>} Never raises.
     */
    async show(name) {
        try {
            if (this.#choice.put(name) === false) {
                return;
            }

            for (const demand of this.#register.held()) {
                await this.#answer(demand);
            }

        } catch (error) {
            this.#say(error);
        }
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Answer one demand.
     *
     * @private
     * @param {IconDemand} demand
     * @returns {Promise<void>}
     */
    async #answer(demand) {
        const set = this.#sets.setFor(demand.name, this.#choice.inForce());

        if (set === null) {
            this.#placer.clear(demand);
            this.#register.hold(demand);
            WexaLogger.warn('IconManager: no set carries the name "'
                + demand.name + '".');
            return;
        }

        try {
            // A ground is laid on a surface: it is never written into the page,
            // so it is never read. Its address is what answers.
            const content = demand.kind === DemandKind.SURFACE
                ? this.#reader.address(set, demand.name)
                : await this.#reader.read(set, demand.name);
            this.#placer.place(demand, content);
        } catch (error) {
            this.#placer.clear(demand);
            this.#say(error);
        }

        this.#register.hold(demand);
    }

    // -----------------------------------------------------------------------

    /**
     * Say what went wrong, and let the page hold.
     *
     * @private
     * @param {Error} error
     * @returns {void}
     */
    #say(error) {
        if (error instanceof IconError) {
            WexaLogger.error('IconManager: ' + error.message);
            return;
        }
        WexaLogger.error('IconManager: ', error);
    }
}
