/**
:filename: tests.js.accessibilityTest.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Test file of the AccessibilityManager class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2024-03-01.
    -------------------------------------------------------------------------

    Copyright (C) 2024 Brigitte Bigi
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

let accessibility_tests = new UnitTest();


// -----------------------------------------------------------------------
// UNIT TESTS
// -----------------------------------------------------------------------

// Default state
accessibility_tests.add_test(() => {
    UnitTest.assert_values_equals("", accessibility_manager.activatedColorMode, "default_color_mode_test");
    UnitTest.assert_values_equals("", accessibility_manager.activatedContrastMode, "default_contrast_mode_test");
});

// -----------------------------------------------------------------------
// Switch color mode
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        const initial = accessibility_manager.activatedColorMode;

        accessibility_manager.switchColorScheme();

        if (initial === "") {
            UnitTest.assert_array_contains(
                AccessibilityManager.COLOR_MODE,
                Array.from(document.body.classList),
                "switch_color_on_test"
            );
            UnitTest.assert_values_equals(
                AccessibilityManager.COLOR_MODE,
                accessibility_manager.activatedColorMode,
                "switch_color_mode_value_on_test"
            );
        } else {
            UnitTest.assert_array_not_contains(
                AccessibilityManager.COLOR_MODE,
                Array.from(document.body.classList),
                "switch_color_off_test"
            );
            UnitTest.assert_values_equals(
                "",
                accessibility_manager.activatedColorMode,
                "switch_color_mode_value_off_test"
            );
        }

        // restore initial state
        accessibility_manager.switchColorScheme();
    });
});

// -----------------------------------------------------------------------
// Switch contrast mode
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        const initial = accessibility_manager.activatedContrastMode;

        accessibility_manager.switchContrastScheme();

        if (initial === "") {
            UnitTest.assert_array_contains(
                AccessibilityManager.CONTRAST_MODE,
                Array.from(document.body.classList),
                "switch_contrast_on_test"
            );
            UnitTest.assert_values_equals(
                AccessibilityManager.CONTRAST_MODE,
                accessibility_manager.activatedContrastMode,
                "switch_contrast_mode_value_on_test"
            );
        } else {
            UnitTest.assert_array_not_contains(
                AccessibilityManager.CONTRAST_MODE,
                Array.from(document.body.classList),
                "switch_contrast_off_test"
            );
            UnitTest.assert_values_equals(
                "",
                accessibility_manager.activatedContrastMode,
                "switch_contrast_mode_value_off_test"
            );
        }

        // restore initial state
        accessibility_manager.switchContrastScheme();
    });
});

// -----------------------------------------------------------------------
// URL parameter loading
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        const url = new URLSearchParams(document.location.search);
        const bodyClasses = Array.from(document.body.classList);

        if (url.has(AccessibilityManager.COLOR_PARAMETER_NAME)) {
            const param = url.get(AccessibilityManager.COLOR_PARAMETER_NAME);
            if (param === AccessibilityManager.COLOR_MODE) {
                UnitTest.assert_values_equals(param, accessibility_manager.activatedColorMode, "color_param_loaded_test");
                UnitTest.assert_array_contains(param, bodyClasses, "color_param_class_test");
            } else {
                UnitTest.assert_values_equals("", accessibility_manager.activatedColorMode, "color_param_ignored_test");
                UnitTest.assert_array_not_contains(param, bodyClasses, "color_param_class_ignored_test");
            }
        } else {
            UnitTest.assert_array_not_contains(AccessibilityManager.COLOR_MODE, bodyClasses, "no_color_param_test");
        }

        if (url.has(AccessibilityManager.CONTRAST_PARAMETER_NAME)) {
            const param = url.get(AccessibilityManager.CONTRAST_PARAMETER_NAME);
            if (param === AccessibilityManager.CONTRAST_MODE) {
                UnitTest.assert_values_equals(param, accessibility_manager.activatedContrastMode, "contrast_param_loaded_test");
                UnitTest.assert_array_contains(param, bodyClasses, "contrast_param_class_test");
            } else {
                UnitTest.assert_values_equals("", accessibility_manager.activatedContrastMode, "contrast_param_ignored_test");
                UnitTest.assert_array_not_contains(param, bodyClasses, "contrast_param_class_ignored_test");
            }
        } else {
            UnitTest.assert_array_not_contains(AccessibilityManager.CONTRAST_MODE, bodyClasses, "no_contrast_param_test");
        }
    });
});


// -----------------------------------------------------------------------
// RUN TESTS
// -----------------------------------------------------------------------

accessibility_tests.launch_unit_test();
