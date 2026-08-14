/**
 :filename: wexa_statics/js/extras/book/biberrors.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: The errors a bibliography can raise.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa

 Copyright (C) 2023-2026 Brigitte Bigi, CNRS
 Laboratoire Parole et Langage, Aix-en-Provence, France

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.

 This banner notice must not be removed.

 -------------------------------------------------------------------------

 */
'use strict';

/**
 * What a bibliography raises when nothing at all can be done.
 *
 * There are only two of these, and they share this parent so that whoever
 * gathers them catches both in one gesture. Anything else that may happen is a
 * mistake in the program, and has to be seen rather than caught.
 *
 * A field that is missing, an entry that cannot be read, a key that names
 * nothing: none of these raise. They concern one reference, are said in the
 * console, and the rest of the work goes on.
 */
export class BibliographyError extends Error {
    /**
     * Instantiate the parent of the errors of a bibliography.
     *
     * @param message {string} What went wrong, for whoever wrote the document.
     */
    constructor(message) {
        super(message);
        this.name = 'BibliographyError';
    }
}

/**
 * Raised when neither the page nor the address gives any BibTeX data.
 *
 * Without data there is no bibliography at all, and the citations cannot be
 * numbered either. The page keeps everything else it has.
 */
export class MissingBibtexData extends BibliographyError {
    /**
     * Instantiate the error.
     *
     * @param message {string} What was looked for, and where.
     */
    constructor(message) {
        super(message);
        this.name = 'MissingBibtexData';
    }
}

/**
 * Raised when the page says nowhere to put the bibliography.
 *
 * The citations are numbered all the same: they are in the text, and the text
 * is there. Only the table has nowhere to go.
 */
export class MissingBibliographyPlace extends BibliographyError {
    /**
     * Instantiate the error.
     *
     * @param message {string} Which element was looked for.
     */
    constructor(message) {
        super(message);
        this.name = 'MissingBibliographyPlace';
    }
}
