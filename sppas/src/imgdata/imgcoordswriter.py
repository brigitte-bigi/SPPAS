# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.imgdata.imgcoordswriter.py
:author:   Florian Hocquet, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Write image with specific options, including coords.

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

    Copyright (C) 2011-2024  Brigitte Bigi, CNRS
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

from random import randint
import codecs
import mimetypes
import os

from sppas.core.coreutils import sppasTypeError
from sppas.src.anndata import sppasXRA
from sppas.src.anndata import sppasMedia
from sppas.src.anndata import sppasTier
from sppas.src.anndata import sppasLocation
from sppas.src.anndata import sppasPoint
from sppas.src.anndata import sppasLabel
from sppas.src.anndata import sppasTag

from .coordinates import sppasCoords
from .image import sppasImage

# ---------------------------------------------------------------------------


class ImageCoordsWriterOptions(object):
    """Class to manage options of an image writer.

    Store the options to write an image and a set of coordinates:

    - write coordinates in a CSV file;
    - write coordinates in an XRA file;
    - write the image with coordinates tagged by a square;
    - write a set of cropped images in a folder;
    - can force all saved images to be resized

    """

    def __init__(self):
        """Create a new ImageWriterOptions instance.

        Set options to their default values, i.e. do not write anything!

        """
        # The dictionary of outputs
        self._outputs = {"csv": False, "xra": True, "tag": False, "crop": False}

        # Force the width of output image files (0=No)
        self._width = 0
        # Force the height of output image files (0=No)
        self._height = 0

    # -----------------------------------------------------------------------

    def get_csv_output(self):
        """Return True if coordinates will be saved in a CSV file."""
        return self._outputs["csv"]

    # -----------------------------------------------------------------------

    def set_csv_output(self, value):
        """Set to True to save coordinates to a CSV file.

        :param value: (bool)

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._outputs["csv"] = value

    # -----------------------------------------------------------------------

    def get_xra_output(self):
        """Return True if coordinates will be saved in an XRA file."""
        return self._outputs["xra"]

    # -----------------------------------------------------------------------

    def set_xra_output(self, value):
        """Set to True to save coordinates to a XRA file.

        :param value: (bool)

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._outputs["xra"] = value

    # -----------------------------------------------------------------------

    def get_tag_output(self):
        """Return True if faces of the image will be surrounded."""
        return self._outputs["tag"]

    # -----------------------------------------------------------------------

    def set_tag_output(self, value):
        """Set to True to surround the faces of the image.

        :param value: (bool)

        """
        self._outputs["tag"] = bool(value)

    # -----------------------------------------------------------------------

    def get_crop_output(self):
        """Return True if the option to crop faces is enabled."""
        return self._outputs["crop"]

    # -----------------------------------------------------------------------

    def set_crop_output(self, value):
        """Set to true to create cropped images.

        :param value: (bool) True to enabled and False to disabled.

        """
        value = bool(value)
        if isinstance(value, bool) is False:
            raise TypeError
        self._outputs["crop"] = value

    # -----------------------------------------------------------------------

    def get_width(self):
        """Return the width of the output image files."""
        return self._width

    # -----------------------------------------------------------------------

    def set_width(self, value):
        """Set the width of output image files.

        :param value: (int) The width of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > sppasCoords.MAX_W:
            raise ValueError
        self._width = value

    # -----------------------------------------------------------------------

    def get_height(self):
        """Return the height of the outputs files."""
        return self._height

    # -----------------------------------------------------------------------

    def set_height(self, value):
        """Set the height of outputs.

        :param value: (int) The height of outputs images and videos.

        """
        if isinstance(value, int) is False:
            raise TypeError
        if value < -1 or value > sppasCoords.MAX_H:
            raise ValueError
        self._height = value

    # -----------------------------------------------------------------------

    def get_size(self):
        """Return the size of the outputs files."""
        return self._width, self._height

    # -----------------------------------------------------------------------

    def set_size(self, width, height):
        """Set the size of outputs.

        :param width: (int) The width of outputs images and videos.
        :param height: (int) The height of outputs images and videos.

        """
        self.set_width(width)
        self.set_height(height)

    csv = property(get_csv_output, set_csv_output)
    xra = property(get_xra_output, set_xra_output)
    tag = property(get_tag_output, set_tag_output)
    crop = property(get_crop_output, set_crop_output)

# ---------------------------------------------------------------------------


class sppasCoordsReader(object):
    """Read&create coords from a CSV/XRA file.

    The CSV file must have the following columns:

        - index of the coords in the image;
        - confidence;
        - x; y; w; h;
        - image name

    """

    def __init__(self, input_file, csv_separator=";"):
        """Set the list of coords defined in the given file.

        :param input_file: (str) coords from a sppasCoordsImageWriter
        :param csv_separator: (char) Columns separator in the CSV file

        """
        # List of coordinates, and corresponding image filenames
        self.coords = list()
        self.names = list()

        fn, fe = os.path.splitext(input_file)
        if fe.lower() == ".csv":
            self.__load_from_csv(input_file, csv_separator)
        elif fe.lower() == ".xra":
            self.__load_from_xra(input_file)
        else:
            raise Exception("Unrecognized extension, expected .csv or .xra."
                            "Got {} instead.".format(fe))

    # -----------------------------------------------------------------------

    def __load_from_csv(self, input_file, separator):
        with codecs.open(input_file, "r") as csv:
            lines = csv.readlines()

        if len(lines) > 0:
            for line in lines:
                content = line.split(separator)
                if len(content) > 5:
                    coord = sppasCoords(int(content[2]), int(content[3]),
                                        int(content[4]), int(content[5]),
                                        float(content[1]))
                    self.coords.append(coord)
                if len(content) > 6:
                    self.names.append(content[6])
                else:
                    self.names.append(content[0])

    # -----------------------------------------------------------------------

    def __load_from_xra(self, input_file):
        trs = sppasXRA("ImageCoordinates")
        trs.read(input_file)
        if len(trs) == 1:
            tier = trs[0]
        else:
            tier = trs.find(sppasCoordsImageWriter().get_xra_tiername())
        if tier is None:
            raise Exception("Invalid tier in XRA. Cant load coordinates.")

        for ann in tier:
            for label in ann.get_labels():
                for tag, score in label:
                    fuzzy_rect = tag.get_typed_content()
                    x, y, w, h = fuzzy_rect.get_midpoint()
                    coord = sppasCoords(x, y, w, h, score)
                    self.coords.append(coord)
                    media_name = ann.get_meta("image_name", "unk")
                    self.names.append(media_name)

# ---------------------------------------------------------------------------


class sppasCoordsImageWriter(object):
    """Write an image and optionally coordinates into files.

    """

    @staticmethod
    def gen_colors(nb):
        """Return a list of visually distinct colors.

        :param nb: (int) A number of colors
        :return: dict of (r, g, b) values

        """
        colors = {k: [] for k in 'rgb'}
        for i in range(nb):
            temp = {k: randint(0, 255) for k in 'rgb'}
            for k in temp:
                while 1:
                    c = temp[k]
                    t = set(j for j in range(c - 15, c + 15) if 0 <= j <= 255)
                    if t.intersection(colors[k]):
                        temp[k] = randint(0, 255)
                    else:
                        break
                colors[k].append(temp[k])
        return colors

    # -----------------------------------------------------------------------

    def __init__(self):
        """Create a new sppasCoordsImageWriter instance.

        Write the given image in the given filename.
        Parts of the image can be extracted in separate image files and/or
        surrounded on the given image.
        Output images can be resized.

        """
        # Initialize the options manager
        self.options = ImageCoordsWriterOptions()
        self._colors = sppasCoordsImageWriter.gen_colors(10)
        self._csv_separator = ";"
        self._xra_tiername = None

    # -----------------------------------------------------------------------

    def get_colors(self):
        """Return the list of (r, g, b) values to tag the image."""
        return self._colors

    # -----------------------------------------------------------------------

    def get_csv_sep(self):
        return self._csv_separator

    # -----------------------------------------------------------------------

    def set_xra_tiername(self, name):
        if self._xra_tiername is None:
            self._xra_tiername = name
            return True
        return False

    # -----------------------------------------------------------------------

    def get_xra_tiername(self):
        return self._xra_tiername

    # -----------------------------------------------------------------------

    def get_width(self):
        return self.options.get_width()

    def get_height(self):
        return self.options.get_height()

    # -----------------------------------------------------------------------

    def set_options(self, csv=None, xra=None, tag=None, crop=None, width=None, height=None):
        """Set the value of each option."""
        if csv is not None:
            self.options.set_csv_output(csv)
        if xra is not None:
            self.options.set_xra_output(xra)
        if tag is not None:
            self.options.set_tag_output(tag)
        if crop is not None:
            self.options.set_crop_output(crop)
        if width is not None:
            self.options.set_width(width)
        if height is not None:
            self.options.set_height(height)

    # -----------------------------------------------------------------------

    def write(self, image, coords, out_img_name, pattern=""):
        """Save the image into file(s) depending on the options.

        :param image: (sppasImage) The image to write
        :param coords: (list or list of list of sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image file
        :param pattern: (str) Pattern to add to a cropped image filename
        :return: List of created file names

        """
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")
        if isinstance(coords, (list, tuple)) is False:
            raise sppasTypeError("coords", "(list, tuple)")

        new_files = list()
        if self.options.csv is True:
            fn, fe = os.path.splitext(out_img_name)
            out_csv_name = fn + ".csv"
            self.write_csv_coords(coords, out_csv_name, out_img_name)
            new_files.append(out_csv_name)

        if self.options.xra is True:
            fn, fe = os.path.splitext(out_img_name)
            out_xra_name = fn + ".xra"
            self.write_xra_coords(coords, out_xra_name, out_img_name)
            new_files.append(out_xra_name)

        if self.options.tag is True:
            self.write_tagged_img(image, coords, out_img_name)
            new_files.append(out_img_name)

        if self.options.crop is True:
            cropped_files = self.write_cropped_img(image, coords, out_img_name, pattern)
            new_files.extend(cropped_files)

        return new_files

    # -----------------------------------------------------------------------

    def write_csv_coords(self, coords, out_csv_name, img_name=""):
        """Write or append a list of coordinates in a CSV file.

        - index of the coords in the image
        - confidence
        - x, y, w, h
        - image name

        :param coords: (sppasCoords) The coordinates of objects
        :param out_csv_name: (str) The filename of the CSV file to write
        :param img_name: (str) The filename of the image

        """
        mode = "w"
        if os.path.exists(out_csv_name) is True:
            mode = "a+"

        with codecs.open(out_csv_name, mode, encoding="utf-8") as f:
            for i, c1 in enumerate(coords):

                if isinstance(c1, (list, tuple)) is False:
                    f.write("{:d}{:s}".format(i + 1, self._csv_separator))
                    self.write_coords(f, c1)
                else:
                    for j, c2 in enumerate(c1):
                        f.write("{:d}{:s}".format(j+1, self._csv_separator))
                        self.write_coords(f, c2, self._csv_separator)

                if len(img_name) > 0:
                    f.write("{:s}{:s}".format(img_name, self._csv_separator))

                f.write("\n")

    # -----------------------------------------------------------------------

    def write_xra_coords(self, coords, out_xra_name, img_name=""):
        """Write or append a list of coordinates in an XRA file.

        - index of the coords in the image
        - confidence
        - x, y, w, h
        - image name

        :param coords: (sppasCoords) The coordinates of objects
        :param out_xra_name: (str) The filename of the XRA file to write
        :param img_name: (str) The filename of the image

        """
        tiername = "ImgCoords"
        if self._xra_tiername is not None:
            tiername = self._xra_tiername

        loc = sppasPoint(1)
        if os.path.exists(out_xra_name):
            trs = sppasXRA("ImageCoordinates")
            trs.read(out_xra_name)
            tier = trs.find(tiername)
            if tier is None:
                raise Exception("Invalid tier in XRA. Cant add coordinates.")
            last_point = tier.get_last_point()
            loc = sppasPoint(last_point.get_midpoint() + 1)
        else:
            m = mimetypes.guess_type(img_name)
            if m[0] is None:
                fn, fe = os.path.splitext(img_name)
                mime_type = "image/" + fe[1:]
            else:
                mime_type = m[0]
            media = sppasMedia(img_name, mime_type=mime_type)
            tier = sppasTier(tiername)
            tier.set_media(media)
            trs = sppasXRA("ImageCoordinates")
            trs.append(tier)

        # Create the annotation representing the given list of coords
        labels = list()
        for c in coords:
            if isinstance(c, sppasCoords) is False:
                c = sppasCoords.to_coords(c)
            tag = sppasTag((c.x, c.y, c.w, c.h), tag_type="rect")
            label = sppasLabel(tag, c.get_confidence())
            labels.append(label)
        ann = tier.create_annotation(sppasLocation(loc), labels)
        ann.set_meta("image_name", img_name)

        # Override the XRA file
        trs.write(out_xra_name)

    # -----------------------------------------------------------------------

    def write_coords(self, fd, coords, sep=";"):
        """Write coordinates in the given stream.

        :param fd: (Stream) File descriptor, String descriptor, stdout, etc
        :param coords: (sppasCoordinates) Coordinates to write in other columns
        :param sep: (char) CSV separator

        """
        fd.write("{:f}{:s}".format(coords.get_confidence(), sep))
        fd.write("{:d}{:s}".format(coords.x, sep))
        fd.write("{:d}{:s}".format(coords.y, sep))
        fd.write("{:d}{:s}".format(coords.w, sep))
        fd.write("{:d}{:s}".format(coords.h, sep))

    # -----------------------------------------------------------------------

    def write_tagged_img(self, image, coords, out_img_name):
        """Tag and save the images with colored squares at given coords.

        :param image: (sppasImage) The image to write
        :param coords: (list or list of list of sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image file

        """
        # Tag the images with squares at the coords
        img = self.tag_image(image, coords)

        # Resize the image, if requested
        if self.options.get_width() > 0 or self.options.get_height() > 0:
            img = img.iresize(self.options.get_width(),
                              self.options.get_height())

        # Save the tagged/resized image
        img.write(out_img_name)
        return img

    # -----------------------------------------------------------------------

    def tag_image(self, image, coords, colors=list()):
        """Tag the image at the given coords.

        :param image: (sppasImage) The image to write
        :param coords: (list of sppasCoords OR list(list of sppasCoords)) The coordinates of objects
        :param colors: list of (r,g,b) List of tuple with RGB int values
        :return: a copy of the image with colored squares at the given coords

        """
        if coords is None:
            return image
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")
        if isinstance(coords, (list, tuple)) is False:
            raise sppasTypeError("coords", "(list, tuple)")

        # Make a copy of the image to tag it without changing the given one
        img = sppasImage(input_array=image.copy())
        w, h = img.size()
        pen_width = max(2, int(float(w + h) / 500.))

        # Add colors if we need more
        if len(colors) == 0 and len(coords) > len(self._colors['r']):
            nb = max(10, len(coords) - len(self._colors['r']) + 1)
            new_colors = sppasCoordsImageWriter.gen_colors(nb)
            self._colors.update(new_colors)

        return self.tag_coords(img, coords, pen_width, colors)
       
    # -----------------------------------------------------------------------

    def tag_coords(self, img, coords, pen_width, colors=list()):
        """Tag image for the given coords.
        
        :param img: (sppasImage) The image to write
        :param coords: (list of sppasCoords OR list(list of sppasCoords)) The coordinates of objects
        :param colors: List of (r,g,b) Tuple with RGB int values
        :return: (sppasImage)
        
        """
        if coords is None:
            return img
        if isinstance(img, sppasImage) is False:
            raise sppasTypeError("image", "sppasImage")
        if isinstance(coords, (list, tuple)) is False:
            raise sppasTypeError("coords", "(list, tuple)")

        for i, c in enumerate(coords):
            if c is None:
                continue
            # Either use the i-th default color or the i-th given one
            if len(colors) != len(coords):
                # Get the i-th color
                n = len(self._colors['r'])
                r = self._colors['r'][i % n]
                g = self._colors['g'][i % n]
                b = self._colors['b'][i % n]
                rgb = (r, g, b)
            else:
                rgb = colors[i]

            # Draw the square and
            # the confidence inside the square if the coord is not a point
            if isinstance(c, (list, tuple)) is False:
                c = [c]
            img = img.isurround(c, color=rgb, thickness=pen_width, score=True)

        return img

    # -----------------------------------------------------------------------

    def write_cropped_img(self, image, coords, out_img_name, pattern=""):
        """Crop and save the images with squares at given coords.

        :param image: (sppasImage) The image to write
        :param coords: (sppasCoords) The coordinates of objects
        :param out_img_name: (str) The filename of the output image files
        :param pattern: (str) Pattern to add to each file
        :return: list of file names

        """
        cropped_files = list()
        for i, c in enumerate(coords):
            # Fix the image filename
            fn, fe = os.path.splitext(out_img_name)
            if len(pattern) > 0 and fn.endswith(pattern):
                # the out_img_name is already including the pattern
                fn = fn[:len(fn)-len(pattern)]
            out_iname = "{:s}_{:d}{:s}{:s}".format(fn, i+1, pattern, fe)

            # Crop the image at the coordinates & resize
            img = self.crop_and_size_image(image, c)

            # Resize the cropped image, if requested
            if self.options.get_width() > 0 or self.options.get_height() > 0:
                img = img.iresize(self.options.get_width(),
                                  self.options.get_height())

            # Save the cropped image
            img.write(out_iname)
            cropped_files.append(out_iname)

        return cropped_files

    # -----------------------------------------------------------------------

    def crop_and_size_image(self, image, coord):
        """Crop the given image at the given coords and resize.

        :param image: (sppasImage) The image to write
        :param coord: (sppasCoords) The coordinates of the area to crop
        :return: (sppasImage)

        """
        # Crop the image at the coordinates
        img = image.icrop(coord)

        # Resize the cropped image
        img = img.iresize(self.options.get_width(),
                          self.options.get_height())

        return sppasImage(input_array=img)
