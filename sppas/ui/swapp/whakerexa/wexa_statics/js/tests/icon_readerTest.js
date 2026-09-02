/**
:filename: tests.js.icon_readerTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the IconContent and IconReader classes.

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
let icon_reader_tests = new UnitTest();


/**
 * Give the set of the framework, as it stands in this repository.
 *
 * @returns {IconSet} A set whose files are really there.
 *
 */
function a_real_set() {
    return new IconSet('mono-svg', '/wexa_statics/icons/mono-svg/',
                       ['back.svg', 'first.svg']);
}


/**
 * Give a set naming files nothing stands behind.
 *
 * @returns {IconSet}
 *
 */
function a_set_of_nothing() {
    return new IconSet('ghost', '/wexa_statics/icons/ghost/',
                       ['home.svg', 'home-image.webp']);
}


// -----------------------------------------------------------------------
// A line drawing is read, and its markup is what answers.
// -----------------------------------------------------------------------

icon_reader_tests.add_test(async () => {
    const reader = new IconReader();
    const content = await reader.read(a_real_set(), 'back');

    UnitTest.assert_values_equals('line', content.form,
        "icon_reader_a_svg_is_a_line_test");
    UnitTest.assert_values_equals(true, content.source.includes('<svg'),
        "icon_reader_a_line_answers_with_its_markup_test");
});


// -----------------------------------------------------------------------
// An image is not read: its address is what answers. Nothing is fetched
// twice, which is what [026] and the RGESN ask.
// -----------------------------------------------------------------------

icon_reader_tests.add_test(async () => {
    const reader = new IconReader();
    const set = new IconSet('logos', '/wexa_statics/logos/', ['whakerexa-128.webp']);
    const content = await reader.read(set, 'whakerexa-128');

    UnitTest.assert_values_equals('image', content.form,
        "icon_reader_an_image_is_an_image_test");
    UnitTest.assert_values_equals('/wexa_statics/logos/whakerexa-128.webp', content.source,
        "icon_reader_an_image_answers_with_its_address_test");
});


// -----------------------------------------------------------------------
// What was gathered into the document answers without anything being read:
// that is how a document opened from a disk is served. [041]
// -----------------------------------------------------------------------

icon_reader_tests.add_test(async () => {
    const reader = new IconReader();
    reader.gather('ghost', 'home', '<svg id="gathered"></svg>');

    const content = await reader.read(a_set_of_nothing(), 'home');

    UnitTest.assert_values_equals('<svg id="gathered"></svg>', content.source,
        "icon_reader_what_was_gathered_answers_test");
});


// -----------------------------------------------------------------------
// A line drawing is read once: the second demand is answered by the first.
// -----------------------------------------------------------------------

icon_reader_tests.add_test(async () => {
    const reader = new IconReader();
    const set = a_real_set();

    const first = await reader.read(set, 'first');
    const second = await reader.read(set, 'first');

    UnitTest.assert_values_equals(first.source, second.source,
        "icon_reader_read_once_test");
});


// -----------------------------------------------------------------------
// A line drawing nothing stands behind cannot be read, and it is said.
// -----------------------------------------------------------------------

icon_reader_tests.add_test(async () => {
    const reader = new IconReader();
    let raised = '';

    try {
        await reader.read(a_set_of_nothing(), 'home');
    } catch (error) {
        raised = error.name;
    }

    UnitTest.assert_values_equals('UnreadableContent', raised,
        "icon_reader_what_cannot_be_read_test");
});


// launch all unit tests added
icon_reader_tests.launch_unit_test();
