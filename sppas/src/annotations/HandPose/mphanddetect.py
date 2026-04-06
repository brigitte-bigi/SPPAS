"""
:filename: sppas.src.annotations.HandPose.mphanddetect.py
:author:   Brigitte Bigi
:contact:  contact@sppas.org
:summary:  MediaPipe detector of hand in an image.

.. _This file is part of SPPAS: https://sppas.org/
..
    ---------------------------------------------------------------------

     ######   ########   ########      ###      ######
    ##    ##  ##     ##  ##     ##    ## ##    ##    ##     the automatic
    ##        ##     ##  ##     ##   ##   ##   ##            annotation
     ######   ########   ########   ##     ##   ######        and
          ##  ##         ##         #########        ##        analysis
    ##    ##  ##         ##         ##     ##  ##    ##         of speech
     ######   ##         ##         ##     ##   ######

    Copyleft (C) 2011-2024  Brigitte Bigi
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

    ---------------------------------------------------------------------

"""

import logging
import mediapipe as mp
import numpy

from sppas.core.coreutils import sppasTypeError
from sppas.core.coreutils import IntervalRangeException
from sppas.core.coreutils import sppasError
from sppas.src.imgdata import sppasCoords
from sppas.src.imgdata import sppasSights
from sppas.src.imgdata import sppasImage

# ---------------------------------------------------------------------------


class HandTypes(object):
    """Enumerates all types of hand detection: LEFT, RIGHT or BOTH.

    :Example:
        >>>with HandTypes() as s:
        >>>    print(s.BOTH)

    """

    def __init__(self):
        """Create the dictionary."""
        self.__dict__ = dict(
            RIGHT=0,
            LEFT=1,
            BOTH=2
        )

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        pass

# ---------------------------------------------------------------------------


