# -*- coding : UTF-8 -*-
"""
:filename: sppas.src.videodata.videobuffer.py
:author: Brigitte Bigi
:contributor: Florian Hocquet
:contact: contact@sppas.org
:summary: Package for the management of video files.

.. _This file is part of SPPAS: <https://sppas.org/>
..
    -------------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

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
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import logging
import os
import shutil

from sppas.core.config import annots
from sppas.core.coreutils import sppasExtensionWriteError
from sppas.core.coreutils import NegativeValueError
from sppas.core.coreutils import IndexRangeException
from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import sppasTrash
from sppas.src.imgdata import sppasImage
from sppas.src.imgdata import image_extensions

from sppas.src.videodata import sppasVideoReader
from sppas.src.videodata import sppasVideoWriter

video_extensions = tuple(sppasVideoWriter.FOURCC.keys())

# ---------------------------------------------------------------------------


class sppasVideoReaderBuffer(sppasVideoReader):
    """Manage a video with a buffer (a queue) of images.

    This class allows to use a buffer of images on a video to manage it
    sequentially, and to have a better control on it.

    :Example:

    Initialize a VideoBuffer with a size of 100 images and overlap of 10:
    >>> v = sppasVideoReaderBuffer(video, 100, 10)

    Bufferize the next sequence of images of the video:
    >>> v.next()

    Release the flow taken by the reading of the video:
    >>> v.close()

    """

    DEFAULT_BUFFER_SIZE = 100
    DEFAULT_BUFFER_OVERLAP = 0
    MAX_MEMORY_SIZE = 1024*1024*1024   # 1 Gb of RAM

    # -----------------------------------------------------------------------

    def __init__(self, video=None, size=-1, overlap=DEFAULT_BUFFER_OVERLAP):
        """Create a new sppasVideoReaderBuffer instance.

        :param video: (mp4, etc...) The video filename to browse
        :param size: (int) Number of images of the buffer or -1 for auto
        :param overlap: (overlap) The number of images to keep
        from the previous buffer

        """
        super(sppasVideoReaderBuffer, self).__init__()

        # Initialization of the buffer size and buffer overlaps
        self.__nb_img = 0
        self.__overlap = 0
        self.set_buffer_size(size)
        self.set_buffer_overlap(overlap)

        # List of images
        self.__images = list()

        # First and last frame indexes of the buffer
        self.__buffer_idx = (-1, -1)

        # Initialization of the video
        if video is not None:
            self.open(video)
            if size == -1:
                self.set_buffer_size(size)

    # -----------------------------------------------------------------------

    def open(self, video):
        """Override. Create an opencv video capture from the given video.

        :param video: (name of video file, image sequence, url or video
        stream, GStreamer pipeline, IP camera) The video to browse.

        """
        self.reset()
        sppasVideoReader.open(self, video)

    # -----------------------------------------------------------------------

    def close(self):
        """Override. Release the flow taken by the reading of the video."""
        self.reset()
        sppasVideoReader.close(self)

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the buffer but does not change anything to the video."""
        # List of images
        self.__images = list()

        # Last read frame
        self.__buffer_idx = (-1, -1)

    # -----------------------------------------------------------------------

    def reset_with_start_idx(self, idx):
        """Reset AND set the index of the 1st frame of the current buffer.

        :return: (tuple) start index of the frames in the buffer

        """
        # List of images
        self.__images = list()

        # Last read frame
        idx = int(idx)
        self.__buffer_idx = (idx, idx)

    # -----------------------------------------------------------------------

    def get_buffer_size(self):
        """Return the defined size of the buffer."""
        return self.__nb_img

    # -----------------------------------------------------------------------

    def set_buffer_size(self, value=-1):
        """Set the size of the buffer.

        The new value is applied to the next buffer, it won't affect the currently in-use data.
        A value of -1 will fix automatically the buffer to use a MAX_MEMORY_SIZE Gb of RAM.

        :param value: (int) New size of the buffer.
        :raises: ValueError: invalid given value

        """
        value = int(value)
        if value == -1:
            if self.is_opened() is False:
                w, h = 1920, 1080
            else:
                w, h = self.get_width(), self.get_height()
            nbytes = w * h * 3    # 3 => uint8 for r, g, and b
            value = sppasVideoReaderBuffer.MAX_MEMORY_SIZE // nbytes
            if self.is_opened() is True and value > self.get_nframes():
                value = self.get_nframes()

        if value <= 0:
            raise NegativeValueError(value)

        # The size of the buffer can't be larger than the video size
        if self.is_opened() is True and value > self.get_nframes():
            value = self.get_nframes()
            # raise IntervalRangeException(value, 1, self.get_nframes())

        if self.__overlap >= value:
            raise ValueError("The already defined overlap value {:d} can't be "
                             "greater than the buffer size.")

        self.__nb_img = value
        logging.info("The video buffer is set to {:d} images".format(self.__nb_img))

    # -----------------------------------------------------------------------

    def get_buffer_overlap(self):
        """Return the overlap value of the buffer."""
        return self.__overlap

    # -----------------------------------------------------------------------

    def set_buffer_overlap(self, value):
        """Set the number of images to keep from the previous buffer.

        The new value is applied to the next buffer, it won't affect the
        currently in-use data.

        :param value: (int) Nb of image
        :raises: ValueError: Invalid given value

        """
        overlap = int(value)
        if overlap >= self.__nb_img or overlap < 0:
            raise ValueError("Invalid buffer overlap")
        self.__overlap = value

    # -----------------------------------------------------------------------

    def seek_buffer(self, value):
        """Set the position of the frame for the next buffer to be read.

        It won't change the current position in the video until "next" is
        invoked. It invalidates the current buffer.

        :param value: (int) Frame position

        """
        value = self.check_frame(value)
        self.reset()
        self.__buffer_idx = (-1, value-1)

    # -----------------------------------------------------------------------

    def tell_buffer(self):
        """Return the frame position for the next buffer to be read.

        Possibly, it can't match the current position in the stream, if
        video.read() was invoked for example.

        """
        return self.__buffer_idx[1] + 1

    # -----------------------------------------------------------------------

    def get_buffer_range(self):
        """Return the indexes of the frames of the current buffer.

        :return: (tuple) start index, end index of the frames in the buffer

        """
        if -1 in self.__buffer_idx:
            return -1, -1
        return self.__buffer_idx

    # -----------------------------------------------------------------------

    def next(self):
        """Fill in the buffer with the next sequence of images of the video.

        :return: False if we reached the end of the video

        """
        if self.is_opened() is False:
            return False
        # Reset the list of images
        self.__images = list()

        # Fix the number of frames to read
        nb_frames = self.__nb_img - self.__overlap
        # But if it's the first frame loading, we'll fill in the buffer of the
        # full size, i.e. no overlap is to be applied.
        if self.__buffer_idx[1] == -1:
            nb_frames = self.__nb_img

        # Set the beginning position to read in the video
        start_frame = self.__buffer_idx[1] + 1
        if start_frame >= self.get_nframes():
            # no remaining frames in the video.
            return False

        # Launch and store the result of the reading
        result = self.__load_frames(start_frame, nb_frames)
        next_frame = start_frame + len(result)

        # Update the buffer and the frame indexes with the current result
        delta = self.__nb_img - self.__overlap
        self.__images = self.__images[delta:]
        self.__buffer_idx = (start_frame - len(self.__images), next_frame - 1)
        self.__images.extend(result)
        result.clear()

        return next_frame < self.get_nframes()

    # -----------------------------------------------------------------------

    def check_buffer_index(self, value):
        """Raise an exception if the given image index is not valid.

        :param value: (int)
        :raises: NegativeValueError
        :raises: IndexRangeException

        """
        value = int(value)
        if value < 0:
            raise NegativeValueError(value)
        (begin, end) = self.get_buffer_range()
        #if begin == -1 or end == -1:
        #    raise ValueError("Invalid index value: no buffer is loaded.")
        if value < self.get_buffer_size():
            return value

        raise IndexRangeException(value, 0, self.get_buffer_size())

    # -----------------------------------------------------------------------

    def append(self, image):
        """Append an image into the buffer and pop the first if full queue.

        :param image: (sppasImage) A new image to append to the list

        """
        if isinstance(image, sppasImage) is False:
            raise sppasTypeError(type(image), "sppasImage")

        self.__images.append(image)
        if len(self.__images) > self.__nb_img:
            self.__images.pop(0)

    # -----------------------------------------------------------------------

    def pop(self, img_idx):
        """Pop an image of the buffer.

        :param img_idx: (int) Index of the image in the buffer
        :raise: IndexRangeException

        """
        img_idx = int(img_idx)
        if 0 <= img_idx < self.get_buffer_size():
            self.__images.pop(img_idx)
        else:
            raise IndexRangeException(img_idx, 0, self.get_buffer_size())

    # -----------------------------------------------------------------------

    def set_at(self, img, img_idx):
        """Set an image of the buffer.

        No verification is performed on the image. It should be the
        same format (size, nb channels, etc) than the other ones.
        Use this method with caution!

        :param img: (sppasImage) Set the image in the buffer
        :param img_idx: (int) Index of the image in the buffer
        :raises: IndexRangeException

        """
        img_idx = int(img_idx)
        if 0 <= img_idx < self.get_buffer_size():
            self.__images[img_idx] = img
        else:
            raise IndexRangeException(img_idx, 0, self.get_buffer_size())

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __load_frames(self, start_frame, nb_frames):
        """Browse a sequence of a video.

        :return: (list) List of either sppasImage or None

        """
        self.seek(start_frame)

        # Fix the exact number of frames to load: adjust nb_frames.
        # It's required to stop reading when the end is reached!
        if start_frame + nb_frames > self.get_nframes():
            logging.info("Not enough remaining {:d} frames. Will read {:d} instead."
                         "".format(nb_frames, self.get_nframes() - start_frame))
            nb_frames = self.get_nframes() - start_frame

        # Create the list to store the images
        images = [None]*nb_frames

        # Browse the video
        for i in range(nb_frames):
            # Grab the next frame.
            images[i] = self.read_frame()
            if images[i] is None:
                logging.warning("A problem occurred when reading image at index {:d}. "
                                "The image is set to 'None' instead.".format(i))

        return images

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of images in the current data buffer."""
        return len(self.__images)

    # -----------------------------------------------------------------------

    def __iter__(self):
        """Browse the current data buffer."""
        for img in self.__images:
            yield img

    # -----------------------------------------------------------------------

    def __getitem__(self, item):
        return self.__images[item]

    # -----------------------------------------------------------------------

    def __str__(self):
        liste = [""]*len(self.__images)
        iterator = self.__iter__()
        for i in range(len(self.__images)):
            liste[i] = str(next(iterator)) + "\n"
        return liste

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

# ---------------------------------------------------------------------------


class sppasBufferVideoWriter(object):
    """Write a video and/or a set of images into files.

    There are 2 main solutions to write the result (video+images):

        1. video
        2. folder with images

    """

    def __init__(self):
        """Create a new instance.

        """
        self._video_writer = None

        # Options
        self._video = False   # save the images of the buffer in a video
        self._folder = False  # save results as images in a folder
        self._fps = 25.       # default video framerate -- important

        # The default output file extensions
        self._video_ext = annots.video_extension
        self._image_ext = annots.image_extension

    # -----------------------------------------------------------------------
    # Getters and setters for the options
    # -----------------------------------------------------------------------

    def get_video_extension(self):
        """Return the extension for video files."""
        return self._video_ext

    # -----------------------------------------------------------------------

    def set_video_extension(self, ext):
        """Set the extension of video files."""
        ext = str(ext)
        if ext.startswith(".") is False:
            ext = "." + ext
        if ext not in video_extensions:
            raise sppasExtensionWriteError(ext)

        self._video_ext = ext

    # -----------------------------------------------------------------------

    def get_image_extension(self):
        """Return the extension for image files."""
        return self._image_ext

    # -----------------------------------------------------------------------

    def set_image_extension(self, ext):
        """Set the extension of image files."""
        ext = str(ext)
        if ext.startswith(".") is False:
            ext = "." + ext
        if ext not in image_extensions:
            raise sppasExtensionWriteError(ext)

        self._image_ext = ext

    # -----------------------------------------------------------------------

    def get_fps(self):
        """Return the defined fps value to write video files (float)."""
        return self._fps

    # -----------------------------------------------------------------------

    def set_fps(self, value):
        """Fix the framerate of the output video.

        :param value: (float) Number of frames per seconds
        :raise: NegativeValueError, IntervalRangeError

        """
        # if the value isn't correct, sppasVideoWriter() will raise an exc.
        w = sppasVideoWriter()
        w.set_fps(value)
        self._fps = value

    # -----------------------------------------------------------------------

    def get_video_output(self):
        """Return True if images will be saved into a video, as it."""
        return self._video

    # -----------------------------------------------------------------------

    def get_folder_output(self):
        """Return True if results will be saved in a folder of image files."""
        return self._folder

    # -----------------------------------------------------------------------

    def set_video_output(self, value):
        """Set true to enable the output of the video."""
        self._video = bool(value)

    # -----------------------------------------------------------------------

    def set_folder_output(self, value):
        """Set true to enable the output of the folder of images."""
        self._folder = bool(value)

    # -----------------------------------------------------------------------
    # Write into VIDEO or IMAGES
    # -----------------------------------------------------------------------

    def is_opened(self):
        """Return True of the video writer opened a video stream."""
        return self._video_writer is not None

    # -----------------------------------------------------------------------

    def close(self):
        """Close the sppasVideoWriter().

        It has to be invoked when writing buffers is finished in order to
        release the video writer.

        """
        if self._video_writer is not None:
            self._video_writer.close()
            self._video_writer = None

    # -----------------------------------------------------------------------

    def write(self, video_buffer, out_name, opt_pattern=""):
        """Save the result into file(s) depending on the options.

        The out_name is a base name, its extension is ignored and replaced by
        the one(s) defined in this class.

        :param video_buffer: (sppasCoordsVideoBuffer) The images and results to write
        :param out_name: (str) The output name for the folder and/or the video
        :param opt_pattern: (str) Un-used
        :return: list of newly created file names

        """
        new_files = list()

        # Remove any existing extension, and ignore it!
        fn, _ = os.path.splitext(out_name)
        out_name = fn

        # Write results in VIDEO format
        if self._video is True:
            new_video_files = self.write_video(video_buffer, out_name, opt_pattern)
            if len(new_video_files) > 1:
                logging.info("{:d} video files created".format(len(new_video_files)))
            new_files.extend(new_video_files)

        # Write results in IMAGE format
        if self._folder is True:
            new_image_files = self.write_folder(video_buffer, out_name, opt_pattern)
            if len(new_image_files) > 1:
                logging.info("{:d} image files created".format(len(new_image_files)))
            # If too many files are created, they can't be added to the GUI...
            # TODO: Find a solution in the GUI to deal with a huge nb of files
            # then un-comment the next line
            # new_files.extend(new_image_files)

        return new_files

    # -----------------------------------------------------------------------

    def write_video(self, video_buffer, out_name, pattern):
        """Save the result in video format.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The filename of the output video file
        :param pattern: (str) Pattern to add to video filename
        :return: list of newly created video file names

        """
        new_files = list()
        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            # Get the i-th image of the buffer
            image = next(iter_images)

            # Create the sppasVideoWriter() if it wasn't already done.
            # An image is required to properly fix the video size.
            if self._video_writer is None:
                self._video_writer, fn = self.create_video_writer(out_name, image, pattern)
                new_files.append(fn)

            # Write the image
            self._video_writer.write(image)

        return new_files

    # -----------------------------------------------------------------------

    def write_folder(self, video_buffer, out_name, pattern=""):
        """Save the result in image format into a folder.

        :param video_buffer: (sppasImage) The image to write
        :param out_name: (str) The folder name of the output image files
        :param pattern: (str) Pattern to add to folder name(s)

        """
        new_files = list()

        # Create the directory with all results
        folder_name = "{:s}{:s}".format(out_name, pattern)
        if os.path.exists(folder_name) is False:
            os.mkdir(folder_name)

        # Create a folder to save results of this buffer
        begin_idx, end_idx = video_buffer.get_buffer_range()
        folder = os.path.join(folder_name, "{:06d}".format(begin_idx))
        if os.path.exists(folder) is True:
            shutil.rmtree(folder)
        os.mkdir(folder)

        iter_images = video_buffer.__iter__()
        for i in range(video_buffer.__len__()):
            # Get the i-th image of the buffer
            image = next(iter_images)
            # Fix the name of the output file
            img_name = self._image_name(begin_idx + i) + self._image_ext
            # Write the image into the folder
            image.write(os.path.join(folder, img_name))
            new_files.append(os.path.join(folder, img_name))

        return new_files

    # -----------------------------------------------------------------------

    def create_video_writer(self, out_name, image, pattern=""):
        """Create a sppasVideoWriter().

        :raise: PermissionError

        """
        # Fix width and height of the video
        w, h = image.size()

        # Fix the video filename
        filename = "{:s}{:s}".format(out_name, pattern) + self._video_ext
        logging.debug("Create a video writer {:s}. Size {:d}, {:d}"
                      "".format(filename, w, h))

        if os.path.exists(filename) is True:
            logging.warning("A file with name {:s} is already existing.".format(filename))
            trash_filename = sppasTrash().put_file_into(filename)
            logging.info("The file was moved into the Trash of SPPAS "
                         "with name: {:s}".format(trash_filename))

        # Create a writer
        try:
            writer = sppasVideoWriter()
            writer.set_size(w, h)
            writer.set_fps(self._fps)
            writer.set_aspect("extend")
            writer.open(filename)
            logging.debug(" ... Video writer opened successfully for {}".format(filename))
        except Exception as e:
            logging.error("OpenCV failed to open the VideoWriter for file "
                          "{}: {}".format(filename, str(e)))
            return None

        return writer, filename

    # -----------------------------------------------------------------------

    @staticmethod
    def _image_name(idx):
        """Return an image name from its index."""
        return "img_{:06d}".format(idx)
