/**
:filename: tests.js.slide_layoutTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlideLayout class.

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
let slide_layout_tests = new UnitTest();


/**
 * Build a block of a given height, at a given place.
 *
 * @param place {Number} Its place in the order the content is written.
 * @param height {Number} Its measured height.
 * @returns {SlideBlock}
 */
function slide_layout_block(place, height) {
    const block = new SlideBlock(document.createElement('p'), place);
    block.height = height;
    return block;
}


// -----------------------------------------------------------------------
// How many slides a layout asks for.
// -----------------------------------------------------------------------

slide_layout_tests.add_test(() => {
    const first = slide_layout_block(1, 100);
    const second = slide_layout_block(2, 100);
    const layout = new SlideLayout([[first], [second]]);

    UnitTest.assert_values_equals(2, layout.count(), "layout_counts_its_parts_test");
    UnitTest.assert_values_equals(first, layout.parts[0][0], "layout_keeps_the_order_test");
    UnitTest.assert_values_equals(second, layout.parts[1][0], "layout_keeps_the_order_of_the_second_test");
});

// -----------------------------------------------------------------------
// A slide holding nothing but its title asks for one slide, and no more.
// -----------------------------------------------------------------------

slide_layout_tests.add_test(() => {
    const layout = new SlideLayout([[]]);

    UnitTest.assert_values_equals(1, layout.count(), "empty_layout_counts_one_test");
    UnitTest.assert_values_equals(0, layout.parts[0].length, "empty_layout_has_no_block_test");
});

// -----------------------------------------------------------------------
// The blocks that are taller than a slide on their own. Console message.
// -----------------------------------------------------------------------

slide_layout_tests.add_test(() => {
    const small = slide_layout_block(1, 100);
    const huge = slide_layout_block(2, 900);
    const layout = new SlideLayout([[small], [huge]]);

    const oversized = layout.oversized(400);

    UnitTest.assert_values_equals(1, oversized.length, "layout_finds_one_oversized_block_test");
    UnitTest.assert_values_equals(huge, oversized[0], "layout_finds_the_right_oversized_block_test");
});

slide_layout_tests.add_test(() => {
    const layout = new SlideLayout([[slide_layout_block(1, 100), slide_layout_block(2, 150)]]);

    UnitTest.assert_values_equals(0, layout.oversized(400).length, "layout_without_oversized_block_test");
});


// launch all unit tests added
slide_layout_tests.launch_unit_test();
