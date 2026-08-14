/**
:filename: tests.js.bibreferenceTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the Reference class.

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
let reference_tests = new UnitTest();


/**
 * Build a reference with the fields a test needs, and nothing else.
 *
 * The constructor is called the way BibtexParser calls it, so that the tests
 * fail if its signature changes.
 *
 * @param {Object} fields - The BibTeX fields, already converted.
 * @param {Author[]} authors - The signatories, in the order they sign.
 * @param {Link[]} links - The addresses of the publication.
 * @returns {Reference} The reference to test.
 */
function build_reference(fields, authors = [], links = []) {
    const map = new Map(Object.entries(fields));
    return new Reference('demo2026key', 'article', map, authors, links, '@article{demo2026key}');
}


// -----------------------------------------------------------------------
// A reference is known by its key, and keeps its type as written.
// Requirement B2.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const reference = build_reference({title: 'A title', year: '2026'});

    UnitTest.assert_values_equals('demo2026key', reference.key, "reference_key_test");
    UnitTest.assert_values_equals('article', reference.type, "reference_type_test");
    UnitTest.assert_values_equals('A title', reference.field('title'), "reference_field_test");
});

// -----------------------------------------------------------------------
// A missing field gives an empty string, never null, so that nothing has
// to test for its existence. Requirement B4.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const reference = build_reference({title: 'A title'});

    UnitTest.assert_values_equals('', reference.field('year'), "reference_missing_field_test");
    UnitTest.assert_values_equals('', reference.field('booktitle'), "reference_unknown_field_test");
});

// -----------------------------------------------------------------------
// A field is asked for by a name whose case does not matter, because
// BibTeX writes ABSTRACT as well as abstract.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const reference = build_reference({title: 'A title'});

    UnitTest.assert_values_equals('A title', reference.field('TITLE'), "reference_field_upper_case_test");
});

// -----------------------------------------------------------------------
// The abstract is a field like any other, and gives an empty string when
// there is none. Requirement B14.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const with_abstract = build_reference({abstract: 'What the paper says.'});
    const without = build_reference({title: 'A title'});

    UnitTest.assert_values_equals('What the paper says.', with_abstract.abstract, "reference_abstract_test");
    UnitTest.assert_values_equals('', without.abstract, "reference_no_abstract_test");
});

// -----------------------------------------------------------------------
// The BibTeX source is kept, so that it can be shown. Requirement B13.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const reference = build_reference({title: 'A title'});

    UnitTest.assert_values_equals('@article{demo2026key}', reference.source, "reference_source_test");
});

// -----------------------------------------------------------------------
// Authors keep the order they sign in. Requirements B2 and B11.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const first = new Author(1, 'Brigitte', '', 'Bigi', '');
    const second = new Author(2, 'Alain', '', 'Ghio', '');
    const reference = build_reference({title: 'A title'}, [first, second]);

    UnitTest.assert_values_equals(2, reference.authors.length, "reference_authors_count_test");
    UnitTest.assert_values_equals('Bigi', reference.authors[0].lastName, "reference_first_author_test");
    UnitTest.assert_values_equals('Ghio', reference.authors[1].lastName, "reference_second_author_test");
});

// -----------------------------------------------------------------------
// A reference without any author or link gives empty lists, never null.
// Requirement B4.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const reference = build_reference({title: 'A title'});

    UnitTest.assert_values_equals(0, reference.authors.length, "reference_no_author_test");
    UnitTest.assert_values_equals(0, reference.links.length, "reference_no_link_test");
});

// -----------------------------------------------------------------------
// Nothing modifies a reference once it is built: the lists it gives out
// are not the ones it keeps.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const author = new Author(1, 'Brigitte', '', 'Bigi', '');
    const reference = build_reference({title: 'A title'}, [author]);

    reference.authors.push(new Author(2, 'Nobody', '', 'Nowhere', ''));

    UnitTest.assert_values_equals(1, reference.authors.length, "reference_authors_not_modified_test");
});


