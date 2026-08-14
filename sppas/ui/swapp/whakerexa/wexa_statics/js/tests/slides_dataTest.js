/**
:filename: tests.js.slides_dataTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlidesData class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-08-13.
    -------------------------------------------------------------------------

    Copyright (C) 2026 Brigitte Bigi
    Laboratoire Parole et Langage, Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    Whakerexa is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Whakerexa is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Whakerexa. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

*/

// instantiate unit tests class
let slides_data_tests = new UnitTest();


/**
 * Build a series of supports the tests of this file work on.
 *
 * @param {number} count - How many supports the presentation holds.
 * @returns {HTMLElement[]} The supports, outside the document.
 */
function slides_data_supports(count) {
    const supports = [];
    for (let rank = 1; rank <= count; rank++) {
        const support = document.createElement('section');
        support.className = 'slide';
        supports.push(support);
    }

    return supports;
}


// -----------------------------------------------------------------------
// A reading stands at the first support, at its beginning, and in the view
// that shows one support at a time.
// -----------------------------------------------------------------------

slides_data_tests.add_test(() => {
    const data = new SlidesData(slides_data_supports(3));

    UnitTest.assert_values_equals(1, data.currentIndex, "data_reading_starts_at_the_first_test");
    UnitTest.assert_values_equals(0, data.currentStep, "data_reading_starts_at_the_beginning_test");
    UnitTest.assert_values_equals('presentation', data.mode, "data_reading_starts_in_presentation_test");
});


// -----------------------------------------------------------------------
// A presentation knows how many supports it holds, and a presentation
// holding none says zero rather than raising.
// -----------------------------------------------------------------------

slides_data_tests.add_test(() => {
    UnitTest.assert_values_equals(3, new SlidesData(slides_data_supports(3)).count,
        "data_counts_its_supports_test");
    UnitTest.assert_values_equals(0, new SlidesData([]).count,
        "data_counts_none_test");
    UnitTest.assert_values_equals(0, new SlidesData(null).count,
        "data_without_supports_test");
});


// -----------------------------------------------------------------------
// Nothing is kept from one opening to the next: two readings of the same
// supports start at the same place.
// -----------------------------------------------------------------------

slides_data_tests.add_test(() => {
    const supports = slides_data_supports(4);
    const first = new SlidesData(supports);
    first.currentIndex = 3;

    const second = new SlidesData(supports);

    UnitTest.assert_values_equals(1, second.currentIndex, "data_nothing_is_kept_test");
});


// launch all unit tests added
slides_data_tests.launch_unit_test();
