/**
 :filename: statics.js.slides.buttons_controller.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Navigation buttons controller for the Slides module.

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
 * Manages all navigation and view-mode buttons.
 *
 * On click: dispatches CustomEvents — no direct calls to logic or views.
 * On mode change: receives data via onModeChange() and updates button states.
 *
 * CustomEvents dispatched on document:
 *   slides:navigate   → { action: 'prev'|'next'|'goStart'|'goEnd'|'goTo', index?, step? }
 *   slides:viewmode   → { mode: 'presentation'|'overview' }
 *   slides:fullscreen → {}
 */
export default class ButtonsController {

    /**
     * @param {Object} buttons
     * @param {HTMLElement|null} [buttons.prevButton]
     * @param {HTMLElement|null} [buttons.nextButton]
     * @param {HTMLElement|null} [buttons.backButton]
     * @param {HTMLElement|null} [buttons.lastButton]
     * @param {HTMLElement|null} [buttons.overviewButton]
     * @param {HTMLElement|null} [buttons.presentationButton]
     * @param {HTMLElement|null} [buttons.fullscreenButton]
     * @param {HTMLElement|null} [buttons.goToButton]
     */
    constructor({
        prevButton         = null,
        nextButton         = null,
        backButton         = null,
        lastButton         = null,
        overviewButton     = null,
        handoutButton      = null,
        noteButton         = null,
        presentationButton = null,
        fullscreenButton   = null,
        goToButton         = null,
    } = {}) {
        this._b = {
            prev:         this._el(prevButton),
            next:         this._el(nextButton),
            back:         this._el(backButton),
            last:         this._el(lastButton),
            overview:     this._el(overviewButton),
            handout:      this._el(handoutButton),
            note:         this._el(noteButton),
            presentation: this._el(presentationButton),
            fullscreen:   this._el(fullscreenButton),
            goto:         this._el(goToButton),
        };

        this._bindEvents();
    }

    // -----------------------------------------------------------------------
    // Called by SlidesAssembler via modeLogic.onModeChange
    // -----------------------------------------------------------------------

    /**
     * Sync the disabled state of view-mode buttons with the current mode.
     * @param {import('./slides_data.js').default} data
     */
    onModeChange(data) {
        if (this._b.overview instanceof HTMLElement) {
            this._b.overview.checked = (data.mode === 'overview');
        }
        if (this._b.handout instanceof HTMLElement) {
            this._b.handout.checked = (data.mode === 'handout');
        }
        if (this._b.note instanceof HTMLElement) {
            this._b.note.checked = (data.mode === 'note');
        }
        if (this._b.presentation instanceof HTMLElement) {
            this._b.presentation.checked = (data.mode === 'presentation');
        }
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    _bindEvents() {
        const b = this._b;

        const nav  = (action, index, step) =>
            document.dispatchEvent(new CustomEvent('slides:navigate', {
                detail: { action, index, step }
            }));

        const mode = (m) =>
            document.dispatchEvent(new CustomEvent('slides:viewmode', {
                detail: { mode: m }
            }));

        b.prev?.addEventListener('click',     () => nav('prev'));
        b.next?.addEventListener('click',     () => nav('next'));
        b.back?.addEventListener('click',     () => nav('goStart'));
        b.last?.addEventListener('click',     () => nav('goEnd'));
        b.overview?.addEventListener('change', () => mode('overview'));
        b.handout?.addEventListener('change',  () => mode('handout'));
        b.note?.addEventListener('change',     () => mode('note'));
        b.presentation?.addEventListener('change', () => mode('presentation'));

        b.fullscreen?.addEventListener('click', () =>
            document.dispatchEvent(new CustomEvent('slides:fullscreen', { detail: {} }))
        );

        b.goto?.addEventListener('click', () => {
            const input = window.prompt('Go to slide number:');
            if (input !== null) {
                nav('goTo', Number(input), 0);
                mode('presentation');
            }
        });
    }

    /** @private */
    _el(e) {
        return e instanceof HTMLElement ? e : null;
    }
}
