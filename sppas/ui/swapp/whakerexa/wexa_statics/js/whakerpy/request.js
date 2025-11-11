/**
:filename: whakerpy.js.request.js
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: A class to simplify the sending of request (on the Javascript side) to the python server of the localhost client and gets data in return.

-------------------------------------------------------------------------

This file is part of WhakerPy: https://whakerpy.sourceforge.io

Copyright (C) 2013-2024 Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

Use of this software is governed by the GNU Public License, version 3.

Whakerpy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Whakerpy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Whakerpy. If not, see <https://www.gnu.org/licenses/>.

This banner notice must not be removed.

-------------------------------------------------------------------------

A class to simplify the sending of request (on the Javascript side) to the
python server of the localhost client and gets data in return.

Careful, this class communicate with the python server with HTTP request,
so the class are asynchronous methods. If you are uncomfortable with this
paradigm consult the javascript documentation:
https://developer.mozilla.org/fr/docs/Learn/JavaScript/Asynchronous
(only async and await keywords are necessary to understand to used the
asynchronous class methods)

Basic URL Structure: <protocol>//<hostname>:<port>/<pathname><search><hash>

- protocol: Specifies the protocol name be used to access the resource on
  the Internet.
  For example: HTTP (without SSL) or HTTPS (with SSL)
- hostname: Host name specifies the host that owns the resource.
  For example, www.somewhere.org.
  A server provides services using the name of the host.
- port: A port number used to recognize a specific process to which an Internet
  or other network message is to be forwarded when it arrives at a server.
- pathname: The path gives info about the specific resource within the host t
  that the Web client wants to access.
  For example, /index.html.
- search: A query string follows the path component, and provides a string
  of information that the resource can utilize for some purpose.
- hash: The anchor portion of a URL, includes the hash sign (#).

*/

function notify_event(action_btn) {
    const form = document.createElement("form");
    form.method = "POST";
    form.style.display = "none";

    const el = document.createElement("input");
    el.name = action_btn.name + "_event";
    el.id = action_btn.name + "_event";
    el.value = action_btn.getAttribute("value")
    el.type = "hidden"
    form.appendChild(el);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}


class RequestManager {

    // FIELDS
    // The declaration outside the constructor and the '#' symbol notify a private attribute.
    #protocol;
    #port;
    #url;
    #status;
    maxFileSize;

    // CONSTRUCTOR
    /**
     * The constructor of the RequestManager class.
     * Initialize private member attributes.
     */
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

    /**
     * Get the protocol of the connexion of the client (In the SPPAS web application case the protocol is 'http').
     *
     * @returns {string} The protocol used.
     *
     */
    get protocol() {
        return this.#protocol;
    }

    // ----------------------------------------------------------------------

    /**
     * Get the port of the client and server address.
     *
     * @returns {string} - The port used.
     *
     */
    get port() {
        return this.#port;
    }

    // ----------------------------------------------------------------------

    /**
     * Get the url of the client and server address.
     *
     * Format: {protocol}://{hostname}:{port}/
     * Example: http://localhost:8080/
     *
     * @returns {string} The url of the localhost address.
     *
     */
    get request_url() {
        return this.#url;
    }

    // ----------------------------------------------------------------------

    /**
     * Get the status of the last response of the server.
     *
     * @returns {int} The code of the response.
     *
     */
    get status() {
        return this.#status;
    }

    // ----------------------------------------------------------------------
    // METHODS
    // ----------------------------------------------------------------------

    /**
     * This method is used to send a GET HTTP request to the python server.
     *
     * @param uri {string} - The pathname of the GET request.
     * @param is_json_response {boolean} - False by default.
     *                                     Boolean value to know if the server response is a json object to parse.
     *
     * @returns {Promise<*>} - The server data response.
     *
     */
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
                    request_response_data = await response.json();
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


    /**
     * Sends a POST HTTP request to the server, posting data in JSON format.
     *
     * Manages both JSON and Blob responses, and opens HTML error pages (like
     * 500 errors) in a new tab if encountered.
     *
     * @param {Object} post_parameters - Data to be sent in the POST request, in JSON format.
     * @param {string} [accept_type="application/json"] - Expected MIME type of the server's response, defaults to JSON.
     * @param {string} [uri=""] - Additional path to append to the base request URL.
     * @returns {Promise<*>} - Returns the parsed response data (JSON or Blob), or an error object.
     * @throws {Error} - Throws an error if there is a network or if an HTML error page is received.
     *
     */
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
                    try {
                        request_response_data = await response.json();
                    } catch (error) {
                        console.error("Failed to parse JSON response", error);
                        const responseText = await response.text();
                        request_response_data = {
                            status: response.status,
                            error: "Failed to parse JSON. See error details in the newly opened tab.",
                            html: responseText
                        };
                        // Open a new tab to display the error content -- probably HTML
                        this.openErrorTab(responseText);
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

    /**
     * This function opens a new tab to display the HTML error content received from the server.
     * It is used when the server returns HTML content, typically in error cases.
     *
     * @param responseText {string} - The HTML response text to display in the new tab.
     */
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

    /**
     * Uploads a file (only one) from an input to the server.
     * Returns the server response in json format (already decoded).
     *
     * @param input {HTMLInputElement} - the input that contains the file to upload
     * @param accept_type {string} - mimetype of the server response, json by default.
     * @param token {string} - the token of the user to authenticate the request
     * @param uri {string} - The pathname of the GET request.
     *
     * @returns {Promise<*>} The server response.
     *
     */
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
