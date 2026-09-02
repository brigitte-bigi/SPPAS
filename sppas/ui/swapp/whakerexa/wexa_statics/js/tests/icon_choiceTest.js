/**
:filename: tests.js.icon_choiceTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconChoice class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-08-31.
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
let icon_choice_tests = new UnitTest();


/**
 * Give the sets the choice is made among.
 *
 * @returns {IconSets} Two declared sets, and the one they fall back to.
 *
 */
function choice_sets() {
    const sets = new IconSets();
    sets.declare(new IconSet('child', 'icons/child/', ['home.svg']));
    sets.declare(new IconSet('adult', 'icons/adult/', ['home.webp']));
    sets.reference(new IconSet('mono-svg', 'icons/mono-svg/', ['home.svg', 'back.svg']));
    return sets;
}


// -----------------------------------------------------------------------
// Nobody having chosen, the reference set is the one in force. [023]
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), '', '');

    UnitTest.assert_values_equals('mono-svg', choice.inForce(),
        "icon_choice_falls_back_on_the_reference_test");
});


// -----------------------------------------------------------------------
// A set named at the start is the one in force.
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), 'adult', '');

    UnitTest.assert_values_equals('adult', choice.inForce(),
        "icon_choice_takes_the_default_test");
});


// -----------------------------------------------------------------------
// A set that was never declared changes nothing. [023]
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), 'nobody', '');

    UnitTest.assert_values_equals('mono-svg', choice.inForce(),
        "icon_choice_an_unknown_default_is_ignored_test");
    UnitTest.assert_values_equals(false, choice.put('nobody'),
        "icon_choice_putting_an_unknown_set_test");
    UnitTest.assert_values_equals('mono-svg', choice.inForce(),
        "icon_choice_an_unknown_set_does_not_take_force_test");
});


// -----------------------------------------------------------------------
// Putting another set says that it changed; putting the one in force says
// that it did not. [025]
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), 'child', '');

    UnitTest.assert_values_equals(true, choice.put('adult'),
        "icon_choice_a_change_is_said_test");
    UnitTest.assert_values_equals('adult', choice.inForce(),
        "icon_choice_the_set_changed_test");
    UnitTest.assert_values_equals(false, choice.put('adult'),
        "icon_choice_no_change_is_said_test");
});


// -----------------------------------------------------------------------
// The set in force is read in the address, before what the page names.
// [024]
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), 'child', 'child?wexa_icons=adult');

    UnitTest.assert_values_equals('adult', choice.inForce(),
        "icon_choice_the_address_comes_first_test");
});


// -----------------------------------------------------------------------
// A set named in the address but never declared leaves the default alone.
// -----------------------------------------------------------------------

icon_choice_tests.add_test(() => {
    const choice = new IconChoice(choice_sets(), 'child', '?wexa_icons=nobody');

    UnitTest.assert_values_equals('child', choice.inForce(),
        "icon_choice_an_unknown_set_in_the_address_test");
});


// The address is left as it was: a test writes nothing outside itself.
icon_choice_tests.add_test(() => {
    const address = new URL(window.location.href);
    address.searchParams.delete(IconChoice.PARAMETER_NAME);
    window.history.replaceState(null, '', address.href);

    UnitTest.assert_values_equals(false,
        window.location.search.includes(IconChoice.PARAMETER_NAME),
        "icon_choice_leaves_the_address_as_it_was_test");
});


// launch all unit tests added
icon_choice_tests.launch_unit_test();
