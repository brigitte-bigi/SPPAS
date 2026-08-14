/**
:filename: tests.js.bibsourceTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the BibtexSource class.

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
let bibtex_source_tests = new UnitTest();


/**
 * Write BibTeX data in the page, the way a document does.
 *
 * @param {string} identifier - The id the element is given.
 * @param {string} content - What is written inside.
 * @returns {HTMLElement} The element, to be removed once the test is over.
 */
function write_data_in_page(identifier, content) {
    const element = document.createElement('pre');
    element.id = identifier;
    element.hidden = true;
    element.textContent = content;
    document.body.appendChild(element);

    return element;
}

/**
 * Read a source and give back the name of what it raised, if anything.
 *
 * @param {BibtexSource} source - The source to read.
 * @returns {Promise<string>} The name of the error, or an empty string.
 */
async function raised_by(source) {
    try {
        await source.read();
    } catch (error) {
        return error.name;
    }

    return '';
}


// -----------------------------------------------------------------------
// Data written in the page are read where they stand. Requirement B1.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const written = '@misc{sample2026page, title = {An entry written in the page}}';
    const element = write_data_in_page('bibtex-in-page', written);

    const source = new BibtexSource('bibtex-in-page');
    const read = await source.read();

    UnitTest.assert_values_equals(written, read, "source_from_page_test");

    element.remove();
});

// -----------------------------------------------------------------------
// Nothing is added and nothing is taken away: the parser is the one that
// reads the data, not this class.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const written = '\n@misc{sample2026raw,\n    title = {Les donn{\\\'e}es}\n}\n';
    const element = write_data_in_page('bibtex-raw', written);

    const read = await new BibtexSource('bibtex-raw').read();

    UnitTest.assert_values_equals(written, read, "source_kept_as_written_test");

    element.remove();
});

// -----------------------------------------------------------------------
// A page that holds nothing and names no file cannot be helped, and says
// so rather than going on with nothing.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const source = new BibtexSource('nothing-like-an-element');

    UnitTest.assert_values_equals('MissingBibtexData', await raised_by(source),
        "source_no_element_test");
});

// -----------------------------------------------------------------------
// An element that is there but empty is an element that holds nothing.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const element = write_data_in_page('bibtex-empty', '   \n  ');
    const source = new BibtexSource('bibtex-empty');

    UnitTest.assert_values_equals('MissingBibtexData', await raised_by(source),
        "source_empty_element_test");

    element.remove();
});

// -----------------------------------------------------------------------
// Data kept in a file next to the document are asked for. Requirement B1.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const source = new BibtexSource('nothing-like-an-element', 'sample.bib');
    const read = await source.read();

    UnitTest.assert_array_contains(true, [read.includes('sample2026file')], "source_from_file_test");
});

// -----------------------------------------------------------------------
// The page comes first: a file is only asked for when the page holds
// nothing, so that a document never waits for what it already has.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const written = '@misc{sample2026first, title = {The page wins}}';
    const element = write_data_in_page('bibtex-first', written);

    const source = new BibtexSource('bibtex-first', 'sample.bib');
    const read = await source.read();

    UnitTest.assert_values_equals(written, read, "source_page_before_file_test");

    element.remove();
});

// -----------------------------------------------------------------------
// A file that is not there is said in the console, and read like nothing
// at all.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const source = new BibtexSource('nothing-like-an-element', 'nothing-like-a-file.bib');

    UnitTest.assert_values_equals('MissingBibtexData', await raised_by(source),
        "source_unknown_file_test");
});

// -----------------------------------------------------------------------
// A file on another server is refused: a document reads its own data.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const source = new BibtexSource('nothing-like-an-element', 'https://example.org/biblio.bib');

    UnitTest.assert_values_equals('MissingBibtexData', await raised_by(source),
        "source_another_server_test");
});

// -----------------------------------------------------------------------
// What is raised is a BibliographyError, so that whoever gathers them
// catches every one of them in one gesture.
// -----------------------------------------------------------------------

bibtex_source_tests.add_test(async () => {
    const source = new BibtexSource('nothing-like-an-element');
    let isBibliographyError = false;

    try {
        await source.read();
    } catch (error) {
        isBibliographyError = error instanceof BibliographyError;
    }

    UnitTest.assert_values_equals(true, isBibliographyError, "source_error_family_test");
});


// launch all unit tests added
bibtex_source_tests.launch_unit_test();
