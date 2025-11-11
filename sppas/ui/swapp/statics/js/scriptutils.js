'use strict';

function checkbox_switch(checkable) {
    const request_manager = new RequestManager();
    const post_data = {};
    post_data[checkable.name + "_posted"] = checkable.value

    request_manager.send_post_request(post_data)
        .then(response => {
            for (const key in response) {
                let current_input = document.getElementById(key);

                if (current_input != null) {
                    current_input.checked = response[key];
                }
            }
        });
}


function notify_action(action_btn) {
    const form = document.createElement("form");
    form.method = "POST";
    form.style.display = "none";

    const el = document.createElement("input");
    el.name = action_btn.name + "_action";
    el.id = action_btn.name + "_action";
    el.value = action_btn.getAttribute("value")
    el.type = "hidden"
    form.appendChild(el);

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}


function notify(form_ident) {
    var form = document.getElementById(form_ident);
    form.submit();
}

function openForm(form_ident) {
    document.getElementById(form_ident).style.display = "block";
}

function closeForm(form_ident) {
    document.getElementById(form_ident).style.display = "none";
}


/* Links with accessibility */

function goToLink(event, url) {
  var type = event.type;

  if (type === 'click' || (type === 'keydown' && event.keyCode === 13)) {
    window.location.href = url;

    event.preventDefault();
    event.stopPropagation();
  }
}

function tabToLink(event, url) {
    let type = event.type;

    if (type === 'click' || (type === 'keydown' && event.keyCode === 13)) {
        event.preventDefault();
        event.stopPropagation();

        window.open(url, "_blank");
    }
}
