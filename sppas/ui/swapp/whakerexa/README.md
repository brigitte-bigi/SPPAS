# Whakerexa — A minimalist and lightweight web kit for accessible contents


## Overview

`Whakerexa` is a lightweight front-end toolkit that blends clarity, accessibility, and flexibility, and long-term maintainability.
It provides a modern CSS foundation and a fully modular ES6 JavaScript components to build interfaces that are both elegant and inclusive — with minimal code and maximum readability, without dependencies.

Designed around accessibility from the start, Whakerexa makes it easy to craft clean, human-friendly HTML that just works — without drowning your pages in class names or dependencies.
Every visual aspect — colors, typography, spacing, animations — is defined through CSS variables, giving you full creative control with a few redefinitions.

Version 2.0 introduces a unified public API through `wexa.js` and a stable global namespace through `wexa.bundle.js`, ensuring support for both modern ES6 module-based applications and offline/static environments.

It pairs naturally with `WhakerPy`, the lightweight Python library for generating dynamic HTML, offering a seamless workflow from code to design.



### Features

- ✨ Lightweight, semantic, dependency-free, and modular
- 🌓 Built-in light / dark themes
- 🔆 High-contrast accessibility mode
- 🎨 Fully customizable through CSS variables
- 🧩 Composable and extensible — adapt to your needs
- ⚙️ Object-oriented ES6 components
- ⚙️ Unified API (`import … from "wexa.js"` or `Wexa.*`)
- ⚙️ Single-file bundle for no-module environments
- ⚙️ Zero dependencies, 100 % open source


## Install Whakerexa

Whakerexa is distributed as a ZIP archive.  
Simply unpack it.


## Quick Start

For usage examples of the CSS and JS frameworks, visit the **online documentation**:

👉 <https://whakerexa.sourceforge.io>

The HTML files available in the `docs` folder are also provided for offline reference,
but note that dynamic examples (those using JavaScript modules) require a web server
and will not work if opened directly from your disk (`file://` protocol).

Browse the local documentation with:
``` 
> python -m http.server 8000 
```
Then open a new tab into Firefox with the url: http://localhost:8000/docs/


## Projects using Whakerexa

Whakerexa was initially developed within SPPAS <https://sppas.org>. 
It was extracted from its original software in 2024 by the author to lead its own life as standalone tool.


### Websites

It is used by the website of the "AutoCuedSpeech" project at <https://auto-cuedspeech.org> and the website of SPPAS <https://sppas.org>.


## Author/Copyright

Copyright (C) 2023-2025 - Brigitte Bigi, CNRS - <contact@sppas.org>
Laboratoire Parole et Langage, Aix-en-Provence, France.

See the AUTHORS file for the full list of contributors.


## License

Whakerexa is under the terms of the GNU Affero General Public License, version 3.


## Support

Whakerexa was initially developed within <https://auto-cuedspeech.org> project, generously funded by FIRAH (Fondation Internationale de Recherche Appliquée sur le Handicap), <https://www.firah.org/>.
It is also developed with the support of Laboratoire Parole et Langage <https://lpl-aix.fr>.



# Changes

## Version 0.1

- Initial version, extracted from SPPAS 4.17.
- Added or updated, and tested JavaScripts 
- Updated CSS frameworks to be more generic
- Added HTML documentation of the CSS frameworks
- Added a CSS/JS framework for playing a video in a popup dialog

## Version 0.2

- Added code.css, a set of colors for highlighting source code.
- Added menu.css, a solution for an accessible responsive sticky menubar
- Added layout.css, a set of classes to easily organize HTML content
- Added accordion.js which must be added when using "rise-panel"

## Version 0.3

- Changed some colors of code.css
- Added variable 'border-radius' in wexa.css
- Modified details/summary to act and look like buttons
- The "rise-panel/accordion" is deprecated (HTML-3), use HTML-5 details/summary instead
- Added modal dialogs to show an alert message: info, success, warning, error, tips, question

## Version 0.4

This is mainly a bug-correction version: adjusted some width, removed transparency of 
background dialogs, corrected a bug in accessibility.

## Version 0.5 

- Added accessibility icons
- Added upload of files in request.js
- Minor CSS changes
- Migrated license, from GPL to AGPL.

## Version 0.6

- Added `sortatable`: a CSS/JS utility designed for sorting table rows in ascending or descending order
- Added `toggleselect`: CSS/JS utility for toggling checkbox states.
- Added custom buttons: introduced CSS classes `text-reveal-button`, `action-button`, `apply-button` and `switch`.
- Updated request.js: better support of upload, better error management in post.

## Version 0.7

- Re-organized documentation
- Updated the switch button
- Debug of action-button
- Minor changes in wexa.css

## Version 0.8

- This is mainly some debug.

## Version 1.0

Version 1.0 establishes Whakerexa as a modular, object-oriented web kit centered on a unified entry point.

- Core entry point: `wexa.js`, which instantiates:
    1. OnLoadManager — Delayed, ordered component initialization.
    2. WexaLogger — Unified logging.
    3. AccessibilityManager — Themes and contrast.
    4. MenuManager — Navigation menus and submenus.
    5. DialogManager — Opening/closing dialogs and popup videos.

- Menus are fully re-implemented (CSS + JS). See `docs/menu.html`.
- Dialogs are managed by `DialogManager` (legacy functions replaced).
- Backward compatibility with pre-1.0 procedural APIs is limited and not fully ensured.
- Not all minor/specialized classes have been ported (e.g., `Book`, `ToggleSelector`, `SortaTable`).

This version also includes a set of monochrome SVG icons.

## Version 2.0 

Version 2.0 is a complete modernization.
Previous procedural APIs are not preserved.

- Unified ES6 entry point (`wexa.js`) exporting all components.
- `wexa.bundle.js` exposes the global namespace `window.Wexa` for `file://` usage.
- The `progress()` function is removed. Use the `ProgressBar` class instead (see `docs/progressbar.html`).
- Use `Wexa.onload` instead of `OnLoadManager`, `Wexa.dialog` instead of `DialogManager`, etc.
- `WexaLogger` is extended: numeric levels from 0 (most verbose) to 50 (critical only). Messages are shown when their level is >= the current `logLevel`.
- Improved `request.js`: JSON detection through `Content-Type` with silent fallback for non-JSON responses.
- Updated documentation and offline demos. Fixed license documentation to GFDL 1.3, except for slides. See: <https://www.gnu.org/licenses/fdl-1.3.en.html> for details.
- Added an "extra" JS package for slides. Currently proposed as a PoC.


## Version 2.1 - stable

Increased accessibility and corrected bugs.

