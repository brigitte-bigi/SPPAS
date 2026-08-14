/**
:filename: tests.js.bibformatterTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the ReferenceFormatter class.

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
let reference_formatter_tests = new UnitTest();


/**
 * Parse one BibTeX entry and give the reference it describes.
 *
 * The parser is used rather than the constructor of Reference, so that what is
 * formatted here is exactly what a document holds.
 *
 * @param {string} entry - One BibTeX entry.
 * @returns {Reference} The reference to format.
 */
function parse_one(entry) {
    const parser = new BibtexParser();
    const references = parser.parse(entry);

    return references.values().next().value;
}


// -----------------------------------------------------------------------
// An article shows its fields in the order the template says. B9.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026article,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    volume = {38},
    pages = {186-234},
    year = {2022}
}`);

    const fragment = formatter.format(reference);
    const text = fragment.textContent;

    UnitTest.assert_array_contains(true, [text.includes('Brigitte Bigi')], "format_author_test");
    UnitTest.assert_array_contains(true, [text.includes('A Title')], "format_title_test");
    UnitTest.assert_array_contains(true, [text.includes('A Journal')], "format_journal_test");
    UnitTest.assert_array_contains(true, [text.includes('2022')], "format_year_test");

    UnitTest.assert_array_contains(true, [text.indexOf('Brigitte Bigi') < text.indexOf('A Title')],
        "format_author_before_title_test");
    UnitTest.assert_array_contains(true, [text.indexOf('A Title') < text.indexOf('A Journal')],
        "format_title_before_journal_test");
});

// -----------------------------------------------------------------------
// Each field is written in an element of its own, so that the stylesheet
// can tell them apart.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026elements,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    year = {2022}
}`);

    const fragment = formatter.format(reference);

    UnitTest.assert_values_equals(1, fragment.querySelectorAll('.bib-title').length,
        "format_title_element_test");
    UnitTest.assert_values_equals(1, fragment.querySelectorAll('.bib-journal').length,
        "format_journal_element_test");
    UnitTest.assert_values_equals(1, fragment.querySelectorAll('.bib-author').length,
        "format_author_element_test");
});

// -----------------------------------------------------------------------
// Every author is written, whatever their number, and never "et al.".
// Requirement B11.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026many,
    author = {Mary Amoyal and Roxane Bertrand and Brigitte Bigi and Auriane Boudin and Christine Meunier and Berthille Pallaud and Stéphane Rauzy and Marion Tellier},
    title = {A Title},
    year = {2022}
}`);

    const text = formatter.format(reference).textContent;

    UnitTest.assert_array_contains(true, [text.includes('Mary Amoyal')], "format_first_author_test");
    UnitTest.assert_array_contains(true, [text.includes('Marion Tellier')], "format_last_author_test");
    UnitTest.assert_array_contains(false, [text.includes('et al')], "format_no_et_al_test");
});

// -----------------------------------------------------------------------
// An unknown type is formatted by the fallback template, and the
// reference is displayed all the same. Requirement B6.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@dataset{demo2026unknown,
    author = {Brigitte Bigi},
    title = {A Title},
    year = {2026}
}`);

    const text = formatter.format(reference).textContent;

    UnitTest.assert_array_contains(true, [text.includes('A Title')], "format_unknown_type_title_test");
    UnitTest.assert_array_contains(true, [text.includes('Brigitte Bigi')], "format_unknown_type_author_test");
    UnitTest.assert_array_contains(true, [text.includes('2026')], "format_unknown_type_year_test");
});

// -----------------------------------------------------------------------
// The case of the type changes nothing: BibTeX is written by hand, and
// @Article, @article and @ARTICLE are the same type seen three times.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const lower = parse_one(String.raw`
@article{demo2026lower,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    year = {2022}
}`);
    const upper = parse_one(String.raw`
@Article{demo2026upper,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    year = {2022}
}`);

    UnitTest.assert_values_equals(formatter.format(lower).textContent,
        formatter.format(upper).textContent, "format_type_case_test");
});

// -----------------------------------------------------------------------
// A field that a type requires, and that the entry does not have, is
// made visible rather than silently dropped. Requirement B4.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026missing,
    author = {Brigitte Bigi},
    title = {A Title}
}`);

    const fragment = formatter.format(reference);
    const missing = fragment.querySelectorAll('.bib-missing');

    UnitTest.assert_values_equals(2, missing.length, "format_missing_count_test");
    UnitTest.assert_array_contains(true, [fragment.textContent.includes('journal')],
        "format_missing_journal_named_test");
    UnitTest.assert_array_contains(true, [fragment.textContent.includes('year')],
        "format_missing_year_named_test");
});

// -----------------------------------------------------------------------
// A field that a type does not require leaves no trace when it is
// absent: an article without a volume is not an article with a hole.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026optional,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal},
    year = {2022}
}`);

    const fragment = formatter.format(reference);

    UnitTest.assert_values_equals(0, fragment.querySelectorAll('.bib-missing').length,
        "format_optional_field_test");
    UnitTest.assert_values_equals(0, fragment.querySelectorAll('.bib-volume').length,
        "format_no_empty_element_test");
});

// -----------------------------------------------------------------------
// What is missing is said, and not only shown. Requirement B4.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@article{demo2026said,
    author = {Brigitte Bigi},
    title = {A Title},
    journal = {A Journal}
}`);

    const missing = formatter.format(reference).querySelector('.bib-missing');

    UnitTest.assert_values_not_equals(null, missing, "format_missing_element_test");
    UnitTest.assert_values_not_equals(null, missing.getAttribute('title'), "format_missing_title_test");
});

// -----------------------------------------------------------------------
// A reference reduced to almost nothing is still formatted, rather than
// giving an empty fragment.
// -----------------------------------------------------------------------

reference_formatter_tests.add_test(() => {
    const formatter = new ReferenceFormatter();
    const reference = parse_one(String.raw`
@misc{demo2026empty,
    title = {A Title}
}`);

    const text = formatter.format(reference).textContent;

    UnitTest.assert_values_not_equals(0, text.length, "format_never_empty_test");
    UnitTest.assert_array_contains(true, [text.includes('A Title')], "format_minimal_title_test");
});

// launch all unit tests added
reference_formatter_tests.launch_unit_test();
