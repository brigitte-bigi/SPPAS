/**
 * :filename: wexa_statics.js.wexa.loader.js
 * :author: Brigitte Bigi
 * :contact: contact@sppas.org
 * :summary: Loads Whakerexa, whatever the protocol the page is read on.
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
 *
 *  A page writes one line instead of the twenty it used to copy:
 *
 *      <script src="../wexa_statics/js/wexa.loader.js"
 *              data-base="../wexa_statics/"
 *              data-links="btn-back"
 *              data-extras="js/extras/sortatable.js,js/toggleselect.js"></script>
 *
 *  data-base    where wexa_statics/ stands, seen from the page. Required.
 *  data-links   the identifiers whose address carries the theme, if any.
 *  data-default the theme to apply when the address names none, if any.
 *  data-themes-base  where the themes stand, when they are not under
 *               css/themes/ of the base: a page served with the minified
 *               stylesheets asks for the minified themes.
 *  data-icons   the sets of icons the page brings, one per line, written
 *               "name:path:file,file,file". A file answers to the name it
 *               bears without its extension.
 *  data-icons-default  the set to show when the address names none.
 *  data-icons-fallback  the set that answers what the others leave
 *               unanswered. What it does not carry either is answered by the
 *               set of the framework.
 *  data-extras  the files to load besides wexa.js, written from the base and
 *               separated by commas. Ignored on file://, where the bundle
 *               already holds them.
 *
 *  A page that has something of its own to start declares a function named
 *  bootPage: it is called once everything is loaded, and receives what the
 *  page can build with — the namespace of the framework and the extras asked
 *  for, under the names they export.
 *
 *  This file is not an ES6 module, and cannot be one: it is what decides
 *  whether modules can be loaded at all. On file:// a browser refuses them,
 *  and the bundle answers for them.
 */

'use strict';

