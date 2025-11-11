"""
:filename: sppas.src.imgdata.tests.test_coordinates.py
:author:   Florian Hocquet, Brigitte Bigi
:contact:  contact@sppas.org
:summary:  Tests of the sppasCoordinates class.

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

import unittest
import math

from sppas.src.imgdata.coordinates import sppasCoords

# ---------------------------------------------------------------------------


class TestCoordinates(unittest.TestCase):

    def setUp(self):
        self.__coordinates = sppasCoords(143, 17, 150, 98, 0.7)

    # ------------------------------------------------------------------------

    def test_init(self):
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.7)
        x = self.__coordinates.x
        self.assertEqual(x, 143)
        y = self.__coordinates.y
        self.assertEqual(y, 17)
        w = self.__coordinates.w
        self.assertEqual(w, 150)
        h = self.__coordinates.h
        self.assertEqual(h, 98)

    # ------------------------------------------------------------------------

    def test_dtype(self):
        c = sppasCoords().to_dtype(3)
        self.assertEqual(c, 3)
        self.assertTrue(isinstance(c, int))
        self.assertFalse(isinstance(c, float))

        c = sppasCoords().to_dtype(3, float)
        self.assertEqual(c, 3.)
        self.assertTrue(isinstance(c, float))
        self.assertFalse(isinstance(c, int))

        c = sppasCoords().to_dtype(3, float, unsigned=False)
        self.assertEqual(c, 3.)
        self.assertTrue(isinstance(c, float))
        self.assertFalse(isinstance(c, int))

        # The default is unsigned values
        with self.assertRaises(TypeError):
            c = sppasCoords().to_dtype(-3)

        # Force to signed value
        c = sppasCoords().to_dtype(-3, unsigned=False)
        self.assertEqual(c, -3)
        self.assertTrue(isinstance(c, int))
        self.assertFalse(isinstance(c, float))

    # ------------------------------------------------------------------------

    def test_get_set_confidence(self):
        self.__coordinates.set_confidence(0.5)
        confidence = self.__coordinates.get_confidence()
        self.assertEqual(confidence, 0.5)

        with self.assertRaises(TypeError):
            self.__coordinates.set_confidence("Bonjour")

        with self.assertRaises(ValueError):
            self.__coordinates.set_confidence(-0.7)

        with self.assertRaises(ValueError):
            self.__coordinates.set_confidence(1.1)

    # ------------------------------------------------------------------------

    def test_get_set_x(self):
        self.__coordinates.x = 18
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.x = "Bonjour"
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.x = -5
        x = self.__coordinates.x
        self.assertEqual(x, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.x = 30721
        x = self.__coordinates.x
        self.assertEqual(x, 18)

    # ------------------------------------------------------------------------

    def test_get_set_y(self):
        self.__coordinates.y = 18
        y = self.__coordinates.y
        self.assertEqual(y, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.y = "Bonjour"
        y = self.__coordinates.y
        self.assertEqual(y, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.y = -5
            y = self.__coordinates.y
            self.assertEqual(y, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.y = 30721
        y = self.__coordinates.y
        self.assertEqual(y, 18)

    # ------------------------------------------------------------------------

    def test_get_set_w(self):
        self.__coordinates.w = 18
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.w = "Bonjour"
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.w = -5
        w = self.__coordinates.w
        self.assertEqual(w, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.w = 30721
        w = self.__coordinates.w
        self.assertEqual(w, 18)

    # ------------------------------------------------------------------------

    def test_get_set_h(self):
        self.__coordinates.h = 18
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.h = "Bonjour"
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(TypeError):
            self.__coordinates.h = -5
        h = self.__coordinates.h
        self.assertEqual(h, 18)

        with self.assertRaises(ValueError):
            self.__coordinates.h = 30721
        h = self.__coordinates.h
        self.assertEqual(h, 18)

    # ------------------------------------------------------------------------

    def test_unsigned(self):
        with self.assertRaises(TypeError):
            coordinates = sppasCoords(-143, -17, 150, 98)
        coordinates = sppasCoords(-143, -17, 150, 98, unsigned=False)
        self.assertEqual(coordinates.x, -143)
        self.assertEqual(coordinates.y, -17)

    # ------------------------------------------------------------------------

    def test_scale(self):
        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale(2.)
        self.assertEqual(coordinates.w, 300)
        self.assertEqual(coordinates.h, 196)
        self.assertEqual(shift_x, -75)
        self.assertEqual(shift_y, -49)

        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale(3)
        self.assertEqual(coordinates.w, 450)
        self.assertEqual(coordinates.h, 294)
        self.assertEqual(shift_x, -150)

        coordinates = sppasCoords(143, 17, 150, 98)
        shift_x, shift_y = coordinates.scale("0.5")
        self.assertEqual(coordinates.w, 75)
        self.assertEqual(coordinates.h, 49)
        self.assertEqual(shift_x, 37)  # it's 37.5... rounded to 37.

        with self.assertRaises(TypeError):
            self.__coordinates.scale("a")

    # ------------------------------------------------------------------------

    def test_shift(self):
        self.__coordinates.shift(20)
        x = self.__coordinates.x
        self.assertEqual(x, 163)

        self.__coordinates.shift(-20)
        x = self.__coordinates.x
        self.assertEqual(x, 143)

        self.__coordinates.shift(20, 10)
        x = self.__coordinates.x
        y = self.__coordinates.y
        self.assertEqual(x, 163)
        self.assertEqual(y, 27)

        self.__coordinates.shift(-20, -10)
        x = self.__coordinates.x
        y = self.__coordinates.y
        self.assertEqual(x, 143)
        self.assertEqual(y, 17)

        with self.assertRaises(TypeError):
            self.__coordinates.shift("a", "a")

        self.__coordinates.shift(20, -20)
        y = self.__coordinates.y
        self.assertEqual(y, 0)

    # ------------------------------------------------------------------------

    def test_equal(self):
        self.assertTrue(self.__coordinates == ([143, 17, 150, 98, 0.2]))
        self.assertFalse(self.__coordinates != ([143, 17, 150, 98, 0.2]))
        self.assertTrue(self.__coordinates != ([14, 1, 150, 98]))

        c = sppasCoords(143, 17, 150, 98)
        self.assertTrue(self.__coordinates.__eq__(c))

        c = sppasCoords(143, 17, 150, 200)
        self.assertFalse(self.__coordinates.__eq__(c))

    # ------------------------------------------------------------------------

    def test_copy(self):
        c = self.__coordinates.copy()
        self.assertEqual(c, sppasCoords(143, 17, 150, 98))
        self.assertTrue(self.__coordinates.__eq__(c))

    # ------------------------------------------------------------------------

    def test_overlap(self):
        c1 = sppasCoords(0, 0, 30, 30)
        c2 = sppasCoords(10, 10, 40, 40)
        self.assertEqual(c1.area(), 900)
        self.assertEqual(c2.area(), 1600)
        self.assertEqual(c1.intersection_area(c2), 400)

        s, o = c1.overlap(c2)
        # the overlapped area is overlapping other of XX percent of its area
        self.assertEqual(s, float(400)/float(1600) * 100.)
        # the overlapped area is overlapping self of XX percent of its area
        self.assertEqual(o, float(400)/float(900) * 100.)

    # ------------------------------------------------------------------------

    def test_print(self):
        c = sppasCoords(143, 17, 0, 0)
        self.assertEqual(str(c), "(143,17)")

        c = sppasCoords(143, 17, 0, 0, 0.123)
        self.assertEqual(str(c), "(143,17): 0.123000")

        c = sppasCoords(143, 17, 150, 98)
        self.assertEqual(str(c), "(143,17) (150,98)")

        c = sppasCoords(143, 17, 150, 98, 0.998)
        self.assertEqual(str(c), "(143,17) (150,98): 0.998000")

    # ------------------------------------------------------------------------

    def test_euclidian_distance(self):
        c = sppasCoords(2, 2)
        self.assertEqual(0, c.euclidian_distance(c))
        self.assertEqual(round(math.sqrt(8), 0), c.euclidian_distance(sppasCoords(4, 4)))
        self.assertEqual(round(math.sqrt(68), 0), c.euclidian_distance(sppasCoords(10, 4)))

    # ------------------------------------------------------------------------

    def test_to_coords(self):
        c = sppasCoords.to_coords((143, 17))
        self.assertEqual(str(c), "(143,17)")
        c = sppasCoords.to_coords((143, 17, 0.123))
        self.assertEqual(str(c), "(143,17): 0.123000")
        c = sppasCoords.to_coords((143, 17, 150, 98))
        self.assertEqual(str(c), "(143,17) (150,98)")
        c = sppasCoords.to_coords((143, 17, 150, 98, 0.998))
        self.assertEqual(str(c), "(143,17) (150,98): 0.998000")
        c = sppasCoords.to_coords((143, 17, 150, 98, 0.998, 'a', 'b'))
        self.assertEqual(str(c), "(143,17) (150,98): 0.998000")

        with self.assertRaises(TypeError):
            sppasCoords.to_coords("toto")

        with self.assertRaises(TypeError):
            sppasCoords.to_coords(("x", "y"))

        with self.assertRaises(TypeError):
            sppasCoords.to_coords(("3", "4"))
