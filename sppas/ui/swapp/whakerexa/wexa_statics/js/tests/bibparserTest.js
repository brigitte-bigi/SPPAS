/**
:filename: tests.js.bibparserTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the BibtexParser class.

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
let bibtex_parser_tests = new UnitTest();


// -----------------------------------------------------------------------
// Entry type, key and fields. Requirement B2.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@InProceedings{bigi2022lrec,
    author = {Brigitte Bigi},
    title = {A Large Open Multi-Speaker Corpus},
    year = {2022},
    pages = {987-994}
}`;

    const references = parser.parse(content);
    const reference = references.get('bigi2022lrec');

    UnitTest.assert_values_equals(1, references.size, "parse_one_entry_test");
    UnitTest.assert_values_equals('bigi2022lrec', reference.key, "parse_key_test");
    UnitTest.assert_values_equals('InProceedings', reference.type, "parse_type_as_written_test");
    UnitTest.assert_values_equals('2022', reference.field('year'), "parse_field_year_test");
    UnitTest.assert_values_equals('987-994', reference.field('pages'), "parse_field_pages_test");
});

// -----------------------------------------------------------------------
// A missing field gives an empty string, never null. Requirement B4.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@misc{demo2026missing,
    title = {An entry without any year}
}`;

    const reference = parser.parse(content).get('demo2026missing');

    UnitTest.assert_values_equals('', reference.field('year'), "parse_missing_field_test");
    UnitTest.assert_values_equals(0, reference.authors.length, "parse_missing_author_test");
    UnitTest.assert_values_equals('', reference.abstract, "parse_missing_abstract_test");
});

// -----------------------------------------------------------------------
// An unknown entry type is parsed like any other. Requirement B6.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@dataset{demo2026unknown,
    title = {An entry with an unknown type}
}`;

    const reference = parser.parse(content).get('demo2026unknown');

    UnitTest.assert_values_equals('dataset', reference.type, "parse_unknown_type_test");
    UnitTest.assert_values_equals('An entry with an unknown type', reference.field('title'),
        "parse_unknown_type_title_test");
});

// -----------------------------------------------------------------------
// Authors: order of signature, and the three BibTeX name forms.
// Requirement B2.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026authors,
    author = {Brigitte Bigi and Ludwig van Beethoven and de La Fontaine, Jean and Smith, Jr, John}
}`;

    const authors = parser.parse(content).get('demo2026authors').authors;

    UnitTest.assert_values_equals(4, authors.length, "parse_authors_count_test");

    // Form "First von Last", without any particle.
    UnitTest.assert_values_equals('Brigitte', authors[0].firstName, "parse_author_first_name_test");
    UnitTest.assert_values_equals('Bigi', authors[0].lastName, "parse_author_last_name_test");
    UnitTest.assert_values_equals(1, authors[0].place, "parse_author_place_test");

    // Form "First von Last": a lowercase word is the particle.
    UnitTest.assert_values_equals('Ludwig', authors[1].firstName, "parse_author_von_first_test");
    UnitTest.assert_values_equals('van', authors[1].particle, "parse_author_von_particle_test");
    UnitTest.assert_values_equals('Beethoven', authors[1].lastName, "parse_author_von_last_test");

    // Form "von Last, First". The particle stops at the last word in lower
    // case, so "La Fontaine" is the family name and "de" alone is the particle.
    UnitTest.assert_values_equals('Jean', authors[2].firstName, "parse_author_comma_first_test");
    UnitTest.assert_values_equals('de', authors[2].particle, "parse_author_comma_particle_test");
    UnitTest.assert_values_equals('La Fontaine', authors[2].lastName, "parse_author_comma_last_test");

    // Form "von Last, Jr, First".
    UnitTest.assert_values_equals('John', authors[3].firstName, "parse_author_suffix_first_test");
    UnitTest.assert_values_equals('Smith', authors[3].lastName, "parse_author_suffix_last_test");
    UnitTest.assert_values_equals('Jr', authors[3].suffix, "parse_author_suffix_test");
});

// -----------------------------------------------------------------------
// Every author is kept, whatever their number. Requirement B11.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026many,
    author = {A One and B Two and C Three and D Four and E Five and F Six and G Seven and H Eight and I Nine}
}`;

    const authors = parser.parse(content).get('demo2026many').authors;

    UnitTest.assert_values_equals(9, authors.length, "parse_all_authors_kept_test");
    UnitTest.assert_values_equals('Nine', authors[8].lastName, "parse_last_author_test");
});

// -----------------------------------------------------------------------
// LaTeX notations become plain characters. Requirement B3.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@inbook{demo2026latex,
    chapter = {Les diff{\'e}rents types de donn{\'e}es recueillies},
    title = {{\"O}sterreich et le fran\c{c}ais},
    publisher = {{Dunod}}
}`;

    const reference = parser.parse(content).get('demo2026latex');

    UnitTest.assert_values_equals('Les différents types de données recueillies',
        reference.field('chapter'), "parse_latex_acute_test");
    UnitTest.assert_values_equals('Österreich et le français',
        reference.field('title'), "parse_latex_umlaut_cedilla_test");

    // Braces protecting the case are removed, what they protect is not.
    UnitTest.assert_values_equals('Dunod', reference.field('publisher'), "parse_case_braces_test");
});

// -----------------------------------------------------------------------
// URL and NOTE both give links. Requirement B12.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026links,
    url = {http://www.lrec-conf.org/proceedings/lrec2022/pdf/2022.lrec-1.104.pdf},
    note = {https://hal.science/hal-03794830}
}`;

    const links = parser.parse(content).get('demo2026links').links;

    UnitTest.assert_values_equals(2, links.length, "parse_two_links_test");
    UnitTest.assert_values_equals('http://www.lrec-conf.org/proceedings/lrec2022/pdf/2022.lrec-1.104.pdf',
        links[0].address, "parse_link_from_url_test");
    UnitTest.assert_values_equals('https://hal.science/hal-03794830',
        links[1].address, "parse_link_from_note_test");
});

// -----------------------------------------------------------------------
// A reference without any link gives an empty list. Requirement B12.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026nolink,
    title = {An entry without any address}
}`;

    const links = parser.parse(content).get('demo2026nolink').links;

    UnitTest.assert_values_equals(0, links.length, "parse_no_link_test");
});

// -----------------------------------------------------------------------
// An equal sign inside a value is not a separator.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026equal,
    abstract = {The accuracy is defined as a = b + c, and the delta = 40 ms.},
    year = {2026}
}`;

    const reference = parser.parse(content).get('demo2026equal');

    UnitTest.assert_values_equals('The accuracy is defined as a = b + c, and the delta = 40 ms.',
        reference.abstract, "parse_equal_sign_inside_value_test");
    UnitTest.assert_values_equals('2026', reference.field('year'), "parse_field_after_equal_sign_test");
});

// -----------------------------------------------------------------------
// A value delimited by double quotes is read like any other.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026quotes,
    TITLE = "Resources Creation of Bengali for SPPAS",
    YEAR = "2026"
}`;

    const reference = parser.parse(content).get('demo2026quotes');

    UnitTest.assert_values_equals('Resources Creation of Bengali for SPPAS',
        reference.field('title'), "parse_quoted_value_test");
    UnitTest.assert_values_equals('2026', reference.field('year'), "parse_quoted_year_test");
});

// -----------------------------------------------------------------------
// A missing closing brace does not lose the following entries.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026broken,
    title = {An entry whose closing brace is missing},
    year = {2026}

@article{demo2026next,
    title = {The entry that follows},
    year = {2026}
}`;

    const references = parser.parse(content);

    UnitTest.assert_values_equals(2, references.size, "parse_recover_broken_entry_test");
    UnitTest.assert_values_equals('The entry that follows',
        references.get('demo2026next').field('title'), "parse_entry_after_broken_test");
});

// -----------------------------------------------------------------------
// Two entries sharing a key: the second replaces the first.
// Requirement B22.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026twice,
    title = {The first one}
}

@article{demo2026twice,
    title = {The second one}
}`;

    const references = parser.parse(content);

    UnitTest.assert_values_equals(1, references.size, "parse_duplicated_key_count_test");
    UnitTest.assert_values_equals('The second one',
        references.get('demo2026twice').field('title'), "parse_duplicated_key_replaced_test");
});

// -----------------------------------------------------------------------
// The BibTeX source of an entry is kept as written. Requirement B13.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const content = String.raw`
@article{demo2026source,
    title = {Les donn{\'e}es}
}`;

    const source = parser.parse(content).get('demo2026source').source;

    UnitTest.assert_array_contains(true, [source.includes(String.raw`{\'e}`)],
        "parse_source_kept_as_written_test");
});

// -----------------------------------------------------------------------
// Content without any entry gives an empty map, and nothing is raised.
// -----------------------------------------------------------------------

bibtex_parser_tests.add_test(() => {
    const parser = new BibtexParser();
    const references = parser.parse('Nothing here looks like a BibTeX entry.');

    UnitTest.assert_values_equals(0, references.size, "parse_no_entry_test");
});


// launch all unit tests added
bibtex_parser_tests.launch_unit_test();
