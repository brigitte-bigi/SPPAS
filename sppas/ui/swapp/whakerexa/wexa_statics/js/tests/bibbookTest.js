/**
:filename: tests.js.bibbookTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the BookBibliography class.

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
let book_bibliography_tests = new UnitTest();


/**
 * Write in the page what a document holds: the data, and a place for the table.
 *
 * Every test writes its own elements under its own name: the tests are started
 * one after the other but not waited for, so two of them live in the page at
 * the same time.
 *
 * @param {string} name - What tells the elements of this test from the others.
 * @param {string} data - The BibTeX data, or an empty string for a page without any.
 * @returns {HTMLElement[]} The two elements, to be removed once the test is over.
 */
function write_document(name, data) {
    const written = document.createElement('pre');
    written.id = name + '-data';
    written.hidden = true;
    written.textContent = data;
    document.body.appendChild(written);

    const place = document.createElement('div');
    place.id = name + '-place';
    document.body.appendChild(place);

    return [written, place];
}


// -----------------------------------------------------------------------
// The bibliography is put where the page says, and holds one row per
// reference.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('rows', String.raw`
@article{book2026one,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    year = {2026}
}

@misc{book2026two,
    author = {Alain Ghio},
    title = {Another Title},
    year = {2023}
}`);

    const biblio = new BookBibliography('rows-data', 'rows-place', 'main-content');
    await biblio.run();

    const place = document.getElementById('rows-place');
    UnitTest.assert_values_not_equals(null, place.querySelector('table'), "book_table_written_test");
    UnitTest.assert_values_equals(2, place.querySelectorAll('tbody tr.bib-row').length, "book_rows_test");
    UnitTest.assert_values_not_equals(null, place.querySelector('#bib-book2026one'),
        "book_row_identifier_test");

    parts.forEach(part => part.remove());
});

// -----------------------------------------------------------------------
// Without any citation, the table has no number column: a page of
// publications is a bibliography nobody cites.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('alone', '@misc{book2026alone, title = {A Title}}');

    await new BookBibliography('alone-data', 'alone-place').run();

    const place = document.getElementById('alone-place');
    UnitTest.assert_values_equals(null, place.querySelector('button[data-sort="number"]'),
        "book_no_number_column_test");

    parts.forEach(part => part.remove());
});

// -----------------------------------------------------------------------
// Without any data, nothing is raised and the page keeps everything else
// it has. Requirement C32 asks no less of a page whose script did run.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('nodata', '');
    let raised = '';

    try {
        await new BookBibliography('nodata-data', 'nodata-place').run();
    } catch (error) {
        raised = error.name;
    }

    UnitTest.assert_values_equals('', raised, "book_no_data_does_not_raise_test");
    UnitTest.assert_values_equals('', document.getElementById('nodata-place').innerHTML,
        "book_no_data_leaves_place_empty_test");

    parts.forEach(part => part.remove());
});

// -----------------------------------------------------------------------
// Without any place to put it, nothing is raised either. The citations
// would still be numbered: they are in the text, and the text is there.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('noplace', '@misc{book2026nowhere, title = {A Title}}');
    let raised = '';

    try {
        await new BookBibliography('noplace-data', 'nothing-like-a-place').run();
    } catch (error) {
        raised = error.name;
    }

    UnitTest.assert_values_equals('', raised, "book_no_place_does_not_raise_test");

    parts.forEach(part => part.remove());
});

// -----------------------------------------------------------------------
// Opening the page again gives the same thing, and never two tables.
// Requirement C30.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('twice', '@misc{book2026twice, title = {A Title}}');
    const biblio = new BookBibliography('twice-data', 'twice-place');

    await biblio.run();
    const once = document.getElementById('twice-place').innerHTML;

    await biblio.run();
    const twice = document.getElementById('twice-place').innerHTML;

    UnitTest.assert_values_equals(1, document.getElementById('twice-place').querySelectorAll('table').length,
        "book_one_table_test");
    UnitTest.assert_values_equals(once, twice, "book_same_result_test");

    parts.forEach(part => part.remove());
});


// -----------------------------------------------------------------------
// A text that cites gets its citations numbered, and the table gets the
// number column and a link back to every place. C11, C26 and C27.
// -----------------------------------------------------------------------

book_bibliography_tests.add_test(async () => {
    const parts = write_document('cited', String.raw`
@misc{book2026cited, author = {Brigitte Bigi}, title = {A Title}, year = {2026}}

@misc{book2026uncited, author = {Alain Ghio}, title = {Another Title}, year = {2023}}`);

    const text = document.createElement('div');
    text.id = 'cited-text';
    text.innerHTML = 'This is said in <span data-bibtex="book2026cited">Bigi, 2026</span>.';
    document.body.appendChild(text);

    await new BookBibliography('cited-data', 'cited-place', 'cited-text').run();

    const place = document.getElementById('cited-place');
    // The number is written twice: the button that opens the reference, and the
    // anchor that stays a link on paper. Both say the same number.
    UnitTest.assert_values_equals('[1]', text.querySelector('[data-bibtex] .bib-citation-control').textContent,
        "book_citation_numbered_test");
    UnitTest.assert_values_equals('[1]', text.querySelector('[data-bibtex] .bib-citation-anchor').textContent,
        "book_citation_anchored_test");
    UnitTest.assert_values_not_equals(null, place.querySelector('button[data-sort="number"]'),
        "book_number_column_test");
    UnitTest.assert_values_equals('1',
        place.querySelector('#bib-book2026cited').cells[0].textContent, "book_number_test");
    UnitTest.assert_values_equals(1,
        place.querySelectorAll('.bib-backlink').length, "book_back_link_test");

    text.remove();
    parts.forEach(part => part.remove());
});


// launch all unit tests added
book_bibliography_tests.launch_unit_test();
