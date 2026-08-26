/**
:filename: tests.js.cssminTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the minified stylesheets.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-08-20.
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
let cssmin_tests = new UnitTest();


/**
 * The stylesheets the framework is made of, and their minified copies.
 *
 * Nothing is written for the test: the sources are the subject, and their
 * minified copies are what is checked against them.
 */
const CSSMIN_SHEETS = [
    'wexa.css',
    'layout.css',
    'menu.css',
    'button.css',
    'code.css',
    'dialog.css',
    'print.css',
    'togglegroup.css',
    'toggleselect.css',
    'extras/book.css',
    'extras/slides.css',
    'extras/keypiano.css',
    'themes/wexa_theme.css'
];


/**
 * Read a stylesheet and give back what the browser understood of it.
 *
 * The sheet is built apart from the document: what is measured is what the
 * engine parsed, not what a page ends up drawing.
 *
 * @param address {String} Where the stylesheet is.
 * @returns {Promise<CSSStyleSheet|null>} The parsed sheet, or null when it cannot be read.
 */
async function cssmin_parse(address) {
    const response = await fetch(address, { cache: 'no-store' });
    if (response.ok === false) {
        return null;
    }

    const sheet = new CSSStyleSheet();
    sheet.replaceSync(await response.text());

    return sheet;
}


/**
 * Give back every rule of a sheet, the ones nested in another included.
 *
 * A rule is described by what it says and not by how it is written: its
 * selector, or its condition when it holds others, and how many declarations
 * it carries. Two sheets saying the same thing give the same list.
 *
 * @param rules {CSSRuleList} The rules to walk through.
 * @returns {String[]} One line per rule, in the order they are written.
 */
function cssmin_describe(rules) {
    const described = [];

    for (const rule of rules) {
        if (rule.cssRules !== undefined && rule.cssRules !== null) {
            const condition = rule.conditionText || rule.name || '';
            described.push('@ ' + condition);
            described.push(...cssmin_describe(rule.cssRules));
            continue;
        }

        if (rule.selectorText === undefined) {
            described.push('? ' + rule.cssText.slice(0, 40));
            continue;
        }

        described.push(rule.selectorText + ' {' + rule.style.length + '}');
    }

    return described;
}


// -----------------------------------------------------------------------
// Every stylesheet of the framework has a minified copy: a page served the
// minified folder is served all of it.
// -----------------------------------------------------------------------

cssmin_tests.add_test(async () => {
    let missing = 0;

    for (const name of CSSMIN_SHEETS) {
        const minified = await cssmin_parse('../../css.min/' + name);
        if (minified === null) {
            missing = missing + 1;
        }
    }

    UnitTest.assert_values_equals(0, missing, "cssmin_every_sheet_is_there_test");
});


// -----------------------------------------------------------------------
// A minified sheet says what its source says: the same rules, in the same
// order, each with the same selector and the same number of declarations.
// -----------------------------------------------------------------------

cssmin_tests.add_test(async () => {
    for (const name of CSSMIN_SHEETS) {
        const source = await cssmin_parse('../../css/' + name);
        const minified = await cssmin_parse('../../css.min/' + name);

        if (source === null || minified === null) {
            continue;
        }

        const written = cssmin_describe(source.cssRules);
        const shortened = cssmin_describe(minified.cssRules);

        UnitTest.assert_values_equals(written.length, shortened.length,
            "cssmin_same_count_" + name.replace(/[^a-z]/g, '_') + "_test");

        const differences = written.filter((line, index) => line !== shortened[index]);
        UnitTest.assert_values_equals(0, differences.length,
            "cssmin_same_rules_" + name.replace(/[^a-z]/g, '_') + "_test");
    }
});


// -----------------------------------------------------------------------
// A minified sheet is smaller than its source, and says as much: what is
// dropped is what a browser does not read.
// -----------------------------------------------------------------------

cssmin_tests.add_test(async () => {
    const source = await fetch('../../css/wexa.css', { cache: 'no-store' });
    const minified = await fetch('../../css.min/wexa.css', { cache: 'no-store' });

    const written = (await source.text()).length;
    const shortened = (await minified.text()).length;

    UnitTest.assert_array_contains(true, [shortened < written],
        "cssmin_is_smaller_test");
});


// launch all unit tests added
cssmin_tests.launch_unit_test();
