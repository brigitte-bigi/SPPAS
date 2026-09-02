/**
:filename: wexa_statics.js.dom-loader.js
:author: Florian Lopitaux
:contributor: Brigitte Bigi
:contact: florian.lopitaux@gmail.com
:summary: file that contains the OnLoadManager class to process multiple functions in an onload event.

.. _This file is part of PureJS-Tools : https://sourceforge.net/projects/purejs-tools/
..
    -------------------------------------------------------------------------

    Copyright (C) 2024  Florian LOPITAUX
    13100 Aix-en-Provence, France

    Use of this software is governed by the GNU Public License, version 3.

    PureJS-Tools is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PureJS-Tools is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PureJS-Tools. If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------
*/

export class OnLoadManager {
    // FIELDS
    static #functions = [];
    static #listenerRegistered = false;

    // PUBLIC STATIC METHODS
    /**
     * Appends the given function to the list of functions to call during the onload event.
     *
     * Registers the window 'load' listener on first use, so callers never need
     * to wire it themselves nor depend on another script's load order.
     *
     * A function given after the page is loaded is called straight away: a
     * module loaded on a promise is built after that event, and a listener
     * added then would never be called.
     *
     * @param func the function to call during the onload event.
     */
    static addLoadFunction(func) {
        if (document.readyState === 'complete') {
            func();
            return;
        }

        OnLoadManager.#functions.push(func);
        OnLoadManager.#registerListener();
    }

    /**
     * Calls all functions added.
     */
    static runLoadFunctions() {
        OnLoadManager.#functions.forEach(func => func());
    }

    // PRIVATE STATIC METHODS
    /**
     * Registers the window 'load' listener once, regardless of how many
     * modules call addLoadFunction().
     */
    static #registerListener() {
        if (OnLoadManager.#listenerRegistered === true) {
            return;
        }
        OnLoadManager.#listenerRegistered = true;
        window.addEventListener('load', OnLoadManager.runLoadFunctions);
    }
}
