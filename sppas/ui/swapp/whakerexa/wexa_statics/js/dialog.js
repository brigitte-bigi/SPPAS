import { WexaLogger } from './logger.js';

/**
 :filename: statics.js.dialog.js
 :author: Brigitte Bigi
 :contributor: Florian Lopitaux
 :contact: contact@sppas.org
 :summary: Manage opening and closing of dialogs and popup videos.

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
 * Class to manage dialogs and popup videos in Whakerexa.
 *
 * This module provides an object-oriented implementation of the legacy dialog system.
 * It preserves all previous behaviors — opening, closing, and managing video popups —
 * while improving code structure, readability, and maintainability.
 *
 */
export class DialogManager {

    // --------------------------------------------------------------------
    // Members
    // --------------------------------------------------------------------
    #dialogs;
    #closeButtonName;
    #videoPrefix;
    #dialogPrefix;

    // --------------------------------------------------------------------
    // Constructor
    // --------------------------------------------------------------------

    /**
     * Create a new DialogManager instance.
     *
     * Initializes internal structures to store dialog references and defines
     * naming conventions for dialog and video identifiers.
     */
    constructor() {
        this.#dialogs = new Map();
        this.#closeButtonName = 'popup-close-btn';
        this.#videoPrefix = 'popup-video-';
        this.#dialogPrefix = 'popup-';
    }

    // --------------------------------------------------------------------
    // Public methods
    // --------------------------------------------------------------------

    /**
     * Open a dialog in standard or modal mode.
     *
     * This method mirrors the legacy `open_dialog()` behavior. It changes the CSS class
     * from 'hidden-alert' to 'hidden-alert-open', injects a close button if missing,
     * and displays the dialog either with `showModal()` or `show()`. The modal mode
     * blocks background interaction until the dialog is closed.
     *
     * @param {string} id - The identifier of the dialog element.
     * @param {boolean} [isModal=false] - Whether to display it as a modal dialog.
     */
    open(id, isModal = false) {
        const dialog = this.#getDialog(id);
        if (dialog === null) return;

        // Replace hidden class to make the dialog visible.
        dialog.classList.replace('hidden-alert', 'hidden-alert-open');

        // Ensure a single close button is available.
        this.#createCloseButton(dialog);

        // Open the dialog, preferring modal mode if requested and supported.
        if (isModal === true && typeof dialog.showModal === 'function') {
            dialog.showModal();
        } else if (typeof dialog.show === 'function') {
            dialog.show();
        } else {
            dialog.setAttribute('open', '');
        }
    }

    // --------------------------------------------------------------------

    /**
     * Close a dialog and restore its initial state.
     *
     * This method reproduces the legacy `close_dialog()` logic. It restores the hidden
     * class, removes the dynamically created close button, and calls the dialog’s native
     * `close()` method if available. It ensures that the dialog’s DOM structure is
     * always reset after closing.
     *
     * @param {string} id - The identifier of the dialog element.
     */
    close(id) {
        const dialog = this.#getDialog(id);
        if (dialog === null) return;

        // Restore the hidden class to hide the dialog.
        dialog.classList.replace('hidden-alert-open', 'hidden-alert');

        // Remove the close button if present.
        Array.from(dialog.children).forEach(child => {
            if (child.name === this.#closeButtonName) {
                child.remove();
            }
        });

        // Close the dialog (prefer the native method if supported).
        if (typeof dialog.close === 'function') {
            dialog.close();
        } else {
            dialog.removeAttribute('open');
        }
    }

    // --------------------------------------------------------------------

    /**
     * Open a video popup and pre-load its content.
     *
     * This method opens the corresponding dialog in modal mode and
     * triggers a short play/pause sequence to force early loading of the
     * video resource by the browser.
     *
     * @param {string} id - Popup identifier (without prefix).
     * @returns {Promise<void>}
     */
    async playVideo(id) {
        const popupId = this.#dialogPrefix + id;
        this.open(popupId, true);

        const video = document.getElementById(this.#videoPrefix + id);
        if (video === null) {
            WexaLogger.error(`DialogManager: video not found for '${id}'.`);
            return;
        }

        // Trigger quick playback to preload video data.
        await video.play();
        video.pause();
    }

    // --------------------------------------------------------------------

    /**
     * Close the video popup and stop playback.
     *
     * This method mirrors the legacy `close_popup_video()` function. It closes the
     * corresponding dialog and ensures that the associated video is paused to free
     * browser resources and maintain consistent playback state.
     *
     * @param {string} id - Popup identifier (without prefix).
     */
    closeVideo(id) {
        const popupId = this.#dialogPrefix + id;
        this.close(popupId);

        const video = document.getElementById(this.#videoPrefix + id);
        if (video !== null) {
            // Pause playback to release resources.
            video.pause();
        } else {
            WexaLogger.warn(`DialogManager: video not found for '${id}'.`);
        }
    }

    // --------------------------------------------------------------------
    // Private methods
    // --------------------------------------------------------------------

    /**
     * Get the dialog element and store it in cache.
     *
     * @private
     * @param {string} id - The dialog identifier.
     * @returns {HTMLDialogElement|null}
     */
    #getDialog(id) {
        if (this.#dialogs.has(id)) {
            return this.#dialogs.get(id);
        }

        const dialog = document.getElementById(id);
        if (dialog === null) {
            WexaLogger.error(`DialogManager: dialog not found: '${id}'.`);
            return null;
        }

        this.#dialogs.set(id, dialog);
        return dialog;
    }

    /**
     * Create and attach a close button to the dialog.
     *
     * @private
     * @param {HTMLDialogElement} dialog - The dialog element.
     */
    #createCloseButton(dialog) {
        if (dialog.querySelector(`button[name="${this.#closeButtonName}"]`) !== null) {
            return;
        }

        const btn = document.createElement('button');
        btn.name = this.#closeButtonName;
        btn.type = 'button';
        btn.innerHTML = '&#10060;';
        btn.addEventListener('click', () => this.close(dialog.id));
        dialog.appendChild(btn);
    }
}
