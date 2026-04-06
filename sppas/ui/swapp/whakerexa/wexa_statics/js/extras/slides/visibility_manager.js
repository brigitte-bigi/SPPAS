import SlidesVisibilityController from './visibility.js';

/**
 :filename: statics.js.slides.controls.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: Manage multiple named visibility controllers.

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
 *
 * This class creates and stores one SlidesVisibilityController
 * per managed HTMLElement. It exposes a simple public API to
 * show, hide, toggle one or all elements. No business logic.
 */
export default class SlidesVisibilityManager {

    /**
     * @param {Object.<string, HTMLElement>} elementsMap
     *        Keys = names, values = HTMLElements to manage.
     */
    constructor(elementsMap = {}) {
        this._controllers = {};

        const names = Object.keys(elementsMap);
        for (const name of names) {
            const element = elementsMap[name];
            this._controllers[name] = new SlidesVisibilityController(element);
        }
    }

    /**
     * @param {string} name
     * @returns {void}
     */
    show(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.show();
        }
    }

    /**
     * @param {string} name
     * @returns {void}
     */
    hide(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.hide();
        }
    }

    /**
     * @param {string} name
     * @returns {void}
     */
    toggle(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.toggle();
        }
    }

    /**
     * @returns {void}
     */
    showAll() {
        const names = Object.keys(this._controllers);
        for (const name of names) {
            this._controllers[name].show();
        }
    }

    /**
     * @returns {void}
     */
    hideAll() {
        const names = Object.keys(this._controllers);
        for (const name of names) {
            this._controllers[name].hide();
        }
    }

    /**
     * @returns {string[]} List of managed element names.
     */
    getNames() {
        return Object.keys(this._controllers);
    }
}
