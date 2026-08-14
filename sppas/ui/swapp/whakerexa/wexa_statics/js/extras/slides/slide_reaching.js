/**
:filename: statics.js.slides.slide_reaching.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Reach a place written in the document, whatever the support carrying it.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa

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
 * Reaches a place written in the document, on the support carrying it.
 *
 * A reader following a renvoi asks for a place, not for a support: a table of
 * contents, a note, and the two links of a bibliography all name a place and
 * none of them knows where it was laid down. This class answers that request:
 * it finds the support carrying the place and asks the navigation for it.
 *
 * Rules:
 * - Receives a place, never a position: the address of the page holds the
 *   reading and nothing else, and a place is never written there.
 * - Reads the document, and moves nothing itself: the reading is moved by the
 *   navigation it was given.
 * - A place no support carries moves nothing.
 * - Nothing inside the support is touched: a support is shown whole, so the
 *   place takes no focus and the support is not scrolled.
 */
export default class SlideReaching {

    // FIELDS
    _data
    _navigation

    // CONSTRUCTOR
    /**
     * Instantiate the reaching of a presentation.
     *
     * @param data {SlidesData} The reading, holding the supports.
     * @param navigation {NavigationLogic} What moves the reading.
     */
    constructor(data, navigation) {
        this._data = data;
        this._navigation = navigation;
    }

    // ----------------------------------------------------------------------
    // PUBLIC
    // ----------------------------------------------------------------------

    /**
     * Give the rank of the support carrying a place.
     *
     * @param place {String} The name of the place, without the sharp sign.
     * @returns {number} The rank, from 1, or 0 when no support carries it.
     */
    supportOf(place) {
        if (typeof place !== 'string' || place === '') {
            return 0;
        }

        const element = document.getElementById(place);
        if (element === null) {
            return 0;
        }

        const supports = this._data.slides;
        for (let index = 0; index < supports.length; index++) {
            if (supports[index].contains(element) === true) {
                return index + 1;
            }
        }

        return 0;
    }

    // ----------------------------------------------------------------------

    /**
     * Show the support carrying a place.
     *
     * The support is shown whole, so the place is under the eyes as soon as
     * that support is the one shown: nothing inside it is touched. Bringing
     * the eyes to what they already see gains nothing, and it costs the
     * rendering, the supports being laid where they are by the view.
     *
     * @param place {String} The name of the place, without the sharp sign.
     * @returns {number} The rank of the support reached, or 0 when none carries it.
     */
    reach(place) {
        const rank = this.supportOf(place);
        if (rank === 0) {
            return 0;
        }

        this._navigation.goTo(rank);

        return rank;
    }
}
