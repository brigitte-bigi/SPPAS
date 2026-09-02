/**
:filename: tests.js.keyboardTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the KeyboardController class.

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
let keyboard_tests = new UnitTest();


/**
 * Press a key on an element of the page.
 *
 * @param {string} key - The key, as KeyboardEvent.key writes it.
 * @param {HTMLElement} [target] - What holds the focus when it is pressed.
 * @returns {KeyboardEvent} The event, to read whether it was prevented.
 */
function keyboard_press(key, target = document.body) {
    const event = new KeyboardEvent('keydown', {key: key, bubbles: true, cancelable: true});
    target.dispatchEvent(event);
    return event;
}


// -----------------------------------------------------------------------
// A declared key calls what the page said, and no other key does.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let pressed = 0;

    keyboard.register({keys: ['h', 'H'], action: () => { pressed = pressed + 1; }});
    keyboard.init();

    keyboard_press('h');
    UnitTest.assert_values_equals(1, pressed, "keyboard_answers_a_declared_key_test");

    keyboard_press('H');
    UnitTest.assert_values_equals(2, pressed, "keyboard_answers_every_key_of_a_shortcut_test");

    keyboard_press('z');
    UnitTest.assert_values_equals(2, pressed, "keyboard_says_nothing_of_a_key_it_was_not_given_test");

    keyboard.destroy();
});


// -----------------------------------------------------------------------
// The focus guard: a key pressed in a field belongs to the field.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let pressed = 0;

    keyboard.register({keys: ['n'], action: () => { pressed = pressed + 1; }});
    keyboard.init();

    const field = document.createElement('input');
    document.body.appendChild(field);
    keyboard_press('n', field);
    UnitTest.assert_values_equals(0, pressed, "keyboard_leaves_a_field_alone_test");
    field.remove();

    const link = document.createElement('a');
    link.setAttribute('href', '#');
    document.body.appendChild(link);
    keyboard_press('n', link);
    UnitTest.assert_values_equals(0, pressed, "keyboard_leaves_a_link_alone_test");
    link.remove();

    const reachable = document.createElement('div');
    reachable.setAttribute('tabindex', '0');
    document.body.appendChild(reachable);
    keyboard_press('n', reachable);
    UnitTest.assert_values_equals(0, pressed, "keyboard_leaves_what_a_page_made_reachable_alone_test");
    reachable.remove();

    const plain = document.createElement('div');
    document.body.appendChild(plain);
    keyboard_press('n', plain);
    UnitTest.assert_values_equals(1, pressed, "keyboard_answers_on_an_element_holding_no_key_test");
    plain.remove();

    keyboard.destroy();
});


// -----------------------------------------------------------------------
// Enter and space operate what holds the focus: they are never declared.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let pressed = 0;

    keyboard.register({keys: ['Enter', ' '], action: () => { pressed = pressed + 1; }});
    keyboard.init();

    keyboard_press('Enter');
    keyboard_press(' ');
    UnitTest.assert_values_equals(0, pressed, "keyboard_never_answers_enter_nor_space_test");

    keyboard.destroy();
});


// -----------------------------------------------------------------------
// A shortcut says an event when it is given a name instead of a function.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let said = null;

    const listener = (event) => { said = event.detail; };
    document.addEventListener('test:keyboard', listener);

    keyboard.register({keys: ['t'], action: 'test:keyboard', detail: {action: 'next'}});
    keyboard.init();
    keyboard_press('t');

    UnitTest.assert_object_equals({action: 'next'}, said, "keyboard_says_the_event_it_was_given_test");

    document.removeEventListener('test:keyboard', listener);
    keyboard.destroy();
});


// -----------------------------------------------------------------------
// A key that scrolls the page says so, and the browser is kept from acting.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();

    keyboard.register({keys: ['ArrowDown'], action: () => {}, preventsDefault: true});
    keyboard.register({keys: ['ArrowUp'], action: () => {}});
    keyboard.init();

    UnitTest.assert_values_equals(true, keyboard_press('ArrowDown').defaultPrevented,
        "keyboard_keeps_the_browser_from_scrolling_test");
    UnitTest.assert_values_equals(false, keyboard_press('ArrowUp').defaultPrevented,
        "keyboard_lets_the_browser_act_when_nothing_asks_otherwise_test");

    keyboard.destroy();
});


// -----------------------------------------------------------------------
// What the page answers is said, for a help dialog to be written from it.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();

    keyboard.register({keys: ['f', 'F'], action: () => {}, label: 'Fullscreen'});
    keyboard.register({keys: ['o'], action: () => {}, label: 'Overview'});

    const said = keyboard.shortcuts;
    UnitTest.assert_values_equals(2, said.length, "keyboard_says_one_entry_per_shortcut_test");
    UnitTest.assert_values_equals('Fullscreen', said[0].label, "keyboard_says_what_the_keys_are_for_test");
    UnitTest.assert_array_contains('F', said[0].keys, "keyboard_says_every_key_of_a_shortcut_test");
});


// -----------------------------------------------------------------------
// A key given back is answered no more.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let pressed = 0;

    keyboard.register({keys: ['g'], action: () => { pressed = pressed + 1; }});
    keyboard.init();
    keyboard_press('g');

    keyboard.forget(['g']);
    keyboard_press('g');
    UnitTest.assert_values_equals(1, pressed, "keyboard_forgets_a_key_test");

    keyboard.destroy();
    keyboard_press('g');
    UnitTest.assert_values_equals(1, pressed, "keyboard_answers_nothing_once_destroyed_test");
});


// -----------------------------------------------------------------------
// Listening twice answers once.
// -----------------------------------------------------------------------

keyboard_tests.add_test(() => {
    const keyboard = new KeyboardController();
    let pressed = 0;

    keyboard.register({keys: ['j'], action: () => { pressed = pressed + 1; }});
    keyboard.init();
    keyboard.init();
    keyboard_press('j');

    UnitTest.assert_values_equals(1, pressed, "keyboard_listens_once_test");

    keyboard.destroy();
});


keyboard_tests.launch_unit_test();
