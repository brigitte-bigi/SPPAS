/**
:filename: tests.js.icon_registerTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconRegister class.

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
let icon_register_tests = new UnitTest();


/**
 * Put an element in the page and give the demand it carries.
 *
 * @param {string} name - The name it asks for.
 * @returns {IconDemand}
 *
 */
function a_held_demand(name) {
    const element = document.createElement('button');
    element.setAttribute('data-icon', name);
    document.body.appendChild(element);
    return IconDemand.of(element);
}


// -----------------------------------------------------------------------
// What is held is given back.
// -----------------------------------------------------------------------

icon_register_tests.add_test(() => {
    const register = new IconRegister();
    const demand = a_held_demand('back');

    register.hold(demand);

    UnitTest.assert_values_equals(1, register.held().length,
        "icon_register_holds_test");
    UnitTest.assert_values_equals('back', register.held()[0].name,
        "icon_register_gives_back_test");

    demand.element.remove();
});


// -----------------------------------------------------------------------
// One demand is held once, however many times it is answered.
// -----------------------------------------------------------------------

icon_register_tests.add_test(() => {
    const register = new IconRegister();
    const demand = a_held_demand('first');

    register.hold(demand);
    register.hold(demand);

    UnitTest.assert_values_equals(1, register.held().length,
        "icon_register_holds_a_demand_once_test");

    demand.element.remove();
});


// -----------------------------------------------------------------------
// A demand whose element left the document is not given back: what is not
// there is not answered again. [027]
// -----------------------------------------------------------------------

icon_register_tests.add_test(() => {
    const register = new IconRegister();
    const staying = a_held_demand('back');
    const leaving = a_held_demand('first');

    register.hold(staying);
    register.hold(leaving);
    leaving.element.remove();

    UnitTest.assert_values_equals(1, register.held().length,
        "icon_register_forgets_what_left_test");
    UnitTest.assert_values_equals('back', register.held()[0].name,
        "icon_register_keeps_what_stayed_test");

    staying.element.remove();
});


// -----------------------------------------------------------------------
// Nothing held, nothing given back.
// -----------------------------------------------------------------------

icon_register_tests.add_test(() => {
    const register = new IconRegister();

    UnitTest.assert_values_equals(0, register.held().length,
        "icon_register_holds_nothing_test");
});


// launch all unit tests added
icon_register_tests.launch_unit_test();
