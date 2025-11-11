/**
:filename: purejs-tools.UnitTest.js
:author: Florian Lopitaux
:contact: florian.lopitaux@gmail.com
:summary: file that contains the UnitTest class.

.. _This file is part of PureJS-Tools : https://sourceforge.net/projects/purejs-tools/
..
    -------------------------------------------------------------------------

    Copyright (C) 2024  Florian LOPITAUX
    13100 Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    PureJS-Tools is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PureJS-Tools is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PureJS-Tools. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------
*/

class UnitTest {
    // FIELDS
    #tests;


    // CONSTRUCTOR
    constructor() {
        // array which stocks all test function to called
        this.#tests = [];
    }


    // PUBLIC METHODS
    /**
     * Added a new unit test function to launch.
     *
     * @param func_test The test function to add
     */
    add_test(func_test) {
        this.#tests.push(func_test);
    }

    /**
     * Launch all unit tests put in the list.
     * This function serves like a run function.
     */
    launch_unit_test() {
        this.#tests.forEach(async (func) => {
            await func();
        });
    }


    // PUBLIC STATIC METHODS
    /**
     * Assertion between two values if there are equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param value_expected the value expected by the test
     * @param value_to_compare the value to test
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_values_equals(value_expected, value_to_compare, assertion_name) {
        if (value_to_compare !== value_expected) {
            this.#print_assert_failed(value_to_compare, value_expected, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two values if there aren't equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param first_value the first value to compare
     * @param second_value the second value to compare
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_values_not_equals(first_value, second_value, assertion_name) {
        if (first_value === second_value) {
            this.#print_assert_failed(first_value, second_value, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two objects if there are equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param object_expected the object expected by the test
     * @param object_to_compare the object to test
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_equals(object_expected, object_to_compare, assertion_name) {
        const first_object = JSON.stringify(object_to_compare);
        const second_object = JSON.stringify(object_expected);

        if (first_object !== second_object) {
            this.#print_assert_failed(object_to_compare, object_expected, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion between two objects if there aren't equals.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param first_object the first object to compare
     * @param second_object the second object to compare
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_not_equals(first_object, second_object, assertion_name) {
        const first_object_stringify = JSON.stringify(first_object);
        const second_object_stringify = JSON.stringify(second_object);

        if (first_object === second_object) {
            this.#print_assert_failed(first_object_stringify, second_object_stringify, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion to check if an array contains a given value.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param value_to_search the value to search in the array
     * @param array the array that possibly contains the value
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_array_contains(value_to_search, array, assertion_name) {
        if (array.includes(value_to_search)) {
            this.#print_assert_success(assertion_name);
        } else {
            this.#print_assert_search_failed(value_to_search, array, assertion_name);
        }
    }

    /**
     * Assertion to check if an array doesn't contain a given value.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param value_to_search the value to search in the array
     * @param array the array that possibly contains the value
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_array_not_contains(value_to_search, array, assertion_name) {
        if (array.includes(value_to_search)) {
            this.#print_assert_search_failed(value_to_search, array, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }

    /**
     * Assertion to check if an object (dictionary) contains a given key.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param key_to_search the key to search in the object
     * @param object the object (dictionary) that possibly contains the key
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_contains_key(key_to_search, object, assertion_name) {
        if (key_to_search in object) {
            this.#print_assert_success(assertion_name);
        } else {
            this.#print_assert_search_failed(key_to_search, object, assertion_name);
        }
    }

    /**
     * Assertion to check if an object (dictionary) doesn't contain a given key.
     * Print in the console if the assertion is succeeded (green message) or failed (red message).
     *
     * @param key_to_search the key to search in the object
     * @param object the object (dictionary) that possibly contains the key
     * @param assertion_name The name of the test, used in the log to know which tests succeed and failed
     */
    static assert_object_not_contains_key(key_to_search, object, assertion_name) {
        if (key_to_search in object) {
            this.#print_assert_search_failed(key_to_search, object, assertion_name);
        } else {
            this.#print_assert_success(assertion_name);
        }
    }


    // PRIVATE STATIC METHODS
    /**
     * Print an assertion failed in the console.
     *
     * @param value_expected the value expected
     * @param value_compared the value tested
     * @param assertion_name the name of the test
     */
    static #print_assert_failed(value_expected, value_compared, assertion_name) {
        console.error("Assertion : " + assertion_name + " failed !"
                + "\nValue expected : " + value_expected + ", value obtain : " + value_compared);
    }

    /**
     * Print an assertion that search element in container (array or object) failed in the console.
     * 
     * @param value_search the value searched
     * @param container the container that contains or not the value
     * @param assertion_name the name of the test
     */
    static #print_assert_search_failed(value_search, container, assertion_name) {
        console.error("Assertion : " + assertion_name + " failed !"
            + "\nValue searched : " + value_search + ", container : " + container);
    }

    /**
     * Print an assertion succeed in the console.
     *
     * @param assertion_name the name of the test
     */
    static #print_assert_success(assertion_name) {
        console.info("%cAssertion : " + assertion_name + " success !", 'color: green');
    }
}
