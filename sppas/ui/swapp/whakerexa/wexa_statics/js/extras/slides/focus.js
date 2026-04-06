/**
 :filename: statics.js.slides.focus_controller.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Focus management for slide content.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://whakerexa.sf.net/

 Copyright (C) 2023-2025 Brigitte Bigi, CNRS
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

 -------------------------------------------------------------------------

 */

'use strict';

/**
 *  This controller ensures that only the active slide exposes focusable
 *  elements to keyboard navigation. It sets tabindex=0 for elements in the
 *  active slide and tabindex=-1 for all other slides, while ignoring disabled
 *  elements.
 */
export default class SlidesFocusController {
    /**
     * Create a SlidesFocusController.
     *
     * @param {Object} [options] - Configuration options.
     * @param {string} [options.focusableSelector] - CSS selector for focusable elements.
     */
    constructor(options = {}) {
        const defaultSelector = [
            'a[href]',
            'button',
            'input',
            'select',
            'textarea',
            'details',
            'summary',
            '[tabindex]:not([tabindex="-1"])',
            '[contenteditable="true"]',
            'video[controls]',
            'audio[controls]'
        ].join(', ');

        this._focusableSelector = typeof options.focusableSelector === 'string'
            ? options.focusableSelector
            : defaultSelector;
    }

    /**
     * Update focusability of all slides.
     *
     * @param {HTMLElement[]} slides - List of slide elements.
     * @param {number} activeIndex - Active slide index (1-based).
     * @returns {void}
     */
    updateFocus(slides, activeIndex) {
        if (!Array.isArray(slides) || slides.length === 0) {
            console.warn("Update focus not available. No slides found.");
            return;
        }

        let safeIndex = activeIndex;
        if (safeIndex < 1) {
            safeIndex = 1;
        }
        if (safeIndex > slides.length) {
            safeIndex = slides.length;
        }

        const activeSlide = slides[safeIndex - 1];

        slides.forEach((slide) => {
            const isActive = slide === activeSlide;
            const tabIndexValue = isActive === true ? 0 : -1;
            this._setTabIndexForSlide(slide, tabIndexValue);
        });
    }

    // -----------------------------------------------------------------------
    // Private utilities
    // -----------------------------------------------------------------------

    /**
     * Set tabindex for all focusable elements inside a slide.
     *
     * @param {HTMLElement} slide - Slide element.
     * @param {number} tabIndexValue - Tabindex value to set (0 or -1).
     * @returns {void}
     * @private
     */
    _setTabIndexForSlide(slide, tabIndexValue) {
        if (!(slide instanceof HTMLElement)) {
            return;
        }

        const elements = this._getFocusableElements(slide);
        const valueString = String(tabIndexValue);

        elements.forEach((element) => {
            const disabled = this._isDisabled(element);
            if (disabled === true) {
                return;
            }
            element.setAttribute('tabindex', valueString);
        });
    }

    /**
     * Get all focusable elements inside a slide.
     *
     * @param {HTMLElement} slide - Slide element.
     * @returns {HTMLElement[]} Focusable elements.
     * @private
     */
    _getFocusableElements(slide) {
        if (!(slide instanceof HTMLElement)) {
            return [];
        }

        const nodeList = slide.querySelectorAll(this._focusableSelector);
        return Array.from(nodeList);
    }

    /**
     * Determine if an element should be considered disabled.
     *
     * @param {HTMLElement} element - Element to inspect.
     * @returns {boolean} True if the element is disabled.
     * @private
     */
    _isDisabled(element) {
        if (!(element instanceof HTMLElement)) {
            return true;
        }

        const hasDisabledAttribute = element.hasAttribute('disabled');
        if (hasDisabledAttribute === true) {
            return true;
        }

        const ariaDisabled = element.getAttribute('aria-disabled');
        if (ariaDisabled !== null && ariaDisabled.toLowerCase() === 'true') {
            return true;
        }

        /*
        const tabIndexAttribute = element.getAttribute('tabindex');
        if (tabIndexAttribute !== null) {
            const parsed = parseInt(tabIndexAttribute, 10);
            const isNumber = Number.isNaN(parsed) === false;
            if (isNumber === true && parsed < 0) {
                return true;
            }
        }*/

        return false;
    }
}