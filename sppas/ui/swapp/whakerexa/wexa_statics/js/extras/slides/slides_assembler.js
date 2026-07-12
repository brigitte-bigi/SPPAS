/**
 :filename: statics.js.slides.slides_assembler.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Composition root for the Slides module.

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

import SlidesData          from './slides_data.js';
import NavigationLogic     from './navigation_logic.js';
import ViewModeLogic       from './viewmode_logic.js';
import PresentationView    from './presentation_view.js';
import NoteView            from './note_view.js';
import OverviewView        from './overview_view.js';
import SlidesFocusController    from './focus.js';
import SlidesFullscreenController from './fullscreen.js';
import SlidesVisibilityManager  from './visibility_manager.js';
import KeyboardController  from './keyboard_controller.js';
import TouchController     from './touch_controller.js';
import ButtonsController   from './buttons_controller.js';
import HelpDialog          from './help_dialog.js';

/**
 * SlidesAssembler instantiates every component and wires them together.
 *
 * Architecture contract:
 *   Controllers  → dispatch CustomEvents on document
 *   Logic        → listens to callbacks set by assembler; transforms SlidesData
 *   Views        → receive data via callbacks; render DOM
 *   Assembler    → owns all event listeners; zero business logic
 *
 * @param {Object} config
 * @param {HTMLElement[]} config.slides
 * @param {HTMLElement|null} [config.progressBar]
 * @param {HTMLElement|null} [config.controls]
 * @param {HTMLElement|null} [config.controlsView]
 * @param {HTMLElement|null} [config.overviewContainer]
 * @param {HTMLElement|null} [config.progressBarContainer]
 * @param {HTMLElement|null} [config.accessibility]
 * @param {HTMLElement|null} [config.logo]
 * @param {boolean} [config.autoPlayEnabled=false]
 * @param {string} [config.mode='presentation']
 */
export default class SlidesAssembler {

