/**
:filename: tests.js.icon_placerTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconDemand and IconPlacer classes.

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
let icon_placer_tests = new UnitTest();


/**
 * Put an element in the page, and give the demand it carries.
 *
 * @param {string} attribute - data-icon for a place, data-ground for a surface.
 * @param {string} name - The name it asks for.
 * @returns {IconDemand} The demand, its element added to the document.
 *
 */
function a_demand(attribute, name) {
    const element = document.createElement('button');
    element.id = 'placer-' + attribute + '-' + name;
    element.setAttribute(attribute, name);
    element.setAttribute('aria-label', 'What it stands for');
    document.body.appendChild(element);

    return IconDemand.of(element);
}


/**
 * Take away what a test put in the page.
 *
 * @param {IconDemand} demand
 * @returns {void}
 *
 */
function forget(demand) {
    demand.element.remove();
}


// -----------------------------------------------------------------------
// An element says what it asks for, and what kind of demand it is. C8
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const place = a_demand('data-icon', 'back');
    const surface = a_demand('data-ground', 'paper');

    UnitTest.assert_values_equals('back', place.name, "icon_demand_name_test");
    UnitTest.assert_values_equals('place', place.kind, "icon_demand_a_place_test");
    UnitTest.assert_values_equals('surface', surface.kind, "icon_demand_a_surface_test");

    forget(place);
    forget(surface);
});


// -----------------------------------------------------------------------
// An element that asks for nothing is no demand at all.
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const element = document.createElement('span');
    document.body.appendChild(element);

    UnitTest.assert_values_equals(null, IconDemand.of(element),
        "icon_demand_of_nothing_test");

    element.remove();
});


// -----------------------------------------------------------------------
// A line drawing is written into the element, so that it takes the color
// of what surrounds it. [032]
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const placer = new IconPlacer();
    const demand = a_demand('data-icon', 'back');
    const content = new IconContent('back', 'line',
        '<svg viewBox="0 0 32 32"><polyline points="20 24 12 16 20 8"/></svg>');

    placer.place(demand, content);

    UnitTest.assert_values_equals(1, demand.element.querySelectorAll('svg').length,
        "icon_placer_a_line_is_written_in_test");
    UnitTest.assert_values_equals(0, demand.element.querySelectorAll('img').length,
        "icon_placer_a_line_is_no_image_test");

    forget(demand);
});


// -----------------------------------------------------------------------
// An image is put in an <img>, which carries the room the place declared,
// so that nothing waits for the file to know it. [037] RGESN
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const placer = new IconPlacer();
    const demand = a_demand('data-icon', 'logo');
    demand.element.style.setProperty('--icon-width', '32px');
    demand.element.style.setProperty('--icon-height', '24px');
    const content = new IconContent('logo', 'image', '/wexa_statics/logos/whakerexa-128.webp');

    placer.place(demand, content);
    const image = demand.element.querySelector('img');

    UnitTest.assert_values_equals('/wexa_statics/logos/whakerexa-128.webp',
        image.getAttribute('src'), "icon_placer_an_image_keeps_its_address_test");
    UnitTest.assert_values_equals('32', image.getAttribute('width'),
        "icon_placer_an_image_carries_its_width_test");
    UnitTest.assert_values_equals('24', image.getAttribute('height'),
        "icon_placer_an_image_carries_its_height_test");
    UnitTest.assert_values_equals('', image.getAttribute('alt'),
        "icon_placer_an_image_says_nothing_test");

    forget(demand);
});


// -----------------------------------------------------------------------
// A ground covers a surface, and is written nowhere: it stands for
// nothing, and a surface keeps the room it has. [074] [075]
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const placer = new IconPlacer();
    const demand = a_demand('data-ground', 'paper');
    const content = new IconContent('paper', 'image', '/wexa_statics/logos/whakerexa-128.webp');

    placer.place(demand, content);

    UnitTest.assert_values_equals(0, demand.element.children.length,
        "icon_placer_a_ground_writes_nothing_in_test");
    UnitTest.assert_values_equals(true,
        demand.element.style.backgroundImage.includes('whakerexa-128.webp'),
        "icon_placer_a_ground_covers_test");

    forget(demand);
});


// -----------------------------------------------------------------------
// Placing again takes the first content away: an element never holds two.
// [027]
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const placer = new IconPlacer();
    const demand = a_demand('data-icon', 'back');

    placer.place(demand, new IconContent('back', 'line', '<svg id="one"></svg>'));
    placer.place(demand, new IconContent('back', 'line', '<svg id="two"></svg>'));

    UnitTest.assert_values_equals(1, demand.element.querySelectorAll('svg').length,
        "icon_placer_one_content_at_a_time_test");
    UnitTest.assert_values_equals('two',
        demand.element.querySelector('svg').getAttribute('id'),
        "icon_placer_the_last_one_stays_test");

    forget(demand);
});


// -----------------------------------------------------------------------
// Clearing leaves the element empty, and says nothing. Calling it twice
// does nothing wrong.
// -----------------------------------------------------------------------

icon_placer_tests.add_test(() => {
    const placer = new IconPlacer();
    const demand = a_demand('data-icon', 'back');

    placer.place(demand, new IconContent('back', 'line', '<svg></svg>'));
    placer.clear(demand);
    placer.clear(demand);

    UnitTest.assert_values_equals(0, demand.element.children.length,
        "icon_placer_clear_leaves_nothing_test");
    UnitTest.assert_values_equals('What it stands for',
        demand.element.getAttribute('aria-label'),
        "icon_placer_clear_leaves_what_it_stands_for_test");

    forget(demand);
});


// launch all unit tests added
icon_placer_tests.launch_unit_test();
