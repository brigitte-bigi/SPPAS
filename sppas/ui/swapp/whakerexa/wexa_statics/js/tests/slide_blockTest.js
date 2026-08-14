/**
:filename: tests.js.slide_blockTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlideBlock class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-08-03.
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
let slide_block_tests = new UnitTest();


// -----------------------------------------------------------------------
// What a block carries, and what it knows before anything measures it.
// -----------------------------------------------------------------------

slide_block_tests.add_test(() => {
    const element = document.createElement('li');
    const block = new SlideBlock(element, 1);

    UnitTest.assert_values_equals(element, block.element, "block_keeps_its_element_test");
    UnitTest.assert_values_equals(1, block.place, "block_keeps_its_place_test");
    UnitTest.assert_values_equals(0, block.height, "block_height_is_zero_before_measure_test");
});

// -----------------------------------------------------------------------
// The height is written once, by whoever measures.
// -----------------------------------------------------------------------

slide_block_tests.add_test(() => {
    const block = new SlideBlock(document.createElement('tr'), 2);
    block.height = 120;

    UnitTest.assert_values_equals(120, block.height, "block_takes_its_measured_height_test");
});

// -----------------------------------------------------------------------
// fitsIn compares two numbers, and nothing else.
// -----------------------------------------------------------------------

slide_block_tests.add_test(() => {
    const block = new SlideBlock(document.createElement('p'), 1);
    block.height = 100;

    UnitTest.assert_values_equals(true, block.fitsIn(150), "block_fits_in_more_room_test");
    UnitTest.assert_values_equals(true, block.fitsIn(100), "block_fits_in_exact_room_test");
    UnitTest.assert_values_equals(false, block.fitsIn(99), "block_does_not_fit_in_less_room_test");
    UnitTest.assert_values_equals(false, block.fitsIn(0), "block_does_not_fit_in_no_room_test");
});


// launch all unit tests added
slide_block_tests.launch_unit_test();
