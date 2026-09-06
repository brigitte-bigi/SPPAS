/**
 * :filename: tests.js.UnitTest.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: What a test file says, and how it says it failed.
 *
 *  -------------------------------------------------------------------------
 *
 *  This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa
 *
 *  Copyright (C) 2023-2026 Brigitte Bigi, CNRS
 *  Laboratoire Parole et Langage, Aix-en-Provence, France
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *  This banner notice must not be removed.
 *
 *  -------------------------------------------------------------------------
 */

'use strict';

/**
 * A suite of tests, and the assertions they are written with.
 *
 * A test file builds one of these, adds its functions to it, and launches
 * them. What passes is said in green, what fails is said in red with the
 * value expected and the value obtained, so that the console alone tells
 * where the work is.
 *
 * This class is loaded as a plain script and not as a module: the test files
 * name it without importing it, and tests.html loads it before them.
 *
 * @example
 * const suite = new UnitTest();
 * suite.add_test(() => UnitTest.assert_values_equals(2, 1 + 1, 'one and one'));
 * suite.launch_unit_test();
 */
class UnitTest {

    /** @type {Function[]} The tests to launch. */
    #tests;

    /**
     * Create an empty suite.
     */
    constructor() {
        this.#tests = [];
    }

    // -----------------------------------------------------------------------

    /**
     * Add a test to the suite.
     *
     * @param {Function} func_test - The test, synchronous or not.
     * @returns {void}
     */
    add_test(func_test) {
        this.#tests.push(func_test);
    }

    // -----------------------------------------------------------------------

    /**
     * Launch the tests of the suite, in the order they were added.
     *
     * @returns {Promise<void>} Kept when the last test is done.
     */
    async launch_unit_test() {
        for (const func_test of this.#tests) {
            await func_test();
        }
    }

    // -----------------------------------------------------------------------
    // ASSERTIONS ON VALUES
    // -----------------------------------------------------------------------

    /**
     * Say whether two values are the same one.
     *
     * @param {*} value_expected - What the test expects.
     * @param {*} value_to_compare - What it got.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_values_equals(value_expected, value_to_compare, assertion_name) {
        if (value_to_compare === value_expected) {
            UnitTest.#succeeded(assertion_name);
            return;
        }
        UnitTest.#failed(value_expected, value_to_compare, assertion_name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether two values differ.
     *
     * @param {*} first_value - One of them.
     * @param {*} second_value - The other.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_values_not_equals(first_value, second_value, assertion_name) {
        if (first_value === second_value) {
            UnitTest.#failedEquality(first_value, assertion_name);
            return;
        }
        UnitTest.#succeeded(assertion_name);
    }

    // -----------------------------------------------------------------------
    // ASSERTIONS ON OBJECTS
    // -----------------------------------------------------------------------

    /**
     * Say whether two objects hold the same thing, read as JSON.
     *
     * @param {*} object_expected - What the test expects.
     * @param {*} object_to_compare - What it got.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_object_equals(object_expected, object_to_compare, assertion_name) {
        const expected = JSON.stringify(object_expected);
        const obtained = JSON.stringify(object_to_compare);

        if (expected === obtained) {
            UnitTest.#succeeded(assertion_name);
            return;
        }
        UnitTest.#failed(expected, obtained, assertion_name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether two objects hold something different, read as JSON.
     *
     * @param {*} first_object - One of them.
     * @param {*} second_object - The other.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_object_not_equals(first_object, second_object, assertion_name) {
        if (JSON.stringify(first_object) === JSON.stringify(second_object)) {
            UnitTest.#failedEquality(JSON.stringify(first_object), assertion_name);
            return;
        }
        UnitTest.#succeeded(assertion_name);
    }

    // -----------------------------------------------------------------------
    // ASSERTIONS ON WHAT A CONTAINER HOLDS
    // -----------------------------------------------------------------------

    /**
     * Say whether an array carries a value.
     *
     * @param {*} value_to_search - The value looked for.
     * @param {Array} array - Where it is looked for.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_array_contains(value_to_search, array, assertion_name) {
        if (array.includes(value_to_search) === true) {
            UnitTest.#succeeded(assertion_name);
            return;
        }
        UnitTest.#failedSearch(value_to_search, array, assertion_name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether an array carries no such value.
     *
     * @param {*} value_to_search - The value looked for.
     * @param {Array} array - Where it is looked for.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_array_not_contains(value_to_search, array, assertion_name) {
        if (array.includes(value_to_search) === true) {
            UnitTest.#failedSearch(value_to_search, array, assertion_name);
            return;
        }
        UnitTest.#succeeded(assertion_name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether an object carries a key.
     *
     * @param {string} key_to_search - The key looked for.
     * @param {Object} object - Where it is looked for.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_object_contains_key(key_to_search, object, assertion_name) {
        if (key_to_search in object) {
            UnitTest.#succeeded(assertion_name);
            return;
        }
        UnitTest.#failedSearch(key_to_search, object, assertion_name);
    }

    // -----------------------------------------------------------------------

    /**
     * Say whether an object carries no such key.
     *
     * @param {string} key_to_search - The key looked for.
     * @param {Object} object - Where it is looked for.
     * @param {string} assertion_name - What is being checked.
     * @returns {void}
     */
    static assert_object_not_contains_key(key_to_search, object, assertion_name) {
        if (key_to_search in object) {
            UnitTest.#failedSearch(key_to_search, object, assertion_name);
            return;
        }
        UnitTest.#succeeded(assertion_name);
    }

    // -----------------------------------------------------------------------
    // PRIVATE
    // -----------------------------------------------------------------------

    /**
     * Say an assertion passed.
     *
     * @private
     * @param {string} assertion_name - What was being checked.
     * @returns {void}
     */
    static #succeeded(assertion_name) {
        console.info('%cAssertion : ' + assertion_name + ' success !', 'color: green');
    }

    // -----------------------------------------------------------------------

    /**
     * Say an assertion got something else than what it expected.
     *
     * @private
     * @param {*} value_expected - What was expected.
     * @param {*} value_obtained - What was there.
     * @param {string} assertion_name - What was being checked.
     * @returns {void}
     */
    static #failed(value_expected, value_obtained, assertion_name) {
        console.error('Assertion : ' + assertion_name + ' failed !'
            + '\nValue expected : ' + value_expected
            + ', value obtained : ' + value_obtained);
    }

    // -----------------------------------------------------------------------

    /**
     * Say an assertion found two things it wanted to tell apart.
     *
     * @private
     * @param {*} value - What both sides hold.
     * @param {string} assertion_name - What was being checked.
     * @returns {void}
     */
    static #failedEquality(value, assertion_name) {
        console.error('Assertion : ' + assertion_name + ' failed !'
            + '\nBoth values are equal : ' + value);
    }

    // -----------------------------------------------------------------------

    /**
     * Say an assertion did not find what it looked for, or found it.
     *
     * @private
     * @param {*} value_search - What was looked for.
     * @param {*} container - Where it was looked for.
     * @param {string} assertion_name - What was being checked.
     * @returns {void}
     */
    static #failedSearch(value_search, container, assertion_name) {
        console.error('Assertion : ' + assertion_name + ' failed !'
            + '\nValue searched : ' + value_search + ', container : ' + container);
    }
}
