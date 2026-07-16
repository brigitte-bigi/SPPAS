# swapp — SPPAS Web-based APPlication

`swapp` is the web-based user interface of SPPAS. It is built on top of
`WhakerPy` for the dynamic HTML generation and `Whakerexa` for the front-end
toolkit. Accessibility is the first priority of any design decision in this
package.


## Taxonomy: App / Page / Dialog

The user interface is made of three kinds of objects. The single decision
criterion is: *does the content keep its meaning outside the current
context?* No: it is a dialog. Yes, without business logic: it is a page.
Yes, with business logic and state: it is an app.

### App

A functional unit with business logic: it has a state, a controller, user
working data, and a life cycle. An app is implemented in its own `app_*`
module, with its own URL and its own JavaScript manager.

Examples: Dashboard, Setup.

### Page

A document with its own URL and without business logic: its content keeps
its meaning independently of the context it is reached from. It contains
either pure information or a single self-contained interaction, such as a
form. A page is reachable from the nav of any app; the user enters it and
leaves it, and nothing persists in it.

Examples: Feedback, About.

### Dialog

A brief interruption *inside* the current context. Its content has no
meaning outside of this context, and the user returns to it immediately:
confirmation, alert, error or information message, consent. A dialog has
no URL and no self-contained content.

Examples: Agreement, error and information alert dialogs.


## Serving mechanism

### How apps are served

Each app is a module named `app_*`. It declares a `WebData` class, derived
from `swappWebData` (see `apps/swapp_bakery.py`), which answers two
questions: `is_page(page_name)` and `bake_response(page_name)`.

All the `WebData` classes are registered in the `WEB_APPLICATIONS` list of
`wapps.py`. When a page is requested, `main_app.py` iterates over this list
and asks each entry `is_page()`; the first one that answers `True` bakes
the response.

**Important:** `WEB_APPLICATIONS` has a second role. The Dashboard model
reads it to create the application cards displayed in the Dashboard. As a
consequence, an entry in `WEB_APPLICATIONS` is, by definition, an app: it
is dispatched *and* it gets a card. 

### How pages are served

Pages live in the `pages/` package. Each page has its own module; a page 
has no model, no dedicated JavaScript manager, and a controller only when 
the page processes events (a form, for example).

A single provider, `swappPagesData`, exposes the same
`is_page()`/`bake_response()` interface and routes all the generic pages.
It is registered in a distinct `WEB_PAGES` registry, consulted by
`main_app.py` after the apps. This keeps the App/Page taxonomy visible in
the code and keeps pages out of the Dashboard cards.
