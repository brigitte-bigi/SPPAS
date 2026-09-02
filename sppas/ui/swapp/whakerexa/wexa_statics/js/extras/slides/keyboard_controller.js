/**
 :filename: statics.js.slides.keyboard_controller.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: The keys a presentation answers, and what each of them says.

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

import { KeyboardController } from '../../keyboard.js';

/**
 * The keys of a presentation, and the events they say.
 *
 * This class is a table and nothing more: which keys, what they are called in
 * the help dialog, and which event each of them dispatches. Answering them --
 * listening once, and standing back when the focus is on something a key
 * belongs to -- is the work of the keyboard controller of the framework, and
 * is not written again here.
 *
 * CustomEvents dispatched on document:
 *   slides:navigate   → { action: 'next'|'prev'|'goStart'|'goEnd' }
 *   slides:viewmode   → { mode: 'presentation' } | { action: 'toggle', mode: string }
 *   slides:visibility → { name: 'accessibility'|'controls'|'progress'|'logo', action: 'toggle' }
 *   slides:fullscreen → {}
 *   slides:help       → { action: 'toggle' }
 */
export default class SlidesKeyboard {

    // CONSTANTS
    /**
     * What a presentation answers.
     *
     * The help dialog reads the keys and the label; the controller reads the
     * event and what it carries. A key that scrolls the page says so, so that
     * moving from one slide to the next does not also move the page.
     */
    static SHORTCUTS = [
        { keys: ['ArrowRight', 'ArrowDown', 'PageDown'], label: 'Next slide',
          event: 'slides:navigate', detail: { action: 'next' }, scrolls: true },
        { keys: ['ArrowLeft', 'ArrowUp', 'PageUp'],      label: 'Previous slide',
          event: 'slides:navigate', detail: { action: 'prev' }, scrolls: true },
        { keys: ['Home'],                                 label: 'First slide',
          event: 'slides:navigate', detail: { action: 'goStart' }, scrolls: true },
        { keys: ['End'],                                  label: 'Last slide',
          event: 'slides:navigate', detail: { action: 'goEnd' }, scrolls: true },
        { keys: ['h', 'H', '?'],                          label: 'Help',
          event: 'slides:help', detail: { action: 'toggle' } },
        { keys: ['f', 'F'],                               label: 'Fullscreen',
          event: 'slides:fullscreen', detail: {} },
        { keys: ['o', 'O'],                               label: 'Overview mode',
          event: 'slides:viewmode', detail: { action: 'toggle', mode: 'overview' } },
        { keys: ['d', 'D'],                               label: 'Handout mode',
          event: 'slides:viewmode', detail: { action: 'toggle', mode: 'handout' } },
        { keys: ['m', 'M'],                               label: 'Memo mode',
          event: 'slides:viewmode', detail: { action: 'toggle', mode: 'note' } },
        { keys: ['Escape', 's', 'S'],                     label: 'Presentation mode',
          event: 'slides:viewmode', detail: { mode: 'presentation' } },
        { keys: ['a', 'A'],                               label: 'Accessibility controls',
          event: 'slides:visibility', detail: { name: 'accessibility', action: 'toggle' } },
        { keys: ['n', 'N'],                               label: 'Navigation controls',
          event: 'slides:visibility', detail: { name: 'controls', action: 'toggle' } },
        { keys: ['b', 'B'],                               label: 'Progress bar',
          event: 'slides:visibility', detail: { name: 'progress', action: 'toggle' } },
        { keys: ['l', 'L'],                               label: 'Logo',
          event: 'slides:visibility', detail: { name: 'logo', action: 'toggle' } },
    ];


    // FIELDS
    #keyboard;


    // CONSTRUCTOR
    /**
     * Declare the keys of a presentation to the keyboard of the framework.
     *
     * @constructor
     * @returns {SlidesKeyboard}
     */
    constructor() {
        this.#keyboard = new KeyboardController();

        SlidesKeyboard.SHORTCUTS.forEach(shortcut => {
            this.#keyboard.register({
                keys: shortcut.keys,
                action: shortcut.event,
                detail: shortcut.detail,
                label: shortcut.label,
                preventsDefault: shortcut.scrolls === true
            });
        });
    }


    // PUBLIC METHODS
    /**
     * Start answering the keys of the presentation.
     *
     * @returns {void}
     */
    init() {
        this.#keyboard.init();
    }

    // -----------------------------------------------------------------------

    /**
     * Stop answering them.
     *
     * @returns {void}
     */
    destroy() {
        this.#keyboard.destroy();
    }
}
