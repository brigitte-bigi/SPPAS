/**
:filename: tests.js.accessibilityTest.js
:author: Florian Lopitaux
:contact: contact@sppas.org
:summary: Test file of the accessibility class.

.. _This file is part of Whakerexa: https://sourceforge.net/projects/whakerexa/ ,
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

// instantiate unit tests class
let accessibility_tests = new UnitTest();



// -----------------------------------------------------------------------
// UNIT TESTS
// -----------------------------------------------------------------------

// getters test
accessibility_tests.add_test(() => {
    // getters test of color schemes
    UnitTest.assert_array_contains("dark", accessibility_manager.color_schemes, "default_colors_test");
    UnitTest.assert_values_equals(1, accessibility_manager.color_schemes.length, "default_colors_size_test");
    UnitTest.assert_values_equals("", accessibility_manager.activated_color_scheme, "activated_color_default_test");

    // getters test of contrast schemes
    UnitTest.assert_array_contains("contrast", accessibility_manager.contrast_schemes, "default_contrasts_test");
    UnitTest.assert_values_equals(1, accessibility_manager.contrast_schemes.length, "default_contrasts_size_test");
    UnitTest.assert_values_equals("", accessibility_manager.activated_contrast_scheme, "activated_contrast_default_test");
});

// -----------------------------------------------------------------------
// setters test
accessibility_tests.add_test(() => {
    const color_test = "desert";
    const contrast_test = "semi-contrast";

    accessibility_manager.add_color_scheme(color_test);
    accessibility_manager.add_contrast_scheme(contrast_test);

    UnitTest.assert_array_contains(color_test, accessibility_manager.color_schemes, "add_color_test");
    UnitTest.assert_array_contains(contrast_test, accessibility_manager.contrast_schemes, "add_contrast_test");

    accessibility_manager.remove_color_scheme(color_test);
    accessibility_manager.remove_contrast_scheme(contrast_test);

    UnitTest.assert_array_not_contains(color_test, accessibility_manager.color_schemes, "remove_color_test");
    UnitTest.assert_array_not_contains(contrast_test, accessibility_manager.contrast_schemes, "remove_contrast_test");
});

// -----------------------------------------------------------------------
// switch color scheme test
accessibility_tests.add_test(() => {
    // check if there is only color scheme to test the switch method
    if (accessibility_manager.color_schemes.length !== 1) {
        return null;
    }

    OnLoadManager.addLoadFunction(() => {
        const old_color = accessibility_manager.activated_color_scheme;
        const color = accessibility_manager.color_schemes[0];

        accessibility_manager.switch_color_scheme();

        if (old_color === "") {
            UnitTest.assert_array_contains(color, Array.from(document.body.classList), "switch_color_1_test");
        } else {
            UnitTest.assert_array_not_contains(color, Array.from(document.body.classList), "switch_color_not_1_test");
        }

        accessibility_manager.switch_color_scheme();

        if (old_color === "") {
            UnitTest.assert_array_not_contains(color, Array.from(document.body.classList), "switch_color_not_2_test");
        } else {
            UnitTest.assert_array_contains(color, Array.from(document.body.classList), "switch_color_2_test");
        }
    });
});

// -----------------------------------------------------------------------
// activate color scheme test
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        let to_delete = false;
        if (accessibility_manager.color_schemes.length === 1) {
            to_delete = true;
            accessibility_manager.add_color_scheme("desert");
        }

        // get the base color scheme for reset after the tests
        const old_color = accessibility_manager.activated_color_scheme;

        // test activate color with all color schemes registered
        accessibility_manager.color_schemes.forEach(element => {
            accessibility_manager.activate_color_scheme(element);

            UnitTest.assert_values_equals(element, accessibility_manager.activated_color_scheme, "activate_color_1_" + element + "_test");
            UnitTest.assert_array_contains(element, Array.from(document.body.classList), "activate_color_2_" + element + "_test")
        });

        // reset base color scheme
        accessibility_manager.activate_color_scheme(old_color);

        if (to_delete) {
            accessibility_manager.remove_color_scheme("desert");
        }
    });
});

// -----------------------------------------------------------------------
// switch contrast scheme test
accessibility_tests.add_test(() => {
    if (accessibility_manager.contrast_schemes.length !== 1) {
        return null;
    }

    OnLoadManager.addLoadFunction(() => {
        const old_contrast = accessibility_manager.activated_contrast_scheme;
        const contrast = accessibility_manager.contrast_schemes[0];

        accessibility_manager.switch_contrast_scheme();

        if (old_contrast === "") {
            UnitTest.assert_array_contains(contrast, Array.from(document.body.classList), "switch_contrast_1_test");
        } else {
            UnitTest.assert_array_not_contains(contrast, Array.from(document.body.classList), "switch_contrast_not_1_test");
        }

        accessibility_manager.switch_contrast_scheme();

        if (old_contrast === "") {
            UnitTest.assert_array_not_contains(contrast, Array.from(document.body.classList), "switch_contrast_not_2_test");
        } else {
            UnitTest.assert_array_contains(contrast, Array.from(document.body.classList), "switch_contrast_2_test");
        }
    });
});

// -----------------------------------------------------------------------
// activate contrast scheme test
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        let to_delete = false;
        if (accessibility_manager.contrast_schemes.length === 1) {
            accessibility_manager.add_contrast_scheme("semi-contrast");
            to_delete = true
        }

        // get the base color scheme for reset after the tests
        let old_contrast = accessibility_manager.activated_contrast_scheme;

        // test activate color with all color schemes registered
        accessibility_manager.contrast_schemes.forEach(element => {
            accessibility_manager.activate_contrast_scheme(element);

            UnitTest.assert_values_equals(element, accessibility_manager.activated_contrast_scheme, "activate_contrast_1_" + element + "_test");
            UnitTest.assert_array_contains(element, Array.from(document.body.classList), "activate_contrast_2_" + element + "_test")
        });

        // reset base contrast scheme
        accessibility_manager.activate_contrast_scheme(old_contrast);

        if (to_delete) {
            accessibility_manager.remove_contrast_scheme("semi-contrast");
        }
    });
});

// -----------------------------------------------------------------------
// load body classes test
accessibility_tests.add_test(() => {
    OnLoadManager.addLoadFunction(() => {
        const url = new URLSearchParams(document.location.search);
        let body_classes = Array.from(document.body.classList);

        // test color scheme
        if (url.has(AccessibilityScheme.COLOR_PARAMETER_NAME)) {
            const param_value = url.get(AccessibilityScheme.COLOR_PARAMETER_NAME);

            if (accessibility_manager.color_schemes.includes(param_value)) {
                UnitTest.assert_values_equals(param_value, accessibility_manager.activated_color_scheme, "activated_color_loaded_test");
                UnitTest.assert_array_contains(param_value, body_classes, "color_parameter_test");
            } else {
                UnitTest.assert_values_not_equals(param_value, accessibility_manager.activated_color_scheme, "activated_color_loaded_test");
                UnitTest.assert_array_not_contains(param_value, body_classes, "color_parameter_test");
            }

        } else {
            accessibility_manager.color_schemes.forEach(element => {
                UnitTest.assert_array_not_contains(element, body_classes, "loaded_color_not_" + element + "_test");
            });
        }

        // test contrast scheme
        if (url.has(AccessibilityScheme.CONTRAST_PARAMETER_NAME)) {
            const param_value = url.get(AccessibilityScheme.CONTRAST_PARAMETER_NAME);

            // check if the wexa_contrast contains a valid value
            if (accessibility_manager.contrast_schemes.includes(param_value)) {
                UnitTest.assert_values_equals(param_value, accessibility_manager.activated_contrast_scheme, "activated_contrast_loaded_test");
                UnitTest.assert_array_contains(param_value, body_classes, "contrast_parameter_test");
            } else {
                UnitTest.assert_values_not_equals(param_value, accessibility_manager.activated_contrast_scheme, "activated_contrast_loaded_test");
                UnitTest.assert_array_not_contains(param_value, body_classes, "contrast_parameter_test");
            }

        } else {
            accessibility_manager.contrast_schemes.forEach(element => {
                UnitTest.assert_array_not_contains(element, body_classes, "loaded_contrast_not_" + element + "_test");
            });
        }
    });
});



// -----------------------------------------------------------------------
// RUN TESTS
// -----------------------------------------------------------------------

// launch all unit tests added
accessibility_tests.launch_unit_test();
