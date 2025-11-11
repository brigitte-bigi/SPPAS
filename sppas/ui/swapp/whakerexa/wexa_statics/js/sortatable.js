/**
:filename: statics.js.sortable.js
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: Class to sort rows of a table.

Copyright (C) 2023-2024 Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This banner notice must not be removed.

**/

/**
 * Class SortaTable
 *
 * This class provides functionality to make an HTML table's columns sortable.
 * It allows attaching event listeners to the headers of a table and sorting
 * the rows based on the values in a specific column, either in ascending or
 * descending order.
 *
 * Key Features:
 * - Attaches 'click' event listeners to headers with the 'sortatable' class.
 * - Sorts table rows based on the 'data-sort' attribute found in the headers.
 * - Supports sorting based on different data types, including dates.
 *
 * Public Methods:
 * - attachSortListeners(): Binds the sorting functionality to the headers of the table.
 * - sort(): Sorts the rows of the table based on the selected column and order.
 *
 * Fields:
 * - _tableElt: The table element selected by its ID.
 * - _className: Stores the class name of sortable headers.
 *
 * Usage:
 * const sortable = new SortaTable('myTableId');
 * sortable.attachSortListeners();
 */
class SortaTable {

    // FIELDS
    _tableElt
    _className

    // CONSTRUCTOR
    /**
     * Instantiate the sortable class.
     *
     * @param tableId {string} The id of the table to sort columns
     *
     */
    constructor(tableId) {
        // Name of the CSS class used by the button in the <th> element
        this._className = ".sortatable";
        console.debug("Sortatable is instantiated for table element: ", tableId);

        // The <table> element which is manipulated in this class
        this._tableElt = document.getElementById(tableId);
        if (!this._tableElt) {
            // Table element is not found, log a warning and prevent further execution
            console.warn(`No table element found with id: ${tableId}. SortaTable instantiation is skipped.`);
        }

        // Store original rows order
        const tbody = this._tableElt.querySelector('tbody');
        const rows = Array.from(tbody.getElementsByTagName('tr'));
        rows.forEach((row, index) => {
            row.setAttribute('data-original-index', index);
        });
    }

    // ----------------------------------------------------------------------
    // PUBLIC
    // ----------------------------------------------------------------------

    /**
     * Returns the identifier (ID) of the table element.
     *
     * This method retrieves the 'id' attribute of the table element that
     * was passed during the instantiation of the class. It allows
     * access to the ID of the HTML table for further manipulations or
     * reference purposes.
     *
     * @returns {string} The ID of the table element.
     *
     */
    getTableId() {
        return this._tableElt.getAttribute("id");
    }

    // ----------------------------------------------------------------------

