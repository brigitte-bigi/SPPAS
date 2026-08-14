/**
:filename: tests.js.bibcitedkeyTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the CitedKey class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-07-30.
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
let cited_key_tests = new UnitTest();


/**
 * Parse one BibTeX entry and give the reference it describes.
 *
 * @param {string} key - The key the entry is given.
 * @returns {Reference} The reference a cited key may name.
 */
function reference_named(key) {
    const entry = '@misc{' + key + ', title = {A Title}}';

    return new BibtexParser().parse(entry).get(key);
}


// -----------------------------------------------------------------------
// A cited key carries the key as it was written, and the reference that
// bears it. Requirement C7.
// -----------------------------------------------------------------------

cited_key_tests.add_test(() => {
    const reference = reference_named('bigi2022lrec');
    const cited = new CitedKey(1, 'bigi2022lrec', reference, '');

    UnitTest.assert_values_equals('bigi2022lrec', cited.writtenKey, "cited_key_written_test");
    UnitTest.assert_values_equals(reference, cited.reference, "cited_key_reference_test");
    UnitTest.assert_values_equals(1, cited.place, "cited_key_place_test");
});

// -----------------------------------------------------------------------
// A key that names nothing gives a cited key all the same: the citation
// stays visible, and says that its reference is missing. C8.
// -----------------------------------------------------------------------

cited_key_tests.add_test(() => {
    const cited = new CitedKey(1, 'nothing2026', null, '');

    UnitTest.assert_values_equals('nothing2026', cited.writtenKey, "cited_key_unknown_written_test");
    UnitTest.assert_values_equals(null, cited.reference, "cited_key_unknown_reference_test");
});

// -----------------------------------------------------------------------
// The page or the chapter aimed at is carried, whether there is one or
// not. Requirement C4, which the first version does not display.
// -----------------------------------------------------------------------

cited_key_tests.add_test(() => {
    const withPage = new CitedKey(1, 'bigi2022lrec', null, '987-994');
    const without = new CitedKey(1, 'bigi2022lrec', null, '');

    UnitTest.assert_values_equals('987-994', withPage.targetPage, "cited_key_target_page_test");
    UnitTest.assert_values_equals('', without.targetPage, "cited_key_no_target_page_test");
});

// -----------------------------------------------------------------------
// Its place in the citation is carried too: a citation may bear more
// than one key. Requirement C3, which the first version does not display.
// -----------------------------------------------------------------------

cited_key_tests.add_test(() => {
    const first = new CitedKey(1, 'bigi2010jep', null, '');
    const second = new CitedKey(2, 'bigi2010lrec', null, '');

    UnitTest.assert_values_equals(1, first.place, "cited_key_first_place_test");
    UnitTest.assert_values_equals(2, second.place, "cited_key_second_place_test");
});

// -----------------------------------------------------------------------
// The reference is looked for before the cited key is built, and never
// put in afterwards: nothing changes once the object is made.
// -----------------------------------------------------------------------

cited_key_tests.add_test(() => {
    const cited = new CitedKey(1, 'bigi2022lrec', null, '');

    // A class of this project only reads what it was built with: writing on it
    // raises, and what it holds does not move either way.
    try {
        cited.reference = reference_named('bigi2022lrec');
    } catch (error) {
        // Nothing to do: refusing the write is the expected answer.
    }

    UnitTest.assert_values_equals(null, cited.reference, "cited_key_not_modified_test");
});


// launch all unit tests added
cited_key_tests.launch_unit_test();
