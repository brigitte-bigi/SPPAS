// Bundle automatically generated on 2026-03-29 10:24:31

// ---------------- logger.js ---------------
class WexaLogger {
    static #logLevel = 20;
    static getLogLevel() {
        return this.#logLevel;
    }
    static setLogLevel(level) {
        if (typeof level !== 'number' || level < 0 || level > 50) {
            console.warn('[WexaWarning] Invalid log level. Must be between 0 and 50.');
            return;
        }
        this.#logLevel = level;
    }
    static debug(msg) {
        if (this.#logLevel <= 10) console.info(`[WexaDebug] ${msg}`);
    }
    static info(msg) {
        if (this.#logLevel <= 20) console.info(`[WexaInfo] ${msg}`);
    }
    static warn(msg) {
        if (this.#logLevel <= 30) console.warn(`[WexaWarning] ${msg}`);
    }
    static error(msg, err) {
        if (this.#logLevel <= 40) console.error(`[WexaError] ${msg}`, err || '');
    }
    static critical(msg, err) {
        console.error(`[WexaCritical] ${msg}`, err || '');
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.WexaLogger = WexaLogger;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- transport/request.js ---------------
class RequestManager {
    // FIELDS
    // The declaration outside the constructor and the '#' symbol notify a private attribute.
    #protocol;
    #port;
    #url;
    #status;
    maxFileSize;
    // CONSTRUCTOR
    constructor() {
        this.#protocol = window.location.protocol;
        this.#port = window.location.port;
        this.#url = this.#protocol + "//" + window.location.hostname + ":" + this.#port + "/";
        this.#status = null;
        this.maxFileSize = 0;  // No upload file size limit
    }
    // ----------------------------------------------------------------------
    // GETTERS
    // ----------------------------------------------------------------------
    get protocol() {
        return this.#protocol;
    }
    // ----------------------------------------------------------------------
    get port() {
        return this.#port;
    }
    // ----------------------------------------------------------------------
    get request_url() {
        return this.#url;
    }
    // ----------------------------------------------------------------------
    get status() {
        return this.#status;
    }
    // ----------------------------------------------------------------------
    // METHODS
    // ----------------------------------------------------------------------
    async send_get_request(uri = "", is_json_response = false) {
        const complete_url = this.request_url + uri;
        let request_response_data = null;
        // send request to the server
        await fetch(complete_url)
            // then gets content of the server response
            .then(async response =>  {
                // get the status response and check if there is an error
                this.#status = response.status;
                // get the content of the server response and parse them if it's a json format
                if (is_json_response) {
                    const text = await response.text();
                    if (text.trim() === '') {
                        request_response_data = {};   // JSON vide → objet vide
                    } else {
                        try {
                            request_response_data = JSON.parse(text);
                        } catch (error) {
                            console.error('Failed to parse JSON response', error);
                            request_response_data = {
                                status: response.status,
                                error: 'Failed to parse JSON.',
                                raw: text
                            };
                        }
                    }
                } else {
                    request_response_data = await response.text();
                }
            })
            // handle error
            .catch(error => {
                this.#status = error.status;
                request_response_data = error;
            });
        return request_response_data;
    }
    // ----------------------------------------------------------------------
    async send_post_request(post_parameters, accept_type = "application/json", uri = "") {
		const complete_url = this.request_url + uri;
        let request_response_data = null;
        // build request header and body depending on parameter passed to the method
        post_parameters = JSON.stringify(post_parameters);
        let request_header = {
            'Accept': accept_type,
            'Content-Type': "application/json; charset=utf-8",
            'Content-Length': post_parameters.length.toString()
        }
        // send request to the server
        await fetch(complete_url, {
            method: "POST",
            headers: request_header,
            body: post_parameters
        })
            // then gets content of the server response
            .then(async response =>  {
                // get the status response and check if there is an error
                this.#status = response.status;
                if (accept_type.includes("application/json")) {
                    const text = await response.text();
                    if (text.trim() === '') {
                        request_response_data = {};
                    } else {
                        try {
                            request_response_data = JSON.parse(text);
                        } catch (error) {
                            if (!response.headers.get('Content-Type')?.includes('application/json')) {
                                // No backend available: ignore silently
                                return {};
                            } else {
                                console.error("Failed to parse JSON response: " + error);
                                request_response_data = {
                                    status: response.status,
                                    error: "Failed to parse JSON. See error details in the newly opened tab.",
                                    html: text
                                };
                                this.openErrorTab(text);
                            }
                        }
                    }
                }
                // Handle HTML responses (e.g., error pages)
                else if (accept_type.includes("text/html")) {
                    // If response is HTML, treat it as a failed request (500 error or other)
                    const responseText = await response.text();
                    request_response_data = {
                        status: response.status,
                        error: "Received HTML instead of JSON. See error details in the newly opened tab.",
                        html: responseText
                    };
                    // Open a new tab to display the HTML error content
                    this.openErrorTab(responseText);
                }
                else {
                    request_response_data = await response.blob();
                }
            })
            // handle error
            .catch(error => {
                this.#status = error.status;
                request_response_data = error;
            })
        ;
        return request_response_data;
    }
    // ----------------------------------------------------------------------
    openErrorTab(responseText) {
        // Optionally open a new tab to display the HTML error content
        const errorTab = window.open();
        if (errorTab) {
            errorTab.document.open();
            errorTab.document.write(responseText);
            errorTab.document.close();
        } else {
            console.error("Failed to open a new tab for the error page.");
        }
    }
    // ----------------------------------------------------------------------
    async upload_file(input, accept_type = "application/json", token = "", uri = "") {
        let response_data = null;
        const complete_url = this.request_url + uri;
        this.#status = 400;
        // Exit the function if no file is selected
        if (!input || !input.files || !input.files[0]) {
            console.warn("No file selected for upload.");
            // Return a JSON object with status 400 and an error message
            return { error: "No file or empty file selected for upload." };
        }
        console.debug("Defined size limit: ", this.maxFileSize);
        console.debug("File size to upload: ", input.files[0].size);
        // Exit the function if size limit
        if (this.maxFileSize !== 0 && input.files[0].size > this.maxFileSize) {
            console.error("File size exceeds maximum of ${this.maxFileSize} bytes.");
            // Return a JSON object with status 400 and an error message
            return { error: "File size exceeds maximum allowed length." };
        }
        // Create a new File instance, with the sanitized filename (no diacritics)
        let sanitizedFileName = input.files[0].name.normalize('NFD').replace(/[\u0300-\u036f]/g, "");
        let sanitizedFile = new File([input.files[0]], sanitizedFileName, {
            type: input.files[0].type,
            lastModified: input.files[0].lastModified,
        });
        // Format file to upload to the server
        let data = new FormData();
        data.append('file', sanitizedFile);
        // Send request to the back-end and wait for the response (response in json)
        await fetch(complete_url, {
            method: 'POST',
            headers: {
                'Accept': accept_type,
                'X-Auth-Token': 'Bearer ' + token
            },
            body: data
        })
        // get the response and update the current status code
        .then(async response => {
            console.debug(" ... server answer: ", response);
            this.#status = response.status;
            // Check if the status is not 200 and there is no error in the response
            if (response.status !== 200 && !response.error) {
                // Return a JSON object with statusText to indicate the error
                response_data = { "error": response.statusText };
            } else {
                // If status is 200 or there is an error, return the JSON response
                response_data = await response.json();
            }
        })
        // handle error
        .catch(error => {
            console.error(" ... server error: ", error);
            this.#status = error.status;
            response_data = error;
        })
        return response_data;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.RequestManager = RequestManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- transport/base_manager.js ---------------
'use strict';
class BaseManager {
    // ----------------------------------------------------------------------
    // Private members shared by all classes
    // ----------------------------------------------------------------------
    // An instance of the RequestManager class responsible for managing HTTP requests.
    _requestManager;
    // A string representing the current URL path, extracted from the window location.
    _uri;
    // ----------------------------------------------------------------------
    // Constructor
    // ----------------------------------------------------------------------
    constructor() {
        this._requestManager = new RequestManager();
        let url = new URL(window.location.href);
        this._uri = url.pathname.substring(1);
        this._dialog = new DialogManager();
    }
    // ----------------------------------------------------------------------
    _showActionResult(error = "", info = "", reload = true) {
        if (this._requestManager.status !== 200) {
            WexaLogger.error(`HTTP error ${this._requestManager.status}: ${error}`);
            this._showDialog('error_dialog', `Erreur ${this._requestManager.status} : ${error}`);
        } else {
            if (info) {
                WexaLogger.info(info);
                this._showDialog('info_dialog', info);
            }
            if (reload) {
                window.location.reload();
            }
        }
    }
    // ----------------------------------------------------------------------
    submitForm(inputName, inputValue) {
            const form = document.createElement('form');
            form.method = 'POST';
            form.style.display = 'none';
            const input = document.createElement('input');
            input.name = inputName;
            input.value = inputValue;
            input.type = 'hidden';
            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
            // Clean the DOM
            document.body.removeChild(form);
    }
    // ----------------------------------------------------------------------
    async postEvents(events) {
        let response;
        let respError= "";
        let respInfo = "";
        try {
            response = await this._requestManager.send_post_request(
                events,
                'application/json',
                this._uri
            );
            WexaLogger.debug(`HTTP status ${this._requestManager.status}`);
            // If there's a message in the response
            respError = response.error || "";
            respInfo = response.info || "";
        } catch (error) {
            // Do not handle any request or network error: it's probably a standard server, not a WhakerPy one!
            // respError = error.toString();
            // No backend available: ignore silently
            return;
        }
        // Server replied: process normally
        if (respError || respInfo) {
            this._showActionResult(respError, '', true);
            return;
        }
        // No server response: ignore silently
        if (!response) {
            return;
        }
        // Return the response if no message sent
        return response;
    }
    // ----------------------------------------------------------------------
    _showDialog = (dialogId, message) => {
        let dlg = document.getElementById(dialogId);
        if (dlg != null) {
            dlg.innerHTML = `<p>${message}</p>`;
            this._dialog.open(dialogId);
        } else {
            alert(message);
        }
    }
    // ----------------------------------------------------------------------
    _hideDialog = (dialogId) => {
        let dlg = document.getElementById(dialogId);
        if (dlg != null) {
            dlg.innerHTML = ``;
            this._dialog.close(dialogId);
        } else {
            WexaLogger.warn(`No such dialog ${dialogId}`);
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.BaseManager = BaseManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/visibility.js ---------------
'use strict';
class SlidesVisibilityController {
    constructor(element) {
        this._element = element instanceof HTMLElement ? element : null;
    }
    show() {
        if (this._element instanceof HTMLElement) {
            this._element.style.display = 'block';
        }
    }
    hide() {
        if (this._element instanceof HTMLElement) {
            this._element.style.display = 'none';
        }
    }
    toggle() {
        if (!(this._element instanceof HTMLElement)) {
            return;
        }
        const current = this._element.style.display;
        if (current === 'none') {
            this._element.style.display = 'block';
        } else {
            this._element.style.display = 'none';
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesVisibilityController = SlidesVisibilityController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/visibility_manager.js ---------------
'use strict';
class SlidesVisibilityManager {
    constructor(elementsMap = {}) {
        this._controllers = {};
        const names = Object.keys(elementsMap);
        for (const name of names) {
            const element = elementsMap[name];
            this._controllers[name] = new SlidesVisibilityController(element);
        }
    }
    show(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.show();
        }
    }
    hide(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.hide();
        }
    }
    toggle(name) {
        const controller = this._controllers[name];
        if (controller instanceof SlidesVisibilityController) {
            controller.toggle();
        }
    }
    showAll() {
        const names = Object.keys(this._controllers);
        for (const name of names) {
            this._controllers[name].show();
        }
    }
    hideAll() {
        const names = Object.keys(this._controllers);
        for (const name of names) {
            this._controllers[name].hide();
        }
    }
    getNames() {
        return Object.keys(this._controllers);
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesVisibilityManager = SlidesVisibilityManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/focus.js ---------------
'use strict';
class SlidesFocusController {
    constructor(options = {}) {
        const defaultSelector = [
            'a[href]',
            'button',
            'input',
            'select',
            'textarea',
            'details',
            'summary',
            '[tabindex]:not([tabindex="-1"])',
            '[contenteditable="true"]',
            'video[controls]',
            'audio[controls]'
        ].join(', ');
        this._focusableSelector = typeof options.focusableSelector === 'string'
            ? options.focusableSelector
            : defaultSelector;
    }
    updateFocus(slides, activeIndex) {
        if (!Array.isArray(slides) || slides.length === 0) {
            console.warn("Update focus not available. No slides found.");
            return;
        }
        let safeIndex = activeIndex;
        if (safeIndex < 1) {
            safeIndex = 1;
        }
        if (safeIndex > slides.length) {
            safeIndex = slides.length;
        }
        const activeSlide = slides[safeIndex - 1];
        slides.forEach((slide) => {
            const isActive = slide === activeSlide;
            const tabIndexValue = isActive === true ? 0 : -1;
            this._setTabIndexForSlide(slide, tabIndexValue);
        });
    }
    // -----------------------------------------------------------------------
    // Private utilities
    // -----------------------------------------------------------------------
    _setTabIndexForSlide(slide, tabIndexValue) {
        if (!(slide instanceof HTMLElement)) {
            return;
        }
        const elements = this._getFocusableElements(slide);
        const valueString = String(tabIndexValue);
        elements.forEach((element) => {
            const disabled = this._isDisabled(element);
            if (disabled === true) {
                return;
            }
            element.setAttribute('tabindex', valueString);
        });
    }
    _getFocusableElements(slide) {
        if (!(slide instanceof HTMLElement)) {
            return [];
        }
        const nodeList = slide.querySelectorAll(this._focusableSelector);
        return Array.from(nodeList);
    }
    _isDisabled(element) {
        if (!(element instanceof HTMLElement)) {
            return true;
        }
        const hasDisabledAttribute = element.hasAttribute('disabled');
        if (hasDisabledAttribute === true) {
            return true;
        }
        const ariaDisabled = element.getAttribute('aria-disabled');
        if (ariaDisabled !== null && ariaDisabled.toLowerCase() === 'true') {
            return true;
        }
        /*
        const tabIndexAttribute = element.getAttribute('tabindex');
        if (tabIndexAttribute !== null) {
            const parsed = parseInt(tabIndexAttribute, 10);
            const isNumber = Number.isNaN(parsed) === false;
            if (isNumber === true && parsed < 0) {
                return true;
            }
        }*/
        return false;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesFocusController = SlidesFocusController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/fullscreen.js ---------------
'use strict';
class SlidesFullscreenController {
    constructor(target = null) {
        const defaultTarget = typeof document !== 'undefined'
            ? document.documentElement
            : null;
        this._target = target instanceof HTMLElement ? target : defaultTarget;
    }
    enter() {
        if (this._target === null) {
            return;
        }
        const request = this._target.requestFullscreen
            || this._target.requestFullScreen
            || this._target.mozRequestFullScreen
            || this._target.webkitRequestFullScreen
            || null;
        if (typeof request === 'function') {
            request.call(this._target);
        }
    }
    exit() {
        if (typeof document === 'undefined') {
            return;
        }
        const exitMethod = document.exitFullscreen
            || document.cancelFullScreen
            || document.mozCancelFullScreen
            || document.webkitCancelFullScreen
            || null;
        if (typeof exitMethod === 'function') {
            exitMethod.call(document);
        }
    }
    toggle() {
        if (typeof document === 'undefined') {
            return;
        }
        const activeElement = document.fullscreenElement
            || document.mozFullScreenElement
            || document.webkitFullscreenElement
            || null;
        if (activeElement === null) {
            this.enter();
        } else {
            this.exit();
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesFullscreenController = SlidesFullscreenController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/keyboard.js ---------------
'use strict';
class SlidesKeyboardController {
    static SLIDE_KEYS = new Set([
        'Escape',  // Switch to Presentation mode
        'o', 'O',  // Switch to Overview mode
        's', 'S',  // Switch to Presentation mode
        'f', 'F',  // Enable/Disable Fullscreen
        'n', 'N',  // Show/Hide controls
        'b', 'B',  // Show/Hide progress bar
        'l', 'L',  // Show/Hide logo
        'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',  // Browse slides
        'PageUp', 'PageDown',
        'Home', 'End'
    ]);
    // ----------------------------------------------------------------------
    // CONSTRUCTOR
    // ----------------------------------------------------------------------
    constructor(slidesManager, options = {}) {
        if (typeof slidesManager !== 'object' || slidesManager === null) {
            throw new Error('SlidesKeyboardController: "slidesManager" must be an object.');
        }
        this._manager = slidesManager;
        this._boundKeyHandler = this._onKeyDown.bind(this);
    }
    // ----------------------------------------------------------------------
    // INITIALIZATION
    // ----------------------------------------------------------------------
    init() {
        document.body.addEventListener('keydown', this._boundKeyHandler, false);
    }
    destroy() {
        document.body.removeEventListener('keydown', this._boundKeyHandler, false);
    }
    // ---------------------------------------------------------------------
    // PRIVATE — ACCESSIBILITY-FIRST KEYBOARD HANDLING
    // ---------------------------------------------------------------------
    _onKeyDown(event) {
        const key = event.key;
        // --- RULE 1: Ignore all keys not part of the Slides UI ----------------
        if (!SlidesKeyboardController.SLIDE_KEYS.has(key)) {
            return;
        }
        // --- RULE 2: Never handle Enter or Space ------------------------------
        // Space is " " (U+0020)
        if (key === 'Enter' || key === ' ') {
            return;
        }
        // --- RULE 3: If focus is on an interactive element → browser priority -
        if (this._isInteractiveTarget(event.target)) {
            return;
        }
        // ----------------------------------------------------------------------
        // From here, we know safely:
        //  - The key is a slide key
        //  - It is not Enter/Space
        //  - The focused element is *not* interactive
        // ----------------------------------------------------------------------
        switch (key) {
            case 'Escape':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.DEFAULT_MODE);
                }
                return;
            case 'o': case 'O':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.MODES.OVERVIEW);
                }
                return;
            case 's': case 'S':
                if (this._manager.viewModeManager !== null) {
                    this._manager.viewModeManager.set(SlidesView.MODES.PRESENTATION);
                }
                return;
            case 'f': case 'F':
                this._manager.toggleFullscreen?.();
                return;
            case 'n': case 'N':
                if (this._manager.visibilityManager !== null) {
                    this._manager.visibilityManager.toggle('controls');
                }
                return;
            case 'l': case 'L':
                if (this._manager.visibilityManager !== null) {
                    //this._manager.visibilityManager.toggle('logo');
                }
                return;
            case 'b': case 'B':
                if (this._manager.visibilityManager !== null) {
                    //this._manager.visibilityManager.toggle('progress');
                }
                return;
            // Navigation backward
            case 'ArrowLeft':
            case 'ArrowUp':
            case 'PageUp':
                event.preventDefault();
                this._manager.prev();
                return;
            // Navigation forward
            case 'ArrowRight':
            case 'ArrowDown':
            case 'PageDown':
                event.preventDefault();
                this._manager.next();
                return;
            case 'Home':
                event.preventDefault();
                this._manager.goStart();
                return;
            case 'End':
                event.preventDefault();
                this._manager.goEnd();
                return;
            default:
                return;
        }
    }
    // ----------------------------------------------------------------------
    _isInteractiveTarget(target) {
        if (!(target instanceof HTMLElement)) {
            return true;
        }
        const tag = target.tagName.toLowerCase();
        // Native interactive elements
        if (tag === 'input' ||
            tag === 'select' ||
            tag === 'textarea' ||
            tag === 'button' ||
            tag === 'summary') {
            return true;
        }
        // Links
        if (tag === 'a' && target.hasAttribute('href')) {
            return true;
        }
        // Media controls
        if ((tag === 'video' || tag === 'audio') && target.hasAttribute('controls')) {
            return true;
        }
        // Any element with tabindex >= 0 is interactive
        const tab = target.getAttribute('tabindex');
        if (tab !== null) {
            const n = parseInt(tab, 10);
            if (!Number.isNaN(n) && n >= 0) {
                return true;
            }
        }
        return false;
    }
    // ---------------------------------------------------------------------
    // Utils
    // ---------------------------------------------------------------------
    _elementOrNull(element) {
        return element instanceof HTMLElement ? element : null;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesKeyboardController = SlidesKeyboardController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/overview.js ---------------
'use strict';
class SlidesOverview {
    constructor(slides, panelElement, onSelectSlide) {
        this._slides = Array.isArray(slides) ? slides : [];
        this._panel = panelElement instanceof HTMLElement ? panelElement : null;
        this._onSelectSlide = (typeof onSelectSlide === 'function') ? onSelectSlide : null;
        if (this._panel !== null) {
            this._panel.style.display = 'none'; // hidden by default
        }
    }
    // -------------------------------------------------------------------------
    //  Public API
    // -------------------------------------------------------------------------
    build() {
        if (this._panel === null) {
            return;
        }
        this._panel.innerHTML = '';
        const total = this._slides.length;
        for (let i = 0; i < total; i++) {
            const slide = this._slides[i];
            const index = i + 1;
            // Create the <article> container.
            const article = document.createElement('article');
            article.className = 'overview-item';
            // Header: slide number.
            const header = document.createElement('header');
            header.textContent = String(index);
            article.appendChild(header);
            // Main: clone of the slide.
            const main = document.createElement('main');
            // only the content, not the section container
            const fragment = document.createRange().createContextualFragment(slide.innerHTML);
            main.appendChild(fragment);
            article.appendChild(main);
            // Footer: GoTo button.
            const footer = document.createElement('footer');
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = 'GoTo';
            btn.addEventListener('click', () => {
                if (typeof this._onSelectSlide === 'function') {
                    this._onSelectSlide(index);
                }
                this.hide();
            });
            footer.appendChild(btn);
            article.appendChild(footer);
            this._panel.appendChild(article);
        }
    }
    // ----------------------------------------------------------------------
    show() {
        if (this._panel !== null) {
            this._panel.style.display = 'block';
        }
    }
    // ----------------------------------------------------------------------
    hide() {
        if (this._panel !== null) {
            this._panel.style.display = 'none';
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesOverview = SlidesOverview;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/presentation.js ---------------
'use strict';
class SlidesPresentation {
    constructor(slides, progressBar = null, controlsElement = null) {
        this._slides = Array.isArray(slides) ? slides : [];
        this._progressBar = progressBar;
        this._controls = controlsElement;
    }
    // -------------------------------------------------------------------------
    //  Public API
    // -------------------------------------------------------------------------
    renderSlide(newIndex, oldIndex) {
        const total = this._slides.length;
        if (oldIndex >= 1 && oldIndex <= total) {
            const prev = this._slides[oldIndex - 1];
            if (prev instanceof HTMLElement) {
                prev.removeAttribute('aria-selected');
            }
        }
        if (newIndex >= 1 && newIndex <= total) {
            const curr = this._slides[newIndex - 1];
            if (curr instanceof HTMLElement) {
                curr.setAttribute('aria-selected', 'true');
            }
        }
    }
    // -------------------------------------------------------------------------
    renderIncremental(currentIndex, step) {
        const slide = this._getSlide(currentIndex);
        if (slide === null) {
            return;
        }
        const containers = slide.querySelectorAll('.incremental');
        containers.forEach(c => this._clearIncrementals(c));
        if (step === 0) {
            return;
        }
        const items = slide.querySelectorAll('.incremental > *');
        const totalItems = items.length;
        if (totalItems === 0 || step > totalItems) {
            return;
        }
        const target = items[step - 1];
        const parent = target.parentElement;
        if (parent instanceof HTMLElement) {
            parent.setAttribute('active', 'true');
        }
        target.setAttribute('aria-selected', 'true');
    }
    // -------------------------------------------------------------------------
    renderProgress(widthPercent) {
        if (this._progressBar instanceof HTMLElement) {
            this._progressBar.style.width = String(widthPercent) + '%';
        }
    }
    // -------------------------------------------------------------------------
    renderControls(visible) {
        if (this._controls instanceof HTMLElement) {
            this._controls.classList.toggle('controls-hidden', visible === false);
        }
    }
    // -------------------------------------------------------------------------
    showPresentation() {
        for (const slide of this._slides) {
            slide.style.display = 'block';
        }
    }
    // -------------------------------------------------------------------------
    hidePresentation() {
        for (const slide of this._slides) {
            slide.style.display = 'none';
        }
    }
    // -------------------------------------------------------------------------
    //  Private Helpers
    // -------------------------------------------------------------------------
    _getSlide(index) {
        if (index < 1 || index > this._slides.length) {
            return null;
        }
        return this._slides[index - 1];
    }
    // -------------------------------------------------------------------------
    _clearIncrementals(container) {
        if (!(container instanceof HTMLElement)) {
            return;
        }
        container.removeAttribute('active');
        const items = container.querySelectorAll('*');
        items.forEach(item => {
            item.removeAttribute('aria-selected');
        });
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesPresentation = SlidesPresentation;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/slides_view.js ---------------
'use strict';
class SlidesView {
    // ---------------------------------------------------------------------------
    // STATIC ENUM OF MODES
    // ---------------------------------------------------------------------------
    static MODES = {
        PRESENTATION: 'presentation',
        OVERVIEW: 'overview',
        //PRINT: 'print',
        //NOTES: 'notes'
    }
    static DEFAULT_MODE = SlidesView.MODES.PRESENTATION;
    // ---------------------------------------------------------------------------
    // CONSTRUCTOR
    // ---------------------------------------------------------------------------
    constructor(slides,
                progressBar = null,
                controlsElement = null,
                controlsViewElement  = null,
                overviewContainer = null) {
        this._slides = slides;
        // Sub-views
        this._presentation = new SlidesPresentation(
            slides,
            progressBar,
            controlsElement
        );
        this._controlsView = controlsViewElement instanceof HTMLElement ? controlsViewElement : null;
        this._controls = controlsElement instanceof HTMLElement ? controlsElement : null;
        this._overviewContainer = overviewContainer instanceof HTMLElement ? overviewContainer : null;
        this._overview = null;
        this._viewMode = SlidesView.MODES.PRESENTATION;
        // Callback for clicking a slide in the overview.
        this.onSelectSlide = null;
    }
    // -----------------------------------------------------------------------
    // INITIALIZATION
    // -----------------------------------------------------------------------
    initOverview(onSelectSlide) {
        if (this._overviewContainer !== null) {
            this._overview = new SlidesOverview(
                (
                    this._slides.map((slide) => slide.cloneNode(true))
                ),
                this._overviewContainer,
                onSelectSlide
            );
        }
    }
    buildOverview() {
        if (this._overview !== null) {
            this._overview.build();
        }
    }
    // ---------------------------------------------------------------------------
    // MODE SWITCHING
    // ---------------------------------------------------------------------------
    setMode(mode) {
        this._mode = mode;
        // Manage the body class="view" to enable the relevant CSS render class
        this._removeBodyView()
        document.body.classList.add(`${mode}-view`);
        // switch to the requested view [presentation by default]
        switch (mode) {
            case SlidesView.MODES.OVERVIEW:
                this._enterOverview();
                return;
            default:
                this._enterPresentation();
                return;
        }
    }
    get mode() {
        return this._mode;
    }
    // ---------------------------------------------------------------------------
    // RENDERING (CALLED ONLY BY SlidesManager)
    // ---------------------------------------------------------------------------
    renderSlide(newIndex, oldIndex) {
        // Presentation view update (always required)
        this._presentation.renderSlide(newIndex, oldIndex);
        /* Overview view update (safe no-op when inactive)
        if (typeof this._overview.renderSlide === 'function') {
            this._overview.renderSlide(newIndex, oldIndex);
        }*/
    }
    renderIncremental(index, step) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderIncremental(index, step);
        }
    }
    renderProgress(percent) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderProgress(percent);
        }
    }
    renderControls(visible) {
        if (this._mode === SlidesView.MODES.PRESENTATION) {
            this._presentation.renderControls(visible);
        }
        if (this._controlsView instanceof HTMLElement) {
            this._controlsView.classList.toggle('controls-hidden', visible === false);
        }
    }
    // ----------------------------------------------------------------------
    // PRIVATE: MODE ENTRY HANDLERS
    // ----------------------------------------------------------------------
    _enterPresentation() {
        if (this._overview !== null) {
            this._overview.hide();
        }
        this._presentation.showPresentation();
    }
    _enterOverview() {
        this._presentation.hidePresentation();
        if (this._overview !== null) {
            this._overview.show();
        }
    }
    _removeBodyView() {
        const modes = Object.values(SlidesView.MODES);
        modes.forEach(mode => {
            document.body.classList.remove(`${mode}-view`);
        });
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesView = SlidesView;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/slides_manager.js ---------------
'use strict';
class SlidesManager {
    // ----------------------------------------------------------------------
    // CONSTRUCTOR
    // ----------------------------------------------------------------------
    constructor(slides, options = {}, dependencies = {}) {
        // Slides validation
        // ------------------------------
        if (!Array.isArray(slides)) {
            console.error('SlidesManager: slides must be an array.');
            this._slides = [];
        } else {
            this._slides = slides;
        }
        if (this._slides.length === 0) {
            console.warn('SlidesManager: no slides found.');
        }
        // State
        // ------------------------------
        this._currentIndex = 1;  // 1-based
        this._currentStep = 0;
        this._autoPlayEnabled = Boolean(options.autoPlayEnabled);
        this._controlsVisible = Boolean(options.controlsVisible);
        // Dependencies
        // ------------------------------
        if (typeof dependencies.visibilityManager === 'object' && dependencies.visibilityManager !== null) {
            this.visibilityManager = dependencies.visibilityManager;
        } else {
            this.visibilityManager = null;
        }
        if (typeof dependencies.viewModeManager === 'object' && dependencies.viewModeManager !== null) {
            this.viewModeManager = dependencies.viewModeManager;
        } else {
            this.viewModeManager = null;
        }
        this._view =
            (typeof dependencies.view === 'object' && dependencies.view !== null)
                ? dependencies.view
                : null;
        this._fullscreen =
            (typeof dependencies.fullscreen === 'object' && dependencies.fullscreen !== null)
                ? dependencies.fullscreen
                : null;
        this._focusController =
            (typeof dependencies.focusController === 'object' &&
                dependencies.focusController !== null)
                ? dependencies.focusController
                : null;
    }
    // ----------------------------------------------------------------------
    // INITIALIZATION
    // ----------------------------------------------------------------------
    init() {
        // Clamp index (safety)
        if (this._slides.length === 0) {
            return;
        }
        // Apply default mode BEFORE any rendering (mandatory for hash)
        // this._view.setMode(this._view.DEFAULT_MODE);
        // Initial render
        this._view.renderSlide(this._currentIndex, 0);
        this._view.renderIncremental(this._currentIndex, this._currentStep);
        // Initial progress
        const pct = (this._currentIndex - 1) * 100 / (this._slides.length - 1);
        this._view.renderProgress(pct);
        // Controls visibility
        this._view.renderControls(this._controlsVisible);
    }
    // ----------------------------------------------------------------------
    //  Public API
    // ----------------------------------------------------------------------
    next() {
        const lastIndex = this._slides.length;
        const incrementalCount = this.getIncrementalCount(this._currentIndex);
        if (this._currentIndex === lastIndex && this._currentStep >= incrementalCount) {
            return;
        }
        if (this._currentStep >= incrementalCount) {
            this.goTo(this._currentIndex + 1, 0);
        } else {
            this.goTo(this._currentIndex, this._currentStep + 1);
        }
    }
    // ----------------------------------------------------------------------
    prev() {
        const atFirstSlide = this._currentIndex === 1 && this._currentStep === 0;
        if (atFirstSlide === true) {
            return;
        }
        if (this._currentStep === 0) {
            const previousIndex = this._currentIndex - 1;
            const lastStep = this.getIncrementalCount(previousIndex);
            this.goTo(previousIndex, lastStep);
        } else {
            this.goTo(this._currentIndex, this._currentStep - 1);
        }
    }
    // ----------------------------------------------------------------------
    goTo(index, step = 0) {
        const previousIndex = this._currentIndex;
        const previousStep = this._currentStep;
        const clampedIndex = this._clampIndex(index);
        const clampedStep = this._clampStep(clampedIndex, step);
        if (clampedIndex === previousIndex && clampedStep === previousStep) {
            return;
        }
        const previousSlide = this.getActiveSlide();
        if (previousSlide !== null) {
            this._pauseVideo(previousSlide);
        }
        this._currentIndex = clampedIndex;
        this._currentStep = clampedStep;
        const currentSlide = this.getActiveSlide();
        if (currentSlide !== null) {
            this._autoplayVideo(currentSlide);
        }
        if (typeof window !== 'undefined') {
            const hashValue = '#' + String(this._currentIndex) + '.' + String(this._currentStep);
            window.location.hash = hashValue;
        }
        this._notifyAll(previousIndex, previousStep);
        if (this._focusController !== null) {
            this._focusController.updateFocus(this._slides, this._currentIndex);
        }
    }
    // ----------------------------------------------------------------------
    goStart() {
        this.goTo(1, 0);
    }
    // ----------------------------------------------------------------------
    goEnd() {
        const lastIndex = this._slides.length;
        const lastStep = this.getIncrementalCount(lastIndex);
        this.goTo(lastIndex, lastStep);
    }
    // ----------------------------------------------------------------------
    toggleContent() {
        const slide = this.getActiveSlide();
        if (slide === null) {
            return;
        }
        const video = this.getVideo(slide);
        if (video === null) {
            return;
        }
        if (video.ended === true || video.paused === true) {
            video.play();
        } else {
            video.pause();
        }
    }
    // ----------------------------------------------------------------------
    toggleFullscreen() {
        if (this._fullscreen) {
            this._fullscreen.toggle();
        } else {
            console.log("No fullscreen available.");
        }
    }
    // ----------------------------------------------------------------------
    updateFromHash(hash) {
        const previousIndex = this._currentIndex;
        const previousStep = this._currentStep;
        const isString = typeof hash === 'string';
        const isEmpty = hash === '';
        const startsWithHash = isString === true && hash.charAt(0) === '#';
        if (isString === false || isEmpty === true || startsWithHash === false) {
            this._currentIndex = this._clampIndex(1);
            this._currentStep = this._clampStep(this._currentIndex, 0);
            this._notifyAll(previousIndex, previousStep);
            return;
        }
        const cursor = hash.substring(1).split('.');
        const parsedIndex = parseInt(cursor[0], 10);
        const parsedStep = cursor.length > 1 ? parseInt(cursor[1], 10) : 0;
        const safeIndex = Number.isNaN(parsedIndex) ? 1 : parsedIndex;
        const safeStep = Number.isNaN(parsedStep) ? 0 : parsedStep;
        const clampedIndex = this._clampIndex(safeIndex);
        const clampedStep = this._clampStep(clampedIndex, safeStep);
        this._currentIndex = clampedIndex;
        this._currentStep = clampedStep;
        this._notifyAll(previousIndex, previousStep);
    }
    // ----------------------------------------------------------------------
    getActiveSlide() {
        const index = this._currentIndex;
        if (index < 1 || index > this._slides.length) {
            return null;
        }
        return this._slides[index - 1];
    }
    // ----------------------------------------------------------------------
    getIncrementalCount(index) {
        const slideIndex = typeof index === 'number' ? index : this._currentIndex;
        const clampedIndex = this._clampIndex(slideIndex);
        const slide = this._slides[clampedIndex - 1];
        if (!(slide instanceof HTMLElement)) {
            return 0;
        }
        const items = slide.querySelectorAll('.incremental > *');
        return items.length;
    }
    // ----------------------------------------------------------------------
    getVideo(slide) {
        const isElement = slide instanceof HTMLElement;
        if (isElement === false) {
            return null;
        }
        const video = slide.querySelector('video');
        const isVideo = video instanceof HTMLVideoElement;
        return isVideo === true ? video : null;
    }
    // ----------------------------------------------------------------------
    // PRIVATE
    // ----------------------------------------------------------------------
    _notifyAll(previousIndex, previousStep) {
        if (this._view !== null) {
            const hasRenderSlide = typeof this._view.renderSlide === 'function';
            const hasRenderIncremental = typeof this._view.renderIncremental === 'function';
            const hasUpdateProgress = typeof this._view.renderProgress === 'function';
            if (hasRenderSlide === true) {
                this._view.renderSlide(this._currentIndex, previousIndex);
            }
            if (hasRenderIncremental === true) {
                this._view.renderIncremental(this._currentIndex, this._currentStep);
            }
            if (hasUpdateProgress === true) {
                const totalSlides = this._slides.length - 1;
                const progressPercent = (this._currentIndex - 1) * 100 / totalSlides;
                this._view.renderProgress(progressPercent);
            }
        }
        const hasFocusController = this._focusController !== null;
        const hasUpdateFocus = hasFocusController === true
            && typeof this._focusController.updateFocus === 'function';
        if (hasUpdateFocus === true) {
            this._focusController.updateFocus(this._slides, this._currentIndex);
        }
    }
    // ----------------------------------------------------------------------
    _pauseVideo(slide) {
        const video = this.getVideo(slide);
        if (video !== null) {
            video.pause();
        }
    }
    // ----------------------------------------------------------------------
    _autoplayVideo(slide) {
        if (this._autoPlayEnabled === false) {
            return;
        }
        const video = this.getVideo(slide);
        if (video !== null) {
            video.play();
        }
    }
    // ----------------------------------------------------------------------
    _clampIndex(index) {
        if (index < 1) {
            return 1;
        }
        if (index > this._slides.length) {
            return this._slides.length;
        }
        return index;
    }
    // ----------------------------------------------------------------------
    _clampStep(index, step) {
        if (step < 0) {
            return 0;
        }
        const maxSteps = this.getIncrementalCount(index);
        if (this._slides.length === 0) {
            return 0;
        }
        if (step > maxSteps) {
            return maxSteps;
        }
        return step;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesManager = SlidesManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/touch.js ---------------
'use strict';
class SlidesTouchController {
    constructor(slidesManager, options = {}) {
        if (typeof slidesManager !== 'object' || slidesManager === null) {
            throw new Error('SlidesTouchController: "slidesManager" must be an object.');
        }
        this._manager = slidesManager;
        const target = options.target;
        this._target = target instanceof HTMLElement ? target : document.body;
        const threshold = options.threshold;
        this._threshold = typeof threshold === 'number' && threshold > 0 ? threshold : 100;
        this._tracking = false;
        this._originX = 0;
        this._onStart = this._touchStart.bind(this);
        this._onMove = this._touchMove.bind(this);
    }
    init() {
        this._target.addEventListener('touchstart', this._onStart, { passive: false });
        this._target.addEventListener('touchmove', this._onMove, { passive: false });
    }
    destroy() {
        this._target.removeEventListener('touchstart', this._onStart, false);
        this._target.removeEventListener('touchmove', this._onMove, false);
    }
    // ---------------------------------------------------------------------
    // Private methods
    // ---------------------------------------------------------------------
    _touchStart(event) {
        if (event.changedTouches.length === 0) {
            return;
        }
        event.preventDefault();
        this._tracking = true;
        this._originX = event.changedTouches[0].pageX;
    }
    _touchMove(event) {
        if (this._tracking === false) {
            return;
        }
        if (event.changedTouches.length === 0) {
            return;
        }
        const newX = event.changedTouches[0].pageX;
        const delta = this._originX - newX;
        if (delta > this._threshold) {
            this._tracking = false;
            this._manager.next();
            return;
        }
        if (delta < -this._threshold) {
            this._tracking = false;
            this._manager.prev();
            return;
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesTouchController = SlidesTouchController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/controls.js ---------------
'use strict';
class SlidesControlsController {
    constructor(manager, {
        prevButton = null,
        nextButton = null,
        backButton = null,
        lastButton = null,
        overviewButton = null,
        presentationButton = null,
        fullscreenButton = null,
        goToButton = null
    } = {}) {
        if (typeof manager !== 'object' || manager === null) {
            throw new Error('SlidesControlsController: "manager" must be an object.');
        }
        this._manager = manager;
        this._buttons = {
            prev: this._elementOrNull(prevButton),
            next: this._elementOrNull(nextButton),
            back: this._elementOrNull(backButton),
            last: this._elementOrNull(lastButton),
            overview: this._elementOrNull(overviewButton),
            presentation: this._elementOrNull(presentationButton),
            fullscreen: this._elementOrNull(fullscreenButton),
            goto: this._elementOrNull(goToButton)
        };
        this._bindEvents();
    }
    // ----------------------------------------------------------------------
    updateViewButtons(mode) {
        // Update the OVERVIEW button
        // Disable it only when the current mode *is* overview.
        if (this._buttons.overview instanceof HTMLElement) {
            if (mode === 'overview') {
                this._buttons.overview.setAttribute('disabled', '');
            } else {
                this._buttons.overview.removeAttribute('disabled');
            }
        }
        // Update the PRESENTATION button
        // Disable it only when the current mode *is* presentation.
        if (this._buttons.presentation instanceof HTMLElement) {
            if (mode === 'presentation') {
                this._buttons.presentation.setAttribute('disabled', '');
            } else {
                this._buttons.presentation.removeAttribute('disabled');
            }
        }
    }
    // ----------------------------------------------------------------------
    _bindEvents() {
        const b = this._buttons;
        if (b.prev !== null) {
            b.prev.addEventListener('click', () => {
                this._manager.prev();
            });
        }
        if (b.next !== null) {
            b.next.addEventListener('click', () => {
                this._manager.next();
            });
        }
        if (b.back !== null) {
            b.back.addEventListener('click', () => {
                this._manager.goStart();
            });
        }
        if (b.last !== null) {
            b.last.addEventListener('click', () => {
                this._manager.goEnd();
            });
        }
        if (b.goto !== null) {
            b.goto.addEventListener('click', () => {
                const index = window.prompt('Go to slide number: ');
                if (index !== null) {
                    // If currently in overview mode, switch to presentation first
                    if (this._manager._view?.mode === SlidesView.MODES.OVERVIEW) {
                        this._switchView(SlidesView.MODES.PRESENTATION);
                    }
                    this._manager.goTo(Number(index), 0);
                }
            });
        }
        if (b.overview !== null) {
            b.overview.addEventListener('click', () => {
                this._switchView(SlidesView.MODES.OVERVIEW);
            });
        }
        if (b.presentation !== null) {
            b.presentation.addEventListener('click', () => {
                this._switchView(SlidesView.MODES.PRESENTATION);
            });
        }
        if (b.fullscreen !== null) {
            b.fullscreen.addEventListener('click', () => {
                if (this._manager._fullscreen &&
                    typeof this._manager._fullscreen.toggle === 'function') {
                    this._manager._fullscreen.toggle();
                }
            });
        }
    }
    // ----------------------------------------------------------------------
    disableAll() {
        for (const key in this._buttons) {
            if (!Object.prototype.hasOwnProperty.call(this._buttons, key)) {
                continue;
            }
            const btn = this._buttons[key];
            if (btn instanceof HTMLElement) {
                btn.setAttribute('disabled', '');
            }
        }
    }
    // ----------------------------------------------------------------------
    enable(feature) {
        if (typeof feature !== 'string') {
            return;
        }
        const btn = this._buttons[feature];
        if (btn instanceof HTMLElement) {
            btn.removeAttribute('disabled');
        }
    }
    // ----------------------------------------------------------------------
    _switchView(viewMode) {
        if (this._manager.viewModeManager !== null &&
            typeof this._manager.viewModeManager.set === 'function') {
            this._manager.viewModeManager.set(viewMode);
        }
    }
    // ----------------------------------------------------------------------
    _elementOrNull(element) {
        return element instanceof HTMLElement ? element : null;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesControlsController = SlidesControlsController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/modeview.js ---------------
'use strict';
class SlidesViewModeManager {
    constructor(slidesView, controlsController) {
        if (typeof slidesView === 'object' && slidesView !== null) {
            this._slidesView = slidesView;
        } else {
            this._slidesView = null;
        }
        if (typeof controlsController === 'object' && controlsController !== null) {
            this._controlsController = controlsController;
        } else {
            this._controlsController = null;
        }
        this._mode = null;
    }
    set(mode) {
        this._mode = mode;
        if (this._slidesView !== null &&
            typeof this._slidesView.setMode === 'function') {
            this._slidesView.setMode(mode);
        }
        if (this._controlsController !== null &&
            typeof this._controlsController.updateViewButtons === 'function') {
            this._controlsController.updateViewButtons(mode);
        }
    }
    get() {
        return this._mode;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesViewModeManager = SlidesViewModeManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/slides_app.js ---------------
'use strict';
class SlidesApp {
    // ----------------------------------------------------------------------
    // CONSTRUCTOR
    // ----------------------------------------------------------------------
    constructor(config) {
        // ****** VIEWS ******
        // -------------------
        this._view = new SlidesView(
            config.slides,
            config.progressBar,
            config.controls,
            config.controlsView,
            config.overviewContainer
        );
        // ****** CONTROLLERS ******
        // -------------------------
        this._fullscreen = new SlidesFullscreenController();
        this._focusController = new SlidesFocusController();
        // ****** MANAGERS ******
        // -------------------------
        this._visibilityManager = new SlidesVisibilityManager({
            controls: config.controls instanceof HTMLElement ? config.controls : null
        });
        this._manager = new SlidesManager(
            config.slides,
            {
                autoPlayEnabled: false,
                controlsVisible: true
            },
            { // dependencies
                view: this._view,
                fullscreen: this._fullscreen,
                focusController: this._focusController,
                visibilityManager: this._visibilityManager
            }
        );
        this._touch = new SlidesTouchController(this._manager);
        this._keyboard = new SlidesKeyboardController(this._manager);
        this._controls = new SlidesControlsController(
            this._manager,
            {
                prevButton: config.controls?.querySelector('#btn-prev') || null,
                nextButton: config.controls?.querySelector('#btn-next') || null,
                backButton: config.controls?.querySelector('#btn-back') || null,
                lastButton:  config.controls?.querySelector('#btn-last')  || null,
                goToButton: config.controls?.querySelector('#btn-goto') || null,
                overviewButton: config.controlsView?.querySelector('#btn-overview')  || null,
                presentationButton: config.controlsView?.querySelector('#btn-presentation')  || null,
                fullscreenButton: config.controls?.querySelector('#btn-fullscreen')|| null
            }
        );
        // ********** VIEWS INITIALIZATIONS *********
        // ------------------------------------------
        // MVC: View emits → Manager handles
        this._view.onSelectSlide = (index) => {
            this._manager.goTo(index, 0);
        };
        // Normalize initial mode safely
        this._initialViewMode = SlidesView.MODES.PRESENTATION;
        if (typeof config.mode === 'string') {
            const values = Object.values(SlidesView.MODES);
            if (values.includes(config.mode)) {
                this._initialViewMode = config.mode;
            }
        }
        // Initialize overview only if an overview container is provided
        if (this._view && config.overviewContainer) {
            this._view.initOverview((index) => this._manager.goTo(index, 0));
        }
        // ***** VIEW !!! ******
        this._viewModeManager = new SlidesViewModeManager(this._view, this._controls);
        this._manager.viewModeManager = this._viewModeManager;
        this._manager.updateFromHash(window.location.hash);
        window.addEventListener('hashchange', () => {
            this._manager.updateFromHash(window.location.hash);
        });
    }
    // ----------------------------------------------------------------------
    // INITIALIZATION
    // ----------------------------------------------------------------------
    init() {
        this._view.buildOverview();
        this._view.setMode(this._initialViewMode);
        this._viewModeManager.set(this._initialViewMode);
        this._manager.init();
        this._keyboard.init();
        this._touch.init();
    }
    // ----------------------------------------------------------------------
    //  Public API
    // ----------------------------------------------------------------------
    get manager() {
        return this._manager;
    }
    get keyboard() {
        return this._keyboard;
    }
    get touch() {
        return this._touch;
    }
    get fullscreen() {
        return this._fullscreen;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SlidesApp = SlidesApp;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- extras/slides/slides.js ---------------
'use strict';
class Slides {
    constructor(config = {}) {
        // --- Normalize configuration -----------------------------------------
        // We guarantee that "slides" is ALWAYS a true Array.
        // If user gives a NodeList, we convert it.
        // If user gives null/undefined, we use an empty Array.
        // Internal classes never need to question it.
        // ---------------------------------------------------------------------
        let slidesArray = [];
        if (Array.isArray(config.slides)) {
            slidesArray = config.slides;
        } else if (config.slides && typeof config.slides.length === 'number') {
            // NodeList or HTMLCollection
            slidesArray = Array.from(config.slides);
        } else {
            console.error('Slides: "slides" was not a valid list. Using [].');
            slidesArray = [];
        }
        const cleanedConfig = {
            ...config,
            slides: slidesArray
        };
        // --- Instantiate the internal application -----------------------------
        this._app = new SlidesApp(cleanedConfig);
    }
    init() {
        this._app.init();
    }
    get manager() {
        return this._app.manager;
    }
    get fullscreen() {
        return this._app.fullscreen;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.Slides = Slides;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- dom-loader.js ---------------
class OnLoadManager {
    // FIELDS
    static #functions = [];
    // PUBLIC STATIC METHODS
    static addLoadFunction(func) {
        OnLoadManager.#functions.push(func);
    }
    static runLoadFunctions() {
        OnLoadManager.#functions.forEach(async func => {
            await func();
        });
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.OnLoadManager = OnLoadManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- accessibility.js ---------------
class AccessibilityManager extends BaseManager {
    // -----------------------------------------------------------------------
    // FIELDS
    // -----------------------------------------------------------------------
    #colors;
    #activated_color;
    #contrasts;
    #activated_contrast;
    // -----------------------------------------------------------------------
    // CONSTRUCTOR
    // -----------------------------------------------------------------------
    constructor() {
        super();
        this.#colors = ["dark"];
        this.#activated_color = "";
        this.#contrasts = ["contrast"];
        this.#activated_contrast = "";
        // add onload events
        OnLoadManager.addLoadFunction(this.#loadBodyClasses.bind(this));
        OnLoadManager.addLoadFunction(this.#setAllLinksCustom.bind(this));
        OnLoadManager.addLoadFunction(this.#setSubmitCustom.bind(this));
    }
    // -----------------------------------------------------------------------
    // GETTERS
    // -----------------------------------------------------------------------
    get colorSchemes() {
        return this.#colors;
    }
    // -----------------------------------------------------------------------
    get activatedColorScheme() {
        return this.#activated_color;
    }
    // -----------------------------------------------------------------------
    get contrastSchemes() {
        return this.#contrasts;
    }
    // -----------------------------------------------------------------------
    get activatedContrastScheme() {
        return this.#activated_contrast;
    }
    // -----------------------------------------------------------------------
    // SETTERS
    // -----------------------------------------------------------------------
    addColorScheme(colorScheme) {
        if (typeof colorScheme === 'string') {
            this.#colors.push(colorScheme);
        } else {
            console.log("The 'colorScheme' parameter must be a string, not a: " + typeof colorScheme);
        }
    }
    // -----------------------------------------------------------------------
    removeColorScheme(colorScheme) {
        if (typeof colorScheme !== 'string') {
            console.log("The 'colorScheme' parameter must be a string, not a: " + typeof colorScheme);
        }
        const colorIndex = this.#colors.indexOf(colorScheme);
        if (colorIndex === -1) {
            console.log("The color scheme '" + colorScheme + "' does not exist!");
        } else {
            this.#colors.splice(colorIndex, 1);
        }
    }
    // -----------------------------------------------------------------------
    addContrastScheme(contrastScheme) {
        if (typeof contrastScheme === 'string') {
            this.#contrasts.push(contrastScheme);
        } else {
            console.log("The 'contrastScheme' parameter must be a string, not a: " + typeof contrastScheme);
        }
    }
    // -----------------------------------------------------------------------
    removeContrastScheme(contrastScheme) {
        if (typeof contrastScheme !== 'string') {
            console.log("The 'contrastScheme' parameter must be a string, not a: " + typeof contrastScheme);
        }
        const contrastIndex = this.#contrasts.indexOf(contrastScheme);
        if (contrastIndex === -1) {
            console.log("The contrast scheme '" + contrastScheme + "' does not exist!");
        } else {
            this.#contrasts.splice(contrastIndex, 1);
        }
    }
    // -----------------------------------------------------------------------
    // PUBLIC STATIC METHODS
    // -----------------------------------------------------------------------
    static get COLOR_PARAMETER_NAME() {
        return "wexa_color";
    }
    static get CONTRAST_PARAMETER_NAME() {
        return "wexa_contrast";
    }
    // -----------------------------------------------------------------------
    // PUBLIC METHODS
    // -----------------------------------------------------------------------
    async switch_color_scheme() {
        await this.switchColorScheme();
    }
    async switchColorScheme() {
        if (this.#colors.length > 1) {
            console.log("Impossible to switch color scheme because multiple color schemes has set !" +
                "You have to use the activate_color_scheme() method!");
        }
        if (this.#activated_color === "") {
            this.#activated_color = this.#colors[0];
            document.body.classList.add(this.#colors[0]);
        } else {
            this.#activated_color = "";
            document.body.classList.remove(this.#colors[0]);
        }
        // Update state of the theme button
        this.#updateButtonState('btn-theme');
        await this.postEvents({"accessibility_color": this.#activated_color});
    }
    // -----------------------------------------------------------------------
    async activate_color_scheme(color_scheme) {
        await this.activateColorScheme(color_scheme);
    }
    async activateColorScheme(colorScheme) {
        if (colorScheme === "" || this.#colors.includes(colorScheme)) {
            if (this.#activated_color !== "") {
                document.body.classList.remove(this.#activated_color);
            }
            if (colorScheme !== "") {
                document.body.classList.add(colorScheme);
            }
            this.#activated_color = colorScheme;
            await this.postEvents({"accessibility_color": this.#activated_color});
        } else {
            console.log("Unknown given color scheme: " + colorScheme);
        }
    }
    // -----------------------------------------------------------------------
    async switch_contrast_scheme() {
        await this.switchContrastScheme();
    }
    async switchContrastScheme() {
        if (this.#contrasts.length > 1) {
            console.log('Impossible to switch contrast scheme because multiple contrast schemes are set! ' +
                'Use activateContrastScheme() instead.');
        }
        if (this.#activated_contrast === '') {
            this.#activated_contrast = this.#contrasts[0];
            document.body.classList.add(this.#contrasts[0]);
        } else {
            this.#activated_contrast = '';
            document.body.classList.remove(this.#contrasts[0]);
        }
        this.#updateButtonState('btn-contrast');
        await this.postEvents({accessibility_contrast: this.#activated_contrast});
    }
    // -----------------------------------------------------------------------
    async activate_contrast_scheme(contrast_scheme) {
        await this.activateContrastScheme(contrast_scheme);
    }
    async activateContrastScheme(contrastScheme) {
        if (contrastScheme === '' || this.#contrasts.includes(contrastScheme)) {
            if (this.#activated_contrast !== '') {
                document.body.classList.remove(this.#activated_contrast);
            }
            if (contrastScheme !== '') {
                document.body.classList.add(contrastScheme);
            }
            this.#activated_contrast = contrastScheme;
            const response = await this.postEvents({accessibility_contrast: this.#activated_contrast});
        } else {
            console.log('Unknown given contrast scheme: ' + contrastScheme);
        }
    }
    // -----------------------------------------------------------------------
    goToLink(element, openInNewTab = false) {
        const rawHref = element.getAttribute('href');
        if (rawHref === null || rawHref === '') {
            return;
        }
        const url = new URL(element.href, window.location.href);
        // Determine whether accessibility parameters must be propagated.
        // They are added when:
        //   - running from localhost (development server), or
        //   - navigating within the same host.
        let targetUrl;
        if (window.location.protocol !== 'file:' && (window.location.hostname === 'localhost' || url.host === window.location.host)) {
            targetUrl = this.setUrlWithParameters(url.href);
        } else {
            targetUrl = url.href;
        }
        // Open either in a new tab or in the current page.
        if (openInNewTab === true) {
            window.open(targetUrl, '_blank', 'noopener');
            return;
        }
        document.location.href = targetUrl;
    }
    // -----------------------------------------------------------------------
    setUrlWithParameters(url) {
        if (url === null || url === '') {
            return '';
        }
        const customUrl = new URL(url, window.location.origin);
        if (this.#activated_color !== '') {
            customUrl.searchParams.set(AccessibilityManager.COLOR_PARAMETER_NAME, this.#activated_color);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.COLOR_PARAMETER_NAME);
        }
        if (this.#activated_contrast !== '') {
            customUrl.searchParams.set(AccessibilityManager.CONTRAST_PARAMETER_NAME, this.#activated_contrast);
        } else {
            customUrl.searchParams.delete(AccessibilityManager.CONTRAST_PARAMETER_NAME);
        }
        return customUrl.href;
    }
    // -----------------------------------------------------------------------
    // PRIVATE METHODS
    // -----------------------------------------------------------------------
    async #loadBodyClasses() {
        const params = new URLSearchParams(window.location.search);
        const events = {};
        // manage color scheme
        if (params.has(AccessibilityManager.COLOR_PARAMETER_NAME)) {
            const color_parameter = params.get(AccessibilityManager.COLOR_PARAMETER_NAME).toLowerCase();
            if (this.#colors.includes(color_parameter)) {
                this.#activated_color = color_parameter;
                document.body.classList.add(color_parameter);
                events.accessibility_color = this.#activated_color
            } else {
                console.log(AccessibilityManager.COLOR_PARAMETER_NAME + " get parameter unknown : " + color_parameter);
            }
        }
        // manage contrast scheme
        if (params.has(AccessibilityManager.CONTRAST_PARAMETER_NAME)) {
            const contrast_param = params.get(AccessibilityManager.CONTRAST_PARAMETER_NAME).toLowerCase();
            if (this.#contrasts.includes(contrast_param)) {
                this.#activated_contrast = contrast_param;
                document.body.classList.add(contrast_param);
                events.accessibility_contrast = this.#activated_contrast
            } else {
                console.log(AccessibilityManager.CONTRAST_PARAMETER_NAME + " get parameter unknown : " + contrast_param);
            }
        }
        // Inform the server in case of change
        if (Object.keys(events).length > 0) {
            await this.postEvents(events);
        }
    }
    // -----------------------------------------------------------------------
    #setAllLinksCustom() {
        let link_elements = Array.from(document.querySelectorAll("a"));
        link_elements = link_elements.filter(el => el.href !== null && el.href !== '');
        link_elements.forEach(element => {
            element.addEventListener("click", event => {
                event.preventDefault();
                this.goToLink(element, element.target === '_blank');
            });
        });
    }
    // -----------------------------------------------------------------------
    #setSubmitCustom() {
        const submitButton = document.querySelector('button[type="submit"]');
        if (!submitButton) return;
        submitButton.addEventListener('click', () => {
            const form = document.querySelector('form');
            if (form) {
                form.action = this.setUrlWithParameters(form.action);
            }
        });
    }
    // -----------------------------------------------------------------------
    #updateButtonState(buttonId) {
        const btn = document.getElementById(buttonId);
        if (btn === null) { console.error(`Button not found: ${buttonId}.`); return; }
        let pressed = false;
        if (buttonId === 'btn-contrast') { pressed = this.#activated_contrast !== ''; }
        else if (buttonId === 'btn-theme') { pressed = this.#activated_color !== ''; }
        else { console.error(`Unknown button id: ${buttonId}.`); return; }
        btn.setAttribute('aria-pressed', String(pressed));
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.AccessibilityManager = AccessibilityManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- menu.js ---------------
'use strict';
// --------------------------------------------------------------------------
// Class: SubMenuManager
// --------------------------------------------------------------------------
class SubMenuManager {
    // --------------------------------------------------------------------
    // Protected members
    // --------------------------------------------------------------------
    #asideElement;
    #menuLinks;
    _focusTrapHandler;
    // --------------------------------------------------------------------
    // Constructor
    // --------------------------------------------------------------------
    constructor(asideId = 'appmenu') {
        this.#asideElement = document.getElementById(asideId);
        // Include both <a> and <button> elements as focusable links.
        this.#menuLinks = this.#asideElement
            ? this.#asideElement.querySelectorAll('a, button')
            : [];
        // Bind the focus trap handler to preserve context when used as an event listener.
        this._focusTrapHandler = this.#trapFocus.bind(this);
    }
    // --------------------------------------------------------------------
    // Public methods
    // --------------------------------------------------------------------
    openSubmenu() {
        this.#setOpenState(true);
    }
    // --------------------------------------------------------------------
    closeSubmenu() {
        this.#setOpenState(false);
    }
    // --------------------------------------------------------------------
    // Private methods
    // --------------------------------------------------------------------
    #setOpenState(open) {
        if (this.#asideElement === null) return;
        const opened = open === true;
        // Toggle CSS class to open or close the submenu.
        this.#asideElement.classList.toggle('open', opened);
        // Update tab index of contained links.
        this.#setLinksTabIndex(opened ? 0 : -1);
        // Manage focus trapping when opened.
        if (opened === true) {
            document.addEventListener('keydown', this._focusTrapHandler, true);
            const onTransitionEnd = (ev) => {
                if (['left', 'right', 'top', 'bottom'].includes(ev.propertyName)) {
                    this.#menuLinks[0]?.focus();
                    this.#asideElement.removeEventListener('transitionend', onTransitionEnd);
                }
            };
            this.#asideElement.addEventListener('transitionend', onTransitionEnd);
        } else {
            document.removeEventListener('keydown', this._focusTrapHandler, true);
        }
        // Apply CSS-based positioning and alignment.
        this.#adjustSubmenuPosition();
        this.#adjustSubmenuAlignment();
    }
    // --------------------------------------------------------------------
    #adjustSubmenuPosition() {
        const position = getComputedStyle(this.#asideElement)
            .getPropertyValue('--appmenu-position')
            .trim();
        // Default to 'left' if no value found.
        this.#asideElement.setAttribute('data-submenu-position', position || 'left');
        // Force a reflow to ensure visual update.
        this.#asideElement.offsetHeight;
    }
    // --------------------------------------------------------------------
    #adjustSubmenuAlignment() {
        const align = getComputedStyle(this.#asideElement)
            .getPropertyValue('--appmenu-align')
            .trim();
        const [horizontal = 'center', vertical = 'center'] = align.split(' ');
        this.#asideElement.setAttribute('data-submenu-align-horizontal', horizontal);
        this.#asideElement.setAttribute('data-submenu-align-vertical', vertical);
        // Force reflow to apply updated alignment.
        this.#asideElement.offsetHeight;
    }
    // --------------------------------------------------------------------
    #trapFocus(e) {
        if (e.key !== 'Tab') return;
        const focusable = Array.from(this.#menuLinks);
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey) {
            // Shift + Tab: move from first to last
            if (document.activeElement === first) {
                e.preventDefault();
                last.focus();
            }
        } else {
            // Tab: move from last to first
            if (document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    }
    // --------------------------------------------------------------------
    #setLinksTabIndex(value) {
        for (const link of this.#menuLinks) {
            link.tabIndex = value;
        }
    }
}
// --------------------------------------------------------------------------
// Manager for an accessible menu
// --------------------------------------------------------------------------
class MenuManager {
    // --------------------------------------------------------------------
    // Protected members
    // --------------------------------------------------------------------
    // The '<nav>' element this class is managing
    #navElement;
    // A dictionary of registered submenus: each key is the submenu
    // identifier, and the value is its associated toggle button element.
    #submenus = new Map();
    // --------------------------------------------------------------------
    // Public members
    // --------------------------------------------------------------------
    static DEFAULT_NAV_ID = 'nav-content';
    // ----------------------------------------------------------------------
    constructor(navId = MenuManager.DEFAULT_NAV_ID) {
        this.#navElement = document.getElementById(navId);
        if (!this.#navElement) {
            throw new Error(`MenuManager: nav with id '${navId}' not found.`);
        }
        // Dictionary of registered submenus.
        this.#submenus = new Map();
        // Close all registered submenus when the mouse re-enters the side menu.
        const sideMenu = this.#navElement.matches('.side') ? this.#navElement : null;
        if (sideMenu) {
            sideMenu.addEventListener('mouseenter', () => {
                // Iterate over the dictionary to close only registered submenus.
                for (const [submenu /* SubMenuManager */, /* toggle */] of this.#submenus) {
                    submenu.closeSubmenu();
                }
            });
        }
        document.addEventListener('click', (e) => this.#handleBodyClick(e), true);
    }
    // ----------------------------------------------------------------------
    registerSubmenu(asideId, toggleButtonId) {
        const aside = document.getElementById(asideId);
        const toggle = document.getElementById(toggleButtonId);
        // Validate required elements.
        if (aside === null || toggle === null) {
            WexaLogger.warn(`MenuManager: Invalid submenu registration: '${asideId}'.`);
            return;
        }
        // Create submenu instance and store association.
        const submenu = new SubMenuManager(asideId);
        this.#submenus.set(submenu, toggle);
        this.#initToggleAttributes(toggle, asideId);
        this.#bindToggleEvents(submenu, toggle);
    }
    // ----------------------------------------------------------------------
    initSideMenu(navSelector = 'nav#nav-content.side.collapsible', pinButtonId = 'pin-menu') {
        const nav = document.querySelector(navSelector);
        const pinBtn = document.getElementById(pinButtonId);
        if (!nav) {
            WexaLogger.warn(`MenuManager: Side menu not found with selector '${navSelector}'.`);
            return;
        }
        if (!pinBtn) {
            WexaLogger.warn(`MenuManager: Pin button not found with id '${pinButtonId}'.`);
            return;
        }
        pinBtn.addEventListener('click', () => {
            const isPinned = nav.classList.toggle('expanded');
            nav.setAttribute('aria-pinned', isPinned ? 'true' : 'false');
            pinBtn.setAttribute('aria-pressed', String(isPinned));
            pinBtn.setAttribute('aria-label', isPinned ? 'Unpin menu' : 'Pin menu');
        });
    }
    // ----------------------------------------------------------------------
    initMobileToggle(checkboxId = 'mobile', buttonId = 'menu-button') {
        const checkbox = document.getElementById(checkboxId);
        const button = document.getElementById(buttonId);
        // Validate required elements.
        if (checkbox === null || button === null) {
            WexaLogger.warn('MenuManager: Missing elements for mobile toggle.');
            return;
        }
        // Bind state synchronization.
        checkbox.addEventListener('change', () => {
            this.#updateMobileState(checkbox, button);
        });
        // Bind button activation.
        button.addEventListener('click', () => {
            checkbox.checked = !checkbox.checked;
            this.#updateMobileState(checkbox, button);
        });
        // Initialize current state.
        this.#updateMobileState(checkbox, button);
    }
    // ----------------------------------------------------------------------
    // Private
    // ----------------------------------------------------------------------
    #initToggleAttributes(toggle, asideId) {
        toggle.setAttribute('aria-controls', asideId);
        toggle.setAttribute('aria-haspopup', 'menu');
        toggle.setAttribute('aria-expanded', 'false');
    }
    // ----------------------------------------------------------------------
    #bindToggleEvents(submenu, toggle) {
        const activate = (event) => {
            event.preventDefault();
            event.stopPropagation();
            // Collapse main menu if not pinned.
            const pin = document.getElementById('pin-menu');
            const isPinned = pin !== null && pin.getAttribute('aria-pressed') === 'true';
            if (isPinned === false) {
                this.#navElement.classList.remove('expanded');
                this.#navElement.setAttribute('aria-expanded', 'false');
            }
            this.#closeOtherSubmenus(submenu);
            submenu.openSubmenu();
            toggle.setAttribute('aria-expanded', 'true');
        };
        toggle.addEventListener('click', activate);
        toggle.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') activate(e);
        });
    }
    // ----------------------------------------------------------------------
    #closeOtherSubmenus(current) {
        for (const [submenu, toggle] of this.#submenus) {
            if (submenu !== current) {
                submenu.closeSubmenu();
                toggle.setAttribute('aria-expanded', 'false');
            }
        }
    }
    // ----------------------------------------------------------------------
    #handleBodyClick(event) {
        const target = event.target;
        // Ignore clicks inside the main nav or any open aside
        const insideNav   = this.#navElement.contains(target);
        const insideAside = target.closest('aside.appmenu.open') !== null;
        if (insideNav || insideAside) return;
        // Otherwise close all submenus
        for (const [submenu, toggle] of this.#submenus) {
            submenu.closeSubmenu();
            toggle.setAttribute('aria-expanded', 'false');
        }
        // Remove transient state flags
        this.#navElement.classList.remove('submenu-active');
    }
    // ----------------------------------------------------------------------
    #updateMobileState(checkbox, button) {
        const expanded = checkbox.checked === true;
        this.#navElement.classList.toggle('expanded', expanded);
        this.#navElement.setAttribute('aria-expanded', String(expanded));
        button.setAttribute('aria-expanded', String(expanded));
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SubMenuManager = SubMenuManager;
window.Wexa.MenuManager = MenuManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- dialog.js ---------------
'use strict';
class DialogManager {
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
    constructor() {
        this.#dialogs = new Map();
        this.#closeButtonName = 'popup-close-btn';
        this.#videoPrefix = 'popup-video-';
        this.#dialogPrefix = 'popup-';
    }
    // --------------------------------------------------------------------
    // Public methods
    // --------------------------------------------------------------------
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
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.DialogManager = DialogManager;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- progressbar.js ---------------
class ProgressBar extends BaseManager {
    // ------------------------------------------------------------------------
    // Constructor
    // ------------------------------------------------------------------------
    constructor(options = {}) {
        super();
        this._updateCallback = options.updateCallback || null;
        this._completeCallback = options.completeCallback || null;
        this._requestManager = options.requestManager || null;
        this._targetUrl = options.targetUrl || '';
        this._intervalMs = options.intervalMs || 1500;
        this._domIds = { percent: '', text: '', header: '' };
        this._domIds = options.domIds || {
            percent: 'percent_progress',
            text: 'progress_text',
            header: 'progress_header'
        };
        this._intervalId = null;
        this._percent = 0;
        this._text = '';
        this._header = '';
    }
    // -----------------------------------------------------------------------
    // Public API
    // -----------------------------------------------------------------------
    start() {
        this.stop();
        WexaLogger.debug("Progress start:")
        this._intervalId = setInterval(async () => {
            const response = await this._fetchProgressData();
            if (response === null) {
                WexaLogger.warn(" == Empty response == ")
                await this._fetchComplete();
                return;
            }
            // Stop updates when installation is completed.
            if ((this._requestManager && this._requestManager.status === 200) || response.status === 200) {
                WexaLogger.debug(" == STATUS 200 RECEIVED ==")
                await this._fetchComplete();
                return
            }
            // The progress is updated
            this._updateDisplay(response.percent, response.text, response.header);
            if (this._percent >= 100) {
                WexaLogger.debug(" == PERCENT COMPLETED ==")
                await this._fetchComplete();
            }
        }, this._intervalMs);
    }
    // -----------------------------------------------------------------------
    stop() {
        WexaLogger.debug("Progress stop:")
        if (this._intervalId !== null) {
            clearInterval(this._intervalId);
            this._intervalId = null;
        }
    }
    // -----------------------------------------------------------------------
    update(percent, text, header) {
        WexaLogger.debug("Progress update:")
        this._updateDisplay(percent, text, header);
    }
    // -----------------------------------------------------------------------
    setRequestManager(requestManager, targetUrl) {
        this._requestManager = requestManager;
        this._targetUrl = targetUrl;
    }
    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------
    async _fetchComplete() {
        this.stop();
        if (this._completeCallback !== null) {
            this._completeCallback();
        } else {
            this.submitForm('event_bake', 'complete');
        }
    }
    // -----------------------------------------------------------------------
    async _fetchProgressData() {
        if (this._updateCallback !== null) {
            return await this._updateCallback();
        }
        if (this._requestManager === null || this._targetUrl === '') {
            WexaLogger.error('ProgressBar: No update callback or RequestManager available.');
            return null;
        }
        const response = await this.postEvents({event_name: 'update'});
        return response
    }
    // -----------------------------------------------------------------------
    _updateDisplay(percent, text, header) {
        if (typeof percent === 'number') {
            this._percent = percent;
        }
        if (typeof text === 'string') {
            this._text = text;
        }
        if (typeof header === 'string') {
            this._header = header;
        }
        this._render();
    }
    // -----------------------------------------------------------------------
    _render() {
        const percentEl = document.getElementById(this._domIds.percent);
        const textEl = document.getElementById(this._domIds.text);
        const headerEl = document.getElementById(this._domIds.header);
        if (percentEl !== null) {
            percentEl.value = this._percent;
        }
        if (textEl !== null) {
            textEl.textContent = this._text;
        }
        if (headerEl !== null) {
            headerEl.textContent = this._header;
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.ProgressBar = ProgressBar;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- book.js ---------------
'use strict';
class Book {
    // FIELDS
    #toc_element;
    #headings_container;
    #html_tags;
    // CONSTRUCTOR
    constructor(id_headings, id_toc = "toc") {
        this.#toc_element = document.getElementById(id_toc);
        this.#headings_container = document.getElementById(id_headings);
        this.#html_tags = "h1, h2, h3, h4";
    }
    // GETTERS
    get dom_toc() {
        return this.#toc_element;
    }
    get headings() {
        return this.#headings_container;
    }
    get html_tags() {
        return this.#html_tags;
    }
    // PUBLIC METHODS
    set_headings(id_headings) {
        this.#headings_container =  document.getElementById(id_headings);
    }
    add_html_tags(...tags) {
        tags.forEach(current => {
            this.#html_tags += ", " + current
        });
    }
    delete_html_tags(...tags) {
        tags.forEach(current => {
            this.#html_tags = this.#html_tags.replace(", " + current, "");
        });
    }
    fill_table(only_numerate_headings = true) {
        const headings = this.#get_headings(only_numerate_headings);
        headings.forEach((heading, index) => {
            /* Add the anchor right before the heading */
            let anchor = document.createElement('a');
            anchor.setAttribute("id", 'toc' + index);
            anchor.setAttribute("name", 'toc' + index);
            /* Add an entry into the table of content */
            let link = document.createElement('a');
            link.setAttribute('href', '#toc' + index);
            link.textContent = heading.textContent;
            let item = document.createElement('li');
            item.setAttribute('class', heading.tagName.toLowerCase());
            item.appendChild(link);
            this.#toc_element.appendChild(item);
            heading.parentNode.insertBefore(anchor, heading);
        });
    }
    // PRIVATE METHODS
    #get_headings(only_numerate_headings) {
        let titles = [].slice.call(this.#headings_container.querySelectorAll(this.#html_tags));
        let headings = [];
        titles.forEach(current => {
            if (only_numerate_headings) {
                // check if the heading begin by a number
                let before = window.getComputedStyle(current,'::before');
                if (before['content'].includes("counter(")) {
                    headings.push(current);
                }
            } else {
                headings.push(current);
            }
        });
        return headings;
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.Book = Book;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- sortatable.js ---------------
class SortaTable {
    // FIELDS
    _tableElt
    _className
    // CONSTRUCTOR
    constructor(tableId) {
        // Name of the CSS class used by the button in the <th> element
        this._className = ".sortatable";
        console.debug("Sortatable is instantiated for table element: ", tableId);
        // The <table> element which is manipulated in this class
        this._tableElt = document.getElementById(tableId);
        if (!this._tableElt) {
            // Table element is not found, log a warning and prevent further execution
            console.warn(`No table element found with id: ${tableId}. SortaTable instantiation is skipped.`);
        }
        // Store original rows order
        const tbody = this._tableElt.querySelector('tbody');
        const rows = Array.from(tbody.getElementsByTagName('tr'));
        rows.forEach((row, index) => {
            row.setAttribute('data-original-index', index);
        });
    }
    // ----------------------------------------------------------------------
    // PUBLIC
    // ----------------------------------------------------------------------
    getTableId() {
        return this._tableElt.getAttribute("id");
    }
    // ----------------------------------------------------------------------
    attachSortListeners() {
        if (!this._tableElt) {
            return;
        }
        console.debug("Attach sort listeners for table " + this._tableElt);
        // Add event listeners to all headers with class 'sortatable'
        const sortButtons = this._tableElt.querySelectorAll(this._className);
        console.debug("Found " + sortButtons.length + " sort buttons in headers");
        sortButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                console.debug(" ... button: ", `[${button}]`);
                // Retrieve the data-sort attribute from the clicked header
                const sortAttribute = button.getAttribute('data-sort');
                const isAsc = button.classList.contains('sort-asc');
                const isDesc = button.classList.contains('sort-desc');
                // Remove sort classes from all headers to reset the state
                this._tableElt.querySelectorAll(this._className).forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                // Call the sortTable function to sort the table rows and update button
                // Toggle between 3 states: no sort -> ascending -> descending
                if (isAsc) {
                    button.classList.remove('sort-asc');
                    button.classList.add('sort-desc');
                    this.#sortTable(sortAttribute, false);
                } else if (isDesc) {
                    button.classList.remove('sort-desc');
                    // No sort applied, reset table
                    this.#noSortTable();
                } else {
                    button.classList.add('sort-asc');
                    this.#sortTable(sortAttribute, true);
                }
                event.stopPropagation();
            });
        });
    }
    // ----------------------------------------------------------------------
    sort(column, isAsc = true) {
        // Sort the table based on the specified column
        this.#sortTable(column, isAsc);
        // Optionally, update the class on the header to reflect the current sort direction
        const headerButton = this._tableElt.querySelector(`button[data-sort="${column}"]`);
        if (headerButton) {
            this._tableElt.querySelectorAll(this._className).forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            headerButton.classList.add(isAsc ? 'sort-asc' : 'sort-desc');
        }
    }
    // ----------------------------------------------------------------------
    toggleColumnVisibility(checkBoxes) {
        // Iterate over each checkbox in checkBoxes
        checkBoxes.forEach(checkbox => {
            // Check if the checkbox has a data-toggle attribute
            const columnName = checkbox.getAttribute('data-toggle');
            if (!columnName) {
                console.warn("Checkbox does not have a data-toggle attribute. Skipping...");
                return; // Skip this checkbox if it doesn't have a data-toggle attribute
            }
            // Initialize column index
            let columnIndex = -1;
            // Iterate through the header cells to find the index
            const headerCells = this._tableElt.querySelectorAll('thead th');
            for (let index = 0; index < headerCells.length; index++) {
                const cell = headerCells[index];
                // Check if the cell has the data-sort attribute matching columnName
                if (cell.getAttribute('data-sort') === columnName) {
                    columnIndex = index; // Store the column index
                    break; // Exit the loop early since we've found the column
                }
                // Find the button with class "sortatable"
                const button = cell.querySelector(this._className);
                // Check if the button exists and matches the column name
                if (button && button.getAttribute('data-sort') === columnName) {
                    columnIndex = index; // Store the column index
                    break; // Exit the loop early since we've found the column
                }
            }
            // If columnIndex is found, toggle its visibility
            if (columnIndex !== -1) {
                // Get the checkbox state (checked or not)
                const checkboxState = checkbox.checked;
                // Use the columnVisibility method to update the visibility
                this.columnVisibility(columnIndex, checkboxState);
                // Optionally recalculate table width after updating visibility
                this._tableElt.style.width = '100%';
            } else {
                console.warn(`Column with name "${columnName}" not found.`);
            }
        });
    }
    // ----------------------------------------------------------------------
    columnVisibility(columnIndex, show) {
        // Get all table rows
        const rows = this._tableElt.rows;
        // Iterate over each row (including header)
        for (let i = 0; i < rows.length; i++) {
            const cell = rows[i].cells[columnIndex];
            if (cell) {
                // Toggle the 'hidden' class based on the show flag
                if (show) {
                    cell.classList.remove('hidden');
                } else {
                    cell.classList.add('hidden');
                }
            }
        }
    }
    // ----------------------------------------------------------------------
    // PRIVATE
    // ----------------------------------------------------------------------
    #noSortTable() {
        const tbody = this._tableElt.querySelector('tbody');
        const rows = Array.from(tbody.getElementsByTagName('tr'));
        // Re-organize lines by their original order
        rows.sort((a, b) => a.getAttribute('data-original-index') - b.getAttribute('data-original-index'));
        rows.forEach(row => tbody.appendChild(row));
    }
    // ----------------------------------------------------------------------
    #sortTable(sortAttribute, isAsc) {
        // Get the index of the column to sort by
        const columnIndex = this._tableElt.querySelector(`button[data-sort="${sortAttribute}"]`).closest('th').cellIndex;
        // Get the tbody element from the table
        const tableBody = this._tableElt.querySelector('tbody');
        // Convert the HTMLCollection of rows into an array for sorting
        const rows = Array.from(tableBody.getElementsByTagName('tr'));
        // Check if the attribute to sort by is 'date'
        const isDate = sortAttribute === 'date';
        // Sort the rows array using a custom comparator
        rows.sort((a, b) => {
            // Fetch the text content of the cells in the current column
            let aValue = a.cells[columnIndex].textContent.trim();
            let bValue = b.cells[columnIndex].textContent.trim();
            // If the attribute is 'date', convert string to Date object
            if (isDate) {
                aValue = new Date(aValue);
                bValue = new Date(bValue);
            }
            // Determine the sort order based on the cell values and isAsc flag
            if (aValue < bValue) return isAsc ? -1 : 1;
            if (aValue > bValue) return isAsc ? 1 : -1;
            return 0;
        });
        // Re-append sorted rows back to the table body
        rows.forEach(row => tableBody.appendChild(row));
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.SortaTable = SortaTable;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- toggleselect.js ---------------
// --------------------------------------------------------------------------
class ToggleSelector {
    // Define base path and icon names as member variables
    static ICON_PATH = "./whakerkit/icons";
    // Icon names for different states
    static ICONS = {
        CHECKED: "checked.png",
        UNCHECKED: "unchecked.png",
        HALF_CHECKED: "half-checked.png",
        HALF_UNCHECKED: "half-unchecked.png",
        HALF_CHECKED_DARK: "half-checked-dark.png",
        HALF_UNCHECKED_DARK: "half-unchecked-dark.png",
        CHECKED_DARK: "checked-dark.png",
        UNCHECKED_DARK: "unchecked-dark.png"
    };
    // Define CSS selectors for buttons and checkboxes
    static BUTTON_SELECTOR = 'button.accordion-action';
    static CHECKBOX_SELECTOR = 'input[type="checkbox"]';
    // Fields
    _iconPath;
    _detailsElt;
    // Constructor
    constructor(icon_path, detailsId) {
        if (icon_path) {
            this._iconPath = icon_path;
        } else {
            this._iconPath = ToggleSelector.ICON_PATH;
        }
        // The <details> element which is manipulated in this class
        this._detailsElt = document.getElementById(detailsId);
        if (!this._detailsElt) {
            throw new Error(`ToggleSelector instantiation failed: No details element found with id: ${detailsId}.`);
        }
        // Call handleInputsOnLoad() to initialize any inputs or settings
        this.handleInputsOnLoad();
    }
    // ----------------------------------------------------------------------
    getCheckboxes() {
        return this._detailsElt.querySelectorAll('input[type="checkbox"][data-toggle]');
    }
    // ----------------------------------------------------------------------
    handleInputsOnLoad() {
        // Setup listeners for checkboxes
        this.setupCheckboxListeners();
        // Update all toggle buttons to adjust colors with theme
        this.updateAllToggleButtons();
        // Attach event listener for click events on checkboxes
        document.addEventListener('click', (event) => {
            const target = event.target;
            if (target.type === 'checkbox') {
                this.updateAllToggleButtons();
            }
        });
    }
    // ----------------------------------------------------------------------
    toggleSelection(event) {
        const checkboxes = this.getCheckboxes();
        const button = event.currentTarget;
        // Check if any of the checkboxes are already checked
        const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        // Toggle the checked state of all checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.checked = !anyChecked;
        });
        // Update the button image based on the new state
        this.updateToggleButton(button, !anyChecked);
    }
    // ----------------------------------------------------------------------
    updateToggleButton(button, anyChecked, oneChecked = false, check = false) {
        // Get the image inside the button
        const toggleImg = button.querySelector('img');
        // Detect if dark mode is active
        const isDarkMode = document.body.classList.contains('dark');
        let imgSrc = ""; // Variable to hold the image source path
        // Determine which image to display based on the checkbox states
        if (oneChecked && check) {
            imgSrc = isDarkMode ?
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED_DARK}` :
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED}`;
        } else if (oneChecked && !check) {
            imgSrc = isDarkMode ?
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_UNCHECKED_DARK}` :
                `${this._iconPath}/${ToggleSelector.ICONS.HALF_CHECKED}`;
        } else {
            imgSrc = anyChecked
                ? (isDarkMode ?
                    `${this._iconPath}/${ToggleSelector.ICONS.CHECKED_DARK}` :
                    `${this._iconPath}/${ToggleSelector.ICONS.CHECKED}`)
                : (isDarkMode ?
                    `${this._iconPath}/${ToggleSelector.ICONS.UNCHECKED_DARK}` :
                    `${this._iconPath}/${ToggleSelector.ICONS.UNCHECKED}`);
        }
        // Update the image source
        if (toggleImg) {
            toggleImg.src = imgSrc;
        } else {
            console.error(`Image not found in button: ${button.id}`);
        }
    }
    // ----------------------------------------------------------------------
    setupCheckboxListeners() {
        const checkboxes = this.getCheckboxes();
        const button = this._detailsElt.querySelector('button.accordion-action[data-toggle]');
        // Add a 'change' event listener to each checkbox
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                // At least one is checked
                const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
                // All are checked
                const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
                // Log the state for debugging purposes
                console.log(`Checkbox ${checkbox.id} changed. Any checked: ${anyChecked}, All checked: ${allChecked}`);
                // Update button based on the state
                this.updateButtonState(button, anyChecked, allChecked);
            });
        });
    }
    // ----------------------------------------------------------------------
    updateButtonState(button, anyChecked, allChecked) {
        if (allChecked) {
            this.updateToggleButton(button, anyChecked);
        } else if (anyChecked) {
            this.updateToggleButton(button, anyChecked, true, true);
        } else {
            this.updateToggleButton(button, anyChecked, false, false);
        }
    }
    // ----------------------------------------------------------------------
    updateAllToggleButtons() {
        const buttons = this._detailsElt.querySelectorAll(ToggleSelector.BUTTON_SELECTOR);
        buttons.forEach(button => {
            const checkboxes = button.closest('details').querySelectorAll(ToggleSelector.CHECKBOX_SELECTOR);
            const anyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
            const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
            // Update button based on the state of checkboxes
            this.updateButtonState(button, anyChecked, allChecked);
        });
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.ToggleSelector = ToggleSelector;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- links.js ---------------
'use strict';
class LinkController {
    constructor() {
        // Nothing to initialize; listeners are attached explicitly via handleLinks().
    }
    // ----------------------------------------------------------------------
    handleLinks(selectors) {
        this._bindLinks(selectors, false);
    }
    handleLinksWithParameters(selectors) {
        this._bindLinks(selectors, true);
    }
    // ----------------------------------------------------------------------
    // Private
    // ----------------------------------------------------------------------
    _bindLinks(selectors, withParameters) {
        if (!Array.isArray(selectors)) {
            console.error('LinkController: Expected a list of element ids.');
            return;
        }
        for (const id of selectors) {
            const element = document.getElementById(id);
            if (element === null) {
                console.warn(`LinkController: No element found with id "${id}".`);
                continue;
            }
            // Avoid multiple bindings on the same element
            element.removeEventListener('click', this._handleActivation);
            element.removeEventListener('keydown', this._handleActivation);
            element.addEventListener('click', (event) => this._handleActivation(event, element, withParameters));
            element.addEventListener('keydown', (event) => this._handleActivation(event, element, withParameters));
        }
    }
    // ----------------------------------------------------------------------
    _handleActivation(event, element, withParameters) {
        const isClick = (event.type === 'click');
        const isEnter = (event.type === 'keydown' && event.key === 'Enter');
        if (isClick === false && isEnter === false) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        const url = element.getAttribute('href') || element.dataset.href;
        if (!url) {
            console.warn(`LinkController: No URL defined for element id="${element.id}".`);
            return;
        }
        const target = element.dataset.target || '_blank';
        this._openUrl(url, target, withParameters);
    }
    // ----------------------------------------------------------------------
    _openUrl(url, target, withParameters) {
        let finalUrl = url;
        if (withParameters === true) {
            const absoluteUrl = new URL(url, window.location.href).href;
            finalUrl = window.Wexa.accessibility.setUrlWithParameters(absoluteUrl);
        }
        if (target === '_blank' || target === '_self') {
            window.open(finalUrl, target, 'noopener');
            return;
        }
        const iframe = document.getElementById(target);
        if (iframe && iframe.tagName.toLowerCase() === 'iframe') {
            iframe.src = finalUrl;
        } else {
            console.warn(`LinkController: No iframe found with id="${target}". Opening in new tab.`);
            window.open(finalUrl, '_blank', 'noopener');
        }
    }
}
// ---- AUTO-GENERATED EXPORTS (Whakerexa bundle) ----
if (typeof window.Wexa !== 'object') { window.Wexa = {}; }
window.Wexa.LinkController = LinkController;
// ---- END AUTO-GENERATED EXPORTS ----


// ---------------- wexa.js ---------------
// --- Debug -------------------------------------------------------
console.debug('Imports OK:', {
    OnLoadManager,
    WexaLogger,
    AccessibilityManager,
    MenuManager,
    DialogManager,
    LinkController,
    SortaTable,
    ToggleSelector,
    ProgressBar,
    Book,
    BaseManager,
    RequestManager
});
// ----- Exports (framework public API) -----
// ---------------------------------------------------------------------------
// Global namespace for Whakerexa.
//
// This namespace exposes:
// - Singletons: framework-level managers that must exist exactly once.
// - Classes: reusable components that applications can instantiate freely.
//
// This unified API ensures consistency between ES6 module usage and the
// bundled (non-module) version. Applications can safely rely on Wexa.*
// regardless of whether modules are loaded or the bundle is used.
// ---------------------------------------------------------------------------
window.Wexa = {
    // ---------------------------------------------------------------
    // Singletons (global services)
    // ---------------------------------------------------------------
    // Logger is a class with only static methods → no cost / no instance.
    logger: WexaLogger,
    // Note: OnLoadManager is not instantiated because it is a scheduler /
    // dispatcher whose methods are static or utility-like.
    onload: OnLoadManager,
    accessibility: new AccessibilityManager(),
    dialog: new DialogManager(),
    links: new LinkController(),
    // ---------------------------------------------------------------
    // Public classes (instantiable components)
    // ---------------------------------------------------------------
    WexaLogger,
    OnLoadManager,
    AccessibilityManager,
    DialogManager,
    LinkController,
    MenuManager,
    ProgressBar,
    ToggleSelector,
    SortaTable,
    Book,
    BaseManager,
    RequestManager
};
// Register the global onload handler so that all deferred load functions
// declared across Whakerexa modules are executed once the document is ready.
window.onload = () => {
    OnLoadManager.runLoadFunctions();
};