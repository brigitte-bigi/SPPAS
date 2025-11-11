/**
 :filename: js.toggleselect.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Class for toggling checkbox states.

 Copyright (C) 2024, Brigitte Bigi, CNRS
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

*/

// --------------------------------------------------------------------------

/**
 *
 * A class that manages the functionality for toggling checkbox states
 * and updating the associated button visuals.
 *
 * This class provides the ability to manage buttons that can select or
 * deselect all checkboxes within a specified group. It also handles a
 * third state where only some checkboxes are selected, ensuring
 * the button accurately reflects the current selection status.
 *
 * The button associated with the checkboxes displays an image that
 * changes based on the following states:
 * - All checkboxes are checked.
 * - Some checkboxes are checked.
 * - No checkbox is checked.
 *
 * The button's image updates dynamically after each checkbox toggling,
 * ensuring real-time feedback on the selection status.
 *
 * This class is useful for forms or interfaces where multiple options
 * can be selected, enhancing user experience through clear visual cues.
 *
 */
class ToggleSelector {
    // Define base path and icon names as member variables
    static ICON_PATH = "./whakerkit/icons";

    // Icon names for different states
    static ICONS = {
        CHECKED: "checked.png",
        UNCHECKED: "unchecked.png",
        HALF_CHECKED: "half-checked.png",
        HALF_UNCHECKED: "half-unchecked.png",
        HALF_CHECKED_DARK: "half-checked-dark.png",
        HALF_UNCHECKED_DARK: "half-unchecked-dark.png",
        CHECKED_DARK: "checked-dark.png",
        UNCHECKED_DARK: "unchecked-dark.png"
    };

    // Define CSS selectors for buttons and checkboxes
    static BUTTON_SELECTOR = 'button.accordion-action';
    static CHECKBOX_SELECTOR = 'input[type="checkbox"]';

    // Fields
    _iconPath;
    _detailsElt;

    // Constructor
    constructor(icon_path, detailsId) {
        if (icon_path) {
            this._iconPath = icon_path;
        } else {
            this._iconPath = ToggleSelector.ICON_PATH;
        }

        // The <details> element which is manipulated in this class
        this._detailsElt = document.getElementById(detailsId);
        if (!this._detailsElt) {
            throw new Error(`ToggleSelector instantiation failed: No details element found with id: ${detailsId}.`);
        }

        // Call handleInputsOnLoad() to initialize any inputs or settings
        this.handleInputsOnLoad();
    }

    // ----------------------------------------------------------------------

    /**
     * Retrieves all checkbox inputs within the details element
     * that have a data-toggle attribute.
     *
     * @returns {NodeList} A NodeList of checkbox input elements
     * that have the data-toggle attribute.
     */
    getCheckboxes() {
        return this._detailsElt.querySelectorAll('input[type="checkbox"][data-toggle]');
    }

    // ----------------------------------------------------------------------

    /**
     * Handles the setup of checkbox listeners and button updates on page load.
     *
     * @returns {void}
     *
     */
    handleInputsOnLoad() {
        // Setup listeners for checkboxes
        this.setupCheckboxListeners();

        // Update all toggle buttons to adjust colors with theme
        this.updateAllToggleButtons();

        // Attach event listener for click events on checkboxes
        document.addEventListener('click', (event) => {
            const target = event.target;
            if (target.type === 'checkbox') {
                this.updateAllToggleButtons();
            }
        });
    }

    // ----------------------------------------------------------------------

    /**
     * Toggles the selection of checkboxes associated with the given button.
     *
     * @returns {void}
     *
     */
    toggleSelection(event) {
        const checkboxes = this.getCheckboxes();
        const button = event.currentTarget;

        // Check if any of the checkboxes are already checked
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

        // Toggle the checked state of all checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.checked = !anyChecked;
        });

        // Update the button image based on the new state
        this.updateToggleButton(button, !anyChecked);
    }

    // ----------------------------------------------------------------------

    /**
     * Updates the button's image based on the checkbox state.
     *
     * @param {HTMLElement} button - The button element to update.
     * @param {boolean} anyChecked - True if any checkbox is checked, false otherwise.
     * @param {boolean} [oneChecked=false] - True if at least one checkbox is checked but not all.
     * @param {boolean} [check=false] - Determines whether the button is in "check" state.
     *
     * @returns {void}
     *
     */
    updateToggleButton(button, anyChecked, oneChecked = false, check = false) {
        // Get the image inside the button
        const toggleImg = button.querySelector('img');
        // Detect if dark mode is active
        const isDarkMode = document.body.classList.contains('dark');

        let imgSrc = ""; // Variable to hold the image source path

        // Determine which image to display based on the checkbox states
        if (oneChecked && check) {
            imgSrc = isDarkMode ?
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED_DARK}` :
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED}`;
        } else if (oneChecked && !check) {
            imgSrc = isDarkMode ?
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_UNCHECKED_DARK}` :
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED}`;
        } else {
            imgSrc = anyChecked
                ? (isDarkMode ?
                    `${this._iconPath}/${ToggleSelector.ICONS.CHECKED_DARK}` :
                    `${this._iconPath}/${ToggleSelector.ICONS.CHECKED}`)
                : (isDarkMode ?
                    `${this._iconPath}/${ToggleSelector.ICONS.UNCHECKED_DARK}` :
                    `${this._iconPath}/${ToggleSelector.ICONS.UNCHECKED}`);
        }

        // Update the image source
        if (toggleImg) {
            toggleImg.src = imgSrc;
        } else {
            console.error(`Image not found in button: ${button.id}`);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Sets up listeners for checkboxes to monitor changes and update the button state accordingly.
     *
     * @returns {void}
     *
     */
    setupCheckboxListeners() {

        const checkboxes = this.getCheckboxes();
        const button = this._detailsElt.querySelector('button.accordion-action[data-toggle]');

        // Add a 'change' event listener to each checkbox
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // At least one is checked
                const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
                // All are checked
                const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);

                // Log the state for debugging purposes
                console.log(`Checkbox ${checkbox.id} changed. Any checked: ${anyChecked}, All checked: ${allChecked}`);

                // Update button based on the state
                this.updateButtonState(button, anyChecked, allChecked);
            });
        });
    }

    // ----------------------------------------------------------------------

    /**
     * Updates the button state based on the checkbox states.
     *
     * @param {HTMLElement} button - The button element to update.
     * @param {boolean} anyChecked - True if any checkbox is checked.
     * @param {boolean} allChecked - True if all checkboxes are checked.
     *
     * @returns {void}
     *
     */
    updateButtonState(button, anyChecked, allChecked) {
        if (allChecked) {
            this.updateToggleButton(button, anyChecked);
        } else if (anyChecked) {
            this.updateToggleButton(button, anyChecked, true, true);
        } else {
            this.updateToggleButton(button, anyChecked, false, false);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Updates all toggle buttons based on the current state of checkboxes in their respective sections.
     *
     * @returns {void}
     *
     */
    updateAllToggleButtons() {
        const buttons = this._detailsElt.querySelectorAll(ToggleSelector.BUTTON_SELECTOR);
        buttons.forEach(button => {
            const checkboxes = button.closest('details').querySelectorAll(ToggleSelector.CHECKBOX_SELECTOR);
            const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
            const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);

            // Update button based on the state of checkboxes
            this.updateButtonState(button, anyChecked, allChecked);
        });
    }

}
