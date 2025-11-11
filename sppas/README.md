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

This is `sppas` module of the SPPAS software tool. 

### Use case

You have recorded audio and/or video files with speech, and you want to analyze some parameters you are interested in. 
You then need automatic or semi-automatic solutions allowing you to annotate the recordings. You also may want these files to be compatible with your favorite manual annotation tool.

> SPPAS allows you to customize the automatic annotations to your own needs: you may implement your custom annotation solution.


### Features

SPPAS is a pure Python, free, open-source software primarily used for **the annotation, segmentation, and analysis of recordings**, facilitating the study of various aspects in phonetics and linguistics.

* SPPAS main page: <https://sppas.org/>
* SPPAS package: <https://sourceforge.net/projects/sppas>


### Content

`sppas` module includes the followings:

1. "core": Python package to configure the application
2. "src": the Python source code of SPPAS API - Application Programming Interface;
3. "ui": the User Interfaces, currently Terminal and Graphical ones;
4. "bin": the Python programs allowing to launch SPPAS features with the Command-Line UI;
5. "scripts": Python programs distributed without any warranty, they are not maintained;
6. "plugins": some plugins. Others can be downloaded from the website.
7. "tests": some of the unittest (currently under migration). 
8. "docs": module and resources documentation 

The API and UI are Object-Oriented Programming - OOP. Some of the packages
contain a "yuml" file to be copied/paste at: https://www.yuml.me/.
They are describing the class diagram of the package.


## Quick start

### Install

Create a virtual environment: 
```
>python -m venv .sppaspyenv~
```

Below, the term "python" refers either to ".sppaspyenv~/bin/python" (Unix-based) or ".sppaspyenv~/Scripts/python.exe" (Windows).

The required dependencies can be installed with: 
```
>python -m pip install .
```

Any other dependency can be installed with the script "preinstall":
```
>python sppas/bin/preinstall.py -h
```


## Help / How to contribute

If you want to report a bug, please send an e-mail to the author.
**Any and all constructive comments are welcome.**

If you plan to contribute to the code, please read carefully and agree both the code of conduct and the code style guide.
If you are contributing code or documentation to the SPPAS project, you are agreeing to the DCO certificate <http://developercertificate.org>. 
Copy/paste the DCO, then you just add a line saying:
```
Signed-off-by: Random Developer <random@developer.example.org>
```
Send this file by e-mail to the author.


## License/Copyright

See the accompanying LICENSE and AUTHORS.md files for the full list of contributors.

Copyright (C) 2011-2025  Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.


## Goodies

SPPAS pronunciation: /spas/

SPPAS name in binary:
01010011 01010000 01010000 01000001 01010011 

SPPAS name in decimal:
83 80 80 65 83 

SPPAS name in hexa:
53 50 50 41 53 
