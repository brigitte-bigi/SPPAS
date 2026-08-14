/**
:filename: tests.js.bibcitationTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the Citation class.

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
let citation_tests = new UnitTest();


/**
 * Write in the page a sentence holding one citation.
 *
 * The citation stands between two words, as it does in a document, so that
 * what happens to the space before it can be seen.
 *
 * @param {string} name - What tells the elements of this test from the others.
 * @param {string} key - The key the citation bears.
 * @returns {Object} The sentence, the element of the citation, and what removes them.
 */
function write_sentence(name, key) {
    const sentence = document.createElement('p');
    sentence.id = name + '-sentence';
    sentence.appendChild(document.createTextNode('The corpus is described in '));

    const element = document.createElement('span');
    element.setAttribute('data-bibtex', key);
    element.textContent = 'Bigi et al., 2022';
    sentence.appendChild(element);
    sentence.appendChild(document.createTextNode('.'));

    document.body.appendChild(sentence);

    return {sentence: sentence, element: element, remove: () => sentence.remove()};
}


// -----------------------------------------------------------------------
// A citation carries where it stands in the text and the keys it bears.
// Requirements C7 and C13.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('carries', 'bigi2022lrec');
    const keys = [new CitedKey(1, 'bigi2022lrec', null, '')];
    const citation = new Citation(written.element, 3, keys);

    UnitTest.assert_values_equals(written.element, citation.element, "citation_element_test");
    UnitTest.assert_values_equals(3, citation.place, "citation_place_test");
    UnitTest.assert_values_equals(1, citation.citedKeys.length, "citation_keys_test");

    written.remove();
});

// -----------------------------------------------------------------------
// A citation shows its number, and nothing else. Requirement C15.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('number', 'bigi2022lrec');
    const citation = new Citation(written.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]);

    citation.showNumber(12);

    UnitTest.assert_values_equals('[12]', written.element.textContent.trim(), "citation_number_test");

    written.remove();
});

// -----------------------------------------------------------------------
// A screen reader says "Reference" and the number, and never the
// brackets. Requirement C16.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('spoken', 'bigi2022lrec');
    const citation = new Citation(written.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]);

    citation.showNumber(12);
    const spoken = written.element.getAttribute('aria-label');

    UnitTest.assert_values_not_equals(null, spoken, "citation_spoken_test");
    UnitTest.assert_array_contains(true, [spoken.includes('12')], "citation_spoken_number_test");
    UnitTest.assert_array_contains(false, [spoken.includes('[')], "citation_spoken_no_bracket_test");

    written.remove();
});

// -----------------------------------------------------------------------
// What is spoken follows the language of the document.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const spoken_language = document.documentElement.lang;

    document.documentElement.lang = 'fr';
    const french = write_sentence('french', 'bigi2022lrec');
    new Citation(french.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]).showNumber(1);

    document.documentElement.lang = 'en';
    const english = write_sentence('english', 'bigi2022lrec');
    new Citation(english.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]).showNumber(1);

    document.documentElement.lang = spoken_language;

    UnitTest.assert_values_not_equals(french.element.getAttribute('aria-label'),
        english.element.getAttribute('aria-label'), "citation_language_test");

    french.remove();
    english.remove();
});

// -----------------------------------------------------------------------
// The number never goes alone to the next line: the space before it
// becomes a non-breaking one. Requirement C19.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('unbreakable', 'bigi2022lrec');
    const citation = new Citation(written.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]);

    citation.showNumber(1);

    UnitTest.assert_array_contains(true, [written.sentence.textContent.includes('in\u00A0[1]')],
        "citation_unbreakable_space_test");

    written.remove();
});

// -----------------------------------------------------------------------
// A key that names nothing stays visible, says that it is missing, and
// gets no number at all. Requirement C8.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('missing', 'nothing2026');
    const citation = new Citation(written.element, 1, [new CitedKey(1, 'nothing2026', null, '')]);

    citation.showMissing();

    UnitTest.assert_values_equals('[?]', written.element.textContent.trim(), "citation_missing_test");
    UnitTest.assert_values_not_equals(null, written.element.getAttribute('aria-label'),
        "citation_missing_spoken_test");

    written.remove();
});

// -----------------------------------------------------------------------
// What was written inside the citation is what a reader gets when
// JavaScript does not run, and is replaced as soon as it does. C32.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('replaced', 'bigi2022lrec');

    UnitTest.assert_values_equals('Bigi et al., 2022', written.element.textContent,
        "citation_written_text_test");

    new Citation(written.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]).showNumber(1);

    UnitTest.assert_array_contains(false, [written.element.textContent.includes('Bigi')],
        "citation_text_replaced_test");

    written.remove();
});

// -----------------------------------------------------------------------
// A citation carries an identifier, so that its reference can lead back
// to it. Requirement C27.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('identified', 'bigi2022lrec');
    const citation = new Citation(written.element, 4, [new CitedKey(1, 'bigi2022lrec', null, '')]);

    citation.showNumber(1);

    UnitTest.assert_values_not_equals('', written.element.id, "citation_identifier_test");

    written.remove();
});


// -----------------------------------------------------------------------
// A citation leads to its reference in the bibliography. On paper the
// number is that link, which a PDF keeps clickable. C26.
// -----------------------------------------------------------------------

citation_tests.add_test(() => {
    const written = write_sentence('anchor', 'bigi2022lrec');
    const citation = new Citation(written.element, 1, [new CitedKey(1, 'bigi2022lrec', null, '')]);

    citation.showReference(7, document.createDocumentFragment(), 'bib-bigi2022lrec');

    const anchor = written.element.querySelector('a.bib-citation-anchor');
    const control = written.element.querySelector('button.bib-citation-control');

    UnitTest.assert_values_not_equals(null, anchor, "citation_anchor_test");
    UnitTest.assert_values_equals('#bib-bigi2022lrec', anchor.getAttribute('href'),
        "citation_anchor_target_test");
    UnitTest.assert_values_equals('[7]', anchor.textContent, "citation_anchor_number_test");
    UnitTest.assert_values_equals(anchor.textContent, control.textContent,
        "citation_anchor_same_mark_test");

    written.remove();
});


// launch all unit tests added
citation_tests.launch_unit_test();
