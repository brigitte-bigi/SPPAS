/**
:filename: tests.js.bibtableTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the BibliographyTable class.

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
let bibliography_table_tests = new UnitTest();


/**
 * The BibTeX data every test of this file works on.
 *
 * Two entries: one with an abstract and two addresses, one with neither.
 */
const TABLE_DATA = String.raw`
@InProceedings{bigi2022lrec,
    author = {Brigitte Bigi and Carine André},
    title = {A Large Open Multi-Speaker Corpus},
    booktitle = {Proceedings of the Conference},
    year = {2022},
    url = {http://www.example.org/paper.pdf},
    note = {https://hal.science/hal-03794830},
    abstract = {What the paper says.}
}

@article{ghio2023dunod,
    author = {Alain Ghio},
    title = {Another Title},
    journal = {A Journal},
    year = {2023}
}`;


/**
 * Parse the data every test works on.
 *
 * @returns {Map} The references, by key.
 */
function table_references() {
    const parser = new BibtexParser();

    return parser.parse(TABLE_DATA);
}


// -----------------------------------------------------------------------
// The table says what it is, and its headers are declared as such. B20.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());

    UnitTest.assert_values_equals('TABLE', table.tagName, "table_element_test");
    UnitTest.assert_values_not_equals(null, table.querySelector('tbody'), "table_body_test");

    const headers = table.querySelectorAll('thead th');
    UnitTest.assert_values_equals('col', headers[0].getAttribute('scope'), "table_header_scope_test");
});

// -----------------------------------------------------------------------
// One row per reference, each carrying an identifier, so that a citation
// can lead to it. Requirement C26.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const rows = table.querySelectorAll('tbody tr.bib-row');

    UnitTest.assert_values_equals(2, rows.length, "table_one_row_per_reference_test");
    UnitTest.assert_values_not_equals(null, table.querySelector('#bib-bigi2022lrec'),
        "table_row_identifier_test");
    UnitTest.assert_values_not_equals(null, table.querySelector('#bib-ghio2023dunod'),
        "table_second_row_identifier_test");
});

// -----------------------------------------------------------------------
// Without any citation, there is no number column and no back link: the
// column would say nothing, and would be one more thing to read.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());

    UnitTest.assert_values_equals(null, table.querySelector('button[data-sort="number"]'),
        "table_no_number_header_test");
    UnitTest.assert_values_equals(0, table.querySelectorAll('.bib-backlink').length,
        "table_no_back_link_test");
});

// -----------------------------------------------------------------------
// With citations, the number column is there, and holds the number the
// reference was given the first time it was cited. Requirement C11.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const cited = new Map();
    cited.set('bigi2022lrec', new CitedReference(1, []));

    const table = new BibliographyTable().build(table_references(), cited);
    const row = table.querySelector('#bib-bigi2022lrec');

    UnitTest.assert_values_not_equals(null, table.querySelector('button[data-sort="number"]'),
        "table_number_header_test");
    UnitTest.assert_values_equals('1', row.cells[0].textContent, "table_number_test");
});

// -----------------------------------------------------------------------
// A reference that is never cited has no number, and the cell stays
// empty rather than showing something that would look like one.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const cited = new Map();
    cited.set('bigi2022lrec', new CitedReference(1, []));

    const table = new BibliographyTable().build(table_references(), cited);
    const row = table.querySelector('#bib-ghio2023dunod');

    UnitTest.assert_values_equals('', row.cells[0].textContent, "table_no_number_for_uncited_test");

    // Sorting on the numbers puts it after every reference that has one: an
    // empty cell would put it first of all.
    const numbered = table.querySelector('#bib-bigi2022lrec');
    UnitTest.assert_array_contains(true,
        [Number(row.cells[0].getAttribute('data-sort-value'))
            > Number(numbered.cells[0].getAttribute('data-sort-value'))],
        "table_uncited_sorts_last_test");
});

// -----------------------------------------------------------------------
// The year has a column of its own, so that it can be sorted on. B16.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const row = table.querySelector('#bib-bigi2022lrec');

    UnitTest.assert_values_not_equals(null, table.querySelector('button[data-sort="year"]'),
        "table_year_header_test");
    UnitTest.assert_values_equals('2022', row.cells[0].textContent, "table_year_test");
});

