![SPPAS](https://sppas.org/SPPAS5/sppas/ui/swapp/statics/images/sppas-splash-v5.png)

# sppas 

**The automatic annotation and analysis of speech.**

`sppas` is the Python package of the [SPPAS software](https://sppas.org/).
It provides an API for annotating, segmenting, and analyzing audio and video
speech recordings, as well as tools for working with annotated data.

- Main Repository: <https://github.com/brigitte-bigi/sppas/>
- Documentation: <https://brigitte-bigi.github.io/sppas/>
- SPPAS software: <https://sppas.org/>
- License: AGPL-3.0-or-later
- Copyright (C) 2011-2026 Brigitte Bigi, CNRS, Laboratoire Parole et Langage, Aix-en-Provence, France


## How SPPAS software can be helpful?

SPPAS is designed to assist researchers and linguists in analyzing speech data by providing a range of tools and functionalities related to phonetics, acoustics, signal processing, video processing, etc.

Among other features, SPPAS allows users to automatically annotate speech data at different phonetic levels. This annotated data can then be used to segment speech into meaningful units (e.g., phonemes, syllables, words) and align it with the original speech signal. SPPAS includes statistical tools for analyzing the data and extracting relevant information from the corpus. The software also offers a manual annotation interface and supports various annotation formats. It can export annotated data in various formats for compatibility with other speech processing and statistical analysis tools.

    SPPAS allows users to customize automatic annotations to their own needs and implement custom annotation solutions.

It is a research-oriented tool and may require some familiarity with speech processing concepts and techniques.


## SPPAS software Features 

SPPAS provides **24 automatic annotation and analysis solutions**, facilitating the study of various aspects of phonetics and linguistics.  

It is primarily used for speech segmentation: the process of taking the orthographic transcription of an audio segment (such as IPUs – Inter-Pausal Units) and determining where particular phonemes or words occur in that segment.

SPPAS is then a free and open-source speech segmentation tool designed to meet the real needs of researchers in linguistics and phonetics. Unlike most systems evaluated only through technical benchmarks, SPPAS offers a transparent, modular and fully traceable architecture. Each step—text normalization, phonetic transcription, forced alignment—is explicit, documented, published and customizable. This FAIR-compliant approach (Findable, Accessible, Interoperable, Reusable) supports scientific reproducibility, adaptability, and *open science practices*. 

SPPAS challenges the limits of conventional evaluation metrics and proposes an alternative, multi-criteria framework for assessing usability, transparency, and research value.

SPPAS features can be extended in two ways: 

* Plugins are extra tools that the user chooses and downloads separately. Once downloaded, SPPAS can install them and make them available. A plugin can also be removed later. 
* Spin-offs are official extensions of SPPAS. They are downloaded and installed automatically by SPPAS during its setup. Spin-offs extend the system permanently and cannot be removed afterward. 
 

## Cite 

**By using SPPAS/sppas, you agree to cite a reference in your publications or product.**

Any publication or product resulting from the use of this software, including but not limited to academic journal and conference publications, technical reports and manuals, or software, must cite at least one reference either among the following works or among any of the references listed in the book:

>   Brigitte Bigi (2015).
    SPPAS - Multi-lingual Approaches to the Automatic Annotation of Speech.
    The Phonetician - International Society of Phonetic Sciences,
    ISSN 0741-6164, Number 111-112 / 2015-I-II, pages 54-69.
    [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5749242.svg)](https://doi.org/10.5281/zenodo.5749242)


## 'sppas' Quick start

### Install

```
$ pip install sppas
```

Install optional components (linguistic resources, models, etc.):

```
$ sppassetup --help
$ sppassetup --eng
```


### API usage

Read an annotated file and convert it to another format:

```python
from sppas.src.anndata import sppasTrsRW

parser = sppasTrsRW("recording.TextGrid")
trs = parser.read()

parser.set_filename("recording.csv")
parser.write(trs)
```

For more examples, see the [API documentation](https://brigitte-bigi.github.io/sppas/).


### Command-line usage

Automatic annotations are available via the scripts in `sppas/bin/`.
For example, full automatic speech segmentation:

```
$ sppasseg -w audio.wav -l eng -e .TextGrid
```

Additional scripts for data processing and analysis are available in `sppas/scripts/`.


## 'sppas' Developer install

```
$ git clone https://github.com/brigitte-bigi/sppas.git sppas-code
$ cd sppas-code
$ python -m venv sppas-venv
$ source sppas-venv/bin/activate
$ pip install -e .
$ python -m sppas        # or: python sppas  — launches the dashboard
```

On Linux, wxPython has no wheel and is not installed by the Setup: run `python -m pip install wxpython` (needs the build dependencies).

The API documentation is available locally in the `docs/` folder — open `docs/index.html` in a browser.
It is generated by [ClammingPy](https://clamming.sourceforge.io) and uses
[Whakerexa](https://sppas.org) for accessibility (light/dark mode, dyslexia-friendly font, WCAG spacing).
To re-generate it:

```
$ pip install pygments markdown2 "ClammingPy>=2.1"
$ python makedoc.py
```


## Contributing to 'sppas'

Bug reports and contributions are welcome by e-mail at contact@sppas.org.
Please read the code of conduct and the code style guide before contributing.
Contributors must agree to the [DCO](http://developercertificate.org).


## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

See the accompanying LICENSE file or <https://www.gnu.org/licenses/>.
