/**
:filename: tests.js.viewmode_logicTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the ViewModeLogic class.

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
let viewmode_logic_tests = new UnitTest();


/**
 * Build the reading the tests of this file act upon.
 *
 * @returns {SlidesData} A reading of three supports.
 */
function viewmode_reading() {
    const supports = [];
    for (let rank = 1; rank <= 3; rank++) {
        supports.push(document.createElement('section'));
    }

    return new SlidesData(supports);
}


// -----------------------------------------------------------------------
// The view in force is read on the reading, and starts as the one showing
// one support at a time.
// -----------------------------------------------------------------------

viewmode_logic_tests.add_test(() => {
    const data = viewmode_reading();
    const view = new ViewModeLogic(data);

    UnitTest.assert_values_equals('presentation', view.current, "viewmode_starts_in_presentation_test");
});


// -----------------------------------------------------------------------
// Asking for a view puts it in force, and asking for a view that does not
// exist changes nothing.
// -----------------------------------------------------------------------

viewmode_logic_tests.add_test(() => {
    const data = viewmode_reading();
    const view = new ViewModeLogic(data);

    view.set('overview');
    UnitTest.assert_values_equals('overview', view.current, "viewmode_set_test");

    view.set('nothing-like-a-view');
    UnitTest.assert_values_equals('overview', view.current, "viewmode_unknown_view_test");
});


// -----------------------------------------------------------------------
// The reading is kept whichever view is in force: changing the way the
// supports are shown never moves the reader.
// -----------------------------------------------------------------------

viewmode_logic_tests.add_test(() => {
    const data = viewmode_reading();
    data.currentIndex = 2;
    data.currentStep = 1;
    const view = new ViewModeLogic(data);

    view.set('overview');
    view.set('note');
    view.set('presentation');

    UnitTest.assert_values_equals(2, data.currentIndex, "viewmode_keeps_the_support_test");
    UnitTest.assert_values_equals(1, data.currentStep, "viewmode_keeps_the_step_test");
});


// -----------------------------------------------------------------------
// One view is in force at a time: asking again for the one already in
// force gives back the view showing one support at a time.
// -----------------------------------------------------------------------

viewmode_logic_tests.add_test(() => {
    const data = viewmode_reading();
    const view = new ViewModeLogic(data);

    view.toggle('overview');
    UnitTest.assert_values_equals('overview', view.current, "viewmode_toggle_in_test");

    view.toggle('overview');
    UnitTest.assert_values_equals('presentation', view.current, "viewmode_toggle_out_test");
});


// -----------------------------------------------------------------------
// A change of view is said, so that what draws the supports may follow it.
// -----------------------------------------------------------------------

viewmode_logic_tests.add_test(() => {
    const data = viewmode_reading();
    const view = new ViewModeLogic(data);
    const said = [];
    view.onModeChange = reading => said.push(reading.mode);

    view.set('overview');
    view.toggle('overview');

    UnitTest.assert_values_equals(2, said.length, "viewmode_change_is_said_test");
    UnitTest.assert_values_equals('presentation', said[1], "viewmode_change_says_the_view_test");
});


// launch all unit tests added
viewmode_logic_tests.launch_unit_test();
