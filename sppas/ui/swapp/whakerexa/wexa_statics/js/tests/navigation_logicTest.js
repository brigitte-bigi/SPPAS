/**
:filename: tests.js.navigation_logicTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the NavigationLogic class.

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
let navigation_logic_tests = new UnitTest();


/**
 * Build a reading of three supports, none of them holding a step.
 *
 * @returns {SlidesData} The reading the test acts upon.
 */
function navigation_reading() {
    const supports = [];
    for (let rank = 1; rank <= 3; rank++) {
        supports.push(document.createElement('section'));
    }

    return new SlidesData(supports);
}


/**
 * Give the address of the page back the fragment it had.
 *
 * Moving the reading says it in the address, and the tests are read in a
 * page of their own: what they write there is theirs to take back.
 *
 * @param {string} fragment - The fragment to restore.
 * @returns {void}
 */
function navigation_restore(fragment) {
    if (fragment === '') {
        window.history.replaceState(null, '', window.location.pathname + window.location.search);
        return;
    }
    window.location.hash = fragment;
}


// -----------------------------------------------------------------------
// The reading goes from one support to the next, and back. Op2.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.next();
    UnitTest.assert_values_equals(2, data.currentIndex, "navigation_next_test");

    navigation.next();
    UnitTest.assert_values_equals(3, data.currentIndex, "navigation_next_again_test");

    navigation.prev();
    UnitTest.assert_values_equals(2, data.currentIndex, "navigation_prev_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// The reading never leaves the presentation: asked to go before the first
// support or after the last, it stays where it is. Op2.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.prev();
    UnitTest.assert_values_equals(1, data.currentIndex, "navigation_stays_at_the_first_test");

    navigation.goEnd();
    navigation.next();
    UnitTest.assert_values_equals(3, data.currentIndex, "navigation_stays_at_the_last_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// A support may be asked for by its rank, and a rank outside the
// presentation is brought back inside it. Op2.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.goTo(2);
    UnitTest.assert_values_equals(2, data.currentIndex, "navigation_goto_test");

    navigation.goTo(9);
    UnitTest.assert_values_equals(3, data.currentIndex, "navigation_goto_beyond_the_last_test");

    navigation.goTo(0);
    UnitTest.assert_values_equals(1, data.currentIndex, "navigation_goto_before_the_first_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// The first and the last support are reached in one request. Op2.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.goEnd();
    UnitTest.assert_values_equals(3, data.currentIndex, "navigation_go_end_test");

    navigation.goStart();
    UnitTest.assert_values_equals(1, data.currentIndex, "navigation_go_start_test");
    UnitTest.assert_values_equals(0, data.currentStep, "navigation_go_start_step_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// A move is said in the address, as the rank of the support and the step
// inside it: an address, once copied, opens the presentation where it was
// left.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.goTo(2);

    UnitTest.assert_values_equals('#2.0', window.location.hash, "navigation_says_the_position_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// A move is said, so that what draws the supports may follow it.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);
    const said = [];
    navigation.onNavigate = reading => said.push(reading.currentIndex);

    navigation.next();
    navigation.next();

    UnitTest.assert_values_equals(2, said.length, "navigation_move_is_said_test");
    UnitTest.assert_values_equals(3, said[1], "navigation_move_says_the_support_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// A position read in the address is applied, and is not written back:
// reading the address is not moving.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.updateFromHash('#3.0');
    UnitTest.assert_values_equals(3, data.currentIndex, "navigation_reads_a_position_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// The address holds the reading and nothing else. A fragment that is not a
// position names a place in the document: it is an entry of Op3, and the
// reading does not move for it.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.goTo(3);
    navigation.updateFromHash('#bib-bigi2022lrec');

    UnitTest.assert_values_equals(3, data.currentIndex,
        "navigation_a_place_is_not_a_position_test");

    navigation_restore(written);
});


// -----------------------------------------------------------------------
// An address without a fragment opens the presentation at its first
// support: there is no reading written to be given back.
// -----------------------------------------------------------------------

navigation_logic_tests.add_test(() => {
    const written = window.location.hash;
    const data = navigation_reading();
    const navigation = new NavigationLogic(data);

    navigation.updateFromHash('');

    UnitTest.assert_values_equals(1, data.currentIndex, "navigation_no_fragment_test");

    navigation_restore(written);
});


// launch all unit tests added
navigation_logic_tests.launch_unit_test();
