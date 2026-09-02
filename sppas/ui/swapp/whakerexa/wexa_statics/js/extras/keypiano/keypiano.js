import { WexaLogger } from '../../logger.js';
import { icons } from '../../customize/icons.js';

/**
 :filename: wexa_statics.js.extras.keypiano.keypiano.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Generic clickable "piano" of buttons composing a technical sequence into a target field.

 -------------------------------------------------------------------------

 This file is part of Whakerexa: https://whakerexa.sf.net/

 Copyright (C) 2026 Brigitte Bigi, CNRS
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

// --------------------------------------------------------------------------
// Constants
// --------------------------------------------------------------------------

const CSS_GROUP = 'wexa-key-piano-group';
const CSS_KEY = 'wexa-key-piano-key';
const CSS_CONTROLS = 'wexa-key-piano-controls';
const CSS_CONTROL = 'wexa-key-piano-control';
const CSS_STATUS = 'wexa-key-piano-status';

const MODE_RADIO = 'radio';
const MODE_FREE = 'free';

const DEFAULT_GROUP_SEP = '-';
const DEFAULT_KEY_SEP = '.';
const DEFAULT_BACKSPACE_LABEL = 'Delete last key';
const DEFAULT_CLEAR_LABEL = 'Clear all';

// --------------------------------------------------------------------------

/**
 * A generic clickable "piano" of buttons that composes a technical sequence
 * (e.g. a Cued Speech key, a phoneme sequence) into a target text field.
 *
 * The piano is entirely declared in HTML: a container carries the target
 * field id and the two separators (inner, between the parts of one entry;
 * outer, between entries). It holds one or more groups of "keys", found as
 * its ".wexa-key-piano-group" children, in document order:
 * - a "radio" group (data-mode="radio") is made of native
 *   <input type="radio"> keys. Groups take turns: only the first group is
 *   enabled initially, the next one is enabled once the current one has a
 *   selection. The composed entry (its choices joined by the inner
 *   separator) is only appended to the target field once every group of
 *   the cycle has a selection.
 * - a "free" group (data-mode="free", or no data-mode) is made of plain
 *   <button> keys. Every click appends its value immediately: no turn,
 *   no exclusivity.
 *
 * Only the content of the keys (images, text, values) is domain-specific
 * and stays in the HTML written by the consuming application; this class
 * only knows about groups, separators and the target field.
 *
 */
export class KeyPiano {

    static #BACKSPACE_ICON = 'backward';
    static #CLEAR_ICON = 'cancel';

    // Fields
    #container;
    #targetField;
    #groupSep;
    #keySep;
    #groups;
    #history;
    #buffer;
    #currentTurn;
    #freeClickCount;
    #statusElt;
    #instanceId;

    /**
     * Create and activate a KeyPiano on the given container.
     *
     * @param {HTMLElement} container - Element holding the target field id, the
     *        separators, and the ".wexa-key-piano-group" children.
     *
     */
    constructor(container) {
        if ((container instanceof HTMLElement) === false) {
            throw new Error(`KeyPiano instantiation failed: container is not an HTMLElement. Got ${container}.`);
        }
        this.#container = container;
        this.#instanceId = container.id.length > 0 ? container.id : `key-piano-${Math.random().toString(36).slice(2)}`;

        this.#targetField = document.getElementById(container.dataset.target);
        if (this.#targetField === null) {
            throw new Error(`KeyPiano instantiation failed: no target field found with `
                + `id: ${container.dataset.target}.`);
        }

        this.#groupSep = container.dataset.groupSep ?? DEFAULT_GROUP_SEP;
        this.#keySep = container.dataset.keySep ?? DEFAULT_KEY_SEP;
        this.#groups = Array.from(container.querySelectorAll(`.${CSS_GROUP}`));
        this.#history = [];
        this.#buffer = new Array(this.#groups.length).fill(null);
        this.#currentTurn = 0;
        this.#freeClickCount = 0;

        this.#setupGroups();
        this.#applyGating();
        this.#injectControls();
        this.#injectStatus();

        WexaLogger.debug(`KeyPiano: activated on #${this.#instanceId} with ${this.#groups.length} group(s).`);
    }

