import { SVGIconsManager } from './svgicons.js';
import { OnLoadManager } from './dom-loader.js';
/**
 :filename: statics.js.toggleselect.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Class for toggling checkbox states.

 Copyright (C) 2023-2026, Brigitte Bigi, CNRS
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
export class ToggleSelector {
    // Define base path and icon names as member variables
    /**
     * The three states of a box, drawn as mono-svg icons.
     *
     * They are injected, not loaded as images: an icon of the framework takes
     * the color of the text it stands in, so a dark mode needs no twin of it.
     */
    static ICONS = {
        CHECKED: "checked",
        UNCHECKED: "unchecked",
        HALF: "half-checked"
    };

    // Define CSS selectors for buttons and checkboxes
    static BUTTON_SELECTOR = 'button.accordion-action';
    static CHECKBOX_SELECTOR = 'input[type="checkbox"]';

    // Fields
    _detailsElt;

    // Constructor
    constructor(detailsId) {
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

        // The icons are drawn once the framework knows where to read them: a
        // page may instantiate this class before wexa.js has said so.
        OnLoadManager.addLoadFunction(() => {
            this.drawBoxes();
            this.updateAllToggleButtons();
        });

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
     * Draw each box with the icon of its state.
     *
     * The native control stays where it is, reachable by the keyboard and read
     * as a checkbox; what is seen is the icon of the framework, injected in the
     * label the control is named by, so that clicking it toggles the control.
     *
     * @returns {void}
     */
    drawBoxes() {
        this.getCheckboxes().forEach(checkbox => {
            const label = this._detailsElt.querySelector('label[for="' + checkbox.id + '"]');
            if (label === null) {
                console.warn(`ToggleSelector: the checkbox "${checkbox.id}" has no label, its box is not drawn.`);
                return;
            }

            let holder = label.querySelector('span.check-box');
            if (holder === null) {
                holder = document.createElement('span');
                holder.className = 'check-box';
                label.insertBefore(holder, label.firstChild);
            }

            holder.replaceChildren();
            SVGIconsManager.inject(holder,
                checkbox.checked === true ? ToggleSelector.ICONS.CHECKED : ToggleSelector.ICONS.UNCHECKED);
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
        // A key that is not the one acting on this button belongs to the page:
        // preventing it would keep the focus from ever leaving.
        if (event.type === 'keydown' && event.key !== 'Enter' && event.key !== ' ') {
            return;
        }

        // A click inside a summary opens or closes the disclosure: this button
        // acts on the boxes, and on nothing else.
        event.preventDefault();
        event.stopPropagation();

        const checkboxes = this.getCheckboxes();
        const button = event.currentTarget;

        // Check if any of the checkboxes are already checked
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

        // Toggle the checked state of all checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.checked = !anyChecked;
        });

        // Update the button image and every box with the new state
        this.updateToggleButton(button, !anyChecked);
        this.drawBoxes();
    }

    // ----------------------------------------------------------------------

    /**
     * Updates the button's image based on the checkbox state.
     *
     * @param {HTMLElement} button - The button element to update.
     * @param {boolean} anyChecked - True if any checkbox is checked, false otherwise.
     * @param {boolean} [oneChecked=false] - True if at least one checkbox is checked but not all.
     *
     * @returns {void}
     *
     */
    updateToggleButton(button, anyChecked, oneChecked = false) {
        let name = ToggleSelector.ICONS.UNCHECKED;

        if (oneChecked === true) {
            name = ToggleSelector.ICONS.HALF;
        } else if (anyChecked === true) {
            name = ToggleSelector.ICONS.CHECKED;
        }

        // inject() leaves an element that already holds an SVG untouched: what
        // is drawn has to go before the new state can be drawn.
        button.replaceChildren();
        SVGIconsManager.inject(button, name);
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

                // Update button and boxes based on the state
                this.updateButtonState(button, anyChecked, allChecked);
                this.drawBoxes();
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
            this.updateToggleButton(button, anyChecked, true);
        } else {
            this.updateToggleButton(button, anyChecked, false);
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
