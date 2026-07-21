/**
 :filename: statics.js.slides.help_dialog.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Help dialog for the Slides module — keyboard shortcuts reference.

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

import { DialogManager } from '../../dialog.js';
import KeyboardController from './keyboard_controller.js';

const DIALOG_ID = 'slides-help-dialog';

/**
 * Help dialog listing keyboard shortcuts for the Slides module.
 * Delegates open/close/close-button behaviour to DialogManager.
 */
export default class HelpDialog {

    constructor() {
        this._manager = new DialogManager();
        this._inject();
    }

    toggle() {
        const dialog = document.getElementById(DIALOG_ID);
        if (dialog && dialog.open) {
            this._manager.close(DIALOG_ID);
        } else {
            this._manager.open(DIALOG_ID, true);
        }
    }

    // -----------------------------------------------------------------------
    // Private
    // -----------------------------------------------------------------------

    _inject() {
        if (document.getElementById(DIALOG_ID)) return;
        document.body.appendChild(this._build());
    }

    _build() {
        const dialog = document.createElement('dialog');
        dialog.id = DIALOG_ID;
        dialog.setAttribute('role', 'alertdialog');
        dialog.setAttribute('aria-label', 'Keyboard shortcuts');
        dialog.classList.add('tips', 'hidden-alert');

        const div = document.createElement('div');

        const h2 = document.createElement('h2');
        h2.textContent = 'Keyboard shortcuts';
        div.appendChild(h2);

        const table = document.createElement('table');
        table.setAttribute('role', 'presentation');
        for (const { keys, label } of KeyboardController.SHORTCUTS) {
            const tr = document.createElement('tr');

            const tdKeys = document.createElement('td');
            tdKeys.textContent = keys.map(k => this._keyLabel(k)).join(' / ');

            const tdLabel = document.createElement('td');
            tdLabel.textContent = label;

            tr.appendChild(tdKeys);
            tr.appendChild(tdLabel);
            table.appendChild(tr);
        }
        div.appendChild(table);

        dialog.appendChild(div);
        return dialog;
    }

    _keyLabel(key) {
        const map = {
            ArrowRight: '→', ArrowLeft: '←', ArrowUp: '↑', ArrowDown: '↓',
            PageUp: 'PgUp', PageDown: 'PgDn',
            Home: 'Home', End: 'End', Escape: 'Esc',
        };
        return map[key] ?? key;
    }
}
