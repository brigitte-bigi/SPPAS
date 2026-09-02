/**
 * :filename: statics.js.customize.icons.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: The icons of a document: one manager, held by this module.
 *
 *  -------------------------------------------------------------------------
 *
 *  This file is part of Whakerexa: https://github.com/brigitte-bigi/Whakerexa
 *
 *  Copyright (C) 2023-2026 Brigitte Bigi, CNRS
 *  Laboratoire Parole et Langage, Aix-en-Provence, France
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 *  This banner notice must not be removed.
 *
 *  -------------------------------------------------------------------------
 */

'use strict';

import { IconSet } from './icon_set.js';
import { IconSets } from './icon_sets.js';
import { IconManager } from './icon_manager.js';
import { REFERENCE_FILES } from './icon_reference.js';

/**
 * The manager of the icons of a document.
 *
 * It is held by this module and not by the namespace: a component that asks
 * for an icon imports it, and does not wait for the namespace to be assigned.
 * The set of the framework is its reference from the start, so that a
 * component finds its icon whenever it asks, and a page adds its own sets
 * afterwards.
 */
// Where this file stands, so that a document finds the icons wherever it is
// read from. The build writes null here, the bundle being a classic script:
// there the drawings are gathered in, and no address is ever asked for.
const here = import.meta.url;
const referenceBase = here === null
    ? 'icons/mono-svg/'
    : new URL('../../icons/mono-svg/', here).href;

const sets = new IconSets();
sets.reference(new IconSet('mono-svg', referenceBase, REFERENCE_FILES));

export const icons = new IconManager(sets);
