/**
 :filename: statics.js.slides.presentation.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: View for the normal slides presentation mode.

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
 * SlidesPresentation handles the entire rendering logic for the normal
 * presentation mode. It updates:
 * - visible slide
 * - incremental items
 * - progress bar
 * - controls visibility
 *
 * This class contains NO navigation logic and NO business logic.
 * It only updates the view according to instructions coming from
 * SlidesView (the orchestrator).
 *
 * Usage:
 *   const pres = new SlidesPresentation(slides, progress, controls);
 */
export default class SlidesPresentation {

    /**
     * Create a SlidesPresentation view.
     *
     * @param {HTMLElement[]} slides - The list of slides managed by the module.
     * @param {HTMLElement|null} progressBar - The inner element of the progress bar.
     * @param {HTMLElement|null} controlsElement - The global control's container.
     */
    constructor(slides, progressBar = null, controlsElement = null) {
        this._slides = Array.isArray(slides) ? slides : [];

        this._progressBar = progressBar;

        this._controls = controlsElement;
    }

    // -------------------------------------------------------------------------
    //  Public API
    // -------------------------------------------------------------------------

    /**
     * Update the selected slide and reset the previous one.
     *
     * @param {number} newIndex - 1-based index of the newly visible slide.
     * @param {number} oldIndex - 1-based index of the slide that was visible.
     * @returns {void}
     */
    renderSlide(newIndex, oldIndex) {
        const total = this._slides.length;

        if (oldIndex >= 1 && oldIndex <= total) {
            const prev = this._slides[oldIndex - 1];
            if (prev instanceof HTMLElement) {
                prev.removeAttribute('aria-selected');
            }
        }

        if (newIndex >= 1 && newIndex <= total) {
            const curr = this._slides[newIndex - 1];
            if (curr instanceof HTMLElement) {
                curr.setAttribute('aria-selected', 'true');
            }
        }
    }

    // -------------------------------------------------------------------------

    /**
     * Render the incremental items for a slide:
     * - Clear all incremental markers
     * - Activate the selected incremental item
     *
     * @param {number} currentIndex - 1-based slide index.
     * @param {number} step - 0 = none; otherwise index of incremental item.
     * @returns {void}
     */
    renderIncremental(currentIndex, step) {
        const slide = this._getSlide(currentIndex);
        if (slide === null) {
            return;
        }

        const containers = slide.querySelectorAll('.incremental');
        containers.forEach(c => this._clearIncrementals(c));

        if (step === 0) {
            return;
        }

        const items = slide.querySelectorAll('.incremental > *');
        const totalItems = items.length;

        if (totalItems === 0 || step > totalItems) {
            return;
        }

        const target = items[step - 1];
        const parent = target.parentElement;

        if (parent instanceof HTMLElement) {
            parent.setAttribute('active', 'true');
        }

        target.setAttribute('aria-selected', 'true');
    }

    // -------------------------------------------------------------------------

    /**
     * Update the progress bar.
     *
     * @param {number} widthPercent - A value between 0 and 100.
     * @returns {void}
     */
    renderProgress(widthPercent) {
        if (this._progressBar instanceof HTMLElement) {
            this._progressBar.style.width = String(widthPercent) + '%';
        }
    }

    // -------------------------------------------------------------------------

    /**
     * Show or hide the controls panel.
     *
     * @param {boolean} visible - true = controls visible; false = hidden.
     * @returns {void}
     */
    renderControls(visible) {
        if (this._controls instanceof HTMLElement) {
            this._controls.classList.toggle('controls-hidden', visible === false);
        }
    }

    // -------------------------------------------------------------------------

    /**
     * Show all slides (this presentation mode active).
     *
     * @returns {void}
     */
    showPresentation() {
        for (const slide of this._slides) {
            slide.style.display = 'block';
        }
    }

    // -------------------------------------------------------------------------

    /**
     * Hide all slides (another view mode is active).
     *
     * @returns {void}
     */
    hidePresentation() {
        for (const slide of this._slides) {
            slide.style.display = 'none';
        }
    }

    // -------------------------------------------------------------------------
    //  Private Helpers
    // -------------------------------------------------------------------------

    /**
     * @private
     * @param {number} index - 1-based index of a slide
     * @returns {HTMLElement|null}
     */
    _getSlide(index) {
        if (index < 1 || index > this._slides.length) {
            return null;
        }
        return this._slides[index - 1];
    }

    // -------------------------------------------------------------------------

    /**
     * Remove active/selected attributes on incremental containers.
     *
     * @private
     * @param {HTMLElement} container
     * @returns {void}
     */
    _clearIncrementals(container) {
        if (!(container instanceof HTMLElement)) {
            return;
        }

        container.removeAttribute('active');

        const items = container.querySelectorAll('*');
        items.forEach(item => {
            item.removeAttribute('aria-selected');
        });
    }
}

