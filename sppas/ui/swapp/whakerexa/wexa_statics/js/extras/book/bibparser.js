/**
 :filename: wexa_statics/js/extras/book/bibparser.js
 :author: Brigitte Bigi
 :contact: contact@sppas.org
 :summary: A class to turn BibTeX data into references.

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

import { Reference } from './bibreference.js';
import { Author } from './bibauthor.js';
import { Link } from './biblink.js';

/**
 * Turn BibTeX data into references.
 *
 * The algorithms come from bib-list.js, written in 2008, whose code is not
 * reused but whose reading of BibTeX is right and handles what a naive one
 * gets wrong: braces are counted rather than matched by a regular expression,
 * an entry is read backwards so that a value holding commas and equal signs
 * costs nothing, and names follow the three forms BibTeX allows.
 *
 * Nothing here ever raises: an entry that cannot be read is left aside and
 * said so, and the others are parsed all the same.
 */
export class BibtexParser {
    // CONSTANTS
    /**
     * Accents, as LaTeX writes them, and the combining mark they stand for.
     *
     * Converting by rule rather than by a closed list of words is what makes
     * an accent that was never met before come out right.
     */
    static ACCENTS = new Map([
        ["'", '́'],    // acute
        ['`', '̀'],    // grave
        ['^', '̂'],    // circumflex
        ['"', '̈'],    // diaeresis
        ['~', '̃'],    // tilde
        ['=', '̄'],    // macron
        ['.', '̇'],    // dot above
        ['c', '̧'],    // cedilla
        ['v', '̌'],    // caron
        ['u', '̆'],    // breve
        ['H', '̋'],    // double acute
        ['r', '̊'],    // ring above
        ['k', '̨']     // ogonek
    ]);

    /**
     * Letters that LaTeX writes as a command of their own.
     *
     * The longest are listed first, so that \o never eats the \oe.
     */
    static LETTERS = new Map([
        ['\\AA', 'Å'], ['\\aa', 'å'], ['\\AE', 'Æ'], ['\\ae', 'æ'],
        ['\\OE', 'Œ'], ['\\oe', 'œ'], ['\\ss', 'ß'],
        ['\\O', 'Ø'], ['\\o', 'ø'], ['\\L', 'Ł'], ['\\l', 'ł'],
        ['\\i', 'ı'], ['\\j', 'ȷ']
    ]);

    /**
     * Characters that LaTeX has to escape, and that mean themselves.
     */
    static ESCAPED = ['&', '%', '$', '#', '_'];

    /**
     * Fields that may hold an address. BibTeX only has URL; NOTE is where a
     * second address goes. This is a habit of the house, not a standard.
     */
    static LINK_FIELDS = ['url', 'note'];


    // PUBLIC METHODS
    /**
     * Read BibTeX data and give back the references it holds.
     *
     * Entries are cut by counting braces. A brace preceded by a backslash does
     * not count. An entry starts at an "@" met outside any brace, and ends when
     * the count is back to zero.
     *
     * An "@" met while an entry is still open means that a closing brace is
     * missing: the entry is closed by force and the reading starts again at
     * that "@", so that a file damaged in one place does not lose the rest.
     *
     * @param content {string} The BibTeX data.
     * @returns {Map} The references, by key. Possibly empty, never null.
     */
    parse(content) {
        const references = new Map();
        let inEntry = false;
        let open = 0;
        let buffer = '';
        let previous = '';

        for (let i = 0; i < content.length; i++) {
            let character = content[i];

            if (open !== 0 && character === '@' && BibtexParser.#startsALine(content, i) === true) {
                console.warn('BibtexParser: a closing brace is missing, the entry is closed by force.');
                character = '}';
                i--;
            }

            if (open === 0 && character === '@') {
                inEntry = true;

            } else if (inEntry === true && character === '{' && previous !== '\\') {
                open++;

            } else if (inEntry === true && character === '}' && previous !== '\\') {
                open--;

                if (open === 0) {
                    inEntry = false;
                    this.#keepEntry(references, buffer);
                    buffer = '';
                }
            }

            if (inEntry === true) {
                buffer += character;
            }
            previous = character;
        }

        // The last entry may have lost its closing brace at the end of the file.
        if (open > 0) {
            console.warn('BibtexParser: the last entry has no closing brace.');
            this.#keepEntry(references, buffer);
        }

        return references;
    }


