/**
 :filename: statics.js.slides.presentation_view.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: DOM rendering for the presentation view mode.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa

 Copyright (C) 2023-2026 Brigitte Bigi, CNRS
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
 * Renders the presentation view mode.
 *
 * Receives SlidesData from callbacks set up by SlidesAssembler.
 * Never imports controllers, logic modules, or other views.
 * Never decides navigation or mode transitions.
 */
export default class PresentationView {

    /**
     * @param {HTMLElement[]} slides
     * @param {HTMLElement|null} progressBar - Inner element of the progress bar.
     * @param {HTMLElement|null} controlsElement - Navigation controls container.
     * @param {HTMLElement|null} controlsViewElement - View-mode buttons container.
     */
    constructor(slides, progressBar = null, controlsElement = null, controlsViewElement = null) {
        this._slides       = Array.isArray(slides) ? slides : [];
        this._progressBar  = progressBar instanceof HTMLElement ? progressBar : null;
        this._controls     = controlsElement instanceof HTMLElement ? controlsElement : null;
        this._controlsView = controlsViewElement instanceof HTMLElement ? controlsViewElement : null;
        this._currentMode  = null;
    }

    // -----------------------------------------------------------------------
    // Called by SlidesAssembler via navLogic.onNavigate
    // -----------------------------------------------------------------------

    /**
     * Full navigation render: slide + incremental items + progress bar.
     * @param {import('./slides_data.js').default} data
     */
    render(data) {
        this._renderSlide(data.currentIndex, data.previousIndex);
        this._renderIncremental(data.currentIndex, data.currentStep);
        this._renderProgress(data.currentIndex, data.count);
    }

    // -----------------------------------------------------------------------
    // Called by SlidesAssembler via modeLogic.onModeChange
    // -----------------------------------------------------------------------

    /**
     * React to a mode switch: show/hide slides, update body class.
     * @param {import('./slides_data.js').default} data
     */
    onModeChange(data) {
        // Sync body class
        if (this._currentMode !== null) {
            document.body.classList.remove(`${this._currentMode}-view`);
        }
        this._currentMode = data.mode;
        document.body.classList.add(`${data.mode}-view`);

        if (data.mode === 'presentation' || data.mode === 'handout' || data.mode === 'note') {
            this._showSlides();
        } else {
            this._hideSlides();
        }

        // The view-mode radio group: keep visible (shows current mode and allows switching back)

    }

    // -----------------------------------------------------------------------
    // Visibility of the controls panel (toggled via keyboard / buttons)
    // -----------------------------------------------------------------------

    /** @param {boolean} visible */
    renderControls(visible) {
        if (this._controls instanceof HTMLElement) {
            this._controls.classList.toggle('controls-hidden', visible === false);
        }
    }

    // -----------------------------------------------------------------------
    // Private rendering helpers
    // -----------------------------------------------------------------------

    /**
     * @private
     * @param {number} newIndex - 1-based
     * @param {number} oldIndex - 1-based (0 = none)
     */
    _renderSlide(newIndex, oldIndex) {
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

    /**
     * @private
     * @param {number} index - 1-based
     * @param {number} step
     */
    _renderIncremental(index, step) {
        const slide = this._getSlide(index);
        if (slide === null) {
            return;
        }

        // Clear all incremental state on this slide
        slide.querySelectorAll('.incremental').forEach(container => {
            container.removeAttribute('active');
            container.querySelectorAll('*').forEach(item => item.removeAttribute('aria-selected'));
        });

        if (step === 0) {
            return;
        }

        const items = slide.querySelectorAll('.incremental > *');
        if (items.length === 0 || step > items.length) {
            return;
        }

        const target = items[step - 1];
        if (target.parentElement instanceof HTMLElement) {
            target.parentElement.setAttribute('active', 'true');
        }
        target.setAttribute('aria-selected', 'true');
    }

    /**
     * @private
     * @param {number} currentIndex
     * @param {number} count
     */
    _renderProgress(currentIndex, count) {
        if (!(this._progressBar instanceof HTMLElement)) {
            return;
        }
        const pct = count <= 1 ? 0 : (currentIndex - 1) * 100 / (count - 1);
        this._progressBar.style.width = `${pct}%`;
    }

    /** @private */
    _showSlides() {
        for (const slide of this._slides) {
            slide.style.display = '';
        }
    }

    /** @private */
    _hideSlides() {
        for (const slide of this._slides) {
            slide.style.display = 'none';
        }
    }

    /**
     * @private
     * @param {number} index - 1-based
     * @returns {HTMLElement|null}
     */
    _getSlide(index) {
        if (index < 1 || index > this._slides.length) {
            return null;
        }
        return this._slides[index - 1];
    }
}
