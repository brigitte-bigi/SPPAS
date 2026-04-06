/**
 :filename: statics.js.slides.slides_manager.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to manage slides.

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
 * Core slide navigation and state manager.
 *
 * This class manages slide indices, incremental steps, and media playback.
 *
 */
export default class SlidesManager {

    // ----------------------------------------------------------------------
    // CONSTRUCTOR
    // ----------------------------------------------------------------------
    /**
     * Create a SlidesManager.
     *
     * @param {HTMLElement[]} slides - List of slide elements. Must be validated upstream.
     * @param {Object} [options={}] -
     * @param {boolean} [options.autoPlayEnabled=false] - If true, videos autoplay when their slide becomes active.
     * @param {boolean} [options.controlsVisible=true] - If true, slide controls are initially visible.
     * @param {Object} [dependencies={}] -
     * @param {Object} [dependencies.view] - Object implementing the rendering API (SlidesView).
     * @param {Object} [dependencies.fullscreen] - Fullscreen handler (toggle only).
     * @param {Object} [dependencies.focusController] - Optional focus manager.
     * @param {Object} [dependencies.visibilityManager] - Optional visibility manager.
     * @param {Object} [dependencies.viewModeManager] - Optional view mode manager.
     */
    constructor(slides, options = {}, dependencies = {}) {

        // Slides validation
        // ------------------------------
        if (!Array.isArray(slides)) {
            console.error('SlidesManager: slides must be an array.');
            this._slides = [];
        } else {
            this._slides = slides;
        }

        if (this._slides.length === 0) {
            console.warn('SlidesManager: no slides found.');
        }

        // State
        // ------------------------------
        this._currentIndex = 1;  // 1-based
        this._currentStep = 0;

        this._autoPlayEnabled = Boolean(options.autoPlayEnabled);
        this._controlsVisible = Boolean(options.controlsVisible);

        // Dependencies
        // ------------------------------

        if (typeof dependencies.visibilityManager === 'object' && dependencies.visibilityManager !== null) {
            this.visibilityManager = dependencies.visibilityManager;
        } else {
            this.visibilityManager = null;
        }

        if (typeof dependencies.viewModeManager === 'object' && dependencies.viewModeManager !== null) {
            this.viewModeManager = dependencies.viewModeManager;
        } else {
            this.viewModeManager = null;
        }

        this._view =
            (typeof dependencies.view === 'object' && dependencies.view !== null)
                ? dependencies.view
                : null;

        this._fullscreen =
            (typeof dependencies.fullscreen === 'object' && dependencies.fullscreen !== null)
                ? dependencies.fullscreen
                : null;

        this._focusController =
            (typeof dependencies.focusController === 'object' &&
                dependencies.focusController !== null)
                ? dependencies.focusController
                : null;
    }

    // ----------------------------------------------------------------------
    // INITIALIZATION
    // ----------------------------------------------------------------------

    /**
     * Initialize the manager state and apply the initial rendering.
     * This method must be called once after construction.
     *
     * @returns {void}
     */
    init() {
        // Clamp index (safety)
        if (this._slides.length === 0) {
            return;
        }

        // Apply default mode BEFORE any rendering (mandatory for hash)
        // this._view.setMode(this._view.DEFAULT_MODE);

        // Initial render
        this._view.renderSlide(this._currentIndex, 0);
        this._view.renderIncremental(this._currentIndex, this._currentStep);

        // Initial progress
        const pct = (this._currentIndex - 1) * 100 / (this._slides.length - 1);
        this._view.renderProgress(pct);

        // Controls visibility
        this._view.renderControls(this._controlsVisible);
    }

    // ----------------------------------------------------------------------
    //  Public API
    // ----------------------------------------------------------------------