    // ------------------------------------------------------------------
    // Retargeting
    // ------------------------------------------------------------------

    /**
     * Point this piano at a different target field, discarding any in-progress entry.
     *
     * For a single shared piano serving several possible fields in turn (e.g.
     * hosted in a dialog opened from different rows of a table): an undo
     * history or a partial radio selection made for the previous field would
     * make no sense applied to the new one, so both are reset.
     *
     * @param {string} fieldId - id of the new target field.
     * @returns {void}
     *
     */
    setTarget(fieldId) {
        const field = document.getElementById(fieldId);
        if (field === null) {
            throw new Error(`KeyPiano.setTarget failed: no field found with id: ${fieldId}.`);
        }
        this.#targetField = field;
        this.#history = [];
        this.#freeClickCount = 0;
        this.#resetCycle();
    }

    // ------------------------------------------------------------------
    // Setup
    // ------------------------------------------------------------------

    /**
     * Normalize the mode of every group and wire its listeners.
     *
     * @returns {void}
     *
     */
    #setupGroups() {
        this.#groups.forEach((group, index) => {
            const mode = group.dataset.mode === MODE_RADIO ? MODE_RADIO : MODE_FREE;
            group.dataset.mode = mode;

            if (mode === MODE_RADIO) {
                this.#setupRadioGroup(group, index);
            } else {
                this.#setupFreeGroup(group);
            }
        });
    }

    // ------------------------------------------------------------------

    /**
     * Give every radio key of a group a unique name and wire its "change" event.
     *
     * The "name" attribute is overwritten so that several KeyPiano instances
     * on the same page never collide, whatever the HTML author wrote there.
     *
     * @param {HTMLElement} group - A ".wexa-key-piano-group" element in "radio" mode.
     * @param {number} index - Position of the group in the piano cycle.
     * @returns {void}
     *
     */
    #setupRadioGroup(group, index) {
        const groupName = `${this.#instanceId}-group-${index}`;
        const radios = group.querySelectorAll('input[type="radio"]');

        radios.forEach((radio) => {
            radio.name = groupName;
            radio.addEventListener('change', () => this.#handleRadioChange(index, radio.value));
        });

        if (radios.length === 0) {
            WexaLogger.warn(`KeyPiano: group ${index} is declared "radio" but has no radio input.`);
        }
    }

    // ------------------------------------------------------------------

    /**
     * Wire the "click" event of every free key of a group.
     *
     * @param {HTMLElement} group - A ".wexa-key-piano-group" element in "free" mode.
     * @returns {void}
     *
     */
    #setupFreeGroup(group) {
        const buttons = group.querySelectorAll(`button.${CSS_KEY}`);

        buttons.forEach((button) => {
            button.addEventListener('click', () => this.#handleFreeClick(button.value));
        });

        if (buttons.length === 0) {
            WexaLogger.warn('KeyPiano: a "free" group has no button key.');
        }
    }

    // ------------------------------------------------------------------
    // Radio groups: turn-taking
    // ------------------------------------------------------------------

    /**
     * Handle a selection change inside a "radio" group.
     *
     * Buffers the choice. If the group was the one currently awaited, the
     * turn moves to the next group; once every group of the cycle has a
     * value, the composed key is appended to the target field and the
     * cycle restarts.
     *
     * @param {number} index - Position of the group in the piano cycle.
     * @param {string} value - Value of the selected radio key.
     * @returns {void}
     *
     */
    #handleRadioChange(index, value) {
        this.#buffer[index] = value;

        if (index === this.#currentTurn) {
            this.#currentTurn += 1;
        }
        this.#applyGating();

        const isCycleComplete = this.#groups.every((group, i) => {
            return group.dataset.mode !== MODE_RADIO || this.#buffer[i] !== null;
        });
        if (isCycleComplete === true) {
            const composedKey = this.#buffer.join(this.#groupSep);
            this.#appendToTarget(composedKey);
            this.#announce(`Key added: ${composedKey}`);
            this.#resetCycle();
        }
    }

    // ------------------------------------------------------------------

    /**
     * Enable only the radio keys of the current turn's group, disable every other group.
     *
     * Strictly one active group at a time: an earlier group whose turn has
     * passed is not left clickable alongside the current one. Correcting an
     * earlier choice goes through "delete last key" (#handleBackspace),
     * which moves the turn back and re-enables that group on its own.
     *
     * @returns {void}
     *
     */
    #applyGating() {
        this.#groups.forEach((group, index) => {
            if (group.dataset.mode !== MODE_RADIO) {
                return;
            }
            const radios = group.querySelectorAll('input[type="radio"]');
            radios.forEach((radio) => {
                radio.disabled = index !== this.#currentTurn;
            });
        });
    }

    // ------------------------------------------------------------------

    /**
     * Reset the radio buffer and turn order after a key was appended, or on "clear all".
     *
     * @returns {void}
     *
     */
    #resetCycle() {
        this.#buffer = new Array(this.#groups.length).fill(null);
        this.#currentTurn = 0;
        this.#groups.forEach((group) => {
            group.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
                radio.checked = false;
            });
        });
        this.#applyGating();
    }

    // ------------------------------------------------------------------
    // Free groups: immediate append
    // ------------------------------------------------------------------

    /**
     * Handle a click on a "free" key: append its value immediately.
     *
     * The separator prefixed to the value cycles through the declared
     * groups: the inner separator within a cycle, the outer (key)
     * separator once a full cycle of groups has been clicked.
     *
     * @param {string} value - Value of the clicked key.
     * @returns {void}
     *
     */
    #handleFreeClick(value) {
        const isCycleStart = this.#freeClickCount % this.#groups.length === 0;
        const separator = isCycleStart ? this.#keySep : this.#groupSep;
        this.#freeClickCount += 1;

        this.#appendToTarget(value, separator);
        this.#announce(`Added: ${value}`);
    }

    // ------------------------------------------------------------------
    // Target field: append, undo, clear
    // ------------------------------------------------------------------

    /**
     * Append a value to the target field, prefixed by a separator if it is not empty.
     *
     * The field's previous value is pushed on the history stack, so a
     * single "delete last key" click can restore it exactly.
     *
     * @param {string} value - Value to append.
     * @param {string} [separator] - Separator to prefix the value with. Defaults to
     *        the outer (key) separator.
     * @returns {void}
     *
     */
    #appendToTarget(value, separator) {
        const sep = typeof separator === 'string' ? separator : this.#keySep;
        this.#history.push(this.#targetField.value);

        this.#setTargetValue(this.#targetField.value.length === 0
            ? value
            : this.#targetField.value + sep + value);
    }

    // ------------------------------------------------------------------

    /**
     * Set the target field's value, and dispatch a real "input" event.
     *
     * Setting ".value" programmatically never fires "input"/"change" on its
     * own: a consuming page relying on those events (e.g. clearing a
     * sibling field when this one is no longer empty) would otherwise never
     * see a piano-driven change, only a real keystroke.
     *
     * @param {string} value - The new value of the target field.
     * @returns {void}
     *
     */
    #setTargetValue(value) {
        this.#targetField.value = value;
        this.#targetField.dispatchEvent(new Event('input', {bubbles: true}));
    }

    // ------------------------------------------------------------------

    /**
     * Handle a click on the "delete last key" control.
     *
     * If a radio cycle is in progress, undo its last selection. Otherwise,
     * restore the target field to the value it had before the last append.
     *
     * @returns {void}
     *
     */
    #handleBackspace() {
        if (this.#currentTurn > 0) {
            const index = this.#currentTurn - 1;
            const group = this.#groups[index];
            group.querySelectorAll('input[type="radio"]:checked').forEach((radio) => {
                radio.checked = false;
            });
            this.#buffer[index] = null;
            this.#currentTurn = index;
            this.#applyGating();
            this.#announce('Last key selection undone.');
            return;
        }

        if (this.#history.length === 0) {
            this.#announce('Nothing to undo.');
            return;
        }

        this.#setTargetValue(this.#history.pop());
        this.#announce('Last entry deleted.');
    }

    // ------------------------------------------------------------------

    /**
     * Handle a click on the "clear all" control: reset the piano and the target field.
     *
     * @returns {void}
     *
     */
    #handleClear() {
        this.#setTargetValue('');
        this.#history = [];
        this.#freeClickCount = 0;
        this.#resetCycle();
        this.#announce('Everything cleared.');
    }

    // ------------------------------------------------------------------
    // Injected controls: "delete last key", "clear all", live status
    // ------------------------------------------------------------------

    /**
     * Build and append the "delete last key" and "clear all" buttons.
     *
     * Icons are retrieved via SVGIconsManager (fetch in module mode, pre-registered
     * cache in bundle mode) and inlined as real "<svg>" markup.
     *
     * @returns {Promise<void>}
     *
     */
    async #injectControls() {
        const backspaceLabel = this.#container.dataset.backspaceLabel ?? DEFAULT_BACKSPACE_LABEL;
        const clearLabel = this.#container.dataset.clearLabel ?? DEFAULT_CLEAR_LABEL;

        const backspaceButton = await this.#createControlButton(
            KeyPiano.#BACKSPACE_ICON, backspaceLabel, () => this.#handleBackspace());
        backspaceButton.classList.add(`${CSS_CONTROL}-backspace`);

        const clearButton = await this.#createControlButton(
            KeyPiano.#CLEAR_ICON, clearLabel, () => this.#handleClear());
        clearButton.classList.add(`${CSS_CONTROL}-clear`);

        // The outer container is a column flex (one row per group): both
        // controls are wrapped in their own row, same idiom as the
        // accessibility buttons sitting side by side in their <nav> section.
        const controls = document.createElement('div');
        controls.classList.add(CSS_CONTROLS);
        controls.appendChild(backspaceButton);
        controls.appendChild(clearButton);
        this.#container.appendChild(controls);
    }

    // ------------------------------------------------------------------

    /**
     * Build one icon-only, accessible control button, its icon inlined as SVG.
     *
     * @param {string} iconName - Icon name passed to icons.get().
     * @param {string} label - Accessible name of the button (visually hidden).
     * @param {Function} onClick - Listener invoked on click.
     * @returns {Promise<HTMLButtonElement>} The created button, not yet attached to the DOM.
     *
     */
    async #createControlButton(iconName, label, onClick) {
        const button = document.createElement('button');
        button.type = 'button';
        button.classList.add(CSS_CONTROL);
        button.setAttribute('aria-label', label);
        button.addEventListener('click', onClick);
        button.innerHTML = await icons.get(iconName);

        return button;
    }

    // ------------------------------------------------------------------

    /**
     * Create the visually-hidden "aria-live" region used to announce every action.
     *
     * @returns {void}
     *
     */
    #injectStatus() {
        this.#statusElt = document.createElement('div');
        this.#statusElt.classList.add(CSS_STATUS);
        this.#statusElt.setAttribute('role', 'status');
        this.#statusElt.setAttribute('aria-live', 'polite');
        this.#container.appendChild(this.#statusElt);
    }

    // ------------------------------------------------------------------

    /**
     * Announce a short message through the live region, for screen reader users.
     *
     * @param {string} message - Message to announce.
     * @returns {void}
     *
     */
    #announce(message) {
        this.#statusElt.textContent = message;
    }

}
