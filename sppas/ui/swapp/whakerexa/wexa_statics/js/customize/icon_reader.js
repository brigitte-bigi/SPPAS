/**
 * :filename: statics.js.customize.icon_reader.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Reads what answers a name. The only one that goes and gets it.
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

import { IconForm } from './icon_set.js';
import { IconContent } from './icon_content.js';
import { UnreadableContent } from './icon_errors.js';

/**
 * Reads what answers a name.
 *
 * It is the only class that goes and gets anything, and it goes as rarely as
 * it can. A line drawing is read once and held: it has to be written into the
 * page to take the color of what surrounds it. An image is never read at all —
 * its address is what answers, and the page gets it once, where it is shown.
 *
 * What was gathered into the document, for a document read where nothing
 * serves it, answers before anything is read.
 */
export class IconReader {

    /**
     * What was gathered into the document, before anything is read.
     *
     * It is held by the class and not by an instance: what gathers writes it
     * when the document is built, and no reader exists then.
     *
     * @type {Map<string, string>} "set/name" → the markup of a line drawing.
     */
    static #gathered = new Map();

    /** @type {Map<string, string>} What this reader has read. */
    #read = new Map();

    // -----------------------------------------------------------------------

    /**
     * Hold the markup of a line drawing, read from nowhere.
     *
     * Called by what gathers the contents into a document that is read where
     * nothing serves it: on such a document a browser refuses to read a file,
     * so what will be needed is written in beforehand.
     *
     * @param {string} setName - The name of the set that carries it.
     * @param {string} name - The name it answers to.
     * @param {string} markup - The markup of the drawing.
     * @returns {void}
     */
    static gather(setName, name, markup) {
        IconReader.#gathered.set(setName + '/' + name, markup);
    }

    // -----------------------------------------------------------------------

    /**
     * Hold the markup of a line drawing for this reader alone.
     *
     * @param {string} setName - The name of the set that carries it.
     * @param {string} name - The name it answers to.
     * @param {string} markup - The markup of the drawing.
     * @returns {void}
     */
    gather(setName, name, markup) {
        this.#read.set(setName + '/' + name, markup);
    }

    // -----------------------------------------------------------------------

    /**
     * Give the address of what answers a name, without reading anything.
     *
     * A ground is laid on a surface, whatever the file it stands in: it is
     * never written into the page, so it is never read.
     *
     * @param {IconSet} set - A set that carries the name.
     * @param {string} name - The name asked for.
     * @returns {IconContent} Its address, under the form of an image.
     */
    address(set, name) {
        return new IconContent(name, IconForm.IMAGE, set.addressOf(name));
    }

    // -----------------------------------------------------------------------

    /**
     * Give what answers a name in a set.
     *
     * @param {IconSet} set - A set that carries the name.
     * @param {string} name - The name asked for.
     * @returns {Promise<IconContent>} What answers it.
     */
    async read(set, name) {
        const form = set.formOf(name);
        const address = set.addressOf(name);

        if (form === IconForm.IMAGE) {
            return new IconContent(name, form, address);
        }

        const key = set.name + '/' + name;
        if (this.#read.has(key) === true) {
            return new IconContent(name, form, this.#read.get(key));
        }

        if (IconReader.#gathered.has(key) === true) {
            return new IconContent(name, form, IconReader.#gathered.get(key));
        }

        const markup = await this.#markupAt(address);
        this.#read.set(key, markup);
        return new IconContent(name, form, markup);
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Read the markup of a line drawing where it stands.
     *
     * @private
     * @param {string} address
     * @returns {Promise<string>}
     */
    async #markupAt(address) {
        let answer = null;

        try {
            answer = await fetch(address);
        } catch (error) {
            throw new UnreadableContent(address);
        }

        if (answer.ok === false) {
            throw new UnreadableContent(address);
        }

        return await answer.text();
    }
}