// -----------------------------------------------------------------------
// The cell of the reference carries the value to sort on, because the
// first author is what a bibliography is sorted by, and it is not
// displayed apart. Requirement B16.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const row = table.querySelector('#bib-bigi2022lrec');

    UnitTest.assert_values_not_equals(null, table.querySelector('button[data-sort="author"]'),
        "table_author_header_test");
    UnitTest.assert_values_equals('Bigi, Brigitte', row.cells[1].getAttribute('data-sort-value'),
        "table_sort_value_test");
});

// -----------------------------------------------------------------------
// The reference is displayed in its cell, formatted by its type.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const cell = table.querySelector('#bib-bigi2022lrec').cells[1];

    UnitTest.assert_array_contains(true, [cell.textContent.includes('A Large Open Multi-Speaker Corpus')],
        "table_reference_displayed_test");
    UnitTest.assert_values_not_equals(null, cell.querySelector('.bib-title'),
        "table_reference_formatted_test");
});

// -----------------------------------------------------------------------
// The abstract and the BibTeX source can be opened, and are hidden until
// they are asked for. Requirements B13 and B14.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const row = table.querySelector('#bib-bigi2022lrec');
    const controls = row.querySelectorAll('button[aria-expanded]');

    UnitTest.assert_values_equals(2, controls.length, "table_two_disclosures_test");
    UnitTest.assert_values_equals('false', controls[0].getAttribute('aria-expanded'),
        "table_disclosure_closed_test");

    // The content is a row of its own, right after the one of the reference.
    const opened = table.querySelectorAll('tr.bib-opened-row[data-opens="bib-bigi2022lrec"]');
    UnitTest.assert_values_equals(2, opened.length, "table_two_opened_rows_test");
    UnitTest.assert_values_equals(true, opened[0].hidden, "table_content_hidden_test");
    UnitTest.assert_array_contains(true, [opened[0].textContent.includes('What the paper says.')],
        "table_abstract_written_test");
});

// -----------------------------------------------------------------------
// A reference without any abstract has no control for one: an empty
// disclosure is a promise that is not kept.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const row = table.querySelector('#bib-ghio2023dunod');

    UnitTest.assert_values_equals(1, row.querySelectorAll('button[aria-expanded]').length,
        "table_one_disclosure_test");
});

// -----------------------------------------------------------------------
// Every address a reference carries is reachable, and a reference that
// carries none has no link at all. Requirement B12.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const table = new BibliographyTable().build(table_references(), new Map());
    const with_links = table.querySelector('#bib-bigi2022lrec').querySelectorAll('a.bib-link[href]');
    const without = table.querySelector('#bib-ghio2023dunod').querySelectorAll('a.bib-link[href]');

    UnitTest.assert_values_equals(2, with_links.length, "table_links_test");
    UnitTest.assert_values_equals('http://www.example.org/paper.pdf', with_links[0].getAttribute('href'),
        "table_link_address_test");
    UnitTest.assert_values_equals(0, without.length, "table_no_link_test");
});

// -----------------------------------------------------------------------
// From a reference, a link leads to every place where it is cited.
// Requirement C27.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const first = document.createElement('span');
    first.id = 'cite-1';
    const second = document.createElement('span');
    second.id = 'cite-4';

    const cited = new Map();
    cited.set('bigi2022lrec', new CitedReference(1, [first, second]));

    const table = new BibliographyTable().build(table_references(), cited);
    const links = table.querySelector('#bib-bigi2022lrec').querySelectorAll('.bib-backlink');

    UnitTest.assert_values_equals(2, links.length, "table_back_links_count_test");
    UnitTest.assert_values_equals('#cite-1', links[0].getAttribute('href'), "table_back_link_target_test");
});

// -----------------------------------------------------------------------
// What the program writes follows the language of the document, and is
// never written in one language only.
// -----------------------------------------------------------------------

bibliography_table_tests.add_test(() => {
    const spoken = document.documentElement.lang;

    document.documentElement.lang = 'fr';
    const french = new BibliographyTable().build(table_references(), new Map());

    document.documentElement.lang = 'en';
    const english = new BibliographyTable().build(table_references(), new Map());

    document.documentElement.lang = spoken;

    UnitTest.assert_values_not_equals(french.querySelector('thead th').textContent,
        english.querySelector('thead th').textContent, "table_language_test");
});


// launch all unit tests added
bibliography_table_tests.launch_unit_test();