(function () {

    // The tag that loaded this file, and what the page says on it.
    const tag = document.querySelector('script[data-base]');
    if (tag === null) {
        console.error('wexa.loader: no script carries data-base. Nothing is loaded.');
        return;
    }

    const base = tag.getAttribute('data-base');
    const links = (tag.getAttribute('data-links') || '')
        .split(',')
        .map(name => name.trim())
        .filter(name => name.length > 0);
    const defaultTheme = tag.getAttribute('data-default') || '';
    const themesBase = tag.getAttribute('data-themes-base') || (base + 'css/themes/');
    const iconSets = tag.getAttribute('data-icons') || '';
    const iconsDefault = tag.getAttribute('data-icons-default') || '';
    const iconsFallback = tag.getAttribute('data-icons-fallback') || '';
    const extras = (tag.getAttribute('data-extras') || '')
        .split(',')
        .map(name => name.trim())
        .filter(name => name.length > 0);

    // The themes of the repository. A document that brings its own registers
    // them itself, as it does today.
    const THEMES = [
        ['wexa_theme',   'wexa_theme.css'],
        ['aurora',       'wexa_theme_aurora.css'],
        ['highcontrast', 'wexa_theme_highcontrast.css'],
    ];

    // -----------------------------------------------------------------------

    /**
     * Register the themes of the repository, and hold them for the page.
     *
     * @param {Function} ThemeManager - The class that switches a theme.
     * @returns {void}
     */
    function registerThemes(ThemeManager) {
        if (typeof ThemeManager !== 'function') {
            return;
        }

        const themes = new ThemeManager();
        THEMES.forEach(theme => themes.register(theme[0], themesBase + theme[1]));
        if (defaultTheme !== '') {
            themes.setDefault(defaultTheme);
        }
        window.themes = themes;
    }

    // -----------------------------------------------------------------------

    /**
     * Declare the sets of icons, and answer the demands of the document.
     *
     * The set of the framework is declared last, so that it is the one a name
     * falls back to. What a page brings is read on its own tag, where it
     * already says what it loads.
     *
     * @param {Object} namespace - What holds the classes of the icons.
     * @returns {void}
     */
    function startIcons(namespace) {
        const icons = namespace.icons || (window.Wexa && window.Wexa.icons) || null;
        if (icons === null || !namespace.IconSet) {
            return;
        }

        // What follows must not take the rest of the page with it: a page
        // whose icons do not answer still navigates and still switches theme.
        try {
            declareSets(icons, namespace);
        } catch (error) {
            console.error('wexa.loader: the sets of icons were not declared.', error);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Hold the sets a page brings, and answer its demands.
     *
     * @param {Object} icons - The manager of the icons.
     * @param {Object} namespace - What holds the classes of the icons.
     * @returns {void}
     */
    function declareSets(icons, namespace) {

        for (const declared of iconSets.split('\n')) {
            const said = declared.trim();
            if (said === '') {
                continue;
            }

            const parts = said.split(':');
            if (parts.length < 3) {
                console.error('wexa.loader: a set of icons is written'
                    + ' "name:path:file,file": ' + said);
                continue;
            }

            // The path is written from data-base, as the page says it is.
            icons.declare(new namespace.IconSet(parts[0].trim(),
                base + parts[1].trim(),
                parts[2].split(',').map(file => file.trim())));
        }

        // What a build gathered into the document, if anything did. It is left
        // on the window by a file the page loads, in no particular order: the
        // drawings are held before the first demand is answered.
        const gathered = window.WEXA_GATHERED_ICONS;
        if (Array.isArray(gathered) === true) {
            gathered.forEach(one => icons.gather(one[0], one[1], one[2]));
        }

        if (iconsFallback !== '') {
            icons.fallback(iconsFallback);
        }

        if (iconsDefault !== '') {
            icons.show(iconsDefault);
        }

        icons.run();
    }

    // -----------------------------------------------------------------------

    /**
     * Give the addresses their parameters back, so a theme survives a link.
     *
     * Waited for when the document is still loading, done straight away when
     * it is not: the modules are loaded on a promise, which may be kept after
     * the page is loaded, and a listener added then would never be called.
     *
     * @param {Object} wexa - The namespace of the framework.
     * @returns {void}
     */
    function handleLinks(wexa) {
        if (links.length === 0) {
            return;
        }
        if (!wexa || !wexa.links || typeof wexa.links.handleLinksWithParameters !== 'function') {
            return;
        }

        if (document.readyState === 'complete') {
            wexa.links.handleLinksWithParameters(links);
        } else {
            window.addEventListener('load',
                () => wexa.links.handleLinksWithParameters(links), { once: true });
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Start what the page has of its own, when it has something.
     *
     * @param {Object} namespace - The framework and the extras asked for.
     * @returns {void}
     */
    function bootPage(namespace) {
        if (typeof window.bootPage === 'function') {
            window.bootPage(namespace);
        }
    }

    // -----------------------------------------------------------------------

    /**
     * Load the bundle, which holds everything under one global name.
     *
     * @returns {void}
     */
    function loadBundle() {
        const script = document.createElement('script');
        script.src = base + 'js/wexa.bundle.js';
        script.addEventListener('load', function () {
            const wexa = window.Wexa;
            if (!wexa) {
                console.error('wexa.loader: the bundle loaded without a namespace.');
                return;
            }
            registerThemes(wexa.ThemeManager);
            startIcons(wexa);
            handleLinks(wexa);
            bootPage(wexa);
        });
        script.addEventListener('error', function () {
            console.error('wexa.loader: the bundle was not found at ' + script.src);
        });
        document.head.appendChild(script);
    }

    // -----------------------------------------------------------------------

    /**
     * Give the address of a file of the framework, seen from the page.
     *
     * data-base is written as the page sees it. An import() called from this
     * file would read it as this file sees it, and would look for
     * wexa_statics inside wexa_statics.
     *
     * @param {String} path - What follows the base.
     * @returns {String} The address, resolved against the document.
     */
    function addressOf(path) {
        return new URL(base + path, document.baseURI).href;
    }

    // -----------------------------------------------------------------------

    /**
     * Load the modules, and the extras the page asked for.
     *
     * @returns {Promise<void>}
     */
    async function loadModules() {
        try {
            const wexa = await import(addressOf('js/wexa.js'));
            const themeModule = await import(addressOf('js/customize/theme_manager.js'));

            const namespace = Object.assign({}, wexa);
            for (const extra of extras) {
                const module = await import(addressOf(extra));
                Object.assign(namespace, module);
            }

            const iconModules = await Promise.all([
                import(addressOf('js/customize/icon_set.js')),
                import(addressOf('js/customize/icons.js'))
            ]);
            iconModules.forEach(module => Object.assign(namespace, module));

            registerThemes(themeModule.ThemeManager);
            startIcons(namespace);
            handleLinks(window.Wexa || wexa);
            bootPage(namespace);

        } catch (error) {
            console.error('wexa.loader: the modules were not loaded.', error);
        }
    }

    // -----------------------------------------------------------------------

    if (window.location.protocol === 'file:') {
        loadBundle();
    } else {
        loadModules();
    }

})();
