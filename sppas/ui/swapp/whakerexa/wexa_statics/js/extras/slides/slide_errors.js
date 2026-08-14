/**
 :filename: statics.js.slides.slide_errors.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: What can stop the layout of a slide.

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
 * What stops the layout, and nothing else.
 *
 * It is the mother class, raised by nobody: it is what SlidesPagination
 * catches, so that both of the others are caught in one gesture. Anything that
 * is not one of these is a programming mistake, and has to be seen.
 */
export class PaginationError extends Error {
}

/**
 * The element given is not a slide of the document.
 */
export class MissingSlide extends PaginationError {
}

/**
 * The slide has no height: it is not rendered, and nothing can be measured in
 * it. A height measured out of the slide is worth nothing.
 */
export class UnmeasurableSlide extends PaginationError {
}
