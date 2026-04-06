# -*- coding: UTF-8 -*-
"""
:filename: sppas.src.imgdata.imgdataexc.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Image data exceptions.

.. _This file is part of SPPAS: https://sppas.org/
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyright (C) 2011-2021  Brigitte Bigi, CNRS
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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

from sppas.core.coreutils import error

# -----------------------------------------------------------------------


class ImageReadError(IOError):
    """:ERROR 2610:.

    Image of file {filename} can't be read by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(2610) + (error(2610, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageWriteError(IOError):
    """:ERROR 2620:.

    Image of file {filename} can't be written by opencv library.

    """

    def __init__(self, name):
        self.parameter = error(2620) + (error(2620, "data")).format(filename=name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageBoundError(ValueError):
    """:ERROR 2330:.

    The value {} can't be superior to the one of the image {}.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2330) + \
                         (error(2330, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageWidthError(ValueError):
    """:ERROR 2332:.

    The width value {} can't be superior to the width {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2332) + \
                         (error(2332, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageHeightError(ValueError):
    """:ERROR 2334:.

    The height value {} can't be superior to the height {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2334) + \
                         (error(2334, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageEastingError(ValueError):
    """:ERROR 2336:.

    The x-axis value {} can't be superior to the width {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2336) + \
                         (error(2336, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class ImageNorthingError(ValueError):
    """:ERROR 2338:.

    The y-axis value {} can't be superior to the height {} of the image.

    """

    def __init__(self, value, img_value):
        self.parameter = error(2338) + \
                         (error(2338, "data")).format(value, img_value)

    def __str__(self):
        return repr(self.parameter)
