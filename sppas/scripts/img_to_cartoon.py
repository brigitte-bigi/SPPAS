#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
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

    scripts.img_to_cartoon.py
    ~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2022  Brigitte Bigi, CNRS
:summary:      a script to turn an image into a cartoon

"""

import sys
import logging
import os
import numpy as np
import cv2
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.core.config import sppasLogSetup
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import image_extensions
from sppas.src.videodata import sppasVideoReader
from sppas.src.videodata import sppasVideoWriter
from sppas.src.videodata import video_extensions

# ----------------------------------------------------------------------------


def cv2show(img):
    cv2.namedWindow("img_to_cartoon")
    while True:
        cv2.imshow("img_to_cartoon", img)
        # The function waitKey waits for a key event infinitely (when delay<=0)
        k = cv2.waitKey(100)
        if k == 27:  # escape key
            break
    cv2.destroyAllWindows()

# ----------------------------------------------------------------------------


def color_quantization_filter(img, nb_down_samp=2, nb_bilateral_filters=50):
    """Smooth colors.

    Down-sample and Up-sample the original image colors.

    :param nb_down_samp: (int) number of downscaling steps
    :param nb_bilateral_filters: (int) number of bilateral filtering steps

    """
    # downsample image using Gaussian pyramid
    img_color = img.copy()

    for _ in range(nb_down_samp):
        img_color = cv2.pyrDown(img_color)

    # repeatedly apply small bilateral filter instead of applying
    # one large filter
    for _ in range(nb_bilateral_filters):
        img_color = cv2.bilateralFilter(img_color, 9, 9, 7)

    # upsample image to original size
    for _ in range(nb_down_samp):
        img_color = cv2.pyrUp(img_color)

    return img_color

# ----------------------------------------------------------------------------


def color_quantization_kmeans(img):
    # Reshape the image
    img_reshaped = img.reshape((-1, 3))

    # convert to np.float32
    img_reshaped = np.float32(img_reshaped)

    # Set the Kmeans criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    # Set the amount of K (colors)
    K = 6

    # Apply Kmeans
    _, label, center = cv2.kmeans(img_reshaped, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert it back to np.int8
    center = np.uint8(center)
    res = center[label.flatten()]

    # Reshape it back to an image
    img_Kmeans = res.reshape((img.shape))
    return img_Kmeans

# ----------------------------------------------------------------------------
# A first solution, shared by all tutorials on the web
# ----------------------------------------------------------------------------


def img_to_cartoon(img, line_size=11, blur_value=5):
    """Cartoonizer effect."""
    # Convert the image to grayscale and slightly blur it
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.medianBlur(img_gray, 3)

    # Get edged image
    img_edges = cv2.adaptiveThreshold(img_gray,
                                      255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,
                                      line_size,
                                      blur_value)
    # return sppasImage(input_array=img_edges)

    # Turn colors of the image into cartoon style
    img_color = cv2.bilateralFilter(img, d=8, sigmaColor=250, sigmaSpace=250)
    # slow: img_color = cv2.edgePreservingFilter(img, flags=2, sigma_s=50, sigma_r=0.4)
    # img_color = color_quantization_kmeans(img.copy())

    return sppasImage(input_array=cv2.bitwise_and(img_color, img_color, mask=img_edges))

# ----------------------------------------------------------------------------
# A second solution, proposed here:
# https://towardsdatascience.com/using-opencv-to-catoonize-an-image-1211473941b6
# ----------------------------------------------------------------------------


def cartoonify(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # apply gaussian blur
    img_gray = cv2.medianBlur(img_gray, 3)
    # detect edges
    img_edges = cv2.Laplacian(img_gray, -1, ksize=9)
    img_edges = 255 - img_edges

    # threshold image
    # ret, img_edges = cv2.threshold(img_edges, 150, 255, cv2.THRESH_BINARY)
    ret, img_edges = cv2.threshold(img_edges, 127, 255, cv2.THRESH_BINARY)

    # blur images heavily using edgePreservingFilter
    # img_color = cv2.edgePreservingFilter(img, flags=2, sigma_s=50, sigma_r=0.4)
    img_color = cv2.bilateralFilter(img, d=8, sigmaColor=250, sigmaSpace=250)

    # combine cartoon image and edges image
    return sppasImage(input_array=cv2.bitwise_and(img_color, img_color, mask=img_edges))

# ----------------------------------------------------------------------------
# The solution used in this script is proposed here:
# https://medium.com/nerd-for-tech/cartoonize-images-with-python-10e2a466b5fb
# ----------------------------------------------------------------------------


def icartoon(img, colorize=True):
    """Cartoonizer effect.

    :param img: (sppasImage or nb.array)
    :param colorize: (bool) Colorized result.
    :return: (sppasImage)

    """
    # Apply some Median blur on the image
    img_blur = cv2.medianBlur(img, 3)
    # Apply a bilateral filter on the image
    # d – Diameter of each pixel neighborhood that is used during filtering.
    # sigmaColor – Filter sigma in the color space. A larger value of the
    #   parameter means that farther colors within the pixel neighborhood
    #   will be mixed together, resulting in larger areas of semi-equal color.
    # sigmaSpace – Filter sigma in the coordinate space. A larger value of
    #   the parameter means that farther pixels will influence each other as
    #   long as their colors are close enough.
    # img_bf = cv2.bilateralFilter(img_blur, d=5, sigmaColor=80, sigmaSpace=80)
    img_bf = cv2.bilateralFilter(img_blur, d=3, sigmaColor=50, sigmaSpace=50)

    # Use the laplace filter to detect edges.
    # For each of the Laplacian filters we use a kernel size of 5.
    # 7 => Too many edges; 3 => not enough edges
    # 'CV_8U' means that we are using 8 bit values (0–255).
    img_lp_al = cv2.Laplacian(img_bf, cv2.CV_8U, ksize=5)

    # Laplacian of the original image detected a lot of noise.
    # The image with all the filters is the sharpest, which comes in handy in
    # a bit. This is however not yet what we want. We need an image preferably
    # black and white that we can use as a mask.
    # Convert the image to greyscale (1D)
    img_lp_al_grey = cv2.cvtColor(img_lp_al, cv2.COLOR_BGR2GRAY)

    # Each variable now contains a 1-dimensional array instead of a 3-dimensional
    # array. Next we are going to use image thresholding to set values that are
    # near black to black and set values that are near white to white.
    # Manual image thresholding
    # _, tresh_al = cv2.threshold(img_lp_al_grey, 127, 255, cv2.THRESH_BINARY)
    # Remove some additional noise
    blur_al = cv2.GaussianBlur(img_lp_al_grey, (5, 5), 0)
    # Apply a threshold (Otsu)
    _, tresh_al = cv2.threshold(blur_al, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # We now have a black image with white edges, we only have to invert the black
    # and the white for our mask.
    # Invert the black and the white
    inverted_Bilateral = cv2.subtract(255, tresh_al)

    if colorize is True:
        # Turn colors of the image into cartoon style
        img_color = cv2.bilateralFilter(img, d=8, sigmaColor=250, sigmaSpace=250)
        # slow: img_color = cv2.edgePreservingFilter(img, flags=2, sigma_s=50, sigma_r=0.4)
        # img_color = color_quantization_kmeans(img.copy())

        return sppasImage(input_array=cv2.bitwise_and(img_color, img_color, mask=inverted_Bilateral))

    return sppasImage(input_array=inverted_Bilateral)

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------


parser = ArgumentParser(usage="{:s} -i image [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to turn image or video into cartoon.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input image or video filename.')

parser.add_argument("-o",
                    metavar="file",
                    required=True,
                    help='Output filename.')

parser.add_argument("--color",
                    action='store_true',
                    help="Turn-on color. If off, the result is black&white.")

parser.add_argument("--quiet",
                    action='store_true',
                    help="Disable the verbosity.")

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

if not args.quiet:
    lgs = sppasLogSetup(0)
else:
    lgs = sppasLogSetup(30)
lgs.stream_handler()

do_color = False
if args.color:
    do_color = True

# ----------------------------------------------------------------------------

if os.path.exists(args.i) is False:
    print("Given input {:s} does not exists.".format(args.i))
    sys.exit(1)

fn, fie = os.path.splitext(args.i)
_, foe = os.path.splitext(args.o)

if fie in image_extensions and (foe in image_extensions or foe in video_extensions):
    # Load the original image
    img = sppasImage(filename=args.i)
    # Turn it into a cartoonized image
    cartoon = icartoon(img, colorize=do_color)
    # Save
    # cv2show(cartoon)
    if foe in image_extensions:
        cartoon.write(args.o)
    else:
        w, h = img.size()
        r = max(w//2, h//2)
        step = r // (3 * 25)
        # for a 3 seconds video, we'll create (3 * fps) images.
        video_writer = sppasVideoWriter()
        video_writer.set_size(w, h)
        video_writer.set_fps(25)
        video_writer.open(args.o)
        for i in range(1, 3 * 25):
            radius = i * step
            # a circular circle mask with an increasing radius
            mask = np.zeros(cartoon.shape[:2], dtype="uint8")
            # cv2.circle(image, center_coordinates, radius, color, thickness)
            cv2.circle(mask, (w // 2, h // 2), radius, 255, -1)
            masked = cv2.bitwise_and(cartoon, cartoon, mask=mask)
            video_writer.write(sppasImage(input_array=masked))
        for i in range(25):
            video_writer.write(cartoon)
        for i in reversed(range(1, 3 * 25)):
            radius = i * step
            mask = np.zeros(cartoon.shape[:2], dtype="uint8")
            # a circular circle mask with an increasing radius
            # cv2.circle(image, center_coordinates, radius, color, thickness)
            cv2.circle(mask, (w // 2, h // 2), radius, 255, -1)
            masked = cv2.bitwise_and(cartoon, cartoon, mask=mask)
            video_writer.write(sppasImage(input_array=masked))
        video_writer.close()

elif fie in video_extensions and foe in video_extensions:

    video_reader = sppasVideoReader()
    video_reader.open(args.i)
    fps = video_reader.get_framerate()
    video_writer = sppasVideoWriter()
    video_writer.open(args.o)

    frame_idx = 0
    # Read a first image then loop on the video
    frame = video_reader.read_frame(process_image=True)
    while frame is not None:
        cartoon = icartoon(frame, colorize=do_color)
        video_writer.write(cartoon)

        frame_idx += 1
        frame = video_reader.read_frame(process_image=True)
        if frame_idx % fps == 0:
            logging.info(" ... {:d} images.".format(frame_idx))

    video_reader.close()
    video_writer.close()

else:
    print("Unsupported file extension: {:s} or {:s}. Supported images are: "
          "{} and videos are: {}"
          "".format(fie, foe, image_extensions, video_extensions))
