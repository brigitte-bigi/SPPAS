/**
:filename: tests.js.sortatableTest.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Test file of the SortaTable class.

.. _This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa ,
.. on 2026-08-13.
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
let sortatable_tests = new UnitTest();


/**
 * Build the table every test of this file works on, and put it in the page.
 *
 * Three columns, two rows of data, and one row holding what a reference opens:
 * a single cell spanning the whole table, the way a bibliography writes an
 * abstract or a BibTeX source.
 *
 * @returns {HTMLTableElement} The table, added to the document.
 */
function sortatable_table() {
    const table = document.createElement('table');
    table.id = 'sortatable-test-table';

    const head = document.createElement('thead');
    const headers = document.createElement('tr');
    ['number', 'year', 'reference'].forEach(name => {
        const header = document.createElement('th');
        header.setAttribute('data-sort', name);
        header.textContent = name;
        headers.appendChild(header);
    });
    head.appendChild(headers);
    table.appendChild(head);

    const body = document.createElement('tbody');

    const row = document.createElement('tr');
    row.id = 'sortatable-test-row';
    ['1', '2022', 'A reference'].forEach(text => {
        const cell = document.createElement('td');
        cell.textContent = text;
        row.appendChild(cell);
    });
    body.appendChild(row);

    const opened = document.createElement('tr');
    opened.id = 'sortatable-test-opened-row';
    const wide = document.createElement('td');
    wide.colSpan = 3;
    wide.textContent = 'What the paper says.';
    opened.appendChild(wide);
    body.appendChild(opened);

    table.appendChild(body);
    document.body.appendChild(table);

    return table;
}


/**
 * Remove the table a test worked on.
 *
 * @param table {HTMLTableElement} The table to remove.
 * @returns {void}
 */
function sortatable_remove(table) {
    table.remove();
}


// -----------------------------------------------------------------------
// Hiding a column hides the cells of that column, in the header as in the
// rows of the references.
// -----------------------------------------------------------------------

sortatable_tests.add_test(() => {
    const table = sortatable_table();
    const sorter = new SortaTable(table.id);

    sorter.columnVisibility(0, false);

    UnitTest.assert_array_contains(true,
        [table.querySelector('thead th').classList.contains('hidden')],
        "sortatable_header_cell_hidden_test");
    UnitTest.assert_array_contains(true,
        [document.getElementById('sortatable-test-row').cells[0].classList.contains('hidden')],
        "sortatable_row_cell_hidden_test");

    sortatable_remove(table);
});


// -----------------------------------------------------------------------
// A cell spanning several columns belongs to none of them: what a row
// opens is never hidden by a column that is unchecked. Requirement B25.
// -----------------------------------------------------------------------

sortatable_tests.add_test(() => {
    const table = sortatable_table();
    const sorter = new SortaTable(table.id);

    sorter.columnVisibility(0, false);

    const opened = document.getElementById('sortatable-test-opened-row');
    UnitTest.assert_array_contains(false,
        [opened.cells[0].classList.contains('hidden')],
        "sortatable_spanning_cell_kept_test");

    sortatable_remove(table);
});


// -----------------------------------------------------------------------
// Whatever the column asked for, a cell spanning several columns is left
// alone: the abstract holds at every width. Requirement B25.
// -----------------------------------------------------------------------

sortatable_tests.add_test(() => {
    const table = sortatable_table();
    const sorter = new SortaTable(table.id);

    sorter.columnVisibility(0, false);
    sorter.columnVisibility(1, false);
    sorter.columnVisibility(2, false);

    const opened = document.getElementById('sortatable-test-opened-row');
    UnitTest.assert_array_contains(false,
        [opened.cells[0].classList.contains('hidden')],
        "sortatable_spanning_cell_kept_whatever_the_column_test");

    sortatable_remove(table);
});


// -----------------------------------------------------------------------
// A column that is checked back gives its cells back, and the cell that
// spans the table has nothing to give back.
// -----------------------------------------------------------------------

sortatable_tests.add_test(() => {
    const table = sortatable_table();
    const sorter = new SortaTable(table.id);

    sorter.columnVisibility(0, false);
    sorter.columnVisibility(0, true);

    UnitTest.assert_array_contains(false,
        [document.getElementById('sortatable-test-row').cells[0].classList.contains('hidden')],
        "sortatable_column_shown_again_test");
    UnitTest.assert_array_contains(false,
        [document.getElementById('sortatable-test-opened-row').cells[0].classList.contains('hidden')],
        "sortatable_spanning_cell_untouched_test");

    sortatable_remove(table);
});


// launch all unit tests added
sortatable_tests.launch_unit_test();
