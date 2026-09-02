/**
:filename: tests.js.icon_managerTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconManager class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-09-01.
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
let icon_manager_tests = new UnitTest();


/**
 * Put a few demands in the page, under one holder.
 *
 * @param {string[]} names - What each element asks for.
 * @returns {HTMLElement} The holder, added to the document.
 *
 */
function manager_document(names) {
    const holder = document.createElement('div');
    holder.id = 'manager-test-holder';

    for (const name of names) {
        const button = document.createElement('button');
        button.setAttribute('data-icon', name);
        button.setAttribute('aria-label', name);
        holder.appendChild(button);
    }

    document.body.appendChild(holder);
    return holder;
}


/**
 * Take the set in force out of the address.
 *
 * A test that shows the document with another set writes that set in the
 * address, where the next test would read it: each one starts from an address
 * that names none.
 *
 * @returns {void}
 *
 */
function an_address_naming_no_set() {
    const address = new URL(window.location.href);
    address.searchParams.delete('wexa_icons');
    window.history.replaceState(null, '', address.href);
}


/**
 * Give a watcher that announces every demand at once.
 *
 * A test cannot wait for a rendering: what says when a demand comes into view
 * is answered for here, so that what the manager does with it is what is
 * tested.
 *
 * @returns {Object} What IconManager asks of a watcher.
 *
 */
function a_watcher_that_sees_everything() {
    return {
        watch: (demands, onView) => demands.forEach(demand => onView(demand)),
        stop: () => {}
    };
}


/**
 * Give sets whose contents are gathered, so that nothing is read.
 *
 * @returns {IconSets}
 *
 */
function manager_sets() {
    IconReader.gather('theirs', 'back', '<svg id="theirs-back"></svg>');
    IconReader.gather('ours', 'back', '<svg id="ours-back"></svg>');
    IconReader.gather('ours', 'first', '<svg id="ours-first"></svg>');

    const sets = new IconSets();
    sets.declare(new IconSet('theirs', 'nowhere/', ['back.svg']));
    sets.reference(new IconSet('ours', 'nowhere/', ['back.svg', 'first.svg']));
    return sets;
}


// -----------------------------------------------------------------------
// The demands of the document are answered, each by the set that carries
// its name: the one in force first, the reference one for the rest. C3
// -----------------------------------------------------------------------

icon_manager_tests.add_test(async () => {
    an_address_naming_no_set();
    const holder = manager_document(['back', 'first']);
    const manager = new IconManager(manager_sets(), 'theirs', a_watcher_that_sees_everything());

    await manager.run(holder);
    await new Promise(resolve => setTimeout(resolve, 300));

    UnitTest.assert_values_equals('theirs-back',
        holder.children[0].querySelector('svg').getAttribute('id'),
        "icon_manager_the_set_in_force_answers_test");
    UnitTest.assert_values_equals('ours-first',
        holder.children[1].querySelector('svg').getAttribute('id'),
        "icon_manager_the_reference_answers_the_rest_test");

    holder.remove();
});


// -----------------------------------------------------------------------
// Showing the document with another set answers again what is shown, and
// changes nothing else. [025] [027]
// -----------------------------------------------------------------------

icon_manager_tests.add_test(async () => {
    an_address_naming_no_set();
    const holder = manager_document(['back']);
    const manager = new IconManager(manager_sets(), 'theirs', a_watcher_that_sees_everything());

    await manager.run(holder);
    await new Promise(resolve => setTimeout(resolve, 300));
    await manager.show('ours');
    await new Promise(resolve => setTimeout(resolve, 300));

    UnitTest.assert_values_equals('ours', manager.inForce(),
        "icon_manager_the_set_changed_test");
    UnitTest.assert_values_equals('ours-back',
        holder.children[0].querySelector('svg').getAttribute('id'),
        "icon_manager_what_is_shown_is_answered_again_test");

    holder.remove();
});


// -----------------------------------------------------------------------
// A name no set carries draws nothing, keeps the room, and breaks no page.
// [061] [063]
// -----------------------------------------------------------------------

icon_manager_tests.add_test(async () => {
    an_address_naming_no_set();
    const holder = manager_document(['nothing-like-a-name', 'back']);
    const manager = new IconManager(manager_sets(), 'theirs', a_watcher_that_sees_everything());

    await manager.run(holder);
    await new Promise(resolve => setTimeout(resolve, 300));

    UnitTest.assert_values_equals(0, holder.children[0].children.length,
        "icon_manager_a_name_nobody_carries_draws_nothing_test");
    UnitTest.assert_values_equals(1, holder.children[1].querySelectorAll('svg').length,
        "icon_manager_the_rest_is_shown_test");

    holder.remove();
});


// -----------------------------------------------------------------------
// Not one set declared: nothing is drawn, and nothing raises. [063]
// -----------------------------------------------------------------------

icon_manager_tests.add_test(async () => {
    an_address_naming_no_set();
    const holder = manager_document(['back']);
    const manager = new IconManager(new IconSets(), '', a_watcher_that_sees_everything());

    await manager.run(holder);
    await new Promise(resolve => setTimeout(resolve, 300));

    UnitTest.assert_values_equals(0, holder.children[0].children.length,
        "icon_manager_no_set_at_all_draws_nothing_test");

    holder.remove();
});


// -----------------------------------------------------------------------
// A content that cannot be read leaves the room empty, and the page holds.
// -----------------------------------------------------------------------

icon_manager_tests.add_test(async () => {
    an_address_naming_no_set();
    const holder = manager_document(['unreadable']);
    const sets = new IconSets();
    sets.reference(new IconSet('ours', '/nowhere-at-all/', ['unreadable.svg']));
    const manager = new IconManager(sets, '', a_watcher_that_sees_everything());

    await manager.run(holder);
    await new Promise(resolve => setTimeout(resolve, 600));

    UnitTest.assert_values_equals(0, holder.children[0].children.length,
        "icon_manager_what_cannot_be_read_draws_nothing_test");

    holder.remove();
});


// launch all unit tests added
icon_manager_tests.launch_unit_test();