    /**
     * Advance to the next incremental item or slide.
     *
     * @returns {void}
     */
    next() {
        const lastIndex = this._slides.length;
        const incrementalCount = this.getIncrementalCount(this._currentIndex);

        if (this._currentIndex === lastIndex && this._currentStep >= incrementalCount) {
            return;
        }

        if (this._currentStep >= incrementalCount) {
            this.goTo(this._currentIndex + 1, 0);
        } else {
            this.goTo(this._currentIndex, this._currentStep + 1);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Go back to the previous incremental item or slide.
     *
     * @returns {void}
     */
    prev() {
        const atFirstSlide = this._currentIndex === 1 && this._currentStep === 0;
        if (atFirstSlide === true) {
            return;
        }

        if (this._currentStep === 0) {
            const previousIndex = this._currentIndex - 1;
            const lastStep = this.getIncrementalCount(previousIndex);
            this.goTo(previousIndex, lastStep);
        } else {
            this.goTo(this._currentIndex, this._currentStep - 1);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Go directly to a slide index and incremental step.
     *
     * @param {number} index - Target slide index (1-based).
     * @param {number} [step=0] - Target incremental step.
     * @returns {void}
     */
    goTo(index, step = 0) {
        const previousIndex = this._currentIndex;
        const previousStep = this._currentStep;

        const clampedIndex = this._clampIndex(index);
        const clampedStep = this._clampStep(clampedIndex, step);

        if (clampedIndex === previousIndex && clampedStep === previousStep) {
            return;
        }

        const previousSlide = this.getActiveSlide();
        if (previousSlide !== null) {
            this._pauseVideo(previousSlide);
        }

        this._currentIndex = clampedIndex;
        this._currentStep = clampedStep;

        const currentSlide = this.getActiveSlide();
        if (currentSlide !== null) {
            this._autoplayVideo(currentSlide);
        }

        if (typeof window !== 'undefined') {
            const hashValue = '#' + String(this._currentIndex) + '.' + String(this._currentStep);
            window.location.hash = hashValue;
        }

        this._notifyAll(previousIndex, previousStep);

        if (this._focusController !== null) {
            this._focusController.updateFocus(this._slides, this._currentIndex);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Go to the very first slide.
     *
     * @returns {void}
     */
    goStart() {
        this.goTo(1, 0);
    }

    // ----------------------------------------------------------------------

    /**
     * Go to the very last slide and last incremental step.
     *
     * @returns {void}
     */
    goEnd() {
        const lastIndex = this._slides.length;
        const lastStep = this.getIncrementalCount(lastIndex);
        this.goTo(lastIndex, lastStep);
    }

    // ----------------------------------------------------------------------

    /**
     * Toggle play/pause on the active slide video, if any.
     *
     * @returns {void}
     */
    toggleContent() {
        const slide = this.getActiveSlide();
        if (slide === null) {
            return;
        }

        const video = this.getVideo(slide);
        if (video === null) {
            return;
        }

        if (video.ended === true || video.paused === true) {
            video.play();
        } else {
            video.pause();
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Toggle fullscreen mode.
     *
     * Called by keyboard or UI controls. Delegates the action
     * to the fullscreen controller.
     */
    toggleFullscreen() {
        if (this._fullscreen) {
            this._fullscreen.toggle();
        } else {
            console.log("No fullscreen available.");
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Update internal state from a hash fragment.
     *
     * @param {string} hash - Hash string such as '#3.1'.
     * @returns {void}
     */
    updateFromHash(hash) {
        const previousIndex = this._currentIndex;
        const previousStep = this._currentStep;

        const isString = typeof hash === 'string';
        const isEmpty = hash === '';
        const startsWithHash = isString === true && hash.charAt(0) === '#';

        if (isString === false || isEmpty === true || startsWithHash === false) {
            this._currentIndex = this._clampIndex(1);
            this._currentStep = this._clampStep(this._currentIndex, 0);
            this._notifyAll(previousIndex, previousStep);
            return;
        }

        const cursor = hash.substring(1).split('.');
        const parsedIndex = parseInt(cursor[0], 10);
        const parsedStep = cursor.length > 1 ? parseInt(cursor[1], 10) : 0;

        const safeIndex = Number.isNaN(parsedIndex) ? 1 : parsedIndex;
        const safeStep = Number.isNaN(parsedStep) ? 0 : parsedStep;

        const clampedIndex = this._clampIndex(safeIndex);
        const clampedStep = this._clampStep(clampedIndex, safeStep);

        this._currentIndex = clampedIndex;
        this._currentStep = clampedStep;

        this._notifyAll(previousIndex, previousStep);
    }

    // ----------------------------------------------------------------------

    /**
     * Get the currently active slide element.
     *
     * @returns {HTMLElement|null} The active slide or null.
     */
    getActiveSlide() {
        const index = this._currentIndex;
        if (index < 1 || index > this._slides.length) {
            return null;
        }
        return this._slides[index - 1];
    }

    // ----------------------------------------------------------------------

    /**
     * Get the number of incremental items for a slide index.
     *
     * @param {number} [index] - Slide index (1-based). Defaults to current slide.
     * @returns {number} Number of incremental items.
     */
    getIncrementalCount(index) {
        const slideIndex = typeof index === 'number' ? index : this._currentIndex;
        const clampedIndex = this._clampIndex(slideIndex);
        const slide = this._slides[clampedIndex - 1];
        if (!(slide instanceof HTMLElement)) {
            return 0;
        }
        const items = slide.querySelectorAll('.incremental > *');
        return items.length;
    }

    // ----------------------------------------------------------------------

    /**
     * Get the first video element inside a slide.
     *
     * @param {HTMLElement} slide - Slide element.
     * @returns {HTMLVideoElement|null} Video element or null.
     */
    getVideo(slide) {
        const isElement = slide instanceof HTMLElement;
        if (isElement === false) {
            return null;
        }
        const video = slide.querySelector('video');
        const isVideo = video instanceof HTMLVideoElement;
        return isVideo === true ? video : null;
    }

    // ----------------------------------------------------------------------
    // PRIVATE
    // ----------------------------------------------------------------------

    /**
     * Notify the view and focus controller after a state change.
     *
     * @param {number|null} previousIndex - Previous slide index.
     * @param {number} previousStep - Previous incremental step.
     * @returns {void}
     * @private
     */
    _notifyAll(previousIndex, previousStep) {
        if (this._view !== null) {
            const hasRenderSlide = typeof this._view.renderSlide === 'function';
            const hasRenderIncremental = typeof this._view.renderIncremental === 'function';
            const hasUpdateProgress = typeof this._view.renderProgress === 'function';

            if (hasRenderSlide === true) {
                this._view.renderSlide(this._currentIndex, previousIndex);
            }
            if (hasRenderIncremental === true) {
                this._view.renderIncremental(this._currentIndex, this._currentStep);
            }
            if (hasUpdateProgress === true) {
                const totalSlides = this._slides.length - 1;
                const progressPercent = (this._currentIndex - 1) * 100 / totalSlides;
                this._view.renderProgress(progressPercent);
            }
        }

        const hasFocusController = this._focusController !== null;
        const hasUpdateFocus = hasFocusController === true
            && typeof this._focusController.updateFocus === 'function';

        if (hasUpdateFocus === true) {
            this._focusController.updateFocus(this._slides, this._currentIndex);
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Pause video playback for a slide if present.
     *
     * @param {HTMLElement} slide - Slide element.
     * @returns {void}
     * @private
     */
    _pauseVideo(slide) {
        const video = this.getVideo(slide);
        if (video !== null) {
            video.pause();
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Autoplay video for a slide if enabled.
     *
     * @param {HTMLElement} slide - Slide element.
     * @returns {void}
     * @private
     */
    _autoplayVideo(slide) {
        if (this._autoPlayEnabled === false) {
            return;
        }
        const video = this.getVideo(slide);
        if (video !== null) {
            video.play();
        }
    }

    // ----------------------------------------------------------------------

    /**
     * Clamp a slide index to valid bounds.
     *
     * @param {number} index - Requested slide index.
     * @returns {number} Clamped index.
     * @private
     */
    _clampIndex(index) {
        if (index < 1) {
            return 1;
        }
        if (index > this._slides.length) {
            return this._slides.length;
        }
        return index;
    }

    // ----------------------------------------------------------------------

    /**
     * Clamp a step value to valid bounds for a slide.
     *
     * @param {number} index - Slide index.
     * @param {number} step - Requested step.
     * @returns {number} Clamped step.
     * @private
     */
    _clampStep(index, step) {
        if (step < 0) {
            return 0;
        }
        const maxSteps = this.getIncrementalCount(index);
        if (this._slides.length === 0) {
            return 0;
        }
        if (step > maxSteps) {
            return maxSteps;
        }
        return step;
    }
}
