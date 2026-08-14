/**
:filename: tests.js.slide_block_readerTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SlideBlockReader class.

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

    The smallest part that can be laid down on its own: a row for a table, an
    item for a list, a child otherwise. This class is the only one that knows.

*/

// instantiate unit tests class
let slide_block_reader_tests = new UnitTest();


/**
 * Build a slide out of written markup, outside of the document.
 *
 * @param markup {String} What the author writes inside the slide.
 * @returns {HTMLElement}
 */
function slide_block_reader_slide(markup) {
    const slide = document.createElement('section');
    slide.className = 'slide';
    slide.innerHTML = markup;
    return slide;
}


// -----------------------------------------------------------------------
// The title is never a block: it is repeated, not distributed.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide('<h2>References</h2><p>One</p><p>Two</p>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(2, blocks.length, "reader_leaves_the_title_out_test");
    UnitTest.assert_values_equals('P', blocks[0].element.tagName, "reader_takes_the_children_test");
    UnitTest.assert_values_equals(1, blocks[0].place, "reader_numbers_from_one_test");
    UnitTest.assert_values_equals(2, blocks[1].place, "reader_numbers_in_order_test");
});

// -----------------------------------------------------------------------
// A table is read row by row.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide(
        '<h2>Timing</h2>'
        + '<table><thead><tr><th>Key</th></tr></thead>'
        + '<tbody><tr><td>C-</td></tr><tr><td>-V</td></tr><tr><td>CV</td></tr></tbody></table>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(3, blocks.length, "reader_reads_a_table_row_by_row_test");
    UnitTest.assert_values_equals('TR', blocks[0].element.tagName, "reader_gives_rows_test");
    UnitTest.assert_values_equals('C-', blocks[0].element.textContent, "reader_keeps_the_first_row_test");
});

// -----------------------------------------------------------------------
// The head of a table is not a block: it is repeated on each slide.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide(
        '<table><thead><tr><th>Key</th></tr></thead><tbody><tr><td>CV</td></tr></tbody></table>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(1, blocks.length, "reader_leaves_the_table_head_out_test");
});

// -----------------------------------------------------------------------
// A list is read item by item.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide('<h2>Summary</h2><ul><li>One</li><li>Two</li><li>Three</li></ul>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(3, blocks.length, "reader_reads_a_list_item_by_item_test");
    UnitTest.assert_values_equals('LI', blocks[0].element.tagName, "reader_gives_items_test");
});

// -----------------------------------------------------------------------
// A container holding a table is read through: what makes it tall is inside
// it. This is what a bibliography written in a slide looks like.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide(
        '<h3>References</h3>'
        + '<div id="bibliography">'
        + '<p class="bib-announcement">Sorted by number</p>'
        + '<table><thead><tr><th>No.</th></tr></thead>'
        + '<tbody><tr><td>1</td></tr><tr><td>2</td></tr><tr><td>3</td></tr></tbody></table>'
        + '</div>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(4, blocks.length, "reader_reads_through_a_container_test");
    UnitTest.assert_values_equals('P', blocks[0].element.tagName, "reader_keeps_what_is_before_the_table_test");
    UnitTest.assert_values_equals('TR', blocks[1].element.tagName, "reader_gives_the_rows_of_a_held_table_test");
});

// -----------------------------------------------------------------------
// A container holding neither a table nor a list stays one block: what was
// written side by side is not taken apart.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide(
        '<h3>Two figures</h3>'
        + '<section class="flex-panel">'
        + '<figure><img src="one.png" alt="one"></figure>'
        + '<figure><img src="two.png" alt="two"></figure>'
        + '</section>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(1, blocks.length, "reader_keeps_a_panel_whole_test");
    UnitTest.assert_values_equals('SECTION', blocks[0].element.tagName, "reader_gives_the_panel_test");
});

// -----------------------------------------------------------------------
// A slide with nothing but a title has nothing to distribute.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide('<h1>The CLeLfPC corpus</h1>');

    UnitTest.assert_values_equals(0, reader.blocks(slide).length, "reader_gives_nothing_for_a_title_only_slide_test");
});

// -----------------------------------------------------------------------
// The notes stay with the slide they were written for: they are not blocks.
// -----------------------------------------------------------------------

slide_block_reader_tests.add_test(() => {
    const reader = new SlideBlockReader();
    const slide = slide_block_reader_slide('<h2>Corpus</h2><p>One</p><aside role="note"><p>Said aloud</p></aside>');

    const blocks = reader.blocks(slide);

    UnitTest.assert_values_equals(1, blocks.length, "reader_leaves_the_notes_out_test");
    UnitTest.assert_values_equals('P', blocks[0].element.tagName, "reader_keeps_the_content_test");
});


// launch all unit tests added
slide_block_reader_tests.launch_unit_test();
