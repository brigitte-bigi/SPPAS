/**
:filename: tests.js.slide_paginatorTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlidePaginator class.

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

    This is the class that needs no browser: it receives heights and gives a
    distribution back. Everything the requirement B23 asks for is checked here.

*/

// instantiate unit tests class
let slide_paginator_tests = new UnitTest();


/**
 * Build blocks of the given heights, in the order they are written.
 *
 * @param heights {Number[]} One height per block.
 * @returns {SlideBlock[]}
 */
function slide_paginator_blocks(heights) {
    return heights.map((height, index) => {
        const block = new SlideBlock(document.createElement('p'), index + 1);
        block.height = height;
        return block;
    });
}

/**
 * Give the places of the blocks of each part, part by part.
 *
 * @param layout {SlideLayout} The distribution to read.
 * @returns {Number[][]}
 */
function slide_paginator_places(layout) {
    return layout.parts.map(part => part.map(block => block.place));
}


// -----------------------------------------------------------------------
// Everything fits: one slide, and nothing is engendered. Requirement B23.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate(slide_paginator_blocks([100, 100, 100]), 400);

    UnitTest.assert_values_equals(1, layout.count(), "paginate_one_slide_when_all_fit_test");
    UnitTest.assert_object_equals([[1, 2, 3]], slide_paginator_places(layout), "paginate_keeps_all_blocks_test");
});

// -----------------------------------------------------------------------
// A slide more as soon as the next block does not fit.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate(slide_paginator_blocks([100, 100, 100, 100]), 250);

    UnitTest.assert_values_equals(2, layout.count(), "paginate_adds_a_slide_test");
    UnitTest.assert_object_equals([[1, 2], [3, 4]], slide_paginator_places(layout), "paginate_cuts_between_blocks_test");
});

// -----------------------------------------------------------------------
// Nothing is lost, nothing is placed twice, and the order is the written one.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate(slide_paginator_blocks([90, 80, 200, 30, 150]), 250);

    const places = slide_paginator_places(layout).flat();

    UnitTest.assert_object_equals([1, 2, 3, 4, 5], places, "paginate_places_every_block_once_and_in_order_test");
});

// -----------------------------------------------------------------------
// A block taller than a slide stays whole, and stands alone.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate(slide_paginator_blocks([100, 900, 100]), 400);

    UnitTest.assert_object_equals([[1], [2], [3]], slide_paginator_places(layout), "paginate_isolates_an_oversized_block_test");
    UnitTest.assert_values_equals(1, layout.oversized(400).length, "paginate_reports_the_oversized_block_test");
});

// -----------------------------------------------------------------------
// A block of exactly the height left fits: the room is what it says.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate(slide_paginator_blocks([200, 200]), 400);

    UnitTest.assert_values_equals(1, layout.count(), "paginate_fills_the_room_exactly_test");
});

// -----------------------------------------------------------------------
// A slide holding nothing but its title: one part, and it is empty.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const layout = paginator.paginate([], 400);

    UnitTest.assert_values_equals(1, layout.count(), "paginate_without_block_gives_one_part_test");
    UnitTest.assert_values_equals(0, layout.parts[0].length, "paginate_without_block_gives_an_empty_part_test");
});

// -----------------------------------------------------------------------
// The same content, in the same room, gives the same distribution.
// -----------------------------------------------------------------------

slide_paginator_tests.add_test(() => {
    const paginator = new SlidePaginator();
    const first = paginator.paginate(slide_paginator_blocks([90, 80, 200, 30, 150]), 250);
    const second = paginator.paginate(slide_paginator_blocks([90, 80, 200, 30, 150]), 250);

    UnitTest.assert_object_equals(slide_paginator_places(first), slide_paginator_places(second),
        "paginate_gives_the_same_result_twice_test");
});


// launch all unit tests added
slide_paginator_tests.launch_unit_test();
