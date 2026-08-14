/**
:filename: tests.js.bibauthorTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the Author class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-07-28.
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
let author_tests = new UnitTest();


// -----------------------------------------------------------------------
// A full name is written in the order it is signed. Requirement B11.
// -----------------------------------------------------------------------

author_tests.add_test(() => {
    const author = new Author(1, 'Brigitte', '', 'Bigi', '');

    UnitTest.assert_values_equals('Brigitte Bigi', author.text(), "author_text_test");
    UnitTest.assert_values_equals(1, author.place, "author_place_test");
});

// -----------------------------------------------------------------------
// A particle and a suffix take their place in the name.
// -----------------------------------------------------------------------

author_tests.add_test(() => {
    const author = new Author(2, 'Ludwig', 'van', 'Beethoven', '');
    const junior = new Author(3, 'John', '', 'Smith', 'Jr');

    UnitTest.assert_values_equals('Ludwig van Beethoven', author.text(), "author_text_particle_test");
    UnitTest.assert_values_equals('John Smith Jr', junior.text(), "author_text_suffix_test");
});

// -----------------------------------------------------------------------
// A name reduced to its last name has no extra space.
// -----------------------------------------------------------------------

author_tests.add_test(() => {
    const author = new Author(1, '', '', 'Aristotle', '');

    UnitTest.assert_values_equals('Aristotle', author.text(), "author_text_last_name_only_test");
});

// -----------------------------------------------------------------------
// The value used to sort puts the last name first. Requirement B16.
// -----------------------------------------------------------------------

author_tests.add_test(() => {
    const author = new Author(1, 'Brigitte', '', 'Bigi', '');
    const with_particle = new Author(2, 'Ludwig', 'van', 'Beethoven', '');

    UnitTest.assert_values_equals('Bigi, Brigitte', author.sortValue(), "author_sort_value_test");
    UnitTest.assert_values_equals('Beethoven, Ludwig van', with_particle.sortValue(),
        "author_sort_value_particle_test");
});

// -----------------------------------------------------------------------
// An author never gives null, whatever is missing. Requirement B4.
// -----------------------------------------------------------------------

author_tests.add_test(() => {
    const author = new Author(1, '', '', '', '');

    UnitTest.assert_values_equals('', author.text(), "author_empty_text_test");
    UnitTest.assert_values_equals('', author.firstName, "author_empty_first_name_test");
    UnitTest.assert_values_equals('', author.particle, "author_empty_particle_test");
    UnitTest.assert_values_equals('', author.suffix, "author_empty_suffix_test");
});


// launch all unit tests added
author_tests.launch_unit_test();
