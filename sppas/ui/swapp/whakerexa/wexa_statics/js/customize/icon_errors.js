/**
 * :filename: statics.js.customize.icon_errors.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: The errors the icons raise.
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
 * The mother of the errors of the icons. Raised by nobody.
 */
export class IconError extends Error {

    /** @param {string} message */
    constructor(message) {
        super(message);
        this.name = 'IconError';
    }
}

/**
 * Not one set was declared, not even the reference one.
 */
export class NoSetAtAll extends IconError {

    constructor() {
        super('No set of icons was declared, not even the reference one.');
        this.name = 'NoSetAtAll';
    }
}

/**
 * A content a set says it carries cannot be read.
 */
export class UnreadableContent extends IconError {

    /**
     * @param {string} address - Where the content was looked for.
     */
    constructor(address) {
        super('The content at "' + address + '" cannot be read.');
        this.name = 'UnreadableContent';
    }
}