    /**
     * Attaches event listeners to table headers with the class 'sortable'.
     *
     * The headers are expected to have a 'data-sort' attribute which specifies the column to sort.
     *
     */
    attachSortListeners() {
        if (!this._tableElt) {
            return;
        }
        console.debug("Attach sort listeners for table " + this._tableElt);
        // Add event listeners to all headers with class 'sortatable'
        const sortButtons = this._tableElt.querySelectorAll(this._className);
        console.debug("Found " + sortButtons.length + " sort buttons in headers");

        sortButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                console.debug(" ... button: ", `[${button}]`);

                // Retrieve the data-sort attribute from the clicked header
                const sortAttribute = button.getAttribute('data-sort');
                const isAsc = button.classList.contains('sort-asc');
                const isDesc = button.classList.contains('sort-desc');

                // Remove sort classes from all headers to reset the state
                this._tableElt.querySelectorAll(this._className).forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });

                // Call the sortTable function to sort the table rows and update button
                // Toggle between 3 states: no sort -> ascending -> descending
                if (isAsc) {
                    button.classList.remove('sort-asc');
                    button.classList.add('sort-desc');
                    this.#sortTable(sortAttribute, false);
                } else if (isDesc) {
                    button.classList.remove('sort-desc');
                    // No sort applied, reset table
                    this.#noSortTable();
                } else {
                    button.classList.add('sort-asc');
                    this.#sortTable(sortAttribute, true);
                }

                event.stopPropagation();
            });
        });
    }

    // ----------------------------------------------------------------------

    /**
     * Sorts the table based on a specified column.
     *
     * @param {string} column - The name of the column to sort by.
     * @param {boolean} [isAsc=true] - Whether to sort in ascending order (true) or descending (false).
     *
     */
    sort(column, isAsc = true) {
        // Sort the table based on the specified column
        this.#sortTable(column, isAsc);

        // Optionally, update the class on the header to reflect the current sort direction
        const headerButton = this._tableElt.querySelector(`button[data-sort="${column}"]`);
        if (headerButton) {
            this._tableElt.querySelectorAll(this._className).forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            headerButton.classList.add(isAsc ? 'sort-asc' : 'sort-desc');
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Update the visibility of toggable columns in the table.
     *
     * @param {NodeList} checkBoxes - List of checkboxes with data-toggle attribute
     *
     */
    toggleColumnVisibility(checkBoxes) {
        // Iterate over each checkbox in checkBoxes
        checkBoxes.forEach(checkbox => {
            // Check if the checkbox has a data-toggle attribute
            const columnName = checkbox.getAttribute('data-toggle');
            if (!columnName) {
                console.warn("Checkbox does not have a data-toggle attribute. Skipping...");
                return; // Skip this checkbox if it doesn't have a data-toggle attribute
            }

            // Initialize column index
            let columnIndex = -1;

            // Iterate through the header cells to find the index
            const headerCells = this._tableElt.querySelectorAll('thead th');
            for (let index = 0; index < headerCells.length; index++) {
                const cell = headerCells[index];

                // Check if the cell has the data-sort attribute matching columnName
                if (cell.getAttribute('data-sort') === columnName) {
                    columnIndex = index; // Store the column index
                    break; // Exit the loop early since we've found the column
                }

                // Find the button with class "sortatable"
                const button = cell.querySelector(this._className);
                // Check if the button exists and matches the column name
                if (button && button.getAttribute('data-sort') === columnName) {
                    columnIndex = index; // Store the column index
                    break; // Exit the loop early since we've found the column
                }
            }

            // If columnIndex is found, toggle its visibility
            if (columnIndex !== -1) {
                // Get the checkbox state (checked or not)
                const checkboxState = checkbox.checked;

                // Use the columnVisibility method to update the visibility
                this.columnVisibility(columnIndex, checkboxState);

                // Optionally recalculate table width after updating visibility
                this._tableElt.style.width = '100%';
            } else {
                console.warn(`Column with name "${columnName}" not found.`);
            }
        });
    }

    // ----------------------------------------------------------------------

    /**
     * Enable or disable the visibility of a column in the table.
     *
     * @param {number} columnIndex - The index of the column to toggle.
     * @param {boolean} show - Whether to show or hide the column.
     *
     */
    columnVisibility(columnIndex, show) {
        // Get all table rows
        const rows = this._tableElt.rows;

        // Iterate over each row (including header)
        for (let i = 0; i < rows.length; i++) {
            const cell = rows[i].cells[columnIndex];
            if (cell) {
                // Toggle the 'hidden' class based on the show flag
                if (show) {
                    cell.classList.remove('hidden');
                } else {
                    cell.classList.add('hidden');
                }
            }
        }
    }

    // ----------------------------------------------------------------------
    // PRIVATE
    // ----------------------------------------------------------------------

    /**
     * Resets the table to its original state (no sorting).
     *
     */
    #noSortTable() {
        const tbody = this._tableElt.querySelector('tbody');
        const rows = Array.from(tbody.getElementsByTagName('tr'));

        // Re-organize lines by their original order
        rows.sort((a, b) => a.getAttribute('data-original-index') - b.getAttribute('data-original-index'));
        rows.forEach(row => tbody.appendChild(row));
    }

    // ----------------------------------------------------------------------

    /**
     * Sorts the table rows based on the selected column.
     *
     * @param {string} sortAttribute - The attribute of the column to sort by (e.g., column name).
     * @param {boolean} isAsc - Whether to sort in ascending order (true) or descending (false).
     *
     */
    #sortTable(sortAttribute, isAsc) {
        // Get the index of the column to sort by
        const columnIndex = this._tableElt.querySelector(`button[data-sort="${sortAttribute}"]`).closest('th').cellIndex;

        // Get the tbody element from the table
        const tableBody = this._tableElt.querySelector('tbody');
        // Convert the HTMLCollection of rows into an array for sorting
        const rows = Array.from(tableBody.getElementsByTagName('tr'));
        // Check if the attribute to sort by is 'date'
        const isDate = sortAttribute === 'date';

        // Sort the rows array using a custom comparator
        rows.sort((a, b) => {
            // Fetch the text content of the cells in the current column
            let aValue = a.cells[columnIndex].textContent.trim();
            let bValue = b.cells[columnIndex].textContent.trim();

            // If the attribute is 'date', convert string to Date object
            if (isDate) {
                aValue = new Date(aValue);
                bValue = new Date(bValue);
            }

            // Determine the sort order based on the cell values and isAsc flag
            if (aValue < bValue) return isAsc ? -1 : 1;
            if (aValue > bValue) return isAsc ? 1 : -1;
            return 0;
        });

        // Re-append sorted rows back to the table body
        rows.forEach(row => tableBody.appendChild(row));
    }

}