    constructor(config) {

        // ── 1. DATA ──────────────────────────────────────────────────────────
        this._data = new SlidesData(config.slides);
        this._data.autoPlay = Boolean(config.autoPlayEnabled);

        // ── 2. LOGIC ─────────────────────────────────────────────────────────
        this._navLogic  = new NavigationLogic(this._data);
        this._modeLogic = new ViewModeLogic(this._data);

        // ── 3. VIEWS ─────────────────────────────────────────────────────────
        this._presentationView = new PresentationView(
            config.slides,
            config.progressBar   instanceof HTMLElement ? config.progressBar   : null,
            config.controls      instanceof HTMLElement ? config.controls      : null,
            config.controlsView  instanceof HTMLElement ? config.controlsView  : null
        );

        this._overviewView = config.overviewContainer instanceof HTMLElement
            ? new OverviewView(config.slides, config.overviewContainer)
            : null;

        this._noteView = new NoteView(config.slides);

        // ── 4. UTILITIES ─────────────────────────────────────────────────────
        this._focus      = new SlidesFocusController();
        this._fullscreen = new SlidesFullscreenController();

        this._visibilityManager = new SlidesVisibilityManager({
            accessibility: config.accessibility       instanceof HTMLElement ? config.accessibility       : null,
            controls:      config.controls            instanceof HTMLElement ? config.controls            : null,
            progress:      config.progressBarContainer instanceof HTMLElement ? config.progressBarContainer : null,
            logo:          config.logo                instanceof HTMLElement ? config.logo                : null,
        });

        // ── 5. CONTROLLERS ───────────────────────────────────────────────────
        this._helpDialog = new HelpDialog();
        this._keyboard = new KeyboardController();
        this._touch    = new TouchController();

        const c = config.controls;
        const v = config.controlsView;
        this._buttons = new ButtonsController({
            prevButton:         c?.querySelector('#btn-prev')         || null,
            nextButton:         c?.querySelector('#btn-next')         || null,
            backButton:         c?.querySelector('#btn-back')         || null,
            lastButton:         c?.querySelector('#btn-last')         || null,
            goToButton:         c?.querySelector('#btn-goto')         || null,
            overviewButton:     v?.querySelector('#btn-overview')     || null,
            handoutButton:      v?.querySelector('#btn-handout')      || null,
            noteButton:         v?.querySelector('#btn-note')         || null,
            presentationButton: v?.querySelector('#btn-presentation') || null,
            fullscreenButton:   c?.querySelector('#btn-fullscreen')   || null,
        });

        // ── 6. WIRE LOGIC → VIEWS (callbacks) ────────────────────────────────

        this._navLogic.onNavigate = (data) => {
            this._presentationView.render(data);
            this._focus.updateFocus(data.slides, data.currentIndex);
            if (this._overviewView !== null) {
                this._overviewView.render(data);
            }
        };

        this._modeLogic.onModeChange = (data) => {
            this._noteView.onModeChange(data);
            this._presentationView.onModeChange(data);
            if (this._overviewView !== null) {
                this._overviewView.onModeChange(data);
            }
            this._buttons.onModeChange(data);
        };

        // ── 7. WIRE CUSTOM EVENTS → LOGIC ────────────────────────────────────

        document.addEventListener('slides:navigate', (e) => {
            this._dispatch(e.detail);
        });

        document.addEventListener('slides:viewmode', (e) => {
            const { mode, action } = e.detail;
            if (action === 'toggle') { this._modeLogic.toggle(mode); }
            else { this._modeLogic.set(mode); }
        });

        document.addEventListener('slides:visibility', (e) => {
            const { name, action } = e.detail;
            if (action === 'toggle') { this._visibilityManager.toggle(name); }
            else if (action === 'show')   { this._visibilityManager.show(name);   }
            else if (action === 'hide')   { this._visibilityManager.hide(name);   }
        });

        document.addEventListener('slides:fullscreen', () => {
            this._fullscreen.toggle();
        });

        document.addEventListener('slides:help', () => {
            this._helpDialog.toggle();
        });

        // ── 8. HASH CHANGE ───────────────────────────────────────────────────
        window.addEventListener('hashchange', () => {
            this._navLogic.updateFromHash(window.location.hash);
        });

        // ── 9. INITIAL MODE ──────────────────────────────────────────────────
        this._initialMode = ViewModeLogic.DEFAULT;
        if (typeof config.mode === 'string') {
            const modes = Object.values(ViewModeLogic.MODES);
            if (modes.includes(config.mode)) {
                this._initialMode = config.mode;
            }
        }
    }

    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------

    /**
     * Build overview, apply initial mode, navigate to initial position,
     * then start input controllers.
     */
    init() {
        // Build overview panel (before any mode is applied)
        if (this._overviewView !== null) {
            this._overviewView.build();
        }

        // Apply initial mode (fires onModeChange → updates views + buttons)
        this._modeLogic.set(this._initialMode);

        // Navigate to position from URL hash (fires onNavigate → renders)
        this._navLogic.updateFromHash(window.location.hash);

        // Start input controllers
        this._keyboard.init();
        this._touch.init();
    }

    /** @returns {SlidesFullscreenController} */
    get fullscreen() {
        return this._fullscreen;
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    /**
     * Route a slides:navigate event detail to the appropriate logic method.
     * @private
     */
    _dispatch(detail) {
        const { action, index, step } = detail;
        switch (action) {
            case 'next':          this._navLogic.next();                           break;
            case 'prev':          this._navLogic.prev();                           break;
            case 'goStart':       this._navLogic.goStart();                        break;
            case 'goEnd':         this._navLogic.goEnd();                          break;
            case 'goTo':          this._navLogic.goTo(Number(index) || 1, Number(step) || 0); break;
            case 'toggleContent': this._navLogic.toggleContent();                  break;
        }
    }
}
