```
-------------------------------------------------------------------------
    
               ██████╗  ██████╗   ██████╗    █████╗    ██████╗
              ██╔════╝  ██╔══██╗  ██╔══██╗  ██╔══██╗  ██╔════╝
              ██████═╗  ██████╔╝  ██████╔╝  ███████║  ██████═╗
              ╚════██║  ██╔═══╝   ██╔═══╝   ██╔══██║  ╚════██║
              ██████ ║  ██║       ██║       ██║  ██║  ██████ ║
              ╚══════╝  ╚═╝       ╚═╝       ╚═╝  ╚═╝  ╚══════╝
                                                    
            the automatic annotation and analysis of speech
        
               Copyright (C) 2011-2025  Brigitte Bigi, CNRS
        Laboratoire Parole et Langage, Aix-en-Provence, France
-------------------------------------------------------------------------
```


## Overview 

SPPAS - the automatic annotation and analysis of speech, is a scientific computer software package developed and maintained by Brigitte Bigi, researcher in Computer Science at the "Laboratoire Parole et Langage", in Aix-en-Provence, France.

The software is primarily utilized for **the annotation, segmentation, and analysis of recordings**, facilitating the study of various aspects of phonetics and linguistics.

* SPPAS main page: <https://sppas.org/>
* SPPAS package: <https://sourceforge.net/projects/sppas>
* Author home page: <https://sppas.org/bigi/>
* Author ORCID: <https://orcid.org/0000-0003-1834-6918>


## How SPPAS software can be helpful?

SPPAS is designed to assist researchers and linguists in analyzing speech data by providing a range of tools and functionalities related to phonetics, acoustics, signal processing, video processing, etc.

Among other features, SPPAS allows users to automatically annotate speech data at different phonetic levels. This annotated data can then be used to segment speech into meaningful units (e.g., phonemes, syllables, words) and align it with the original speech signal. SPPAS includes statistical tools for analyzing the data and extracting relevant information from the corpus. The software also offers a manual annotation interface and supports various annotation formats. It can export annotated data in various formats for compatibility with other speech processing and statistical analysis tools.

> SPPAS allows users to customize automatic annotations to their own needs and 
> implement custom annotation solutions.

It is a research-oriented tool and may require some familiarity with speech processing concepts and techniques.


## Quick Start

Carefully follow the installation instructions at <https://sppas.org/installation.html> to install Python. Then launch `setup.bat` or `setup.command` depending on your OS to install other required dependencies and optional dependencies.

Launch `sppas.bat` or `sppas.command` depending on your OS. See chapter 1 of the book for details: <https://sppas.org/book_01_introduction.html>.


## Cite

**By using SPPAS, you agree to cite a reference in your publications.**

Any publication or product resulting from the use of this software, including but not limited to academic journal and conference publications, technical reports and manuals, or software, must cite at least one reference either among the following works or among any of the references listed in the book:

>   Brigitte Bigi (2015).
    SPPAS - Multi-lingual Approaches to the Automatic Annotation of Speech.
    The Phonetician - International Society of Phonetic Sciences,
    ISSN 0741-6164, Number 111-112 / 2015-I-II, pages 54-69.
    [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5749242.svg)](https://doi.org/10.5281/zenodo.5749242)

>   Brigitte Bigi (2016).
    A Phonetization Approach for the Forced-Alignment Task in SPPAS.
    Lecture Notes in Computer Science, vol 9561. Springer, Cham.
    <https://doi.org/10.1007/978-3-319-43808-5_30>

>  Brigitte Bigi (2024). SPPAS - the automatic annotation and analysis of speech.
   2011-2024. <https://hal.science/hal-04392175>


## Features 

SPPAS provides **24 automatic annotation and analysis solutions**, facilitating the study of various aspects of phonetics and linguistics.  

It is primarily used for speech segmentation: the process of taking the orthographic transcription of an audio segment (such as IPUs – Inter-Pausal Units) and determining where particular phonemes or words occur in that segment.

SPPAS features can be extended in two ways: 

* Plugins are extra tools that the user chooses and downloads separately. Once downloaded, SPPAS can install them and make them available. A plugin can also be removed later. 
* Spin-offs are official extensions of SPPAS. They are downloaded and installed automatically by SPPAS during its setup. Spin-offs extend the system permanently and cannot be removed afterward. 
 
In short, a plugin is an optional extra that you download yourself, and you can remove, and a spin-off is an official extension SPPAS installs for you and which stays permanently.


## Help

- Tutorials, the F.A.Q. and the book are available on the website;
- Explore the 'help' folder of the SPPAS package.


## Licenses

> SPPAS is a *Research Software* distributed in the context of the "Open Science".

* SPPAS software source code is governed by AGPL version 3 or any later version;
* Help files of SPPAS are governed by GNU Free Documentation License, version 1.3;
* The demo files of SPPAS are under the terms of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License;
* Both plugins, spin-offs and resources may have individual licenses — see their individual documentation.


## Contribute

Send an e-mail to the author at `contact@sppas.org` if you intend to:

- declare an issue;
- contribute to resource creation;
- propose a plugin;
- help in SPPAS development. You'll then need to clone the package with `git --depth=1 https://git.code.sf.net/p/sppas/code`;
- collaborate on a research project. 

The author of SPPAS has a visual impairment, so please keep your email concise.
