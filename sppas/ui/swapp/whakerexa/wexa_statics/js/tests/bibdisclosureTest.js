/**
:filename: tests.js.bibdisclosureTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the ReferenceDisclosure class.

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
let reference_disclosure_tests = new UnitTest();


/**
 * Write in the page a control and the content it opens.
 *
 * The content follows the control in the order of the document, which is what
 * lets the keyboard reach it without anything having to move.
 *
 * @param {string} name - What tells the elements of this test from the others.
 * @returns {Object} The control, the content, and what removes them.
 */
function write_disclosure(name) {
    const holder = document.createElement('div');
    holder.id = name + '-holder';

    const control = document.createElement('button');
    control.type = 'button';
    control.className = 'bib-disclosure-control';
    control.setAttribute('aria-expanded', 'false');
    control.setAttribute('aria-controls', name + '-content');
    control.textContent = 'Abstract';

    const content = document.createElement('div');
    content.className = 'bib-disclosure-content';
    content.id = name + '-content';
    content.hidden = true;
    content.textContent = 'What the paper says.';

    holder.appendChild(control);
    holder.appendChild(content);
    document.body.appendChild(holder);

    return {control: control, content: content, remove: () => holder.remove()};
}


// -----------------------------------------------------------------------
// A content starts closed, and says so.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('closed');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    UnitTest.assert_values_equals(false, disclosure.isOpen, "disclosure_starts_closed_test");
    UnitTest.assert_values_equals('false', written.control.getAttribute('aria-expanded'),
        "disclosure_control_says_closed_test");
    UnitTest.assert_values_equals(true, written.content.hidden, "disclosure_content_hidden_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Opening shows the content and says that the reading has begun. C25.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('open');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    disclosure.open();

    UnitTest.assert_values_equals(true, disclosure.isOpen, "disclosure_open_test");
    UnitTest.assert_values_equals('true', written.control.getAttribute('aria-expanded'),
        "disclosure_control_says_open_test");
    UnitTest.assert_values_equals(false, written.content.hidden, "disclosure_content_shown_test");

    written.remove();
});

// -----------------------------------------------------------------------
// The focus does not move when a content opens: the page would scroll,
// and the reader would lose the sentence they were in. C28.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('focus-open');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    written.control.focus();
    disclosure.open();

    UnitTest.assert_values_equals(written.control, document.activeElement,
        "disclosure_focus_does_not_move_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Closing gives the focus back to the control, which matters when the
// closing came from inside the content: what held the focus is gone.
// Requirements B15 and C24.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('focus-close');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    disclosure.open();
    disclosure.close();

    UnitTest.assert_values_equals(false, disclosure.isOpen, "disclosure_closed_test");
    UnitTest.assert_values_equals(true, written.content.hidden, "disclosure_content_hidden_again_test");
    UnitTest.assert_values_equals(written.control, document.activeElement,
        "disclosure_focus_comes_back_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Whether it is open is read on the control, and never kept beside it:
// two places would be two truths.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('derived');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    written.control.setAttribute('aria-expanded', 'true');

    UnitTest.assert_values_equals(true, disclosure.isOpen, "disclosure_state_is_derived_test");

    written.remove();
});

// -----------------------------------------------------------------------
// A click opens, another closes. The control is a button, so Enter and
// Space do the same without anything being written for them.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('click');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    written.control.click();
    UnitTest.assert_values_equals(true, disclosure.isOpen, "disclosure_click_opens_test");

    written.control.click();
    UnitTest.assert_values_equals(false, disclosure.isOpen, "disclosure_click_closes_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Opening what is already open does nothing wrong: nobody has to know
// the state before asking.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('again');
    const disclosure = new ReferenceDisclosure(written.control, written.content);

    disclosure.open();
    disclosure.open();
    UnitTest.assert_values_equals(true, disclosure.isOpen, "disclosure_open_twice_test");

    disclosure.close();
    disclosure.close();
    UnitTest.assert_values_equals(false, disclosure.isOpen, "disclosure_close_twice_test");

    written.remove();
});

// -----------------------------------------------------------------------
// Opening one content leaves the others alone: closing what nobody asked
// to close makes what is being read disappear.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const first = write_disclosure('first');
    const second = write_disclosure('second');
    const one = new ReferenceDisclosure(first.control, first.content);
    const other = new ReferenceDisclosure(second.control, second.content);

    one.open();
    other.open();

    UnitTest.assert_values_equals(true, one.isOpen, "disclosure_several_open_test");
    UnitTest.assert_values_equals(true, other.isOpen, "disclosure_other_still_open_test");

    first.remove();
    second.remove();
});

// -----------------------------------------------------------------------
// A control placed inside the content closes it too, and the focus comes
// back to the control that opened it.
// -----------------------------------------------------------------------

reference_disclosure_tests.add_test(() => {
    const written = write_disclosure('inside');
    const closing = document.createElement('button');
    closing.type = 'button';
    closing.className = 'bib-disclosure-close';
    closing.textContent = 'Close';
    written.content.appendChild(closing);

    const disclosure = new ReferenceDisclosure(written.control, written.content);
    disclosure.open();
    closing.focus();
    closing.click();

    UnitTest.assert_values_equals(false, disclosure.isOpen, "disclosure_closed_from_inside_test");
    UnitTest.assert_values_equals(written.control, document.activeElement,
        "disclosure_focus_back_from_inside_test");

    written.remove();
});


// launch all unit tests added
reference_disclosure_tests.launch_unit_test();