class MediaPipeHandPoseDetector(object):
    """SPPAS wrapper of MediaPipe Hand Detection and Pose Detection.

    See <https://google.github.io/mediapipe/solutions/hands.html>
    See <https://google.github.io/mediapipe/solutions/pose.html>
    for details:

    MediaPipe Hands is a high-fidelity hand and finger tracking solution.
    It employs machine learning (ML) to infer 21 3D landmarks of a hand
    from just a single frame.
    MediaPipe Hands utilizes an ML pipeline consisting of multiple models
    working together: A palm detection model that operates on the full image
    and returns an oriented hand bounding box. A hand landmark model that
    operates on the cropped image region defined by the palm detector and
    returns high-fidelity 3D hand key points.

    Important:

        - If enabled, only one pose can be detected, and 2 hands at max.
        - If pose is disabled, more than 2 hands can be detected.

    """

    # Link between Hand sights and Pose sights of fingers (right, left)
    HANDS = dict()
    HANDS[0] = (16, 15)   # WRIST
    HANDS[4] = (22, 21)   # THUMB
    HANDS[8] = (20, 19)   # INDEX
    HANDS[20] = (18, 17)  # PINKY

    # -----------------------------------------------------------------------

    def __init__(self):
        # The hand and finger detector
        self._detector = None
        self._rescue_detector = None
        # The pose detector (body)
        self._pose_detector = None

        # The list of hands, each one with its 21 detected sights
        self._hands = list()   # sights of hands
        self._coords = list()  # coordinates of hands

        # The pose is 32 detected sights
        self._pose = None   # sights of the body

        # Store the z-value results of the detector
        self.__mesh_mode = False

    # -----------------------------------------------------------------------

    def invalidate(self):
        """Invalidate current lists of sight values."""
        self._hands = list()
        self._coords = list()
        self._pose = None

    # -----------------------------------------------------------------------

    def enable_mesh(self, value=True):
        """Enable the mesh mode.

        :param value: (bool) True to enable z-values

        """
        self.__mesh_mode = bool(value)

    # -----------------------------------------------------------------------

    @staticmethod
    def hand_sights():
        return 21

    # -----------------------------------------------------------------------

    def get_hand_sights(self, hand_idx):
        """Return a copy of the sights of a given hand.

        :param hand_idx: Index of the hand
        :return: (sppasSights)
        :raises: IntervalRangeException

        """
        if hand_idx < 0 or hand_idx >= len(self._coords):
            raise IntervalRangeException(hand_idx, 0, len(self._coords)-1)
        return self._hands[hand_idx].copy()

    # -----------------------------------------------------------------------

    def get_hand_coordinates(self, hand_idx):
        """Return a copy of the coordinates of a given hand.

        :param hand_idx: Index of the hand
        :return: (sppasCoords)
        :raises: IntervalRangeException

        """
        if hand_idx < 0 or hand_idx >= len(self._coords):
            raise IntervalRangeException(hand_idx, 0, len(self._coords)-1)
        return self._coords[hand_idx].copy()

    # -----------------------------------------------------------------------

    def get_pose_sights(self):
        """Return a copy of the 32 body sights.

        :return: (sppasSights or None)

        """
        if self._pose is None:
            return None
        return self._pose.copy()

    # -----------------------------------------------------------------------

    def load_model(self, model=None, *args):
        """Instantiate the detectors.

        :param model: Unused.

        """
        self._set_detector()

    # -----------------------------------------------------------------------

    def get_best_hand_idx(self):
        """Return the index of the hand with the better score (or -1).

        """
        if len(self._coords) == 0:
            return -1
        maxi = 0
        for i, c in enumerate(self._coords):
            if c.get_confidence() > self._coords[maxi].get_confidence():
                maxi = i
        return maxi

    # -----------------------------------------------------------------------

    def get_best_overlapping_hand_idx(self, coords, min_ratio=0.):
        """Return the index of the hand with the best intersection (or -1).

        Search for a detected hand that is overlapping the given coords
        and check if their overlapping area is large enough.

        :param coords: (sppasCoords) The area to be considered
        :param min_ratio: (float) Minimum ratio between the coords and the hand areas
        :return: hand_idx or -1

        """
        if len(self._coords) == 0:
            return -1

        overlapping_area = 0
        overlapping_idx = -1
        for hand_idx in range(len(self._hands)):
            hand_coords = self._coords[hand_idx]
            intersect = coords.intersection_area(hand_coords)
            if intersect > overlapping_area:
                overlapping_idx = hand_idx
                overlapping_area = intersect

        # Check if the overlapping area is large enough to be considered
        area = coords.area()
        if area > 0:
            ratio = float(overlapping_area) / float(coords.area())
            if ratio >= min_ratio:
                return overlapping_idx

        return -1

    # -----------------------------------------------------------------------
    # Detection is here
    # -----------------------------------------------------------------------

    def detect(self, image):
        """Detect sights of a human body and of his hands on an image.

        sppasSights of the hands&pose are internally stored.
        Get access with an iterator for hands or getters.

        Return value is :
             -1 if no pose detected
            - 0 if a pose is detected but no hand
            - 1 if a pose is detected and one hand
            - 2 if a pose is detected and two hands

        :param image: (sppasImage or numpy.ndarray) The image to be processed.
        :return: (int)

        """
        if self._pose_detector is None or self._detector is None:
            raise sppasError("The detectors were not initialized.")
        # Convert image to sppasImage, if needed.
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_array=image)
        # Remove alpha channel
        img = image.ibgra_to_bgr()
        # Convert the BGR image to RGB before processing
        img = img.ito_rgb()
        img = img.iuint8()

        # Delete previous results and prepare this detection
        self.invalidate()

        # Process the pose predictions on the given image
        success = self._detect_pose(img)
        if success is True and len(self._hands) > 1 and len(self._coords) > 1:
            success = 0

            # Make a copy of the currently detected pose, hand and coords
            copied_coords = [c.copy() for c in self._coords]
            copied_hands = [h.copy() for h in self._hands]
            self._hands = list()
            self._coords = list()

            # Process the hands predictions on the given image
            success = self._detect_hands(img)
            if success is False:
                success = self._detect_hands(img, rescue=True)

            # Make a match between the detected hands from pose and from hand detection
            # for right and left hands
            for h in (0, 1):
                hands, coords = self.__match_pose_with_hands(img, copied_coords[h])
                if hands is not None:
                    success += 1
                    copied_hands[h] = hands
                    copied_coords[h] = coords
                    for fh in MediaPipeHandPoseDetector.HANDS:
                        self._pose.set_sight(MediaPipeHandPoseDetector.HANDS[fh][h],
                                             hands.x(fh), hands.y(fh))

            self._hands = copied_hands
            self._coords = copied_coords
            return success
        else:
            logging.debug(" - no pose detected.")

        return -1

    # -----------------------------------------------------------------------

    def detect_hands(self, image):
        """Detect sights of hands on an image.

        sppasSights of the hands are internally stored.
        Get access with an iterator or getters.

        :param image: (sppasImage or numpy.ndarray) The image to be processed.

        """
        if self._detector is None:
            raise sppasError("The hand detector was not initialized.")
        # Convert image to sppasImage if necessary
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_array=image)
        # remove alpha channel
        img = image.ibgra_to_bgr()
        # convert the BGR image to RGB before processing
        img = img.ito_rgb()

        # Delete previous results
        self.invalidate()

        # Make predictions on the given image.
        success = self._detect_hands(img.iuint8())
        if success is False:
            success = self._detect_hands(img.iuint8(), rescue=True)
            if success is False:
                logging.info(" - no hand detected.")
        return success

    # -----------------------------------------------------------------------

    def detect_pose(self, image):
        """Determine the sights of the detected pose.

        Important: Only one pose can be detected.

        :param image: (sppasImage or numpy.ndarray)

        """
        if self._pose_detector is None:
            raise sppasError("The pose detector was not initialized.")
        # Convert image to sppasImage if necessary
        if isinstance(image, sppasImage) is False:
            image = sppasImage(input_array=image)
        # remove alpha channel
        img = image.ibgra_to_bgr()
        # convert the BGR image to RGB before processing
        img = img.ito_rgb()

        # Delete previous results
        self.invalidate()

        # Make predictions on the given image.
        success = self._detect_pose(img)
        return success

    # -----------------------------------------------------------------------
    # Utility
    # -----------------------------------------------------------------------

    @staticmethod
    def to_dtype(value, dtype=int):
        """Convert a value to dtype or raise the appropriate exception.

        :param value: (any type)
        :param dtype: (type) Expected type of the value
        :return: Value of the given type
        :raises: TypeError

        """
        try:
            value = dtype(value)
            if isinstance(value, dtype) is False:
                raise sppasTypeError(value, str(dtype))
        except ValueError:
            raise sppasTypeError(value, str(dtype))

        return value

    # -----------------------------------------------------------------------
    # Private estimators
    # -----------------------------------------------------------------------

    def _set_detector(self):
        """Initialize the detector.

        :raises: Exception

        """
        self._detector = None
        self._rescue_detector = None
        self._pose_detector = None
        try:
            self._detector = mp.solutions.hands.Hands(
                static_image_mode=True,
                model_complexity=0,       # (0=low / 1=high). 0 detects more hands
                max_num_hands=20,
                min_detection_confidence=0.05
               )
            self._rescue_detector = mp.solutions.hands.Hands(
                static_image_mode=True,
                model_complexity=1,  # 0 detects more hands in large images, 1 in small images
                max_num_hands=20,
                min_detection_confidence=0.01
               )
            self._pose_detector = mp.solutions.pose.Pose(
                static_image_mode=True,     # really worse results if False
                model_complexity=1,         # (0=low / 1=medium / 2=high)
                enable_segmentation=False,
                min_detection_confidence=self.__min_score)
        except:
            try:
                # The version of mediapipe is too old.
                # model_complexity and enable_segmentation are not recognized;
                # but there's no mediapipe.__version__ to test it before!
                self._detector = mp.solutions.hands.Hands(
                    static_image_mode=True,
                    max_num_hands=20,
                    min_detection_confidence=0.1
                   )
                self._rescue_detector = mp.solutions.hands.Hands(
                    static_image_mode=True,
                    max_num_hands=20,
                    min_detection_confidence=0.01
                   )
                self._pose_detector = mp.solutions.pose.Pose(
                    static_image_mode=True,     # really worse results if False
                    min_detection_confidence=0.01)
            except Exception as e:
                logging.error("MediaPipe hand or pose detection system failed "
                              "to be instantiated.")
                raise sppasError(str(e))

    # -----------------------------------------------------------------------

    def _detect_hands(self, image, handtype=HandTypes().BOTH, rescue=False):
        """Determine the coordinates of the detected hands.

        :param image: (sppasImage)
        :param handtype: (HandType) RIGHT, LEFT or BOTH will be selected among those detected
        :param rescue: (bool) Use the rescue detector instead of the default one

        """
        w, h = image.size()
        if w*h == 0:
            return False

        # make predictions
        if rescue is False:
            results = self._detector.process(image)
        else:
            results = self._rescue_detector.process(image)

        # Convert detections of each hand into a list of sppasSights
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                sights = sppasSights(nb=21)
                for i in range(len(hand.landmark)):
                    # the x- and y- coordinates are normalized screen coordinates
                    mark = hand.landmark[i]
                    x_coord = max(0, int(mark.x * float(w)))
                    y_coord = max(0, int(mark.y * float(h)))
                    if self.__mesh_mode is False:
                        sights.set_sight(i, x_coord, y_coord)
                    else:
                        # 'z' represents the landmark depth with the depth at the
                        # wrist being the origin, and the smaller the value the
                        # closer the landmark is to the camera. The magnitude of
                        # 'z' uses roughly the same scale as 'x'.
                        z_coord = max(0, int(mark.z * float(w)))
                        sights.set_sight(i, x_coord, y_coord, z_coord)
                self._hands.append(sights)
                coords = self._fix_hand_coords(sights)
                self._coords.append(coords)

            if handtype != HandTypes().BOTH:
                self.__filter_handtype(results, handtype)

            if len(self._hands) > 0:
                return True

        return False

    # -----------------------------------------------------------------------

    def __filter_handtype(self, results,  handtype):
        """Remove Left or Right hands."""
        # Filter hands: keep only the ones of the given hand type
        # and set the confidence score
        if len(results.multi_hand_landmarks) != len(results.multi_handedness):
            logging.error("Hum... multi_hand_landmarks != multi_handedness")
            return
        to_remove = list()
        for i, hand in enumerate(results.multi_handedness):
            if len(hand.classification) > 0:
                if handtype == HandTypes().RIGHT and hand.classification[0].label != "Right":
                    to_remove.append(i)
                elif handtype == HandTypes().LEFT and hand.classification[0].label != "Left":
                    to_remove.append(i)
                else:
                    self._coords[i].set_confidence(hand.classification[0].score)
        for i in reversed(to_remove):
            self._hands.pop(to_remove[i])
            self._coords.pop(to_remove[i])

    # -----------------------------------------------------------------------

    def _detect_pose(self, image):
        """Determine the 32 sights of the detected human body.

        If there are more than one human in the picture, only one is
        detected.

        :param image: (sppasImage or numpy.ndarray)

        """
        # make predictions
        results = self._pose_detector.process(image)

        # Convert detections of each hand into a list of sppasSights
        if results.pose_landmarks:
            w, h = image.size()
            self._pose = sppasSights(nb=len(results.pose_landmarks.landmark))
            for i, mark in enumerate(results.pose_landmarks.landmark):
                # the x- and y- coordinates are normalized screen coordinates
                x_coord = max(0, int(mark.x * float(w)))
                y_coord = max(0, int(mark.y * float(h)))
                if self.__mesh_mode is False:
                    self._pose.set_sight(i, x_coord, y_coord)
                else:
                    # 'z' represents the landmark depth with the depth at the
                    # wrist being the origin, and the smaller the value the
                    # closer the landmark is to the camera. The magnitude of
                    # 'z' uses roughly the same scale as 'x'.
                    z_coord = max(0, int(mark.z * float(w)))
                    self._pose.set_sight(i, x_coord, y_coord, z_coord, mark.visibility)

            # Update hands coordinates and sights
            right_hand_sights = sppasSights(4)
            right_hand_sights.set_sight(0, self._pose.x(16), self._pose.y(16))
            right_hand_sights.set_sight(1, self._pose.x(18), self._pose.y(18))
            right_hand_sights.set_sight(2, self._pose.x(20), self._pose.y(20))
            right_hand_sights.set_sight(3, self._pose.x(22), self._pose.y(22))
            self._hands.append(right_hand_sights)
            right_coords = self._fix_hand_coords(right_hand_sights)
            self._coords.append(right_coords)

            left_hand_sights = sppasSights(4)
            left_hand_sights.set_sight(0, self._pose.x(15), self._pose.y(15))
            left_hand_sights.set_sight(1, self._pose.x(17), self._pose.y(17))
            left_hand_sights.set_sight(2, self._pose.x(19), self._pose.y(19))
            left_hand_sights.set_sight(3, self._pose.x(21), self._pose.y(21))
            left_coords = self._fix_hand_coords(left_hand_sights)
            self._coords.append(left_coords)
            self._hands.append(left_hand_sights)
            return True

        return False

    # -----------------------------------------------------------------------

    def __match_pose_with_hands(self, image, coords):
        """Search for a match between the detected hands of mp and the coords.

        """
        new_hand_sights = None
        new_coords = None

        # Search for a detected hand that is overlapping the given coords
        overlapping_idx = self.get_best_overlapping_hand_idx(coords)
        if overlapping_idx != -1:
            # A hand of the hand detection system is matching
            logging.debug("  - a hand is matching (overlapping)")
            new_hand_sights = self._hands[overlapping_idx].copy()
            new_coords = self._coords[overlapping_idx].copy()

        else:
            # No detected hand is matching the right hand of the pose detection
            # Rescue with a hand detection in a more specific restricted area
            # save current results
            copy_hands = [h.copy() for h in self._hands]
            copy_coords = [c.copy() for c in self._coords]

            # crop the original image to get a larger hand area
            zoomed_coords = coords.copy()
            maxi = -1
            try:
                self._adjust_hand_coords(zoomed_coords, image)
                # detect the hands in the cropped part
                success = self._detect_hands(image.icrop(zoomed_coords))
                if success is False:
                    success = self._detect_hands(image.icrop(zoomed_coords), rescue=True)
                maxi = self.get_best_overlapping_hand_idx(coords)
            except IntervalRangeException as e:
                logging.warning(str(e))
            if maxi != -1:
                new_hand_sights = self._hands[maxi].copy()
                # re-adjust (x,y) because we cropped the image...
                for i, sight in enumerate(new_hand_sights):
                    x, y, z, s = sight
                    x += zoomed_coords.x
                    y += zoomed_coords.y
                    new_hand_sights.set_sight(i, x, y, z, s)
                new_coords = self._fix_hand_coords(new_hand_sights)
                new_coords.set_confidence(self._coords[maxi].get_confidence())
                logging.debug("  - a hand is matching (cropping)")
            else:
                logging.debug("  - no hand is matching among the {:d} detected"
                              "".format(len(self._hands)))

            # restore results
            self._hands = copy_hands
            self._coords = copy_coords

        return new_hand_sights, new_coords

    # -----------------------------------------------------------------------

    def _fix_hand_coords(self, sights):
        """Return the coords surrounding the hand."""
        all_x = sights.get_x()
        all_y = sights.get_y()
        min_x = min(all_x)
        min_y = min(all_y)
        max_x = max(all_x)
        max_y = max(all_y)
        w = max_x - min_x
        h = max_y - min_y

        return sppasCoords(min_x, min_y, w, h)

    # -----------------------------------------------------------------------

    def _adjust_hand_coords(self, coord, image=None, min_s=512):
        """Adjust the coords with a given min size .

        Min size won't be more than the image size and less than 8 times
        the coords size.

        :raises: TypeError, IntervalRangeException, ImageWidthError, ImageHeightError

        """
        w = coord.w
        h = coord.h
        if w*h == 0:
            return
        min_size = min(image.width, image.height, max(min_s, 4*w, 4*h))
        r1 = float(min_size) / float(w)
        r2 = float(min_size) / float(h)

        shift_x, shift_y = coord.scale(max(r1, r2))
        if image is None:
            coord.shift(shift_x, shift_y)
        else:
            try:
                coord.shift(shift_x, 0, image)
                shifted_x = True
            except:
                shifted_x = False
            try:
                coord.shift(0, shift_y, image)
                shifted_y = True
            except:
                shifted_y = False

            w, h = image.size()
            if coord.x + coord.w > w or shifted_x is False:
                coord.x = max(0, w - coord.w)

            if coord.y + coord.h > h or shifted_y is False:
                coord.y = max(0, h - coord.h)

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __len__(self):
        """Return the number of detected hands."""
        return len(self._hands)

    # -----------------------------------------------------------------------

    def __iter__(self):
        for i in range(len(self._hands)):
            yield self._hands[i]

    # ----------------------------------------------------------------------

    def __getitem__(self, i):
        return self._hands[i]

    # -----------------------------------------------------------------------

    def __repr__(self):
        return self.__class__.__name__

    # -----------------------------------------------------------------------

    def __format__(self, fmt):
        return str(self).__format__(fmt)

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        del self._detector
        del self._pose_detector
        del self._rescue_detector
