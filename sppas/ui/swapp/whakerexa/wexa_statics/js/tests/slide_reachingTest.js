/**
:filename: tests.js.slide_reachingTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlideReaching class.

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
let slide_reaching_tests = new UnitTest();


/**
 * Build a presentation of three supports, and put it in the page.
 *
 * The second support carries a citation, the third the reference it names:
 * the two places a bibliography leads from and to.
 *
 * @returns {HTMLElement} What holds the supports, added to the document.
 */
function reaching_presentation() {
    const holder = document.createElement('div');
    holder.id = 'reaching-test-holder';

    for (let rank = 1; rank <= 3; rank++) {
        const support = document.createElement('section');
        support.className = 'slide';
        support.id = 'reaching-support-' + rank;
        holder.appendChild(support);
    }

    const citation = document.createElement('span');
    citation.id = 'reaching-citation';
    holder.children[1].appendChild(citation);

    const reference = document.createElement('tr');
    reference.id = 'reaching-reference';
    const table = document.createElement('table');
    const body = document.createElement('tbody');
    body.appendChild(reference);
    table.appendChild(body);
    holder.children[2].appendChild(table);

    document.body.appendChild(holder);

    return holder;
}


/**
 * Give back the reading and the navigation the tests act upon.
 *
 * @param {HTMLElement} holder - What holds the supports.
 * @returns {Object} The reading, the navigation and the reaching.
 */
function reaching_parts(holder) {
    const supports = Array.from(holder.querySelectorAll('.slide'));
    const data = new SlidesData(supports);
    const navigation = new NavigationLogic(data);

    return { data, navigation, reaching: new SlideReaching(data, navigation) };
}


// -----------------------------------------------------------------------
// A place is looked for in the document, and the support carrying it is
// given by its rank. Op3.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const holder = reaching_presentation();
    const parts = reaching_parts(holder);

    UnitTest.assert_values_equals(2, parts.reaching.supportOf('reaching-citation'),
        "reaching_finds_the_support_of_a_citation_test");
    UnitTest.assert_values_equals(3, parts.reaching.supportOf('reaching-reference'),
        "reaching_finds_the_support_of_a_reference_test");

    holder.remove();
});


// -----------------------------------------------------------------------
// A place no element bears, and a place carried by no support, are said to
// be nowhere rather than raising. Op3.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const holder = reaching_presentation();
    const outside = document.createElement('p');
    outside.id = 'reaching-outside';
    document.body.appendChild(outside);
    const parts = reaching_parts(holder);

    UnitTest.assert_values_equals(0, parts.reaching.supportOf('nothing-like-a-place'),
        "reaching_unknown_place_test");
    UnitTest.assert_values_equals(0, parts.reaching.supportOf('reaching-outside'),
        "reaching_place_outside_the_supports_test");
    UnitTest.assert_values_equals(0, parts.reaching.supportOf(''),
        "reaching_empty_place_test");

    outside.remove();
    holder.remove();
});


// -----------------------------------------------------------------------
// Reaching a place makes the reading stand at the support carrying it: a
// citation read on the second support leads to its reference on the third.
// Requirements C26 and C27 of the bibliography.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const written = window.location.hash;
    const holder = reaching_presentation();
    const parts = reaching_parts(holder);

    const reached = parts.reaching.reach('reaching-reference');

    UnitTest.assert_values_equals(3, reached, "reaching_gives_the_support_reached_test");
    UnitTest.assert_values_equals(3, parts.data.currentIndex, "reaching_moves_the_reading_test");

    window.location.hash = written === '' ? '#1.0' : written;
    holder.remove();
});


// -----------------------------------------------------------------------
// And back: from the reference, the place of the citation is reached the
// same way, on the support carrying it.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const written = window.location.hash;
    const holder = reaching_presentation();
    const parts = reaching_parts(holder);
    parts.navigation.goTo(3);

    parts.reaching.reach('reaching-citation');

    UnitTest.assert_values_equals(2, parts.data.currentIndex, "reaching_moves_back_test");

    window.location.hash = written === '' ? '#1.0' : written;
    holder.remove();
});


// -----------------------------------------------------------------------
// A place no support carries moves nothing: the reading stays where it is.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const written = window.location.hash;
    const holder = reaching_presentation();
    const parts = reaching_parts(holder);
    parts.navigation.goTo(2);

    const reached = parts.reaching.reach('nothing-like-a-place');

    UnitTest.assert_values_equals(0, reached, "reaching_nowhere_gives_zero_test");
    UnitTest.assert_values_equals(2, parts.data.currentIndex, "reaching_nowhere_moves_nothing_test");

    window.location.hash = written === '' ? '#1.0' : written;
    holder.remove();
});


// -----------------------------------------------------------------------
// Nothing inside the support is touched: a support is shown whole, so the
// place reached takes no focus, and the keyboard stands where it stood.
// -----------------------------------------------------------------------

slide_reaching_tests.add_test(() => {
    const written = window.location.hash;
    const holder = reaching_presentation();
    const parts = reaching_parts(holder);

    const elsewhere = document.createElement('button');
    elsewhere.id = 'reaching-elsewhere';
    document.body.appendChild(elsewhere);
    elsewhere.focus();

    parts.reaching.reach('reaching-citation');

    UnitTest.assert_values_equals('reaching-elsewhere', document.activeElement.id,
        "reaching_leaves_the_focus_where_it_was_test");

    const place = document.getElementById('reaching-citation');
    UnitTest.assert_values_equals(false, place.hasAttribute('tabindex'),
        "reaching_adds_no_stop_to_the_keyboard_order_test");

    window.location.hash = written === '' ? '#1.0' : written;
    elsewhere.remove();
    holder.remove();
});


// launch all unit tests added
slide_reaching_tests.launch_unit_test();
