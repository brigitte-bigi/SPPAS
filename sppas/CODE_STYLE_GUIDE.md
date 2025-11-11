# Code style guide

## General rules

### Base coding rules

The base rules are in PEP8 Style Guide: <https://peps.python.org/pep-0008/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Commit message

A correct commit message must therefore be structured as:
`name.of.module: Action message`
where Action includes but is not limited to "added", "fixed", "cleaned", "removed".
Example: 
```
sppas.src.annotations.Cuedpseech.whenhend: Fixed test for the model 4 -- custom rules.
\n\nA long description is welcome explaining the reason(s) of these changes but
not the changes themselves.
```

### Naming

- General class names are in Pascal Case. Example: `class WorkerOnSomething:`.
- SPPAS integrated class names are in CamelCase. Example: `class sppasWorkerOnSomething:`
- Function names are Snake Cases: all words lowercase separated by underscores. Example `def work_hard():`
- Variable names and objects are Snake Cases: all words lowercase separated by underscores,
   and must express their use more than their type. Example `work_hard = True`. Exceptions: 
   local iterators variables like i, j, k.
- Constants are Upper Case with Underscores. Example: `MSG_HELLO = _("Hello")`.
- Files that define a class should have the same name as the class but in Snake Case;
   and it should contain only one class. Example: `worker_on_something.py`. Abbreviations are 
   allowed. Example: `worker_on_sth.py`.

### Formatting

- Special characters like page break must be avoided.
- Indentation must use 4 spaces everywhere.

### Commenting

Comments are in American English. 
Consider a comment to be like a sentence: it starts with an uppercase,
it contains a verb, and it explains something that is not obvious when reading the lines
of code. The sentences should be in the passive voice, so they do not use 'you' or 'we'.

There can never be too many comments in a program! However, tricky code should not be 
commented on but rewritten! In general, the use of comments should be minimized through
appropriate naming choices and an explicit logical structure.


## Python Programming Language


### Documentation Strings

The base rules are in PEP257 Style Guide: <https://peps.python.org/pep-0257/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.

### Type Hints

The base rules are in PEP484 Style Guide: <https://peps.python.org/pep-0484/>.

All specific rules below replace the corresponding base rules. For any subject 
not mentioned below, please refer to the base.


## SPPAS specific rules

### Coding rules

- Limit all lines to a maximum of 119 characters.
- Do not use in-line comments.
- For type hints, **do not use 'typing' library**.
- Do not use property decorator. Use "property" function instead.

- Always explicit what is compared to what. Do not use 'not'. Examples:
```python
>>> # Correct -- also because it makes everything clear:
>>> # if boolean
>>> if greeting is False:
>>>     pass
>>> # if int
>>> if greeting == 0:
>>>     pass
>>> # if string
>>> if greeting == '0':
>>>     pass
>>> # if None
>>> if greeting is None:
>>>     pass
>>> # if list, tuple or dict
>>> if len(greeting) == 0:
>>>    pass

>>> # Wrong because it's too confusing and can induce an error:
>>> if greeting: 
>>>    pass
>>> if not greeting:
>>>    pass
```

### Documentation Strings

- The short summary is limited to 79 characters. It starts with an uppercase and ends with a dot.
- Markdown syntax can be used but is limited to `markdown2` support.
- An extra blank-line must be added before closing.
- Notice that there's a space after 'param' but both 'return', 'raises' and 'example' are surrounded by ":".

Example:

```python
>>>def add(a: int, b: int) -> int:
>>>"""Return the sum of two integers.

   It checks the types of given parameters and return their sum if both are integers.
   
   :example:
   >>> add(3, 4)
   7
   >>> add(3, -4)
   -1
   >>> add('3', 4)
   TypeError("First parameter is not an int")
   
   :param a: (int) First value to be added
   :param b: (int) Second value to be added
   :raises: TypeError: First parameter is not an int
   :raises: TypeError: Second parameter is not an int
   :return: (int) The sum of the given parameters

   """
```

See ClammingPy for additional details and examples: <https://clamming.sourceforge.io/>.

### Justification for Style Adaptations

The author of the SPPAS has a visual impairment, and these modifications 
to standard coding guidelines are aimed at enhancing code readability and 
accessibility.

