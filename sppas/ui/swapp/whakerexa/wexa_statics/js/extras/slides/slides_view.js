import SlidesOverview from './overview.js';
import SlidesPresentation from './presentation.js';

/**
 :filename: statics.js.slides.slides_view.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Visual rendering for slide transitions, incremental items and progress bar.

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
 * SlidesView is responsible for display only. It never decides navigation.
 * It receives state from SlidesManager and updates the DOM accordingly.
 *
 *
 * To achieve full MVC separation and modularity, SlidesView delegates
 * work to SlidesPresentation or SlidesOverview, keeping SlidesManager
 * blind to internal sub-view components.
 *
 */
export default class SlidesView {
    // ---------------------------------------------------------------------------
    // STATIC ENUM OF MODES
    // ---------------------------------------------------------------------------

    /**
     * Modes supported by this view orchestrator.
     */
    static MODES = {
        PRESENTATION: 'presentation',
        OVERVIEW: 'overview',
        //PRINT: 'print',
        //NOTES: 'notes'
    }

    static DEFAULT_MODE = SlidesView.MODES.PRESENTATION;

    // ---------------------------------------------------------------------------
    // CONSTRUCTOR
    // ---------------------------------------------------------------------------

    /**
     * Construct the view orchestrator.
     *
     * @param {HTMLElement[]} slides - Source slide elements.
     * @param {HTMLElement|null} progressBar - Optional progress bar inner element.
     * @param {HTMLElement|null} controlsElement - Global control's container.
     * @param {HTMLElement|null} controlsViewElement - The container for view modes.
     * @param {HTMLElement|null} overviewContainer - Overview container element.
     */
    constructor(slides,
                progressBar = null,
                controlsElement = null,
                controlsViewElement  = null,
                overviewContainer = null) {

        this._slides = slides;

        // Sub-views

        this._presentation = new SlidesPresentation(
            slides,
            progressBar,
            controlsElement
        );

        this._controlsView = controlsViewElement instanceof HTMLElement ? controlsViewElement : null;
        this._controls = controlsElement instanceof HTMLElement ? controlsElement : null;
        this._overviewContainer = overviewContainer instanceof HTMLElement ? overviewContainer : null;

        this._overview = null;

        this._viewMode = SlidesView.MODES.PRESENTATION;

        // Callback for clicking a slide in the overview.
        this.onSelectSlide = null;
    }

    // -----------------------------------------------------------------------
    // INITIALIZATION
    // -----------------------------------------------------------------------

    /**
     * Create the SlidesOverview instance.
     *
     * @param {function(number):void} onSelectSlide
     *        Called when a GoTo button is clicked in the overview.
     *
     * @returns {void}
     */
    initOverview(onSelectSlide) {
        if (this._overviewContainer !== null) {
            this._overview = new SlidesOverview(
                (
                    this._slides.map((slide) => slide.cloneNode(true))
                ),
                this._overviewContainer,
                onSelectSlide
            );
        }
    }

    /**
     * Build the overview panel contents.
     *
     * @returns {void}
     */
    buildOverview() {
        if (this._overview !== null) {
            this._overview.build();
        }
    }

    // ---------------------------------------------------------------------------
    // MODE SWITCHING
    // ---------------------------------------------------------------------------

    /**
     * Set the active view mode.
     *
     * @param {string} mode - One of SlidesView.MODES.* [presentation by default]
     * @returns {void}
     */
    setMode(mode) {
        this._mode = mode;

        // Manage the body class="view" to enable the relevant CSS render class
        this._removeBodyView()
        document.body.classList.add(`${mode}-view`);

        // switch to the requested view [presentation by default]
        switch (mode) {
            case SlidesView.MODES.OVERVIEW:
                this._enterOverview();
                return;
            default:
                this._enterPresentation();
                return;
        }
    }

    /**
     * @returns {string}
     */
    get mode() {
        return this._mode;
    }

    // ---------------------------------------------------------------------------
    // RENDERING (CALLED ONLY BY SlidesManager)
    // ---------------------------------------------------------------------------

    /**
     * Render the active slide for any current mode.
     * Mandatory: always update views before mode application
     * so hash-based navigation (#N.S) works at load time.
     *
     * @param {number} newIndex 1-based index of the new active slide
     * @param {number} oldIndex 1-based index of the previous slide
     */
    renderSlide(newIndex, oldIndex) {

        // Presentation view update (always required)
        this._presentation.renderSlide(newIndex, oldIndex);

        /* Overview view update (safe no-op when inactive)
        if (typeof this._overview.renderSlide === 'function') {
            this._overview.renderSlide(newIndex, oldIndex);
        }*/
    }

    /**
     * @param {number} index
     * @param {number} step
     * @returns {void}
     */
    renderIncremental(index, step) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderIncremental(index, step);
        }
    }

    /**
     * @param {number} percent
     * @returns {void}
     */
    renderProgress(percent) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderProgress(percent);
        }
    }

    /**
     * @param {boolean} visible
     * @returns {void}
     */
    renderControls(visible) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderControls(visible);
        }

        if (this._controlsView instanceof HTMLElement) {
            this._controlsView.classList.toggle('controls-hidden', visible === false);
        }
    }

    // ----------------------------------------------------------------------
    // PRIVATE: MODE ENTRY HANDLERS
    // ----------------------------------------------------------------------

    /**
     * Enter presentation mode.
     *
     * @private
     * @returns {void}
     */
    _enterPresentation() {
        if (this._overview !== null) {
            this._overview.hide();
        }
        this._presentation.showPresentation();
    }

    /**
     * Enter overview mode.
     *
     * @private
     * @returns {void}
     */
    _enterOverview() {
        this._presentation.hidePresentation();
        if (this._overview !== null) {
            this._overview.show();
        }
    }

    /**
     * Remove any body view class.
     *
     * @private
     * @returns {void}
     */
    _removeBodyView() {
        const modes = Object.values(SlidesView.MODES);
        modes.forEach(mode => {
            document.body.classList.remove(`${mode}-view`);
        });
    }
}
