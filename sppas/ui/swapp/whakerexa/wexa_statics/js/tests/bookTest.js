/**
:filename: tests.js.bookTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the Book class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-07-31.
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
let book_tests = new UnitTest();


/**
 * Write in the page a document made of chapters, sections and sub-sections.
 *
 * The markup is the one book.css numbers: a chapter holds sections, a section
 * holds sub-sections, and a chapter bearing "nonumber" is numbered by nobody.
 *
 * @param {string} name - What tells the elements of this test from the others.
 * @param {string} content - The chapters, written in HTML.
 * @returns {Object} The container, the list of the table of contents, and what removes them.
 */
function write_book(name, content) {
    const holder = document.createElement('div');
    holder.id = name + '-holder';

    const list = document.createElement('ul');
    list.id = name + '-toc';

    const container = document.createElement('div');
    container.id = name + '-content';
    container.innerHTML = content;

    holder.appendChild(list);
    holder.appendChild(container);
    document.body.appendChild(holder);

    return {
        container: container,
        list: list,
        entries: () => Array.from(list.querySelectorAll('a')).map(link => link.textContent),
        remove: () => holder.remove()
    };
}


// -----------------------------------------------------------------------
// An entry says which level it comes from: book.css numbers it from that,
// and nothing counts anything twice.
// -----------------------------------------------------------------------

book_tests.add_test(() => {
    const written = write_book('levels', `
        <section class="chapter"><h1>First chapter</h1>
            <section class="ssection"><h2>A section</h2>
                <article class="subssection"><h3>A sub-section</h3></article>
            </section>
        </section>`);

    new Book('levels-content', 'levels-toc').fill_table(false);
    const items = written.list.querySelectorAll('li');

    UnitTest.assert_values_equals('h1', items[0].getAttribute('class'), "book_entry_h1_test");
    UnitTest.assert_values_equals('h2', items[1].getAttribute('class'), "book_entry_h2_test");
    UnitTest.assert_values_equals('h3', items[2].getAttribute('class'), "book_entry_h3_test");

    written.remove();
});

// -----------------------------------------------------------------------
// An entry coming from a chapter that bears "nonumber" bears it too: it is
// the one thing a stylesheet cannot see from the table of contents.
// -----------------------------------------------------------------------

book_tests.add_test(() => {
    const written = write_book('nonumber', `
        <section class="chapter"><h1>First chapter</h1></section>
        <section class="chapter nonumber"><h1>Foreword</h1>
            <section class="ssection"><h2>A section of the foreword</h2></section>
        </section>`);

    new Book('nonumber-content', 'nonumber-toc').fill_table(false);
    const items = written.list.querySelectorAll('li');

    UnitTest.assert_values_equals('h1', items[0].getAttribute('class'), "book_numbered_entry_test");
    UnitTest.assert_values_equals('h1 nonumber', items[1].getAttribute('class'),
        "book_nonumber_entry_test");
    UnitTest.assert_values_equals('h2 nonumber', items[2].getAttribute('class'),
        "book_nonumber_section_entry_test");

    written.remove();
});

// -----------------------------------------------------------------------
// The text of an entry is the text of its title, and nothing more: the
// number is written by book.css, on the entry itself.
// -----------------------------------------------------------------------

book_tests.add_test(() => {
    const written = write_book('text', '<section class="chapter"><h1>A chapter</h1></section>');

    new Book('text-content', 'text-toc').fill_table(false);

    UnitTest.assert_values_equals('A chapter', written.entries()[0], "book_entry_text_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Every heading leads to where it stands in the document.
// -----------------------------------------------------------------------

book_tests.add_test(() => {
    const written = write_book('links', '<section class="chapter"><h1>A chapter</h1></section>');

    new Book('links-content', 'links-toc').fill_table(false);
    const link = written.list.querySelector('a');

    UnitTest.assert_values_equals('#toc0', link.getAttribute('href'), "book_link_target_test");
    UnitTest.assert_values_not_equals(null, written.container.querySelector('#toc0'),
        "book_anchor_written_test");

    written.remove();
});


// launch all unit tests added
book_tests.launch_unit_test();
