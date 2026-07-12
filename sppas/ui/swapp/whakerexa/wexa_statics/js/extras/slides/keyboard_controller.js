/**
 :filename: statics.js.slides.keyboard_controller.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Keyboard input controller for the Slides module.

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
 * Captures keyboard events and dispatches CustomEvents.
 *
 * This controller is *pure input*: it does not know about logic modules,
 * views, or state. It only translates key presses into semantic events.
 *
 * Accessibility rules (unchanged from the previous implementation):
 * - Only handles a restricted set of slide keys.
 * - Never handles Enter or Space.
 * - Never intercepts any key when focus is on an interactive element.
 *
 * CustomEvents dispatched on document:
 *   slides:navigate  → { action: 'next'|'prev'|'goStart'|'goEnd'|'toggleContent' }
 *   slides:viewmode  → { mode: 'presentation' } | { action: 'toggle', mode: string }
 *   slides:visibility → { name: 'accessibility'|'controls'|'progress'|'logo', action: 'toggle' }
 *   slides:fullscreen → {}
 *   slides:help      → { action: 'toggle' }
 */
export default class KeyboardController {

    static SHORTCUTS = [
        { keys: ['ArrowRight', 'ArrowDown', 'PageDown'], label: 'Next slide' },
        { keys: ['ArrowLeft', 'ArrowUp', 'PageUp'],      label: 'Previous slide' },
        { keys: ['Home'],                                 label: 'First slide' },
        { keys: ['End'],                                  label: 'Last slide' },
        { keys: ['h', 'H', '?'],                          label: 'Help' },
        { keys: ['f', 'F'],                               label: 'Fullscreen' },
        { keys: ['o', 'O'],                               label: 'Overview mode' },
        { keys: ['d', 'D'],                               label: 'Handout mode' },
        { keys: ['m', 'M'],                               label: 'Memo mode' },
        { keys: ['Escape', 's', 'S'],                     label: 'Presentation mode' },
        { keys: ['a', 'A'],                               label: 'Accessibility controls' },
        { keys: ['n', 'N'],                               label: 'Navigation controls' },
        { keys: ['b', 'B'],                               label: 'Progress bar' },
        { keys: ['l', 'L'],                               label: 'Logo' },
    ];

    static SLIDE_KEYS = new Set(KeyboardController.SHORTCUTS.flatMap(s => s.keys));

    constructor() {
        this._boundHandler = this._onKeyDown.bind(this);
    }

    /** Attach the keydown listener. */
    init() {
        document.body.addEventListener('keydown', this._boundHandler, false);
    }

    /** Remove the keydown listener. */
    destroy() {
        document.body.removeEventListener('keydown', this._boundHandler, false);
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    _onKeyDown(event) {
        const key = event.key;

        if (!KeyboardController.SLIDE_KEYS.has(key)) return;
        if (key === 'Enter' || key === ' ')            return;
        if (this._isInteractiveTarget(event.target))   return;

        switch (key) {

            case 'h': case 'H': case '?':
                this._emit('slides:help', { action: 'toggle' });
                return;

            case 'Escape':
            case 's': case 'S':
                this._emit('slides:viewmode', { mode: 'presentation' });
                return;

            case 'o': case 'O':
                this._emit('slides:viewmode', { action: 'toggle', mode: 'overview' });
                return;

            case 'd': case 'D':
                this._emit('slides:viewmode', { action: 'toggle', mode: 'handout' });
                return;

            case 'm': case 'M':
                this._emit('slides:viewmode', { action: 'toggle', mode: 'note' });
                return;

            case 'f': case 'F':
                this._emit('slides:fullscreen', {});
                return;

            case 'a': case 'A':
                this._emit('slides:visibility', { name: 'accessibility', action: 'toggle' });
                return;

            case 'n': case 'N':
                this._emit('slides:visibility', { name: 'controls', action: 'toggle' });
                return;

            case 'b': case 'B':
                this._emit('slides:visibility', { name: 'progress', action: 'toggle' });
                return;

            case 'l': case 'L':
                this._emit('slides:visibility', { name: 'logo', action: 'toggle' });
                return;

            case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
                event.preventDefault();
                this._emit('slides:navigate', { action: 'prev' });
                return;

            case 'ArrowRight': case 'ArrowDown': case 'PageDown':
                event.preventDefault();
                this._emit('slides:navigate', { action: 'next' });
                return;

            case 'Home':
                event.preventDefault();
                this._emit('slides:navigate', { action: 'goStart' });
                return;

            case 'End':
                event.preventDefault();
                this._emit('slides:navigate', { action: 'goEnd' });
                return;
        }
    }

    /** @private */
    _emit(type, detail) {
        document.dispatchEvent(new CustomEvent(type, { detail }));
    }

    /**
     * Returns true if the event target is an interactive element that must
     * receive full browser keyboard handling without interference.
     * @private
     * @param {EventTarget} target
     * @returns {boolean}
     */
    _isInteractiveTarget(target) {
        if (!(target instanceof HTMLElement)) {
            return true;
        }

        const tag = target.tagName.toLowerCase();

        if (['input', 'select', 'textarea', 'button', 'summary'].includes(tag)) {
            return true;
        }

        if (tag === 'a' && target.hasAttribute('href')) {
            return true;
        }

        if ((tag === 'video' || tag === 'audio') && target.hasAttribute('controls')) {
            return true;
        }

        const tab = target.getAttribute('tabindex');
        if (tab !== null) {
            const n = parseInt(tab, 10);
            if (!Number.isNaN(n) && n >= 0) {
                return true;
            }
        }

        return false;
    }
}