While the general principles of PEP8, PEP257, and PEP484 are followed, 
certain adjustments are made to accommodate specific needs related to 
visual clarity, for example:

- Avoiding the 'typing' Library: The use of type hints from the 'typing' 
  library is deliberately avoided as they tend to clutter the code, making 
  declarations more difficult to read. By removing this layer of complexity,   
  the code remains clear and manageable, allowing for faster comprehension 
  and easier maintenance.
- Explicit Comparisons: The preference for explicit comparisons (e.g., if 
  greeting == 0: instead of if greeting:) is designed to minimize ambiguity.
  This makes the logical flow of the code more apparent, reducing the 
  cognitive load when navigating through conditions and comparisons.
- Line Length Limit: A line length of 119 characters is permitted, slightly 
  longer than PEP8’s recommendation of 79. This provides more flexibility, 
  reducing unnecessary line breaks while still maintaining readability on 
  modern wide-screen displays.

These adaptations are essential for maintaining efficient and **accessible**
coding practices while adhering to the general spirit of Python's style 
guidelines. They ensure that the code remains functional and clean, while 
also addressing the specific needs of developers with visual impairments.


## Javascript Programming Language

### General Guidelines

As in Python, code readability and reusability are top priorities. Code should 
be designed to be clear, maintainable, and generic to facilitate reuse across 
different contexts. Object-oriented programming (OOP) is strongly encouraged 
to structure and modularize the code effectively.  

All functions, methods, and classes must include well-written docstrings to 
document their purpose, parameters, and return values.

### Coding Rules

- **Use Object-Oriented Programming**: Encapsulate functionality in classes or modules. Avoid global variables.
- **Consistent Naming Convention**: 
  - Classes: PascalCase (e.g., `class DataManager`).
  - Functions, variables, and methods: camelCase (e.g., `fetchData`).
  - Constants: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`).
- **Max Line Length**: Limit all lines to 119 characters.
- **Comments**: Write concise comments in American English. Explain the "why," not the "how."
- **Error Handling**: Provide feedback when objects or elements are not found. 
- **Explicit Comparisons**: Avoid implicit truthy or falsy comparisons. Example:

```javascript
// Correct:
if (items.length === 0) { /* handle empty case */ }
if (user === null) { /* handle null case */ }
if (isActive === true) { /* handle active case */ }

// Wrong:
if (!items) { /* unclear */ }
if (user) { /* unclear */ }
if (isActive) { /* unclear */ }
```


#### Example of Bad Practice

Avoid writing code that is unclear, difficult to debug, or silently makes 
decisions, like this:

```javascript
// Wrong -- unclear logic, silent decisions:
document.querySelector('input[name="general_condition"]:checked')?.value === 'true' || true;
```

This code lacks readability, hides the logic behind the condition, and silently
defaults to true without notifying the user when the expected element is not 
found. Instead, you should explicitly handle the logic and provide feedback 
when issues occur:

```javascript
// Correct -- explicit logic, feedback provided if error:
let value = true;
const input = document.querySelector('input[name="general_condition"]:checked');

if (input === null) {
    console.error('Input not found: general_condition. Set to default: true.');
} else {
    ...
}
```

### Formating

- Use 2 spaces for indentation.
- Use single quotes (') unless double quotes are required.
- End statements with semicolons (;).
- Avoid hardcoding; use constants or configuration variables.
- Favor modular design with ES6 modules.
- Handle errors gracefully using try...catch blocks.
- Reuse code with generic, well-tested utilities.
- Leverage modern syntax (e.g., let, const, template literals, destructuring).


### Commenting and docstrings

Use JSDoc format for documentation. Write in American English. 
Use full sentences, starting with an uppercase letter and ending with a 
period. Explain why the code exists, not what it does (this should be clear 
from the code itself). Avoid over-commenting; instead, strive for clear and 
self-explanatory code.

Example of a well-documented function:

```javascript
/**
 * Fetch data from a given API endpoint.
 *
 * This function sends an HTTP GET request to the specified URL and
 * processes the JSON response. If the request fails, an error is logged.
 *
 * @param {string} url - The API endpoint to fetch data from.
 * @returns {Promise<Object>} The JSON response data.
 * 
 */
async function fetchData(url) {
...
}

```