// -----------------------------------------------------------------------
// The BibTeX source is given without its abstract: the abstract is shown
// on its own, and a wall of text between the fields helps nobody.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = String.raw`@article{demo2026abstract,
    author = {Brigitte Bigi},
    abstract = {What the paper says, at length.},
    year = {2026}
}`;
    const reference = new BibtexParser().parse(entry).get('demo2026abstract');
    const shown = reference.sourceWithoutAbstract;

    UnitTest.assert_array_contains(false, [shown.includes('at length')],
        "reference_source_without_abstract_test");
    UnitTest.assert_array_contains(true, [shown.includes('Brigitte Bigi')],
        "reference_source_keeps_author_test");
    UnitTest.assert_array_contains(true, [shown.includes('year = {2026}')],
        "reference_source_keeps_year_test");
    UnitTest.assert_array_contains(true, [shown.includes('@article{demo2026abstract,')],
        "reference_source_keeps_key_test");
});

// -----------------------------------------------------------------------
// What is kept is left exactly as it was written. Requirement B13.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = String.raw`@article{demo2026kept,
    title = {Les donn{\'e}es},
    abstract = {Something}
}`;
    const reference = new BibtexParser().parse(entry).get('demo2026kept');

    UnitTest.assert_array_contains(true, [reference.sourceWithoutAbstract.includes(String.raw`{\'e}`)],
        "reference_source_kept_as_written_test");
    UnitTest.assert_array_contains(true, [reference.source.includes('Something')],
        "reference_whole_source_test");
});

// -----------------------------------------------------------------------
// An entry without any abstract is given back untouched.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = '@misc{demo2026none, title = {A Title}, year = {2026}}';
    const reference = new BibtexParser().parse(entry).get('demo2026none');

    UnitTest.assert_values_equals(reference.source, reference.sourceWithoutAbstract,
        "reference_source_untouched_test");
});

// -----------------------------------------------------------------------
// A field written in capitals is a field: BibTeX is written by hand.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = String.raw`@article{demo2026capitals,
    ABSTRACT = "What the paper says",
    YEAR = "2026"
}`;
    const reference = new BibtexParser().parse(entry).get('demo2026capitals');

    UnitTest.assert_array_contains(false, [reference.sourceWithoutAbstract.includes('What the paper')],
        "reference_source_capitals_test");
    UnitTest.assert_array_contains(true, [reference.sourceWithoutAbstract.includes('2026')],
        "reference_source_capitals_keeps_year_test");
});

// -----------------------------------------------------------------------
// An abstract holding braces of its own is followed to its real end.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = String.raw`@article{demo2026braces,
    abstract = {It says {SPPAS} and {LPC}, twice.},
    year = {2026}
}`;
    const reference = new BibtexParser().parse(entry).get('demo2026braces');

    UnitTest.assert_array_contains(false, [reference.sourceWithoutAbstract.includes('twice')],
        "reference_source_braces_test");
    UnitTest.assert_array_contains(true, [reference.sourceWithoutAbstract.includes('year = {2026}')],
        "reference_source_braces_keeps_year_test");
});

// -----------------------------------------------------------------------
// An abstract written last leaves no comma hanging before the brace that
// closes the entry: what is given back is pasted into a bibliography.
// -----------------------------------------------------------------------

reference_tests.add_test(() => {
    const entry = String.raw`@article{demo2026last,
    year = {2026},
    abstract = {What the paper says.}
}`;
    const reference = new BibtexParser().parse(entry).get('demo2026last');
    const shown = reference.sourceWithoutAbstract;

    UnitTest.assert_array_contains(false, [shown.includes(',}')], "reference_source_no_hanging_comma_test");
    UnitTest.assert_array_contains(true, [shown.trim().endsWith('}')], "reference_source_closed_test");
});


// launch all unit tests added
reference_tests.launch_unit_test();
