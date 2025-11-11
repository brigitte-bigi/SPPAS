/**
:filename: purejs-tools.OnLoadManager.js
:author: Florian Lopitaux
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

class OnLoadManager {
    // FIELDS
    static #functions = [];


    // PUBLIC STATIC METHODS
    /**
     * Appends the given function to the list of functions to call during the onload event.
     * 
     * @param func the function to call during the onload event.
     */
    static addLoadFunction(func) {
        OnLoadManager.#functions.push(func);
    }

    /**
     * Calls all functions added.
     * This function has to be called in the 'window.onload' event.
     */
    static runLoadFunctions() {
        OnLoadManager.#functions.forEach(async func => {
            await func();
        });
    }
}


// set the window onload event
window.onload = () => {
    OnLoadManager.runLoadFunctions();
};
