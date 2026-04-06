'use strict';

/* Links with accessibility */

function tabToLink(event, url) {
    let type = event.type;

    if (type === 'click' || (type === 'keydown' && event.keyCode === 13)) {
        event.preventDefault();
        event.stopPropagation();

        window.open(url, "_blank");
    }
}