    // PRIVATE METHODS
    /**
     * Parse one entry and put it with the others, or say why it was left aside.
     *
     * @param references {Map} The references gathered so far.
     * @param buffer {string} The entry, without its closing brace.
     * @returns {void}
     */
    #keepEntry(references, buffer) {
        const reference = this.#parseEntry(buffer + '}');

        if (reference === null) {
            return;
        }

        if (references.has(reference.key) === true) {
            console.warn(`BibtexParser: the key "${reference.key}" is used twice, the second entry wins.`);
        }

        references.set(reference.key, reference);
    }

    /**
     * Parse one entry, reading it backwards.
     *
     * The last equal sign is looked for, the value taken from there, then the
     * last comma before it, which gives the name of the field. What is left at
     * the beginning carries the type and the key. Reading backwards is what
     * makes a value holding commas and equal signs cost nothing: an abstract
     * always holds some.
     *
     * @param source {string} The entry, as written in the data.
     * @returns {Reference} The reference, or null when the entry is unreadable.
     */
    #parseEntry(source) {
        const fields = new Map();
        let entry = source.substring(0, source.length - 1);

        while (entry.includes('=') === true) {
            let position = entry.lastIndexOf('=');

            while (position !== -1 && BibtexParser.#isSeparator(entry, position) === false) {
                position = entry.lastIndexOf('=', position - 1);
            }
            if (position === -1) {
                break;
            }

            const value = entry.substring(position + 1);
            entry = entry.substring(0, position);

            const comma = entry.lastIndexOf(',');
            if (comma === -1) {
                break;
            }

            const name = entry.substring(comma + 1).trim().toLowerCase();
            entry = entry.substring(0, comma);

            if (name.length > 0) {
                fields.set(name, this.#cleanValue(value));
            }
        }

        const brace = entry.indexOf('{');
        if (brace === -1) {
            console.warn('BibtexParser: an entry has no opening brace, it is left aside.');
            return null;
        }

        const type = entry.substring(0, brace).trim().replace('@', '');
        const key = entry.substring(brace + 1).trim();

        if (key.length === 0) {
            console.warn('BibtexParser: an entry has no key, it is left aside.');
            return null;
        }

        let authors = [];
        if (fields.has('author') === true) {
            authors = this.#parseAuthors(fields.get('author'));
        }

        return new Reference(key, type, fields, authors, this.#readLinks(fields), source);
    }

    /**
     * Cut a value out of what was written after the equal sign.
     *
     * @param value {string} What follows the equal sign, delimiters included.
     * @returns {string} The value, ready to be displayed.
     */
    #cleanValue(value) {
        let cleaned = value.trim();

        if (cleaned.endsWith(',') === true) {
            cleaned = cleaned.substring(0, cleaned.length - 1).trim();
        }

        cleaned = BibtexParser.#stripDelimiters(cleaned);
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        cleaned = this.#decodeLatex(cleaned);

        // Braces that protected a case have done their work; what they
        // protected is left untouched.
        return cleaned.replace(/(^|[^\\])[{}]/g, '$1');
    }

    /**
     * Convert the LaTeX notations of a value into plain characters.
     *
     * Accents are converted by rule, an accent and a letter, and put together
     * with the letter they belong to. A notation that is not known is left as
     * it was written rather than thrown away.
     *
     * @param text {string} The value, as written.
     * @returns {string} The value, with plain characters.
     */
    #decodeLatex(text) {
        let converted = text;

        BibtexParser.LETTERS.forEach((letter, command) => {
            converted = converted.split(command + '{}').join(letter);
            converted = converted.split(command + ' ').join(letter);
            converted = converted.split(command).join(letter);
        });

        const accents = Array.from(BibtexParser.ACCENTS.keys()).map(BibtexParser.#escapeForRegExp).join('');
        const pattern = new RegExp('\\\\([' + accents + '])\\s*\\{?([A-Za-z])\\}?', 'g');

        converted = converted.replace(pattern, (whole, accent, letter) => {
            return letter + BibtexParser.ACCENTS.get(accent);
        });

        BibtexParser.ESCAPED.forEach(character => {
            converted = converted.split('\\' + character).join(character);
        });

        // Two hyphens are how LaTeX writes a range; one hyphen reads better.
        converted = converted.split('--').join('-');

        return converted.normalize('NFC');
    }

    /**
     * Cut the list of signatories, and each name into its four parts.
     *
     * Names are separated by " and ". Each of them follows one of the three
     * forms BibTeX allows: "First von Last", "von Last, First", and
     * "von Last, Jr, First". The number of commas says which one.
     *
     * @param value {string} The value of the AUTHOR field.
     * @returns {Author[]} The signatories, in the order they sign.
     */
    #parseAuthors(value) {
        const written = value.split(' and ');
        const authors = [];

        written.forEach((name, index) => {
            const parts = BibtexParser.#splitName(name.trim());
            authors.push(new Author(index + 1, parts.first, parts.particle, parts.last, parts.suffix));
        });

        return authors;
    }

    /**
     * Keep the addresses written in the fields that may hold one.
     *
     * The name of the field says nothing about where its address leads, and a
     * NOTE that is not an address is a note: only what looks like an address
     * becomes a link.
     *
     * @param fields {Map} The fields of the entry.
     * @returns {Link[]} The addresses, possibly none.
     */
    #readLinks(fields) {
        const links = [];

        BibtexParser.LINK_FIELDS.forEach(name => {
            if (fields.has(name) === false) {
                return;
            }

            const value = fields.get(name).trim();
            if (value.startsWith('http') === true) {
                links.push(new Link(value));
            }
        });

        return links;
    }


    // PRIVATE STATIC METHODS
    /**
     * Tell whether an equal sign separates a field from its value.
     *
     * The braces are counted backwards from the end of what is left up to the
     * equal sign: when the count is not zero, that equal sign sits inside a
     * value. A value delimited by double quotes is checked apart, because its
     * braces are balanced even when the equal sign belongs to an equation.
     *
     * @param entry {string} What is left of the entry.
     * @param position {number} Where the equal sign is.
     * @returns {boolean} True when it separates a field from its value.
     */
    static #isSeparator(entry, position) {
        if (position > 0 && entry[position - 1] === '\\') {
            return false;
        }

        let open = 0;
        for (let i = entry.length - 1; i >= position; i--) {
            if (entry[i] === '{' && entry[i - 1] !== '\\') {
                open++;
            }
            if (entry[i] === '}' && entry[i - 1] !== '\\') {
                open--;
            }
        }
        if (open !== 0) {
            return false;
        }

        let tail = entry.trimEnd();
        if (tail.endsWith(',') === true) {
            tail = tail.substring(0, tail.length - 1).trimEnd();
        }
        if (tail.endsWith('"') === false) {
            return true;
        }

        let found = 0;
        for (let i = entry.length - 1; i >= position; i--) {
            if (entry[i] === '"' && entry[i - 1] !== '\\') {
                found++;
            }
            if (found === 2) {
                return true;
            }
        }

        return false;
    }

    /**
     * Remove the delimiters BibTeX puts around a value.
     *
     * @param value {string} The value, delimiters included.
     * @returns {string} The value alone.
     */
    static #stripDelimiters(value) {
        if (value.startsWith('{') === true && value.endsWith('}') === true) {
            return value.substring(1, value.length - 1);
        }
        if (value.startsWith('"') === true && value.endsWith('"') === true) {
            return value.substring(1, value.length - 1);
        }

        return value;
    }

    /**
     * Cut one name into its four parts.
     *
     * @param name {string} One name, as written between two " and ".
     * @returns {Object} The four parts: first, particle, last, suffix.
     */
    static #splitName(name) {
        const parts = name.split(',');

        if (parts.length === 1) {
            return BibtexParser.#splitFirstVonLast(name);
        }

        const vonLast = BibtexParser.#splitVonLast(parts[0].trim());
        let suffix = '';

        if (parts.length > 2) {
            suffix = parts[1].trim();
        }

        return {
            first: parts[parts.length - 1].trim(),
            particle: vonLast.particle,
            last: vonLast.last,
            suffix: suffix
        };
    }

    /**
     * Cut a name written as "First von Last".
     *
     * Words are given to the first name until one starts in lower case: that
     * one starts the particle, which runs up to the last word in lower case.
     * The last word always belongs to the family name.
     *
     * @param name {string} The name, without any comma.
     * @returns {Object} The four parts: first, particle, last, suffix.
     */
    static #splitFirstVonLast(name) {
        const words = name.split(/\s+/).filter(word => word.length > 0);

        if (words.length === 1) {
            return {first: '', particle: '', last: words[0], suffix: ''};
        }

        const lastLower = BibtexParser.#lastLowerCaseWord(words, words.length - 1);

        if (lastLower === -1) {
            return {
                first: words.slice(0, words.length - 1).join(' '),
                particle: '',
                last: words[words.length - 1],
                suffix: ''
            };
        }

        const firstLower = BibtexParser.#firstLowerCaseWord(words, lastLower);

        return {
            first: words.slice(0, firstLower).join(' '),
            particle: words.slice(firstLower, lastLower + 1).join(' '),
            last: words.slice(lastLower + 1).join(' '),
            suffix: ''
        };
    }

    /**
     * Cut what stands before the first comma, written as "von Last".
     *
     * @param text {string} What stands before the first comma.
     * @returns {Object} Two parts: particle and last.
     */
    static #splitVonLast(text) {
        const words = text.split(/\s+/).filter(word => word.length > 0);

        if (words.length === 1) {
            return {particle: '', last: words[0]};
        }

        const lastLower = BibtexParser.#lastLowerCaseWord(words, words.length - 1);

        if (lastLower === -1) {
            return {particle: '', last: words.join(' ')};
        }

        const firstLower = BibtexParser.#firstLowerCaseWord(words, lastLower);

        return {
            particle: words.slice(firstLower, lastLower + 1).join(' '),
            last: words.slice(lastLower + 1).join(' ')
        };
    }

    /**
     * Find the last word in lower case, the family name set apart.
     *
     * @param words {string[]} The words of a name.
     * @param limit {number} The place of the word that always belongs to the family name.
     * @returns {number} The place of that word, or -1 when there is none.
     */
    static #lastLowerCaseWord(words, limit) {
        for (let i = limit - 1; i >= 0; i--) {
            if (BibtexParser.#isLowerCase(words[i]) === true) {
                return i;
            }
        }

        return -1;
    }

    /**
     * Find where the particle starts, walking back from its last word.
     *
     * @param words {string[]} The words of a name.
     * @param lastLower {number} The place of the last word in lower case.
     * @returns {number} The place where the particle starts.
     */
    static #firstLowerCaseWord(words, lastLower) {
        let start = lastLower;

        while (start > 0 && BibtexParser.#isLowerCase(words[start - 1]) === true) {
            start--;
        }

        return start;
    }

    /**
     * Tell whether a word starts in lower case.
     *
     * The case is read on the first letter met outside braces, because braces
     * are how BibTeX protects a case. A word without any letter, a number for
     * instance, has no case and belongs to the family name.
     *
     * @param word {string} One word of a name.
     * @returns {boolean} True when the word starts in lower case.
     */
    static #isLowerCase(word) {
        let depth = 0;

        for (const character of word) {
            if (character === '{') {
                depth++;
            } else if (character === '}') {
                depth--;
            } else if (depth === 0 && /[A-Za-zÀ-ÖØ-öø-ÿ]/.test(character) === true) {
                return character === character.toLowerCase();
            }
        }

        return false;
    }

    /**
     * Tell whether an "@" starts a line, and so a new entry.
     *
     * An "@" written inside a value, in an address for instance, never starts
     * a line by itself.
     *
     * @param content {string} The BibTeX data.
     * @param position {number} Where the "@" is.
     * @returns {boolean} True when nothing but spaces stands before it on its line.
     */
    static #startsALine(content, position) {
        for (let i = position - 1; i >= 0; i--) {
            const character = content[i];

            if (character === '\n') {
                return true;
            }
            if (character !== ' ' && character !== '\t' && character !== '\r') {
                return false;
            }
        }

        return true;
    }

    /**
     * Protect a character that has a meaning of its own in a regular expression.
     *
     * @param character {string} The character to protect.
     * @returns {string} The character, ready to sit in a character class.
     */
    static #escapeForRegExp(character) {
        return character.replace(/[.*+?^${}()|[\]\\-]/g, '\\$&');
    }
}
