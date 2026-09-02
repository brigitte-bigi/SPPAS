/**
:filename: tests.js.icon_setsTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconSet and IconSets classes.

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
let icon_sets_tests = new UnitTest();


/**
 * Give a set of line drawings, carrying three names.
 *
 * @returns {IconSet} A set nothing stands behind: nothing is read.
 *
 */
function a_line_set() {
    return new IconSet('child', 'icons/child/', ['home.svg', 'back.svg', 'next.svg']);
}


/**
 * Give a set of files of several formats, carrying two of the same names.
 *
 * An author brings the files he has: an image beside a line drawing.
 *
 * @returns {IconSet}
 *
 */
function a_mixed_set() {
    return new IconSet('adult', 'icons/adult/', ['home.webp', 'back.svg']);
}


/**
 * Give the set every name falls back to.
 *
 * @returns {IconSet}
 *
 */
function a_reference_set() {
    return new IconSet('mono-svg', 'icons/mono-svg/',
                       ['home.svg', 'back.svg', 'next.svg', 'first.svg', 'last.svg']);
}


// -----------------------------------------------------------------------
// A set says its name and what it carries. It reads nothing.
// [I6], decision 2.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const set = a_line_set();

    UnitTest.assert_values_equals('child', set.name, "icon_set_name_test");
    UnitTest.assert_values_equals(true, set.carries('home'), "icon_set_carries_test");
    UnitTest.assert_values_equals(false, set.carries('first'),
        "icon_set_does_not_carry_test");
    UnitTest.assert_values_equals(false, set.carries(''),
        "icon_set_carries_no_empty_name_test");
});


// -----------------------------------------------------------------------
// The form of a content is read in its file, and a set holds files of
// several formats side by side: an author brings what he has. C5, [031]
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const set = a_mixed_set();

    UnitTest.assert_values_equals('image', set.formOf('home'),
        "icon_set_an_image_is_an_image_test");
    UnitTest.assert_values_equals('line', set.formOf('back'),
        "icon_set_a_svg_is_a_line_test");
    UnitTest.assert_values_equals('image', new IconSet('x', '', ['a.ico']).formOf('a'),
        "icon_set_an_unknown_format_is_an_image_test");
});


// -----------------------------------------------------------------------
// A set says where a content stands, from its own base.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const set = a_line_set();

    UnitTest.assert_values_equals('icons/child/home.svg', set.addressOf('home'),
        "icon_set_address_of_a_drawing_test");
    UnitTest.assert_values_equals('icons/adult/home.webp', a_mixed_set().addressOf('home'),
        "icon_set_address_of_an_image_test");
});


// -----------------------------------------------------------------------
// A set carrying nothing is a set: it answers no name, and raises nothing.
// [013]
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const set = new IconSet('empty', 'icons/empty/', []);

    UnitTest.assert_values_equals(false, set.carries('home'),
        "icon_set_empty_carries_nothing_test");
    UnitTest.assert_values_equals('empty', set.name, "icon_set_empty_has_a_name_test");
});


// -----------------------------------------------------------------------
// A name the set in force carries is answered by that set. C3
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());

    const answering = sets.setFor('home', 'child');

    UnitTest.assert_values_equals('child', answering.name,
        "icon_sets_the_set_in_force_answers_test");
});


// -----------------------------------------------------------------------
// A name the set in force does not carry is answered by the reference set,
// name by name and not set by set. C3, decision 3.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());

    const answering = sets.setFor('first', 'child');

    UnitTest.assert_values_equals('mono-svg', answering.name,
        "icon_sets_the_reference_answers_what_is_missing_test");
});


// -----------------------------------------------------------------------
// A name no set carries is answered by nothing, and raises nothing. [061]
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());

    UnitTest.assert_values_equals(null, sets.setFor('nothing-like-a-name', 'child'),
        "icon_sets_no_set_answers_test");
});


// -----------------------------------------------------------------------
// A set in force that was never declared answers nothing of its own: the
// reference set answers what it carries. [023]
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());

    const answering = sets.setFor('home', 'nobody');

    UnitTest.assert_values_equals('mono-svg', answering.name,
        "icon_sets_unknown_set_in_force_test");
});


// -----------------------------------------------------------------------
// Two sets under one name: the first is kept. C1
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.declare(new IconSet('child', 'icons/other/', ['home.webp']));
    sets.reference(a_reference_set());

    UnitTest.assert_values_equals('icons/child/home.svg',
        sets.setFor('home', 'child').addressOf('home'),
        "icon_sets_a_name_declared_twice_keeps_the_first_test");
});


// -----------------------------------------------------------------------
// The sets are given back by their names, the reference one last.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.declare(a_mixed_set());
    sets.reference(a_reference_set());

    const names = sets.names();

    UnitTest.assert_values_equals(3, names.length, "icon_sets_how_many_test");
    UnitTest.assert_values_equals('mono-svg', names[names.length - 1],
        "icon_sets_the_reference_comes_last_test");
    UnitTest.assert_array_contains('child', names, "icon_sets_names_hold_the_declared_test");
});


// -----------------------------------------------------------------------
// A name the set in force does not carry is answered by the set that
// answers for the others, before the reference one. C3, [016]
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(new IconSet('colored', 'icons/colored/', ['home.png']));
    sets.declare(new IconSet('refine', 'icons/refine/', ['home.png', 'first.png']));
    sets.reference(a_reference_set());
    sets.fallback('refine');

    UnitTest.assert_values_equals('refine', sets.setFor('first', 'colored').name,
        "icon_sets_the_fallback_answers_before_the_reference_test");
    UnitTest.assert_values_equals('colored', sets.setFor('home', 'colored').name,
        "icon_sets_the_set_in_force_still_answers_first_test");
    UnitTest.assert_values_equals('mono-svg', sets.setFor('last', 'colored').name,
        "icon_sets_the_reference_answers_last_test");
});


// -----------------------------------------------------------------------
// The chain is read once: a set that answers for itself answers as if it
// answered for nothing. C10
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());
    sets.fallback('child');

    UnitTest.assert_values_equals('child', sets.setFor('home', 'child').name,
        "icon_sets_a_set_answering_for_itself_test");
    UnitTest.assert_values_equals('mono-svg', sets.setFor('first', 'child').name,
        "icon_sets_no_cycle_test");
});


// -----------------------------------------------------------------------
// A set that was never declared answers for nobody.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());
    sets.reference(a_reference_set());
    sets.fallback('nobody');

    UnitTest.assert_values_equals('mono-svg', sets.setFor('first', 'child').name,
        "icon_sets_an_unknown_fallback_test");
});


// -----------------------------------------------------------------------
// Without a reference set, a name nobody carries is answered by nothing.
// -----------------------------------------------------------------------

icon_sets_tests.add_test(() => {
    const sets = new IconSets();
    sets.declare(a_line_set());

    UnitTest.assert_values_equals(null, sets.setFor('first', 'child'),
        "icon_sets_no_reference_test");
    UnitTest.assert_values_equals('child', sets.setFor('home', 'child').name,
        "icon_sets_no_reference_but_the_set_answers_test");
});


// launch all unit tests added
icon_sets_tests.launch_unit_test();
